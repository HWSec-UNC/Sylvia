import pyverilog
import z3
from z3 import Solver, Int, BitVec, Context, BitVecSort, ExprRef, BitVecRef, If, BitVecVal
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement, SingleStatement, And, Constant, Rvalue, Plus
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block, SystemCall, Land, InstanceList, IntConst
from pyverilog.vparser.ast import Value, Reg, Initial, Eq, Identifier, Initial,  NonblockingSubstitution, Decl, Always, Assign, NotEql
import sys
import os
from optparse import OptionParser
from typing import Optional
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
    tokens = str(rvalue).replace('(','').replace(')','').split()
    print(tokens)
    op = ""
    if 'Plus' in tokens[0]:
        op = "+"
    elif 'Minus' in tokens[0]:
        op = '-'
    lhs = tokens[1]
    rhs = tokens[2]
    if not lhs.isdigit():
        lhs = store[lhs]
    if not rhs.isdigit():
        rhs = store[rhs]
    return (lhs, op, rhs)
     
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

    def solve_pc(self, s: Solver) -> None:
        """Solve path condition."""
        result = str(s.check())
        if str(result) == "sat":
            model = s.model()
            print(model)
        else:
            print("UNSAT/FAILED")

    def count_conditionals(self, m: ExecutionManager, items):
        """Identify control flow structures to count total number of paths."""
        stmts = items
        if isinstance(items, Block):
            stmts = items.statements
            items.cname = "Block"
        if hasattr(stmts, '__iter__'):
            for item in stmts:
                if isinstance(item, CONDITIONALS):
                    if isinstance(item, IfStatement):
                        m.num_paths *= 2
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

    def init_run(self, m: ExecutionManager, module: ModuleDef) -> None:
        """Initalize run."""
        self.count_conditionals(m, module.items)

    def visit_expr(self, m: ExecutionManager, s: SymbolicState, expr: Value) -> None:
        if isinstance(expr, Reg):
            s.store[expr.name] = expr.name + "_0"
        elif isinstance(expr, Eq):
            # assume left is identifier
            x = BitVec(expr.left.name, 32)
            # assume right is a value
            y = BitVec(int(expr.right.value), 32)
            if self.branch:
                s.pc.add(x == y)
            else: 
                s.pc.add(x != y)
        elif isinstance(expr, Identifier):
            # change this to one since inst is supposed to just be 1 bit width
            # and the identifier class actually doesn't have a width param
            x = BitVec(expr.name, 1)
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
        elif isinstance(stmt, Assign):
            if isinstance(stmt.right.var, IntConst):
                s.store[stmt.left.var.name] = stmt.right.var.value
            else:
                (lhs, op, rhs) = parse_rvalue(stmt.right.var, s.store)
                if (lhs, op, rhs) != ("","",""):
                    s.store[stmt.left.var.name] = lhs + op + rhs
                else:
                    s.store[stmt.left.var.name] = s.store[stmt.right.var.name]
        elif isinstance(stmt, NonblockingSubstitution):
            if isinstance(stmt.right.var, IntConst):
                s.store[stmt.left.var.name] = stmt.right.var.value
            else:
                (lhs, op, rhs) = parse_rvalue(stmt.right.var, s.store)
                if (lhs, op, rhs) != ("","",""):
                    s.store[stmt.left.var.name] = lhs + op + rhs
                else:
                    s.store[stmt.left.var.name] = s.store[stmt.right.var.name]
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
            if (m.path_code[len(m.path_code) - m.curr_level] == '1'):
                self.branch = True
                self.visit_expr(m, s, stmt.cond)
                if (m.abandon):
                    m.abandon = False
                    return
                self.visit_stmt(m, s, stmt.true_statement)
            else:
                self.branch = False
                self.visit_expr(m, s, stmt.cond)
                if (m.abandon):
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
        for item in module.items:
            if isinstance(item, Value):
                self.visit_expr()
            else:
                self.visit_stmt(m, s, item)
        
            
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