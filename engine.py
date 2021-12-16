import pyverilog
import z3
from z3 import Solver, Int, BitVec, Context, BitVecSort, ExprRef, BitVecRef, If, BitVecVal
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement, SingleStatement, And, Constant, Rvalue, Plus, Input, Output
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block, SystemCall, Land, InstanceList, IntConst, Partselect, Ioport
from pyverilog.vparser.ast import Value, Reg, Initial, Eq, Identifier, Initial,  NonblockingSubstitution, Decl, Always, Assign, NotEql
import sys
import os
from optparse import OptionParser
from typing import Optional
import random, string
import time


INFO = "Verilog code parser"
VERSION = pyverilog.__version__
USAGE = "Usage: python example_parser.py file ..."

CONDITIONALS = (IfStatement, ForStatement, WhileStatement, CaseStatement)
EXPRESSIONS = ["Decl"]

class SymbolicState:
    pc = Solver()
    sort = BitVecSort(32)
    clock_cycle: int = 0
    store = {}

    # set to true when evaluating a conditoin so that
    # evaluating the expression knows to add the expr to the
    # PC, set to false after
    cond: bool = False

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
    seen = []
    final = False
    completed = []

def to_binary(i: int, digits: int = 32) -> str:
    num: str = bin(i)[2:]
    padding_len: int = digits - len(num)
    return  ("0" * padding_len) + num 

def parse_expr_to_Z3(e: Value, s: Solver, branch: bool):
    """Takes in a complex Verilog Expression and converts it to 
    a Z3 query."""
    if isinstance(e, And):
        lhs = parse_expr_to_Z3(e.left, s, branch)
        rhs = parse_expr_to_Z3(e.right, s, branch)
        return s.add(lhs and rhs)
    elif isinstance(e, Identifier):
        return BitVec(e.name + "_0", 32)
    elif isinstance(e, Constant):
        return BitVec(int(e.value), 32)
    elif isinstance(e, Eq):
        lhs = parse_expr_to_Z3(e.left, s, branch)
        rhs = parse_expr_to_Z3(e.right, s, branch)
        if branch:
            s.add(lhs == rhs)
        else:
            s.add(lhs != rhs)
        return (lhs == rhs)
    elif isinstance(e, NotEql):
        lhs = parse_expr_to_Z3(e.left, s, branch)
        rhs = parse_expr_to_Z3(e.right, s, branch)
        if branch:          
            # only RHS is BitVec (Lhs is a more complex expr)
            if isinstance(rhs, z3.z3.BitVecRef) and not isinstance(lhs, BitVecRef):
                c = If(lhs, BitVecVal(1, 32), BitVecVal(0, 32))
                s.add(c != rhs)
            else:
                s.add(lhs != rhs)
        else:
            # only RHS is bitVEC 
            if isinstance(rhs, z3.z3.BitVecRef) and not isinstance(lhs, BitVecRef):
                c = If(lhs, BitVecVal(1, 32), BitVecVal(0, 32))
                s.add(c == rhs)
            else:
                s.add(lhs == rhs)
    elif isinstance(e, Land):
        lhs = parse_expr_to_Z3(e.left, s, branch)
        rhs = parse_expr_to_Z3(e.right, s, branch)
        return s.add(lhs and rhs)
    return s


def parse_rvalue(rvalue: Rvalue, store) -> (str, str, str): 
    #print(rvalue)
    tokens = str(rvalue).replace('(','').replace(')','').split()
    #print(tokens)
    op = ""
    if 'Plus' in tokens[0]:
        op = "+"
    elif 'Minus' in tokens[0]:
        op = '-'
    lhs = tokens[1]
    rhs = tokens[2]
    if not lhs.isdigit():
        if lhs == "Plus":
            lhs = tokens[2]
            rhs = tokens[3]
        lhs = store[lhs]
    if not rhs.isdigit():
        # print(store)
        # print(rvalue)
        rhs = store[rhs]
    return (lhs, op, rhs)


