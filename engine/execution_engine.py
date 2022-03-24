import z3
from z3 import Solver, Int, BitVec, Context, BitVecSort, ExprRef, BitVecRef, If, BitVecVal, And
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement, SingleStatement, And, Constant, Rvalue, Plus, Input, Output
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block, SystemCall, Land, InstanceList, IntConst, Partselect, Ioport
from pyverilog.vparser.ast import Value, Reg, Initial, Eq, Identifier, Initial,  NonblockingSubstitution, Decl, Always, Assign, NotEql, Case, Pointer
from pyverilog.vparser.ast import Concat, BlockingSubstitution, Parameter, StringConst, Wire, PortArg
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

CONDITIONALS = (IfStatement, ForStatement, WhileStatement, CaseStatement)

class ExecutionEngine:
    module_depth: int = 0
    search_strategy = DepthFirst()
    debug: bool = False

    def check_pc_SAT(self, s: Solver, constraint: ExprRef) -> bool:
        """Check if pc is satisfiable before taking path."""
        # the push adds a backtracking point if unsat
        s.push()
        s.add(constraint)
        result = s.check()
        if str(result) == "sat":
            return True
        else:
            s.pop()
            return False

    def check_dup(self, m: ExecutionManager) -> bool:
        """Checks if the current path is a duplicate/worth exploring."""
        for i in range(len(m.path_code)):
            if m.path_code[i] == "1" and i in m.completed:
                return True
        return False

    def solve_pc(self, s: Solver) -> bool:
        """Solve path condition."""
        result = str(s.check())
        if str(result) == "sat":
            model = s.model()
            return True
        else:
            return False

    def count_conditionals_2(self, m:ExecutionManager, items) -> int:
        """Rewrite to actually return an int."""
        stmts = items
        if isinstance(items, Block):
            stmts = items.statements
            items.cname = "Block"

        if hasattr(stmts, '__iter__'):
            for item in stmts:
                if isinstance(item, CONDITIONALS):
                    if isinstance(item, IfStatement) or isinstance(item, CaseStatement):
                        if isinstance(item, IfStatement):
                            return self.count_conditionals_2(m, item.true_statement) + self.count_conditionals_2(m, item.false_statement)  + 1
                        if isinstance(items, CaseStatement):
                            return self.count_conditionals_2(m, items.caselist) + 1
                if isinstance(item, Block):
                    return self.count_conditionals_2(m, item.items)
                elif isinstance(item, Always):
                   return self.count_conditionals_2(m, item.statement)             
                elif isinstance(item, Initial):
                    return self.count_conditionals_2(m, item.statement)
        elif items != None:
            if isinstance(items, IfStatement):
                return  ( self.count_conditionals_2(m, items.true_statement) + 
                self.count_conditionals_2(m, items.false_statement)) + 1
            if isinstance(items, CaseStatement):
                return self.count_conditionals_2(m, items.caselist) + len(items.caselist)
        return 0

    def count_conditionals(self, m: ExecutionManager, items):
        """Identify control flow structures to count total number of paths."""
        stmts = items
        if isinstance(items, Block):
            stmts = items.statements
            items.cname = "Block"
        if hasattr(stmts, '__iter__'):
            for item in stmts:
                if isinstance(item, CONDITIONALS):
                    if isinstance(item, IfStatement) or isinstance(item, CaseStatement):
                        if isinstance(item, IfStatement):
                            m.num_paths *= 2
                            self.count_conditionals(m, item.true_statement)
                            self.count_conditionals(m, item.false_statement)
                        if isinstance(item, CaseStatement):
                            for case in item.caselist:
                                m.num_paths *= 2
                                self.count_conditionals(m, case.statement)
                if isinstance(item, Block):
                    self.count_conditionals(m, item.items)
                elif isinstance(item, Always):
                    self.count_conditionals(m, item.statement)             
                elif isinstance(item, Initial):
                    self.count_conditionals(m, item.statement)
                elif isinstance(item, Case):
                    self.count_conditionals(m, item.statement)
        elif items != None:
            if isinstance(items, IfStatement):
                m.num_paths *= 2
                self.count_conditionals(m, items.true_statement)
                self.count_conditionals(m, items.false_statement)
            if isinstance(items, CaseStatement):
                for case in items.caselist:
                    m.num_paths *= 2
                    self.count_conditionals(m, case.statement)

    def lhs_signals(self, m: ExecutionManager, items):
        """Take stock of which signals are written to in which always blocks for COI analysis."""
        stmts = items
        if isinstance(items, Block):
            stmts = items.statements
            items.cname = "Block"
        if hasattr(stmts, '__iter__'):
            for item in stmts:
                if isinstance(item, IfStatement) or isinstance(item, CaseStatement):
                    if isinstance(item, IfStatement):
                        self.lhs_signals(m, item.true_statement)
                        self.lhs_signals(m, item.false_statement)
                    if isinstance(item, CaseStatement):
                        for case in item.caselist:
                            self.lhs_signals(m, case.statement)
                if isinstance(item, Block):
                    self.lhs_signals(m, item.items)
                elif isinstance(item, Always):
                    m.curr_always = item
                    m.always_writes[item] = []
                    self.lhs_signals(m, item.statement)             
                elif isinstance(item, Initial):
                    self.lhs_signals(m, item.statement)
                elif isinstance(item, Case):
                    self.lhs_signals(m, item.statement)
                elif isinstance(item, Assign):
                    if isinstance(item.left.var, Partselect):
                        if m.curr_always is not None and item.left.var.var.name not in m.always_writes[m.curr_always]:
                            m.always_writes[m.curr_always].append(item.left.var.var.name)
                    elif isinstance(item.left.var, Pointer):
                        m.always_writes[m.curr_always].append(item.left.var.ptr)
                    elif isinstance(item.left.var, Concat) and m.curr_always is not None:
                        for sub_item in item.left.var.list:
                            m.always_writes[m.curr_always].append(sub_item.name)
                    elif m.curr_always is not None and item.left.var.name not in m.always_writes[m.curr_always]:
                        m.always_writes[m.curr_always].append(item.left.var.name)
                elif isinstance(item, NonblockingSubstitution):
                    if isinstance(item.left.var, Partselect):
                        if m.curr_always is not None and item.left.var.var.name not in m.always_writes[m.curr_always]:
                            m.always_writes[m.curr_always].append(item.left.var.var.name)
                    elif m.curr_always is not None and item.left.var.name not in m.always_writes[m.curr_always]:
                        m.always_writes[m.curr_always].append(item.left.var.name)
                elif isinstance(item, BlockingSubstitution):
                    if isinstance(item.left.var, Partselect):
                        if m.curr_always is not None and item.left.var.var.name not in m.always_writes[m.curr_always]:
                            m.always_writes[m.curr_always].append(item.left.var.var.name)
                    elif m.curr_always is not None and item.left.var.name not in m.always_writes[m.curr_always]:
                        m.always_writes[m.curr_always].append(item.left.var.name)
        elif items != None:
            if isinstance(items, IfStatement):
                self.lhs_signals(m, items.true_statement)
                self.lhs_signals(m, items.false_statement)
            if isinstance(items, CaseStatement):
                for case in items.caselist:
                    self.lhs_signals(m, case.statement)
            elif isinstance(items, Assign):
                if m.curr_always is not None and items.left.var.name not in m.always_writes[m.curr_always]:
                    m.always_writes[m.curr_always].append(items.left.var.name)
            elif isinstance(items, NonblockingSubstitution):
                if isinstance(items.left.var, Concat):
                    for sub_item in items.left.var.list:
                        if sub_item.name not in m.always_writes[m.curr_always]:
                            m.always_writes[m.curr_always].append(sub_item.name)
                elif m.curr_always is not None and items.left.var.name not in m.always_writes[m.curr_always]:
                    m.always_writes[m.curr_always].append(items.left.var.name)
            elif isinstance(items, BlockingSubstitution):
                if m.curr_always is not None and items.left.var.name not in m.always_writes[m.curr_always]:
                    m.always_writes[m.curr_always].append(items.left.var.name)


    def get_assertions(self, m: ExecutionManager, items):
        """Traverse the AST and get the assertion violating conditions."""
        stmts = items
        if isinstance(items, Block):
            stmts = items.statements
            items.cname = "Block"
        if hasattr(stmts, '__iter__'):
            for item in stmts:
                if isinstance(item, IfStatement) or isinstance(item, CaseStatement):
                    if isinstance(item, IfStatement):
                        # starting to check for the assertions
                        if isinstance(item.true_statement, Block):
                            if isinstance(item.true_statement.statements[0], SingleStatement):
                                if isinstance(item.true_statement.statements[0].statement, SystemCall) and "ASSERTION" in item.true_statement.statements[0].statement.args[0].value:
                                    m.assertions.append(item.cond)
                                    print("assertion found")
                            else:     
                                self.get_assertions(m, item.true_statement)
                            #self.get_assertions(m, item.false_statement)
                    if isinstance(item, CaseStatement):
                        for case in item.caselist:
                            self.get_assertions(m, case.statement)
                elif isinstance(item, Block):
                    self.get_assertions(m, item.items)
                elif isinstance(item, Always):
                    self.get_assertions(m, item.statement)             
                elif isinstance(item, Initial):
                    self.get_assertions(m, item.statement)
                elif isinstance(item, Case):
                    self.get_assertions(m, item.statement)
        elif items != None:
            if isinstance(items, IfStatement):
                self.get_assertions(m, items.true_statement)
                self.get_assertions(m, items.false_statement)
            if isinstance(items, CaseStatement):
                for case in items.caselist:
                    self.get_assertions(m, case.statement)

    def map_assertions_signals(self, m: ExecutionManager):
        """Map the assertions to a list of relevant signals."""
        signals = []
        for assertion in m.assertions:
            # TODO write function to exhaustively get all the signals from assertions
            # this is just grabbing the left most
            if isinstance(assertion.right, IntConst):
                ...
            elif isinstance(assertion.right.left, Identifier):
                signals.append(assertion.right.left.name)
        return signals

    def assertions_always_intersect(self, m: ExecutionManager):
        """Get the always blocks that have the signals relevant to the assertions."""
        signals_of_interest = self.map_assertions_signals(m)
        blocks_of_interest = []
        for block in m.always_writes:
            for signal in signals_of_interest:
                if signal in m.always_writes[block]:
                    blocks_of_interest.append(block)
        m.blocks_of_interest = blocks_of_interest


    def seen_all_cases(self, m: ExecutionManager, bit_index: int, nested_ifs: int) -> bool:
        """Checks if we've seen all the cases for this index in the bit string.
        We know there are no more nested conditionals within the block, just want to check 
        that we have seen the path where this bit was turned on but the thing to the left of it
        could vary."""
        # first check if things less than me have been added.
        # so index 29 shouldnt be completed before 30
        for i in range(bit_index + 1, 32):
            if not i in m.completed:
                return False
        count = 0
        seen = m.seen
        #print(seen)
        for path in seen[m.curr_module]:
            if path[bit_index] == '1':
                count += 1
        if count >  2 * nested_ifs:
            return True
        return False

    def module_count(self, m: ExecutionManager, items) -> None:
        """Traverse a top level module and count up the instances of each type of module."""
        if isinstance(items, Block):
            items = items.statements
        if hasattr(items, '__iter__'):
            for item in items:
                if isinstance(item, InstanceList):
                    if item.module in m.instance_count:
                        m.instance_count[item.module] += 1
                    else:
                        m.instance_count[item.module] = 1
                    self.module_count(m, item.instances)
                if isinstance(item, Block):
                    self.module_count(m, item.items)
                elif isinstance(item, Always):
                    self.module_count(m, item.statement)             
                elif isinstance(item, Initial):
                    self.module_count(m, item.statement)
        elif items != None:
                if isinstance(items, InstanceList):
                    if items.module in m.instance_count:
                        m.instance_count[items.module] += 1
                    else:
                        m.instance_count[items.module] = 1
                    self.module_count(m, items.instances)



    def init_run(self, m: ExecutionManager, module: ModuleDef) -> None:
        """Initalize run."""
        m.init_run = True
        self.count_conditionals(m, module.items)
        self.lhs_signals(m, module.items)
        self.get_assertions(m, module.items)
        m.init_run = False
        #self.module_count(m, module.items)


    def populate_child_paths(self, manager: ExecutionManager) -> None:
        """Populates child path codes based on number of paths."""
        for child in manager.child_num_paths:
            manager.child_path_codes[child] = []
            if manager.piece_wise:
                manager.child_path_codes[child] = []
                for i in manager.child_range:
                    manager.child_path_codes[child].append(to_binary(i))
            else:
                for i in range(manager.child_num_paths[child]):
                    manager.child_path_codes[child].append(to_binary(i))

    def populate_seen_mod(self, manager: ExecutionManager) -> None:
        """Populates child path codes but in a format to keep track of corresponding states that we've seen."""
        for child in manager.child_num_paths:
            manager.seen_mod[child] = {}
            for i in range(manager.child_num_paths[child]):
                manager.seen_mod[child][(to_binary(i))] = {}

    def merge_states(self, manager: ExecutionManager, state: SymbolicState, store):
        """Merges two states."""
        for key, val in state.store.items():
            if type(val) != dict:
                continue
            else:
                for key2, var in val.items():
                    if var in store.values():
                        prev_symbol = state.store[key][key2]
                        new_symbol = store[key][key2]
                        state.store[key][key2].replace(prev_symbol, new_symbol)
                    else:
                        state.store[key][key2] = store[key][key2]

    def piece_wise_execute(self, ast: ModuleDef, manager: Optional[ExecutionManager], modules) -> None:
        """Drives symbolic execution piecewise when number of paths is too large not to breakup. 
        We break it up to avoid the memory blow up."""
        print("piece")
        self.module_depth += 1
        manager.piece_wise = True
        state: SymbolicState = SymbolicState()
        if manager is None:
            manager: ExecutionManager = ExecutionManager()
            manager.debugging = False
        modules_dict = {}
        for module in modules:
            modules_dict[module.name] = module
            manager.seen_mod[module.name] = {}
            sub_manager = ExecutionManager()
            manager.names_list.append(module.name)
            self.init_run(sub_manager, module)
            self.module_count(manager, module.items)
            if module.name in manager.instance_count:
                manager.instances_seen[module.name] = 0
                num_instances = manager.instance_count[module.name]
                for i in range(num_instances):
                    instance_name = f"{module.name}_{i}"
                    manager.names_list.append(instance_name)
                    manager.child_path_codes[instance_name] = to_binary(0)
                    manager.child_num_paths[instance_name] = sub_manager.num_paths
                    manager.config[instance_name] = to_binary(0)
                    state.store[instance_name] = {}
                    manager.dependencies[instance_name] = {}
                    manager.cond_assigns[instance_name] = {}
                manager.names_list.remove(module.name)
            else:
      
                manager.child_path_codes[module.name] = to_binary(0)
                manager.child_num_paths[module.name] = sub_manager.num_paths
                manager.config[module.name] = to_binary(0)
                state.store[module.name] = {}
                manager.dependencies[module.name] = {}
                manager.cond_assigns[module.name] = {}

        total_paths = sum(manager.child_num_paths.values())
        print(total_paths)
        manager.piece_wise = True
        #TODO: things piecewise, say 10,000 at a time.
        for i in range(0, total_paths, 10000):
            manager.child_range = range(i*10000, i*10000+10000)
            self.populate_child_paths(manager)
            if len(modules) > 1:
                self.populate_seen_mod(manager)
                manager.opt_1 = True
            else:
                manager.opt_1 = False
            manager.modules = modules_dict
            paths = list(product(*manager.child_path_codes.values()))
            #print(f" Upper bound on num paths {len(paths)}")
            self.init_run(manager, ast)

            manager.seen = {}
            for name in manager.names_list:
                manager.seen[name] = []
            manager.curr_module = manager.names_list[0]

            stride_length = len(manager.names_list)
            # for each combinatoin of multicycle paths
            for i in range(len(paths)):
                manager.cycle = 0

                for j in range(0, len(paths[i])):
                #print(f"Single cycle path {j} {paths[i][j]}")
                #print(f"yee {manager.names_list[j  % len(manager.names_list)]}")
                    for name in manager.names_list:
                        manager.config[name] = paths[i][j]

                manager.path_code = paths[i][0]
                manager.prev_store = state.store
                manager.init_state(state, manager.prev_store, ast)
                self.search_strategy.visit_module(manager, state, ast, modules_dict)
                manager.cycle += 1
                manager.curr_level = 0
                if self.check_dup(manager):
                # #if False:
                    if self.debug:
                        print("----------------------")
                    ...
                else:
                    if self.debug:
                        print("------------------------")
                    ...
                    #print(f"{ast.name} Path {i}")
                manager.seen[ast.name].append(manager.path_code)
                if (manager.assertion_violation):
                    print("Assertion violation")
                    counterexample = {}
                    symbols_to_values = {}
                    if self.solve_pc(state.pc):
                        solved_model = state.pc.model()
                        decls =  solved_model.decls()
                        for item in decls:
                            symbols_to_values[item.name()] = solved_model[item]

                        # plug in phase
                        for module in state.store:
                            for signal in state.store[module]:
                                for symbol in symbols_to_values:
                                    if state.store[module][signal] == symbol:
                                        counterexample[signal] = symbols_to_values[symbol]

                        print(counterexample)
                    else:
                        print("UNSAT")
                    return 
                for module in manager.dependencies:
                    module = {}
                state.pc.reset()

                manager.ignore = False
                manager.abandon = False
                manager.reg_writes.clear()
                for name in manager.names_list:
                    state.store[name] = {}

            #manager.path_code = to_binary(0)
            #print(f" finishing {ast.name}")
            self.module_depth -= 1

    def multicycle_helper(self, ast: ModuleDef, modules_dict, paths,  s: SymbolicState, manager: ExecutionManager, num_cycles: int) -> None:
        """Recursive Helper to resolve multi cycle execution."""
        #TODO: Add in the merging state element to this helper function
        for a in range(num_cycles):
            for i in range(len(paths)):
                for j in range(len(paths[i])):
                    manager.config[manager.names_list[j]] = paths[i][j]


    #@profile     
    def execute(self, ast: ModuleDef, modules, manager: Optional[ExecutionManager], directives, num_cycles: int) -> None:
        """Drives symbolic execution."""
        gc.collect()
        print(f"Executing for {num_cycles} clock cycles")
        self.module_depth += 1
        state: SymbolicState = SymbolicState()
        if manager is None:
            manager: ExecutionManager = ExecutionManager()
            manager.debugging = False
            modules_dict = {}
            for module in modules:
                modules_dict[module.name] = module
                manager.seen_mod[module.name] = {}
                sub_manager = ExecutionManager()
                manager.names_list.append(module.name)
                self.init_run(sub_manager, module)
                self.module_count(manager, module.items) 
                if module.name in manager.instance_count:
                    manager.instances_seen[module.name] = 0
                    num_instances = manager.instance_count[module.name]
                    for i in range(num_instances):
                        instance_name = f"{module.name}_{i}"
                        manager.names_list.append(instance_name)
                        manager.child_path_codes[instance_name] = to_binary(0)
                        manager.child_num_paths[instance_name] = sub_manager.num_paths
                        manager.config[instance_name] = to_binary(0)
                        state.store[instance_name] = {}
                        manager.dependencies[instance_name] = {}
                        manager.cond_assigns[instance_name] = {}
                    manager.names_list.remove(module.name)
                else:        
                    manager.child_path_codes[module.name] = to_binary(0)
                    manager.child_num_paths[module.name] = sub_manager.num_paths
                    manager.config[module.name] = to_binary(0)
                    state.store[module.name] = {}
                    manager.dependencies[module.name] = {}
                    manager.cond_assigns[module.name] = {}
            total_paths = 1
            for x in manager.child_num_paths.values():
                total_paths *= x
            #print(total_paths)
            # have do do things piece wise
            if total_paths > 100000:
                start = time.time()
                self.piece_wise_execute(ast, manager, modules)
                end = time.time()
                print(f"Elapsed time {end - start}")
                sys.exit()
            self.populate_child_paths(manager)
            if len(modules) > 1:
                self.populate_seen_mod(manager)
                #manager.opt_1 = True
            else:
                manager.opt_1 = False
            manager.modules = modules_dict
            paths = list(product(*manager.child_path_codes.values(), repeat=int(num_cycles)))
            #paths = list(product(*manager.child_path_codes.values()))

            #print(f" Upper bound on num paths {len(paths)}")
        # print(manager.instance_count)
        # print(manager.always_writes)
        # print(manager.assertions)

        if self.debug:
            manager.debug = True
        self.assertions_always_intersect(manager)
        #print(manager.blocks_of_interest)
        #print(f"Num paths: {manager.num_paths}")
        #print(f"Upper bound on num paths {manager.num_paths}")
        manager.seen = {}
        for name in manager.names_list:
            manager.seen[name] = []
        manager.curr_module = manager.names_list[0]


        stride_length = len(manager.names_list)
        # for each combinatoin of multicycle paths
        for i in range(len(paths)):
            manager.cycle = 0
            # extract the single cycle path code for this iteration and execute, then merge the states
            for j in range(0, len(paths[i])):
                #print(f"Single cycle path {j} {paths[i][j]}")
                #print(f"yee {manager.names_list[j  % len(manager.names_list)]}")
                for name in manager.names_list:
                    manager.config[name] = paths[i][j]
            # makes assumption top level module is first in line
            manager.path_code = paths[i][0]
            manager.prev_store = state.store
            manager.init_state(state, manager.prev_store, ast)
            self.search_strategy.visit_module(manager, state, ast, modules_dict)
            manager.cycle += 1
            manager.curr_level = 0
            for module_name in manager.instances_seen:
                manager.instances_seen[module_name] = 0
            if self.check_dup(manager):
            #if False:
                if self.debug:
                    print("------------------------")
                ...
                #continue
            else:
                if self.debug:
                    print("------------------------")
                ...
                #print(f"{ast.name} Path {i}")
                
            manager.seen[ast.name].append(manager.path_code)
            if (manager.assertion_violation):
                print("Assertion violation")
                #manager.assertion_violation = False
                counterexample = {}
                symbols_to_values = {}
                if self.solve_pc(state.pc):
                    solved_model = state.pc.model()
                    decls =  solved_model.decls()
                    for item in decls:
                        symbols_to_values[item.name()] = solved_model[item]

                    # plug in phase
                    for module in state.store:
                        for signal in state.store[module]:
                            for symbol in symbols_to_values:
                                if state.store[module][signal] == symbol:
                                    counterexample[signal] = symbols_to_values[symbol]

                    print(counterexample)
                else:
                    print("UNSAT")
                return
            for module in manager.dependencies:
                module = {}
            state.pc.reset()
            
            manager.ignore = False
            manager.abandon = False
            manager.reg_writes.clear()
            for name in manager.names_list:
                state.store[name] = {}

            # for module_store in state.store:
            #     for signal in module_store:
            #         if signal != "CLK" or signal != "RST":
            #             print("hi")
            #             state.store[module_store][signal] = init_symbol()
        #manager.path_code = to_binary(0)
        #print(f" finishing {ast.name}")
        self.module_depth -= 1
        ## print(state.store)


    def execute_child(self, ast: ModuleDef, state: SymbolicState, manager: Optional[ExecutionManager]) -> None:
        """Drives symbolic execution of child modules."""
        # different manager
        # same state
        # dont call pc solve
        manager_sub = ExecutionManager()
        manager_sub.is_child = True
        manager_sub.curr_module = ast.name
        self.init_run(manager_sub, ast)
        #print(f"Num paths: {manager.num_paths}")
        #print(f"Num paths {manager_sub.num_paths}")
        manager_sub.path_code = manager.config[ast.name]
        manager_sub.seen = manager.seen

        # mark this exploration of the submodule as seen and store the state so we don't have to explore it again.
        if manager.seen_mod[ast.name][manager_sub.path_code] == {}:
            manager.seen_mod[ast.name][manager_sub.path_code] = state.store
        else:
            ...
            #print("already seen this")
        # i'm pretty sure we only ever want to do 1 loop here
        for i in range(1):
        #for i in range(manager_sub.num_paths):
            manager_sub.path_code = manager.config[ast.name]
            #print("------------------------")
            #print(f"{ast.name} Path {i}")
            self.search_strategy.visit_module(manager_sub, state, ast, manager.modules)
            if (manager.assertion_violation):
                print("Assertion violation")
                manager.assertion_violation = False
                counterexample = {}
                symbols_to_values = {}
                if self.solve_pc(state.pc):
                    solved_model = state.pc.model()
                    decls =  solved_model.decls()
                    for item in decls:
                        symbols_to_values[item.name()] = solved_model[item]

                    # plug in phase
                    for module in state.store:
                        for signal in state.store[module]:
                            for symbol in symbols_to_values:
                                if state.store[module][signal] == symbol:
                                    counterexample[signal] = symbols_to_values[symbol]

                    print(counterexample)
                else:
                    print("UNSAT")
            manager.curr_level = 0
            #state.pc.reset()
        #manager.path_code = to_binary(0)
        #print(f" finishing {ast.name}")
        if manager_sub.ignore:
            manager.ignore = True
        self.module_depth -= 1
        #manager.is_child = False
        ## print(state.store)
