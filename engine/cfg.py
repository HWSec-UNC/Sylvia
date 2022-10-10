"""Extracting the CFG from the AST."""
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
import os
from optparse import OptionParser
from typing import Optional
import random, string
import time
import gc
from itertools import product, permutations
import logging
from helpers.utils import to_binary
from strategies.dfs import DepthFirst
import sys
import networkx as nx
import matplotlib.pyplot as plt


class CFG:
    """CFG of Verilog RTL."""
    basic_block_list = []
    # for partitioning
    curr_idx = 0

    # add all nodes in the always block
    all_nodes = []

    # partition indices
    partition_points = set()
    partition_points.add(0)

    # basic blocks. A list made up of slices of all_nodes determined by partition_points.
    basic_blocks = []

    # the edgelist will be a list of tuples of indices of the ast nodes blocks
    edgelist = []

    # edges between basic blocks, determined by the above edgelist
    cfg_edges = []
    
    def get_always(self, m: ExecutionManager, s: SymbolicState, ast):
        """get always block"""
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
                    #basic_block.append(item)
                    self.get_always(m, s, item.items)
                elif isinstance(item, Always):
                    print("found")
                    return item            
                elif isinstance(item, Initial):
                    #basic_block.append(item)
                    self.get_always(m, s, item.statement)
                else:
                    ...
        elif ast != None:
            if isinstance(ast, IfStatement):
                self.get_always(m, s, ast.true_statement) 
                #self.basic_blocks(m, s, ast.false_statement))
            elif isinstance(ast, CaseStatement):
                self.get_always(m, s, ast.caselist)
            elif isinstance(ast, ForStatement):
                self.get_always(m, s, ast.statement)
            elif isinstance(ast, Block):
                self.get_always(m, s, ast.items)
            elif isinstance(ast, Always):
                return ast            
            elif isinstance(ast, Initial):
                self.get_always(m, s, ast.statement)
            else:
                return None

    def basic_blocks(self, m:ExecutionManager, s: SymbolicState, ast):
        """We want to get a list of AST nodes partitioned into basic blocks.
        Need to keep track of children/parent indices of each block in the list."""

        if hasattr(ast, '__iter__'):
            if isinstance(ast[0], IfStatement):
                self.all_nodes.append(ast[0])
                self.partition_points.add(self.curr_idx)
                parent_idx = self.curr_idx
                self.curr_idx += 1
                edge_1 = (parent_idx, self.curr_idx)
                self.partition_points.add(self.curr_idx)
                self.basic_blocks(m, s, ast[0].true_statement) 
                edge_2 = (parent_idx, self.curr_idx)
                self.partition_points.add(self.curr_idx)
                self.basic_blocks(m, s, ast[0].false_statement)
                self.edgelist.append(edge_1)
                self.edgelist.append(edge_2)
            elif isinstance(ast[0], CaseStatement):
                self.all_nodes.append(ast)
                self.partition_points.add(self.curr_idx)
                self.curr_idx += 1
                self.basic_blocks(m, s, ast[0].caselist) 
            elif isinstance(ast[0], ForStatement):
                self.all_nodes.append(ast)
                self.partition_points.append(self.curr_idx)
                self.curr_idx += 1
                self.basic_blocks(m, s, ast[0].statement) 
            elif isinstance(ast[0], Block):
                #self.all_nodes.append(ast[0])
                #self.curr_idx += 1
                self.basic_blocks(m, s, ast[0].items)
            elif isinstance(ast[0], Always):
                # print("entering always")
                self.all_nodes.append(ast[0])
                self.curr_idx += 1
                self.basic_blocks(m, s, ast[0].statement)             
            elif isinstance(ast[0], Initial):
                self.all_nodes.append(ast[0])
                self.curr_idx += 1
                self.basic_blocks(m, s, ast[0].statement)
            else:
                print(f"{ast[0]} else top")
                self.curr_idx += 1
                self.all_nodes.append(ast[0])
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
                #self.all_nodes.append(ast)
                #self.curr_idx += 1
                self.basic_blocks(m, s, ast.statements)
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

    def partition(self):
        """Slices up the list of all nodes into the actual basic blocks"""
        self.partition_points.add(len(self.all_nodes)-1)
        partition_list = list(self.partition_points)
        print(partition_list)
        for i in range(len(partition_list)):
            if i == len(partition_list) - 1: 
                basic_block = self.all_nodes[partition_list[i]]
                self.basic_block_list.append(basic_block)
            elif i > 0: 
                basic_block = self.all_nodes[partition_list[i]+1:partition_list[i+1]+1]
                self.basic_block_list.append(basic_block)
            else:
                basic_block = self.all_nodes[partition_list[i]:partition_list[i+1]+1]
                self.basic_block_list.append(basic_block)
            print(f" {basic_block} {i}")

    def find_basic_block(self, node_idx: int):
        """Given a node index, find the basic block that we're in."""

    def make_paths(self):
        """Map the edge between AST nodes to a path between basic blocks."""
        for edge in self.edgelist:
            block1 = self.find_basic_block(edge[0])
            block2 = self.find_basic_block(edge[1])
            path = (block1, block2)
            self.cfg_edges.append(path)


    def build_cfg(self, m: ExecutionManager, s: SymbolicState):
        """Build networkx digraph."""
        G = nx.Graph()
        for block in self.basic_block_list:
            hashable_block = (tuple(block[0]), block[1])
            G.add_node(hashable_block)
        
        G.add_node(("Dummy Start", -1))
        G.add_node(("Dummy End", 3))

        for u in G.nodes():
            for v in G.nodes():
                if u[1] > v[1] and v[1] != -1 and u[1] !=3 :
                    G.add_edge(u, v)
                elif v[1] == -1 and u[1] == 0:
                    G.add_edge(u, v)
                elif u[1] == 3 and v[1] == 1:
                    G.add_edge(u, v)

        print(G.edges())
        subax1 = plt.subplot(121)
        nx.draw(G, with_labels=True, font_weight='bold')
        plt.show()