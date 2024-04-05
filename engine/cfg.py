"""Extracting the CFG from the AST."""
from math import comb
from operator import indexOf
import z3
from z3 import Solver, Int, BitVec, Context, BitVecSort, ExprRef, BitVecRef, If, BitVecVal, And
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement, SingleStatement, And, Constant, Rvalue, Plus, Input, Output
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block, SystemCall, Land, InstanceList, IntConst, Partselect, Ioport
from pyverilog.vparser.ast import Value, Reg, Initial, Eq, Identifier, Initial,  NonblockingSubstitution, Decl, Always, Assign, NotEql, Case, Pointer
from pyverilog.vparser.ast import Concat, BlockingSubstitution, Parameter, StringConst, Wire, PortArg, Instance
from .execution_manager import ExecutionManager
from .symbolic_state import SymbolicState
from copy import deepcopy
import os
from optparse import OptionParser
from typing import Optional
import random, string
import time
import gc
from itertools import product, permutations, combinations
import logging
from helpers.utils import to_binary
from strategies.dfs import DepthFirst
import sys
import networkx as nx
import matplotlib.pyplot as plt


class CFG:
    """CFG of Verilog RTL."""
    # basic blocks. A list made up of slices of all_nodes determined by partition_points.
    basic_block_list = []

    # for partitioning
    curr_idx = 0

    # add all nodes in the always block
    all_nodes = []

    # partition indices
    partition_points = set()
    partition_points.add(0)

    # the edgelist will be a list of tuples of indices of the ast nodes blocks
    edgelist = []

    # edges between basic blocks, determined by the above edgelist
    cfg_edges = []

    # indices of basic blocks that need to connect to dummy exit node
    leaves = set()

    #paths... list of paths with start and end being the dummy nodes
    paths = []

    # name corresponding to the module. there could be multiple always blocks (or CFGS) per module
    module_name = ""

    # Decl nodes outside the always block to be executed once up front for all paths
    decls = []

    # Combinational logic nodes outside the always block to be visited twice for all paths
    comb = []

    # the nodes in the AST that correspond to always blocks
    always_blocks = []

    # the nodes in the AST that correspond to initial blocks
    initial_blocks = []

    # branch-point set
    # for each basic statement, there may be some indpendent branching points
    ind_branch_points = {1: set()}

    # stack of flags for if we are looking at a block statement
    block_smt = [False]

    # how many nested block statements we've seen so far
    block_stmt_depth = 0

    #submodules defined
    submodules = []

    # basic blocks that don't have out edges
    dangling = set()

    def reset(self):
        """Return to defaults."""
        self.basic_block_list = []
        self.curr_idx = 0
        self.all_nodes = []
        self.partition_points = set()
        self.partition_points.add(0)
        self.edgelist = []
        self.cfg_edges = []
        self.leaves = set()
        self.paths = []
        #self.always_blocks = []
        self.ind_branch_points = {1: set()}
        self.block_smt = [False]
        self.block_stmt_depth = 0
        self.dangling = set()

    def compute_direction(self, path):
        """Given a path, figure out the direction"""
        directions = []
        for i in range(1, len(path)-1):
            if path[i] + 1 == path[i + 1]:
                directions.append(1)
            else:
                directions.append(0)
        return directions
    
    def resolve_independent_branch_pts(self, idx):
        """After visiting a basic block, form edges between the branching points at that same level."""
        if len(self.ind_branch_points[idx]) <= 1:
            return 

        res = list(combinations(self.ind_branch_points[idx], r=len(self.ind_branch_points[idx])))
        self.edgelist += res 

    def get_initial(self, m: ExecutionManager, s: SymbolicState, ast):
        """Populate the initial block list."""
        if isinstance(ast, Block):
            ast = ast.statements

        if hasattr(ast, '__iter__'):
            for item in ast:
                if isinstance(item, IfStatement):
                    self.get_initial(m, s, item.true_statement) 
                    self.get_initial(m, s, item.false_statement)
                elif isinstance(ast, CaseStatement):
                    return self.get_initial(m, s, ast.caselist) 
                elif isinstance(ast, ForStatement):
                    return self.get_initial(m, s, ast.statement) 
                elif isinstance(item, Block):
                    self.get_initial(m, s, item.items)
                elif isinstance(item, Always):
                    ...           
                elif isinstance(item, Initial):
                    self.initial_blocks.append(item)
                elif isinstance(item, SingleStatement):
                    self.get_initial(m, s, item.statement)
                else:
                    if isinstance(item, Decl):
                        self.decls.append(item)
                    elif isinstance(item, Assign):
                        self.comb.append(item)
                    elif isinstance(item, InstanceList):
                        print("FOUND SUBModule!")
                        print(item.module)
                        self.submodules.append(item)
                    ...
        elif ast != None:
            if isinstance(ast, IfStatement):
                self.get_initial(m, s, ast.true_statement) 
                self.get_initial(m, s, ast.false_statement)
            elif isinstance(ast, CaseStatement):
                self.get_initial(m, s, ast.caselist)
            elif isinstance(ast, ForStatement):
                self.get_initial(m, s, ast.statement)
            elif isinstance(ast, Block):
                self.get_initial(m, s, ast.items)
            elif isinstance(ast, Always):
                ...        
            elif isinstance(ast, Initial):
                self.initial_blocks.append(ast)
            elif isinstance(ast, SingleStatement):
                self.get_initial(m, s, ast.statement)
            else:
                if isinstance(ast, Decl):
                    self.decls.append(ast)
                elif isinstance(ast, Assign):
                    self.comb.append(ast)
                elif isinstance(ast, InstanceList):
                    print("FOUND SUBModule!")
                ...


    def get_always(self, m: ExecutionManager, s: SymbolicState, ast):
        """Populate the always block list."""
        if isinstance(ast, Block):
            ast = ast.statements

        if hasattr(ast, '__iter__'):
            for item in ast:
                if isinstance(item, IfStatement):
                    self.get_always(m, s, item.true_statement) 
                    self.get_always(m, s, item.false_statement)
                elif isinstance(ast, CaseStatement):
                    return self.get_always(m, s, ast.caselist) 
                elif isinstance(ast, ForStatement):
                    return self.get_always(m, s, ast.statement) 
                elif isinstance(item, Block):
                    self.get_always(m, s, item.items)
                elif isinstance(item, Always):
                    self.always_blocks.append(item)           
                elif isinstance(item, Initial):
                    self.get_always(m, s, item.statement)
                elif isinstance(item, SingleStatement):
                    self.get_always(m, s, item.statement)
                else:
                    if isinstance(item, Decl):
                        self.decls.append(item)
                    elif isinstance(item, Assign):
                        self.comb.append(item)
                    elif isinstance(item, InstanceList):
                        self.submodules.append(item)
                    ...
        elif ast != None:
            if isinstance(ast, IfStatement):
                self.get_always(m, s, ast.true_statement) 
                self.get_always(m, s, ast.false_statement)
            elif isinstance(ast, CaseStatement):
                self.get_always(m, s, ast.caselist)
            elif isinstance(ast, ForStatement):
                self.get_always(m, s, ast.statement)
            elif isinstance(ast, Block):
                self.get_always(m, s, ast.items)
            elif isinstance(ast, Always):
                self.always_blocks.append(ast)          
            elif isinstance(ast, Initial):
                self.get_always(m, s, ast.statement)
            elif isinstance(ast, SingleStatement):
                self.get_always(m, s, ast.statement)
            else:
                if isinstance(ast, Decl):
                    self.decls.append(ast)
                elif isinstance(ast, Assign):
                    self.comb.append(ast)
                elif isinstance(ast, InstanceList):
                    print("FOUND SUBModule!")
                ...

    def basic_blocks(self, m:ExecutionManager, s: SymbolicState, ast):
        """We want to get a list of AST nodes partitioned into basic blocks.
        Need to keep track of children/parent indices of each block in the list."""
        if hasattr(ast, '__iter__'):
            for item in ast:
                if self.block_smt[self.block_stmt_depth] and (isinstance(item, IfStatement) or isinstance(item, CaseStatement)
                or isinstance(item, ForStatement)):
                    if not self.block_stmt_depth in self.ind_branch_points:
                        self.ind_branch_points[self.block_stmt_depth] = set()

                    self.ind_branch_points[self.block_stmt_depth].add(self.curr_idx)

                if isinstance(item, IfStatement):
                    self.all_nodes.append(item)
                    self.partition_points.add(self.curr_idx)
                    parent_idx = self.curr_idx
                    self.basic_blocks(m, s, item.true_statement)
                    snapshot_before_else = deepcopy(self.all_nodes)
                    edge_1 = (parent_idx, self.curr_idx)
                    self.partition_points.add(self.curr_idx)
                    self.basic_blocks(m, s, item.false_statement)
                    
                    # if there are no other nodes added after this 
                    # AST traversal, then we know that we don't have the 
                    # else to worry about, shouldn't add the edge
                    if len(self.all_nodes) > len(snapshot_before_else):
                        edge_2 = (parent_idx, self.curr_idx)
                        self.edgelist.append(edge_2)
                        self.partition_points.add(self.curr_idx)
                        self.curr_idx += 1
                    self.edgelist.append(edge_1)
                elif isinstance(item, CaseStatement):
                    self.all_nodes.append(ast)
                    self.partition_points.add(self.curr_idx)
                    self.curr_idx += 1
                    self.basic_blocks(m, s, item.caselist) 
                elif isinstance(item, ForStatement):
                    self.all_nodes.append(ast)
                    self.partition_points.add(self.curr_idx)
                    self.curr_idx += 1
                    self.basic_blocks(m, s, item.statement) 
                elif isinstance(item, Block):
                    print("found block stmt")
                    self.basic_blocks(m, s, item.items)
                elif isinstance(item, Always):
                    self.all_nodes.append(item)
                    self.curr_idx += 1
                    self.basic_blocks(m, s, item.statement)             
                elif isinstance(item, Initial):
                    self.all_nodes.append(item)
                    self.curr_idx += 1
                    self.basic_blocks(m, s, item.statement)
                else:
                    self.all_nodes.append(item)
                    self.curr_idx += 1

        elif ast != None:
            if isinstance(ast, IfStatement):
                self.partition_points.add(self.curr_idx)
                self.all_nodes.append(ast)
                parent_idx = self.curr_idx
                self.curr_idx += 1
                edge_1 = (parent_idx, self.curr_idx)
                self.partition_points.add(self.curr_idx)
                self.basic_blocks(m, s, ast.true_statement) 
                edge_2 = (parent_idx, self.curr_idx)
                self.partition_points.add(self.curr_idx)
                self.basic_blocks(m, s, ast.false_statement)
                self.edgelist.append(edge_1)
                self.edgelist.append(edge_2)
            elif isinstance(ast, CaseStatement):
                self.all_nodes.append(ast)
                self.partition_points.add(self.curr_idx)
                self.curr_idx += 1
                self.basic_blocks(m, s, ast.caselist)
            elif isinstance(ast, ForStatement):
                self.all_nodes.append(ast)
                self.partition_points.add(self.curr_idx)
                self.curr_idx += 1
                self.basic_blocks(m, s, ast.statement) 
            elif isinstance(ast, Block):
                self.block_stmt_depth += 1
                self.block_smt.append(True)
                self.basic_blocks(m, s, ast.statements)
                if self.block_stmt_depth in self.ind_branch_points:
                    self.resolve_independent_branch_pts(self.block_stmt_depth)
                self.block_smt.pop()
                self.block_stmt_depth -= 1
            elif isinstance(ast, Always):
                self.all_nodes.append(ast)
                self.curr_idx += 1
                self.basic_blocks(m, s, ast.statement)             
            elif isinstance(ast, Initial):
                self.all_nodes.append(ast)
                self.curr_idx += 1
                self.basic_blocks(m, s, ast.statement)
            else:
                self.all_nodes.append(ast)
                self.curr_idx += 1

    def map_to_path(self):
        """Just return the paths"""
        return self.paths

    def partition(self):
        """Slices up the list of all nodes into the actual basic blocks"""
        self.partition_points.add(len(self.all_nodes)-1)
        partition_list = list(self.partition_points)
        for i in range(len(partition_list)-1):
            if i > 0: 
                basic_block = self.all_nodes[partition_list[i]+1:partition_list[i+1]+1]
                self.basic_block_list.append(basic_block)
            else:
                basic_block = self.all_nodes[partition_list[i]:partition_list[i+1]+1]
                self.basic_block_list.append(basic_block)

    def find_basic_block(self, node_idx) -> int:
        """Given a node index, find the index of the basic block that we're in."""
        if node_idx < len(self.all_nodes):
            node = self.all_nodes[node_idx]
        else:
            node = self.all_nodes[len(self.all_nodes)-1]
        found_block = None
        for block in self.basic_block_list:
            if node in block:
                found_block = indexOf(self.basic_block_list, block)
                return found_block

    def make_paths(self):
        """Map the edge between AST nodes to a path between basic blocks."""
        for edge in self.edgelist:
            block1 = self.find_basic_block(edge[0])
            block2 = self.find_basic_block(edge[1])
            path = (block1, block2)
            self.cfg_edges.append(path)

    def find_dangling(self):
        """Find dangling nodes in CFG, to know which should connect to exit."""
        ends = set(edges[1] for edges in self.cfg_edges)
        for edge in self.cfg_edges:
            for end in ends:
                if edge[0] == end and edge[1] == end:
                    self.dangling.add(end)
        

    def find_leaves(self):
        """Find leaves in cfg, to know which nodes need to connect to dummy exit."""
        starts = set(edge[0] for edge in self.cfg_edges)
        ends = set(edges[1] for edges in self.cfg_edges)
        self.leaves = ends - starts

    def display_cfg(self, graph):
        """Display CFG."""
        subax1 = plt.subplot(121)
        nx.draw(graph, with_labels=True, font_weight='bold')
        plt.show()

    def build_cfg(self, m: ExecutionManager, s: SymbolicState):
        """Build networkx digraph."""
        self.cfg_edges = []
        self.make_paths()

        G = nx.DiGraph()
        for block in self.basic_block_list:
            # converts the list into a tuple. Needs to be hashable type
            G.add_node(indexOf(self.basic_block_list, block), data=tuple(block))
        
        G.add_node(-1, data="Dummy Start")
        G.add_node(-2, data="Dummy End")

        for edge in self.cfg_edges:
            start = edge[0]
            end = edge[1]
            G.add_edge(start, end)
        
        # edgecase lol
        if self.edgelist == []:
            G.add_edge(0, -2)

        # link up dummy start
        G.add_edge(-1, 0)
        self.find_leaves()
        
        # link of dummy exit
        for leaf in self.leaves:
            G.add_edge(leaf, -2)

        self.find_dangling()
        # also need to link up the dangling nodes that had self loops
        for dangling in self.dangling:
            G.add_edge(dangling, -2)


        #self.display_cfg(G)

        #traversed = nx.edge_dfs(G, source=-1)
        self.paths = list(nx.all_simple_paths(G, source=-1, target=-2))
        #print(list(traversed))
        #print(list(self.paths))