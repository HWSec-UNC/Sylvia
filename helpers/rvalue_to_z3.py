"""Helpers for working with Z3, specifically parsing the symbolic expressions into 
Z3 expressions and solving for assertion violations."""

import z3
from z3 import Solver, Int, BitVec, Context, BitVecSort, ExprRef, BitVecRef, If, BitVecVal, And, IntVal, Int2BV
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement, SingleStatement, And, Constant, Rvalue, Plus, Input, Output
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block, SystemCall, Land, InstanceList, IntConst, Partselect, Ioport
from pyverilog.vparser.ast import Value, Reg, Initial, Eq, Identifier, Initial,  NonblockingSubstitution, Decl, Always, Assign, NotEql, Case
from pyverilog.vparser.ast import Concat, BlockingSubstitution, Parameter, StringConst, Wire, PortArg
from helpers.rvalue_parser import parse_tokens, tokenize
from engine.execution_manager import ExecutionManager
from engine.symbolic_state import SymbolicState

BINARY_OPS = ("Plus", "Minus", "Power", "Times", "Divide", "Mod", "Sll", "Srl", "Sla", "Sra", "LessThan",
"GreaterThan", "LessEq", "GreaterEq", "Eq", "NotEq", "Eql", "NotEql", "And", "Xor",
"Xnor", "Or", "Land", "Lor")
op_map = {"Plus": "+", "Minus": "-", "Power": "**", "Times": "*", "Divide": "/", "Mod": "%", "Sll": "<<", "Srl": ">>>",
"Sra": ">>", "LessThan": "<", "GreaterThan": ">", "LessEq": "<=", "GreaterEq": ">=", "Eq": "=", "NotEq": "!=", "Eql": "===", "NotEql": "!==",
"And": "&", "Xor": "^", "Xnor": "<->", "Land": "&&", "Lor": "||"}

def get_constants_list(new_constraint, s: SymbolicState, m: ExecutionManager):
    """Get list of constants that need to be added to z3 context from pyverilog tokens."""
    res = []
    words = new_constraint.split(" ")
    for word in words:
        if word in s.store[m.curr_module].values():
            res.append(word)
    return res


def parse_expr_to_Z3(e: Value, s: SymbolicState, m: ExecutionManager):
    """Takes in a complex Verilog Expression and converts it to 
    a Z3 query."""
    tokens_list = parse_tokens(tokenize(e, s, m))
    new_constraint = evaluate_expr(tokens_list, s, m)
    #print(f"new_constraint{new_constraint}")
    new_constants = []
    if not new_constraint is None: 
        new_constants = get_constants_list(new_constraint, s, m)
    # print(f"New consts {new_constants}")
    # decl_str = ""
    # const_decls = {}
    # for i in range(len(new_constants)):
    #     const_decls[i] = BitVec(new_constants[i], 32)
    #     decl_str += f"(declare-const {const_decls[i]} (BV32))"
    # decl_str.rstrip("\n")
    # zero_const = BitVecVal(0, 32)
    # print(f" \
    # (set-option :pp.bv.enable_int2bv true) \
    # (set-option :pp.bv_literals true) \
    # {decl_str} \
    # (assert {new_constraint})")
    # F = z3.parse_smt2_string(f" \
    # (set-option :pp.bv_literals true) \
    # {decl_str} \
    # (assert {new_constraint})", sorts={ 'BV32' : BitVecSort(32) })
 
    # print(s.pc)
    # s.pc.add(F)
    # print(s.pc)
    if isinstance(e, And):
        lhs = parse_expr_to_Z3(e.left, s, m)
        rhs = parse_expr_to_Z3(e.right, s, m)
        return s.pc.add(lhs.assertions() and rhs.assertions())
    elif isinstance(e, Identifier):
        module_name = m.curr_module
        if not e.scope is None:
            module_name = e.scope.labellist[0].name
        if s.store[module_name][e.name].isdigit():
            int_val = IntVal(int(s.store[module_name][e.name]))
            return Int2BV(int_val, 32)
        else:
            return BitVec(s.store[module_name][e.name], 32)
    elif isinstance(e, Constant):
        int_val = IntVal(e.value)
        return Int2BV(int_val, 32)
    elif isinstance(e, Eq):
        lhs = parse_expr_to_Z3(e.left, s, m)
        rhs = parse_expr_to_Z3(e.right, s, m)
        if m.branch:
            s.pc.add(lhs == rhs)
        else:
            s.pc.add(lhs != rhs)
        return (lhs == rhs)
    elif isinstance(e, NotEql):
        lhs = parse_expr_to_Z3(e.left, s, m)
        rhs = parse_expr_to_Z3(e.right, s, m)
        if m.branch:          
            # only RHS is BitVec (Lhs is a more complex expr)
            if isinstance(rhs, z3.z3.BitVecRef) and not isinstance(lhs, z3.z3.BitVecRef):
                c = If(lhs, BitVecVal(1, 32), BitVecVal(0, 32))
                s.pc.add(c != rhs)
            else:
                s.pc.add(lhs != rhs)
        else:
            # only RHS is bitVEC 
            if isinstance(rhs, z3.z3.BitVecRef) and not isinstance(lhs, z3.z3.BitVecRef):
                c = If(lhs, BitVecVal(1, 32), BitVecVal(0, 32))
                #print("a")
                s.pc.add(c == rhs)
            else:
                s.pc.push()
                s.pc.add(lhs == rhs)
                if not solve_pc(s.pc):
                    s.pc.pop()
                    m.abandon = True
                    m.ignore = True
    elif isinstance(e, Land):
        lhs = parse_expr_to_Z3(e.left, s, m)
        rhs = parse_expr_to_Z3(e.right, s, m)

        # if lhs and rhs are just simple bit vecs
        if isinstance(rhs, BitVecRef) and isinstance(lhs, BitVecRef):
            #TODO fix this right now im not doing anything
            #s.pc.add(rhs)
            return s
        elif isinstance(rhs, BitVecRef):
            return  s
        elif isinstance(lhs, BitVecRef):
            return  s
        else:
            if lhs is None:
                return s.pc.add(rhs.pc.assertions())
            
            if rhs is None:
                return s.pc.add(rhs.pc.assertions())

            return s.pc.add(lhs.pc.assertions() and rhs.pc.assertions())
    return s

