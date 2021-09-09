import pyverilog
from z3 import Solver, Int, BitVec, Context
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import Description, ModuleDef
import sys
import os
from optparse import OptionParser


INFO = "Verilog code parser"
VERSION = pyverilog.__version__
USAGE = "Usage: python example_parser.py file ..."

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
    return ""

def parse_expr(class_name: str) -> str:
    """Return the Expression type."""
    if "Reg" in class_name:
        return "Reg"

def visit_stmt(stmt) -> None:
    """Visit a statement."""
    if stmt.cname == "Decl":
        for item in stmt.list:
            item.cname = parse_expr(str(type(item)))
            ref_name = item.name
            ref_width = int(item.width.msb.value) + 1
            # probs dont want to actually call z3 here, just when looking at PC
            x = BitVec(ref_name, ref_width)
    elif stmt.cname == "Always":
        sens_list = stmt.sens_list
        print(sens_list)
        print(sens_list.list[0].sig) # clock
        print(sens_list.list[0].type) # posedge
        sub_stmt = stmt.statement
        print(sub_stmt)

def main():
    """Entrypoint of the program."""
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
    # x = Int('x')
    # y = Int('y')
    # s = Solver()
    # s.add(x > 0)
    # s.add(x < 2)
    # s.add(y == x + 1)
    # print(s.check())
    # model = s.model()
    # print(model)
    description: Description = ast.children()[0]
    module: ModuleDef = description.children()[0]
    stmts = module.items
    for stmt in stmts:
        stmt.cname = parse_stmt(str(type(stmt)))
        print(stmt.cname)
        visit_stmt(stmt)
    # for lineno, directive in directives:
        # print('Line %d : %s' % (lineno, directive))

if __name__ == '__main__':
    main()