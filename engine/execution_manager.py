"""The main class that controls the flow of execution. Most of the bookkeeping happens here, and 
a lot of this information will probably be useful when working in a specific search strategy."""
from __future__ import annotations
from .symbolic_state import SymbolicState
from pyverilog.vparser.ast import ModuleDef
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement, SingleStatement, And, Constant, Rvalue, Plus, Input, Output
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block, SystemCall, Land, InstanceList, IntConst, Partselect, Ioport
from pyverilog.vparser.ast import Value, Reg, Initial, Eq, Identifier, Initial,  NonblockingSubstitution, Decl, Always, Assign, NotEql, Case
from pyverilog.vparser.ast import Concat, BlockingSubstitution, Parameter, StringConst, Wire, PortArg
from typing import Optional
from helpers.rvalue_to_z3 import solve_pc

CONDITIONALS = (IfStatement, ForStatement, WhileStatement, CaseStatement)

class ExecutionManager:
    num_paths: int = 1
    curr_level: int = 0
    path_code: str = "0" * 12
    ast_str: str = ""
    debugging: bool = False
    abandon: bool = False
    assertion_violation: bool = False
    in_always: bool = False
    modules = {}
    dependencies = {}
    updates = {}
    seen = {}
    final = False
    completed = []
    is_child: bool = False
    # Map of module name to path nums for child module
    child_num_paths = {}    
    # Map of module name to path code for child module
    child_path_codes = {}
    paths = []
    config = {}
    names_list = []
    instance_count = {}
    seen_mod = {}
    opt_1: bool = True
    curr_module: str = ""
    piece_wise: bool = False
    child_range: range = None
    always_writes = {}
    curr_always = None
    opt_2: bool = True
    opt_3: bool = False
    assertions = []
    blocks_of_interest = []
    init_run: bool = False
    ignore = False
    inital_state = {}
    engine_instance = None

    def execute_child(self, ast: ModuleDef, state: SymbolicState, parent_manager: Optional[ExecutionManager]) -> None:
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
        manager_sub.path_code = parent_manager.config[ast.name]
        manager_sub.seen = parent_manager.seen

        # mark this exploration of the submodule as seen and store the state so we don't have to explore it again.
        if parent_manager.seen_mod[ast.name][manager_sub.path_code] == {}:
            parent_manager.seen_mod[ast.name][manager_sub.path_code] = state.store
        else:
            ...
            #print("already seen this")
        # i'm pretty sure we only ever want to do 1 loop here
        for i in range(1):
        #for i in range(manager_sub.num_paths):
            manager_sub.path_code = parent_manager.config[ast.name]
            #print("------------------------")
            #print(f"{ast.name} Path {i}")
            self.visit_module(manager_sub, state, ast, parent_manager.modules)
            if (parent_manager.assertion_violation):
                print("Assertion violation")
                parent_manager.assertion_violation = False
                solve_pc(state.pc)
            parent_manager.curr_level = 0
            #state.pc.reset()
        #manager.path_code = to_binary(0)
        #print(f" finishing {ast.name}")
        if manager_sub.ignore:
            parent_manager.ignore = True
        parent_manager.engine_instance.module_depth -= 1
        #manager.is_child = False
        ## print(state.store)

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
                return self.count_conditionals_2(m, items.caselist) + 1
        return 0


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