def solve_pc(s: Solver) -> bool:
    """Solve path condition."""
    result = str(s.check())
    if str(result) == "sat":
        model = s.model()
        return True
    else:
        return False

def evaluate_expr(parsedList, s: SymbolicState, m: ExecutionManager):
    for i in parsedList:
	    res = eval_expr(i, s, m)
    return res

def evaluate_expr_to_smt(lhs, rhs, op, s: SymbolicState, m: ExecutionManager) -> str: 
    """Helper function to resolve binary symbolic expressions."""
    if (isinstance(lhs,tuple) and isinstance(rhs,tuple)):
        return f"({op} ({eval_expr(lhs, s, m)})  ({eval_expr(rhs, s, m)}))"
    elif (isinstance(lhs,tuple)):
        if (isinstance(rhs,str)) and not rhs.isdigit():
            return f"({op} ({eval_expr(lhs, s, m)}) {s.get_symbolic_expr(m.curr_module, rhs)})"
        else:
            return f"({op} ({eval_expr(lhs, s, m)}) {str(rhs)})"
    elif (isinstance(rhs,tuple)):
        if (isinstance(lhs,str)) and not lhs.isdigit():
            return f"({op} ({s.get_symbolic_expr(m.curr_module, lhs)}) ({eval_expr(rhs, s, m)}))"
        else:
            return f"({op} {str(lhs)}  ({eval_expr(rhs, s, m)}))"
    else:
        if (isinstance(lhs ,str) and isinstance(rhs , str)) and not lhs.isdigit() and not rhs.isdigit():
            return f"({op} {s.get_symbolic_expr(m.curr_module, lhs)} {s.get_symbolic_expr(m.curr_module, rhs)})"
        elif (isinstance(lhs ,str)) and not lhs.isdigit():
            return f"({op} {s.get_symbolic_expr(m.curr_module, lhs)} {str(rhs)})"
        elif (isinstance(rhs ,str)) and not rhs.isdigit():
            return f"({op} {str(lhs)}  {s.get_symbolic_expr(m.curr_module, rhs)})"
        else: 
            return f"({op} {str(lhs)} {str(rhs)})"
 
def eval_expr(expr, s: SymbolicState, m: ExecutionManager) -> str:
    """Takes in an AST and should return the new symbolic expression for the symbolic state."""
    if not expr is None and expr[0] in BINARY_OPS:
        return evaluate_expr_to_smt(expr[1], expr[2], op_map[expr[0]], s, m)