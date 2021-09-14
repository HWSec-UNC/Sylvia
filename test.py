import pyverilog
from z3 import Solver, Int, BitVec, Context, BitVecSort, ExprRef
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block
from pyverilog.vparser.ast import Value, Reg
import sys
import os
from optparse import OptionParser


INFO = "Verilog code parser"
VERSION = pyverilog.__version__
USAGE = "Usage: python example_parser.py file ..."

CONDITIONALS = ["IfStatement", "WhileStatement", "ForStatement", "CaseStatement"]
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
    assertion_violation: bool = False

class ExecutionManager:
    num_paths: int = 1
    curr_level: int = 0
    path_code: str = "0" * 12
    ast_str: str = ""
    debugging: bool = False
    abandon: bool = False

def to_binary(i: int, digits: int = 32) -> str:
    num: str = bin(i)[2:]
    padding_len: int = digits - len(num)
    return ("0" * padding_len) + num

class ExecutionEngine:
    branch: bool = True

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
        for item in stmts:
            item.cname = parse_stmt(str(type(item)))
            if item.cname in CONDITIONALS:
                m.num_paths *= 2
            if item.cname == "Block":
                self.count_conditionals(m, item.items)
            elif item.cname == "Always":
                self.count_conditionals(m, item.statement)

    def init_run(self, m: ExecutionManager, module: ModuleDef) -> None:
        """Initalize run."""
        self.count_conditionals(m, module.items)

    def visit_expr(self, s: SymbolicState, expr: Value) -> None:
        if isinstance(expr, Reg):
            s.store[expr.name] = "i"
        return None

    def visit_stmt(self, m: ExecutionManager, s: SymbolicState, stmt: Node):
        if stmt.cname == "Decl":
            for item in stmt.list:
                if isinstance(item, Value):
                    self.visit_expr(s, item)
                else:
                    self.visit_stmt(m, s, item)
                # ref_name = item.name
                # ref_width = int(item.width.msb.value) + 1
                #  dont want to actually call z3 here, just when looking at PC
                # x = BitVec(ref_name, ref_width)
        elif stmt.cname == "Always":
            sens_list = stmt.sens_list
            # print(sens_list.list[0].sig) # clock
            # print(sens_list.list[0].type) # posedge
            sub_stmt = stmt.statement
            self.visit_stmt(m, s, sub_stmt)
        elif stmt.cname == "Assign":
            s.store[stmt.left.var.name] = "hi"
        elif stmt.cname == "NonblockSub":
            s.store[stmt.left.var.name] = "yo"
        elif stmt.cname == "Block":
            for item in stmt.statements: 
                self.visit_stmt(m, s, item)

    def visit_module(self, m: ExecutionManager, s: SymbolicState, module: ModuleDef):
        """Visit module."""
        m.currLevel = 0
        for item in module.items:
            if isinstance(item, Value):
                self.visit_expr()
            else:
                self.visit_stmt(m, s, item)
        
            
    def execute(self, ast: ModuleDef) -> None:
        """Drives symbolic execution."""
        state: SymbolicState = SymbolicState()
        manager: ExecutionManager = ExecutionManager()
        manager.debugging = False
        self.init_run(manager, ast)
        print(f"Num paths: {manager.num_paths}")
        for i in range(manager.num_paths):
            self.visit_module(manager, state, ast)
        print(state.store)


def showVersion():
    print(INFO)
    print(VERSION)
    print(USAGE)
    sys.exit()

def parse_stmt(class_name: str) -> str:
    """Return the general statement type."""
    if "Decl" in class_name:
        return "Decl"
    elif "Always" in class_name:
        return "Always"
    elif "Assign" in class_name:
        return "Assign"
    elif "IfStatement" in class_name:
        return "IfStatement"
    elif "WhileStatement" in class_name:
        return "WhileStatement"
    elif "ForStatement" in class_name:
        return "ForStatement"
    elif "CaseStatement" in class_name:
        return "ClassStatement"
    elif "Block" in class_name:
        return "Block"
    elif "NonblockingSubstitution" in class_name:
        return "NonblockSub"
    return ""

def parse_expr(class_name: str) -> str:
    """Return the Expression type."""
    if "Reg" in class_name:
        return "Reg"

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

    ast.show()

    description: Description = ast.children()[0]
    module: ModuleDef = description.children()[0]
    engine.execute(module)
    # for lineno, directive in directives:
        # print('Line %d : %s' % (lineno, directive))

if __name__ == '__main__':
    main()