"""Extracting the CFG from the AST."""
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

    def basic_blocks(self, m: ExecutionManager, s: SymbolicState, ast, basic_block=[]):
        """Populates the basic block list."""
        leader = ast
        if isinstance(ast, Block):
            ast = ast.statements

        if hasattr(ast, '__iter__'):
            print("up!")
            #for item in ast:
            if isinstance(ast[0], IfStatement):
                basic_block.append(ast[0])
                self.basic_block_list.append((basic_block, 0))
                then_block = []
                self.basic_blocks(m, s, ast[0].true_statement, then_block) 
                self.basic_block_list.append((then_block, 1))
                else_block = []
                self.basic_blocks(m, s, ast[0].false_statement, else_block)
                self.basic_block_list.append((else_block, 1))
            elif isinstance(ast, CaseStatement):
                return self.basic_blocks(m, s, ast.caselist) 
            elif isinstance(ast, ForStatement):
                return self.basic_blocks(m, s, ast.statement) 
            elif isinstance(ast[0], Block):
                #basic_block.append(item)
                self.basic_blocks(m, s, ast[0].items)
            elif isinstance(ast[0], Always):
                print("entering always")
                #basic_block.append(item)
                self.basic_block_list.append(basic_block)
                basic_block = []
                self.basic_blocks(m, s, ast[0].statement, basic_block)             
            elif isinstance(ast[0], Initial):
                #basic_block.append(item)
                self.basic_blocks(m, s, ast[0].statement)
            else:
                print(f"{ast[0]} else top")
                basic_block.append(ast[0])
            #self.basic_block_list.append(basic_block)
        elif ast != None:
            if isinstance(ast, IfStatement):
                return self.basic_blocks(m, s, ast.true_statement) 
                #self.basic_blocks(m, s, ast.false_statement))
            elif isinstance(ast, CaseStatement):
                return self.basic_blocks(m, s, ast.caselist)
            elif isinstance(ast, ForStatement):
                return self.basic_blocks(m, s, ast.statement)
            elif isinstance(ast, Block):
                basic_block.append(ast)
                return self.basic_blocks(m, s, ast.items)
            elif isinstance(ast, Always):
                basic_block.append(ast)
                return self.basic_blocks(m, s, ast.statement)             
            elif isinstance(ast, Initial):
                basic_block.append(ast)
                return self.basic_blocks(m, s, ast.statement)
            else:
                basic_block.append(ast)

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