def init_symbol() -> str:
    """Initializes signal with random symbol."""
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    
     
class ExecutionEngine:
    branch: bool = True
    module_depth: int = 0

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
        print(m.completed)
        for i in range(len(m.path_code)):
            if m.path_code[i] == "1" and i in m.completed:
                return True
        return False

    def solve_pc(self, s: Solver) -> None:
        """Solve path condition."""
        result = str(s.check())
        if str(result) == "sat":
            model = s.model()
            print(model)
        else:
            print("UNSAT/FAILED")

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
                        m.num_paths *= 2
                        if isinstance(item, IfStatement):
                            self.count_conditionals(m, item.true_statement)
                            self.count_conditionals(m, item.false_statement)
                if isinstance(item, Block):
                    self.count_conditionals(m, item.items)
                elif isinstance(item, Always):
                    self.count_conditionals(m, item.statement)             
                elif isinstance(item, Initial):
                    self.count_conditionals(m, item.statement)
        elif items != None:
            if isinstance(items, IfStatement):
                m.num_paths *= 2
                self.count_conditionals(m, items.true_statement)
                self.count_conditionals(m, items.false_statement)


    def seen_all_cases(self, m: ExecutionManager, bit_index: int, nested_ifs: int) -> bool:
        """Checks if we've seen all the cases for this index in the bit string.
        We know there are no more nested conditionals within the block, just want to check 
        that we have seen the path where this bit was turned on but the thing to the left of it
        could vary."""
        print(f"bit index: {bit_index}")

        # first check if things less than me have been added.
        # so index 29 shouldnt be completed before 30
        for i in range(bit_index + 1, 32):
            if not i in m.completed:
                return False
        count = 0
        seen = m.seen
        for path in seen:
            if path[bit_index ] == '1':
                count += 1
        print(f"count: {count}")
        if count >=  nested_ifs:
            return True
        return False
        

    def init_run(self, m: ExecutionManager, module: ModuleDef) -> None:
        """Initalize run."""
        self.count_conditionals(m, module.items)

    def visit_expr(self, m: ExecutionManager, s: SymbolicState, expr: Value) -> None:
        if isinstance(expr, Reg):
            s.store[expr.name] =''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        elif isinstance(expr, Eq):
            # assume left is identifier
            x = BitVec(s.store[expr.left.name], 32)
            # assume right is a value
            y = BitVec(int(expr.right.value), 32)
            if self.branch:
                s.pc.add(x == y)
            else: 
                s.pc.add(x != y)
        elif isinstance(expr, Identifier):
            # change this to one since inst is supposed to just be 1 bit width
            # and the identifier class actually doesn't have a width param
            x = BitVec(s.store[expr.name], 1)
            y = BitVec(1, 1)
            if self.branch:
                s.pc.add(x == y)
            else: 
                s.pc.add(x != y)


        # Handling Assertions
        elif isinstance(expr, NotEql):
            parse_expr_to_Z3(expr, s.pc, self.branch)
            # x = BitVec(expr.left.name, 32)
            # y = BitVec(int(expr.right.value), 32)
            # if self.branch:
            #     s.pc.add(x != y)
            # else: 
            #     s.pc.add(x == y)
        elif isinstance(expr, Land):
            parse_expr_to_Z3(expr, s.pc, self.branch)
        return None

    def visit_stmt(self, m: ExecutionManager, s: SymbolicState, stmt: Node):
        #print(type(stmt))
        if isinstance(stmt, Decl):
            for item in stmt.list:
                if isinstance(item, Value):
                    self.visit_expr(m, s, item)
                else:
                    self.visit_stmt(m, s, item)
                # ref_name = item.name
                # ref_width = int(item.width.msb.value) + 1
                #  dont want to actually call z3 here, just when looking at PC
                # x = BitVec(ref_name, ref_width)
        elif isinstance(stmt, Always):
            sens_list = stmt.sens_list
            # print(sens_list.list[0].sig) # clock
            # print(sens_list.list[0].type) # posedge
            sub_stmt = stmt.statement
            m.in_always = True
            self.visit_stmt(m, s, sub_stmt)
            for signal in m.dependencies:
                if m.dependencies[signal] in m.updates:
                    if m.updates[m.dependencies[signal]][0] == 1:
                        prev_symbol = m.updates[m.dependencies[signal]][1]
                        new_symbol = s.store[m.dependencies[signal]]
                        s.store[signal] = s.store[signal].replace(prev_symbol, new_symbol)
        elif isinstance(stmt, Assign):
            if isinstance(stmt.right.var, IntConst):
                s.store[stmt.left.var.name] = stmt.right.var.value
            elif isinstance(stmt.right.var, Partselect):
                s.store[stmt.left.var.name] = f"{s.store[stmt.right.var.var.name]}[{stmt.right.var.msb}:{stmt.right.var.lsb}]"
                m.dependencies[stmt.left.var.name] = stmt.right.var.var.name
                m.updates[stmt.left.var.name] = 0
            else:
                (lhs, op, rhs) = parse_rvalue(stmt.right.var, s.store)
                if (lhs, op, rhs) != ("","",""):
                    s.store[stmt.left.var.name] = lhs + op + rhs
                else:
                    s.store[stmt.left.var.name] = s.store[stmt.right.var.name]
        elif isinstance(stmt, NonblockingSubstitution):
            prev_symbol = s.store[stmt.left.var.name]
            if isinstance(stmt.right.var, IntConst):
                s.store[stmt.left.var.name] = stmt.right.var.value
            else:
                (lhs, op, rhs) = parse_rvalue(stmt.right.var, s.store)
                if (lhs, op, rhs) != ("","",""):
                    s.store[stmt.left.var.name] = lhs + op + rhs
                else:
                    s.store[stmt.left.var.name] = s.store[stmt.right.var.name]
            m.updates[stmt.left.var.name] = (1, prev_symbol)
        elif isinstance(stmt, Block):
            for item in stmt.statements: 
                self.visit_stmt(m, s, item)
        elif isinstance(stmt, Initial):
            self.visit_stmt(m, s, stmt.statement)
        elif isinstance(stmt, IfStatement):
            # print("forking")
            # print(stmt.__dict__)
            m.curr_level += 1
            self.cond = True
            bit_index = len(m.path_code) - m.curr_level

            if (m.path_code[len(m.path_code) - m.curr_level] == '1'):
                self.branch = True

                # check if i am the final thing/no more conditionals after me
                # basically, we never want me to be true again after this bc we are wasting time reexploring this

                self.visit_expr(m, s, stmt.cond)
                if (m.abandon):
                    m.abandon = False
                    print("Abandoning this path!")
                    return
                nested_ifs = self.count_conditionals_2(m, stmt.true_statement)
                print(f"Nested ifs {nested_ifs}")
                diff = 32 - bit_index
                print(diff)
                print(m.seen)
                # m.curr_level == (32 - bit_index) this is always true
                #if nested_ifs == 0 and m.curr_level < 2 and self.seen_all_cases(m, bit_index, nested_ifs):
                if self.seen_all_cases(m, bit_index, nested_ifs):
                    m.completed.append(bit_index)
                self.visit_stmt(m, s, stmt.true_statement)
            else:
                self.branch = False
                self.visit_expr(m, s, stmt.cond)
                if (m.abandon):
                    print("Abandoning this path!")
                    m.abandon = False
                    return
                self.visit_stmt(m, s, stmt.false_statement)
        elif isinstance(stmt, SystemCall):
            m.assertion_violation = True
        elif isinstance(stmt, SingleStatement):
            self.visit_stmt(m, s, stmt.statement)
        elif isinstance(stmt, InstanceList):
            if stmt.module in m.modules:
                print(stmt.module)
                self.execute_child(m.modules[stmt.module], s, m)

    def visit_module(self, m: ExecutionManager, s: SymbolicState, module: ModuleDef):
        """Visit module."""
        m.currLevel = 0
        print(m.path_code)
        params = module.paramlist.params
        ports = module.portlist.ports
        for port in ports:
            if isinstance(port, Ioport):
                s.store[port.first.name] = init_symbol()
            else:
                s.store[port.name] = init_symbol()

        for item in module.items:
            if isinstance(item, Value):
                self.visit_expr(m, s, item)
            else:
                self.visit_stmt(m, s, item)
        print("Final state:")
        print(s.store)
        print("Final path condition:")
        print(s.pc)
        
            
    def execute(self, ast: ModuleDef, modules, manager: Optional[ExecutionManager]) -> None:
        """Drives symbolic execution."""
        self.module_depth += 1
        state: SymbolicState = SymbolicState()
        if manager is None:
            manager: ExecutionManager = ExecutionManager()
            manager.debugging = False
            modules_dict = {}
            for module in modules:
                modules_dict[module.name] = module
            manager.modules = modules_dict
        self.init_run(manager, ast)
        #print(f"Num paths: {manager.num_paths}")
        print(f"Upper bound on num paths {manager.num_paths}")
        manager.seen = []
        for i in range(manager.num_paths):
            manager.path_code = to_binary(i)
            if self.check_dup(manager):
            #if False:
                continue
            else:
                print("------------------------")
                print(f"Path {i}")
            self.visit_module(manager, state, ast)
            manager.seen.append(manager.path_code)
            print(manager.updates)
            print(manager.completed)
            if (manager.assertion_violation):
                print("Assertion violation")
                manager.assertion_violation = False
                self.solve_pc(state.pc)
            manager.curr_level = 0
            manager.dependencies = {}
            state.pc.reset()
        #manager.path_code = to_binary(0)
        print(f" finishing {ast.name}")
        self.module_depth -= 1
        ## print(state.store)


    def execute_child(self, ast: ModuleDef, state: SymbolicState, manager: Optional[ExecutionManager]) -> None:
        """Drives symbolic execution of child modules."""
        # different manager
        # same state
        # dont call pc solve
        manager = ExecutionManager()
        self.init_run(manager, ast)
        #print(f"Num paths: {manager.num_paths}")
        print(f"Num paths {manager.num_paths}")
        for i in range(manager.num_paths):
            manager.path_code = to_binary(i)
            self.visit_module(manager, state, ast)
            if (manager.assertion_violation):
                print("Assertion violation")
                manager.assertion_violation = False
                self.solve_pc(state.pc)
            manager.curr_level = 0
            state.pc.reset()
        #manager.path_code = to_binary(0)
        print(f" finishing {ast.name}")
        self.module_depth -= 1
        ## print(state.store)
    

def showVersion():
    print(INFO)
    print(VERSION)
    print(USAGE)
    sys.exit()
    
def main():
    """Entrypoint of the program."""
    engine: ExecutionEngine = ExecutionEngine()
    optparser = OptionParser()
    optparser.add_option("-v", "--version", action="store_true", dest="showversion",
                         default=False, help="Show the version")
    optparser.add_option("-I", "--include", dest="include", action="append",
                         default=[], help="Include path")
    optparser.add_option("-D", dest="define", action="append",
                         default=[], help="Macro Definition")
    (options, args) = optparser.parse_args()

    filelist = args
    if options.showversion:
        showVersion()

    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)

    if len(filelist) == 0:
        showVersion()

    ast, directives = parse(filelist,
                            preprocess_include=options.include,
                            preprocess_define=options.define)

    #ast.show()

    description: Description = ast.children()[0]
    top_level_module: ModuleDef = description.children()[0]
    modules = description.definitions
    start = time.time()
    engine.execute(top_level_module, modules, None)
    end = time.time()
    print(f"Elapsed time {end - start}")

if __name__ == '__main__':
    main()