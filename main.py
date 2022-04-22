"""This file is the entrypoint of the execution."""
from __future__ import absolute_import
from __future__ import print_function
import pyverilog
import z3
from z3 import Solver, Int, BitVec, Context, BitVecSort, ExprRef, BitVecRef, If, BitVecVal, And
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement, SingleStatement, And, Constant, Rvalue, Plus, Input, Output
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block, SystemCall, Land, InstanceList, IntConst, Partselect, Ioport
from pyverilog.vparser.ast import Value, Reg, Initial, Eq, Identifier, Initial,  NonblockingSubstitution, Decl, Always, Assign, NotEql, Case
from pyverilog.vparser.ast import Concat, BlockingSubstitution, Parameter, StringConst, Wire, PortArg
import sys
import os
from optparse import OptionParser
from typing import Optional
import random, string
import time
from itertools import product
import logging
import gc
from pyverilog.vparser.preprocessor import preprocess
from engine.execution_manager import ExecutionManager
from engine.symbolic_state import SymbolicState
from helpers.rvalue_parser import tokenize, parse_tokens, evaluate
from strategies.dfs import DepthFirst
from engine.execution_engine import ExecutionEngine
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
from pyverilog.dataflow.optimizer import VerilogDataflowOptimizer
from pyverilog.dataflow.graphgen import VerilogGraphGenerator
import pygraphviz as pgv

gc.collect()

with open('errors.log', 'w'):
    pass
logging.basicConfig(filename='errors.log', level=logging.DEBUG)
logging.debug("Starting over")


INFO = "Verilog Symbolic Execution Engine"
VERSION = pyverilog.__version__
USAGE = "Usage: python3 -m main <num_cycles> <verilog_file>.v > out.txt"
    

def showVersion():
    print(INFO)
    print(VERSION)
    print(USAGE)
    sys.exit()
    
def main():
    """Entrypoint of the program."""
    engine: ExecutionEngine = ExecutionEngine()
    search_strategy: DepthFirst = DepthFirst()
    optparser = OptionParser()
    optparser.add_option("-v", "--version", action="store_true", dest="showversion",
                         default=False, help="Show the version")
    optparser.add_option("-I", "--include", dest="include", action="append",
                         default=["designs/or1200/", "darkriscv/", "designs"], help="Include path")
    optparser.add_option("-D", dest="define", action="append",
                         default=[], help="Macro Definition")
    optparser.add_option("-B", "--debug", action="store_true", dest="showdebug", help="Debug Mode")
    optparser.add_option("-t", "--top", dest="topmodule",
                         default="top", help="Top module, Default=top")
    optparser.add_option("--nobind", action="store_true", dest="nobind",
                         default=False, help="No binding traversal, Default=False")
    optparser.add_option("--noreorder", action="store_true", dest="noreorder",
                         default=False, help="No reordering of binding dataflow, Default=False")
    optparser.add_option("-o", "--output", dest="outputfile",
                         default="out.png", help="Graph file name, Default=out.png")
    optparser.add_option("-s", "--search", dest="searchtarget", action="append",
                         default=[], help="Search Target Signal")
    optparser.add_option("--walk", action="store_true", dest="walk",
                         default=False, help="Walk contineous signals, Default=False")
    optparser.add_option("--identical", action="store_true", dest="identical",
                         default=False, help="# Identical Laef, Default=False")
    optparser.add_option("--step", dest="step", type='int',
                         default=1, help="# Search Steps, Default=1")
    optparser.add_option("--reorder", action="store_true", dest="reorder",
                         default=False, help="Reorder the contineous tree, Default=False")
    optparser.add_option("--delay", action="store_true", dest="delay",
                         default=False, help="Inset Delay Node to walk Regs, Default=False")
    (options, args) = optparser.parse_args()


    num_cycles = args[0]
    filelist = args[1:]

    if options.showversion:
        showVersion()

    if options.showdebug:
        engine.debug = True

    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)

    if len(filelist) == 0:
        showVersion()

    text = preprocess(filelist, include=options.include, define=options.define)
    #print(text)
    ast, directives = parse(filelist,
                            preprocess_include=options.include,
                            preprocess_define=options.define)


    analyzer = VerilogDataflowAnalyzer(filelist, options.topmodule,
                                        noreorder=options.noreorder,
                                        nobind=options.nobind,
                                        preprocess_include=options.include,
                                        preprocess_define=options.define)
    analyzer.generate()

    directives = analyzer.get_directives()
    terms = analyzer.getTerms()
    binddict = analyzer.getBinddict()

    optimizer = VerilogDataflowOptimizer(terms, binddict)

    optimizer.resolveConstant()
    resolved_terms = optimizer.getResolvedTerms()
    resolved_binddict = optimizer.getResolvedBinddict()
    constlist = optimizer.getConstlist()

    graphgen = VerilogGraphGenerator(options.topmodule, terms, binddict,
                                      resolved_terms, resolved_binddict, constlist, options.outputfile)

    for target in options.searchtarget:
        graphgen.generate(target, walk=options.walk, identical=options.identical,
                          step=options.step)

    #graphgen.draw()

    #ast.show()
    #print(ast.children()[0].definitions)

    description: Description = ast.children()[0]
    top_level_module: ModuleDef = description.children()[0]
    modules = description.definitions
    start = time.process_time()
    engine.execute(top_level_module, modules, None, directives, num_cycles)
    end = time.process_time()
    print(f"Elapsed time {end - start}")

if __name__ == '__main__':
    main()



