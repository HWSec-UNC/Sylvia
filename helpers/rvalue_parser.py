"""Utilities to parse the rvalues of pyverilog, which are specified in prefix notation, evaluate them,
and update our symbolic state. This may not be exhaustive and needs to be updated as we hit more 
cases in the designs we evaluate. Please open a Github issue if you run into a design with an 
rvalue not handled by this."""

import sys
from pyverilog.vparser.ast import Rvalue
from engine.execution_manager import ExecutionManager
from engine.symbolic_state import SymbolicState
from z3 import If, BitVec, IntVal, Int2BV, BitVecVal

# Mapping from PyVerilog Operands to Z3 approximations (for later)
BINARY_OPS = ("Plus", "Minus", "Power", "Times", "Divide", "Mod", "Sll", "Srl", "Sla", "Sra", "LessThan",
"GreaterThan", "LessEq", "GreaterEq", "Eq", "NotEq", "Eql", "NotEql", "And", "Xor",
"Xnor", "Or", "Land", "Lor")
op_map = {"Plus": "+", "Minus": "-", "Power": "**", "Times": "*", "Divide": "/", "Mod": "%", "Sll": "<<", "Srl": ">>>",
"Sra": ">>", "LessThan": "<", "GreaterThan": ">", "LessEq": "<=", "GreaterEq": ">=", "Eq": "==", "NotEq": "!=", "Eql": "===", "NotEql": "!==",
"And": "&", "Xor": "^"}

def tokenize(rvalue):
    """Takes a PyVerilog Rvalue expression and splits it into Tokens."""
    str_rvalue = str(rvalue)
    tokens = []
    str_rvalue = str_rvalue.replace("(","( ").replace(")"," )").replace("  "," ")
    tokens = str_rvalue.split(" ")
    return tokens

def parse_tokens(tokens):
    l = []
    iterat = iter(tokens)
    next(iterat) 
    while True:
	    l += (parser_helper(iterat),)
	    if (next(iterat, None) == None):
		    break
    return l

def parser_helper(iterat):
	tup = ()
	for i in iterat:
		if (i == '('):
			tup += ( parser_helper(iterat), )
		elif (i.isdigit()): 
			tup += (int(i),)
		elif ( i == ')'): 
			return tup
		else:
			tup += (i,)

def evaluate(parsedList, s: SymbolicState, m: ExecutionManager):
    for i in parsedList:
	    res = eval_rvalue(i, s, m)
    return res

def evaluate_binary_op(lhs, rhs, op, s: SymbolicState, m: ExecutionManager) -> str: 
    """Helper function to resolve binary symbolic expressions."""
    if (isinstance(lhs,tuple) and isinstance(rhs,tuple)):
        return f"{eval_rvalue(lhs, s, m)} {op} {eval_rvalue(rhs, s, m)}"
    elif (isinstance(lhs,tuple)):
        if (isinstance(rhs,str)) and not rhs.isdigit():
            return f"{eval_rvalue(lhs, s, m)} {op} {s.get_symbolic_expr(m.curr_module, rhs)}"
        else:
            return f"{eval_rvalue(lhs, s, m)} {op} {str(rhs)}"
    elif (isinstance(rhs,tuple)):
        if (isinstance(lhs,str)) and not lhs.isdigit():
            return f"{s.get_symbolic_expr(m.curr_module, lhs)} {op} {eval_rvalue(rhs, s, m)}"
        else:
            return f"{str(lhs)} {op} {eval_rvalue(rhs, s, m)}"
    else:
        if (isinstance(lhs ,str) and isinstance(rhs , str)) and not lhs.isdigit() and not rhs.isdigit():
            return f"{s.get_symbolic_expr(m.curr_module, lhs)} {op} {s.get_symbolic_expr(m.curr_module, rhs)}"
        elif (isinstance(lhs ,str)) and not lhs.isdigit():
            return f"{s.get_symbolic_expr(m.curr_module, lhs)} {op} {str(rhs)}"
        elif (isinstance(rhs ,str)) and not rhs.isdigit():
            return f"{str(lhs)} {op} {s.get_symbolic_expr(m.curr_module, rhs)}"
        else: 
            return f"{str(lhs)} {op} {str(rhs)}"

def evaluate_cond_expr(cond, true_expr, false_expr, s: SymbolicState, m: ExecutionManager) -> str:
    """Helper function to resolve conditional symbolic expressions.
    The format is intentionally meant to match z3 to make parsing easier later."""
    if (isinstance(true_expr,tuple) and isinstance(false_expr,tuple)):
        return f"If({s.store[m.curr_module][cond]}, {evaluate_cond_expr(true_expr[0], true_expr[1], true_expr[2], m, s)}, {evaluate_cond_expr(false_expr[0], false_expr[1], false_expr[2], m, s)})"
    elif (isinstance(true_expr,tuple)):
        if false_expr.isdigit():
            return f"If({s.store[m.curr_module][cond]}, {evaluate_cond_expr(true_expr[0], true_expr[1], true_expr[2], m, s)}, {false_expr})"
        else:
            return f"If({s.store[m.curr_module][cond]}, {evaluate_cond_expr(true_expr[0], true_expr[1], true_expr[2], m, s)}, {s.store[m.curr_module][false_expr]})"
    elif (isinstance(false_expr,tuple)):
        if true_expr.isdigit():
            return f"If({s.store[m.curr_module][cond]}, {true_expr}, {evaluate_cond_expr(false_expr[0], false_expr[1], false_expr[2], m, s)} )"
        else:
            return f"If({s.store[m.curr_module][cond]}, {s.store[m.curr_module][true_expr]}, {evaluate_cond_expr(false_expr[0], false_expr[1], false_expr[2], m, s)} )"
    else:
        if str(true_expr).isdigit() and str(false_expr).isdigit():
            return f"If({s.store[m.curr_module][cond]}, {true_expr}, {false_expr})"
        elif str(true_expr).isdigit():
            return f"If({s.store[m.curr_module][cond]}, {true_expr}, {s.store[m.curr_module][false_expr]} )"
        elif str(false_expr).isdigit():
            return f"If({s.store[m.curr_module][cond]}, {s.store[m.curr_module][true_expr]}, {false_expr})"
        else:
            return f"If({s.store[m.curr_module][cond]}, {s.store[m.curr_module][true_expr]}, {s.store[m.curr_module][false_expr]})"

def eval_rvalue(rvalue, s: SymbolicState, m: ExecutionManager) -> str:
    """Takes in an AST and should return the new symbolic expression for the symbolic state."""
    if rvalue[0] in BINARY_OPS:
        return evaluate_binary_op(rvalue[1], rvalue[2], op_map[rvalue[0]], s, m)
    elif rvalue[0] == "Cond":
        # TODO this is not good  need to handle in z3 parser
        result = evaluate_cond_expr(rvalue[1], rvalue[2], rvalue[3], s, m)
        cond = BitVec(rvalue[1], 1)
        one = IntVal(1)
        one_bv = Int2BV(one, 1)
        if not rvalue[2].isdigit():
            true_expr = BitVec(s.store[m.curr_module][rvalue[2]], 32)
        else:
            true_expr_int = IntVal(rvalue[2], 32)
            true_expr = Int2BV(true_expr_int, 32)
        if not str(rvalue[3]).isdigit():
            false_expr = BitVec(s.store[m.curr_module][rvalue[3]], 32)
        else:
            false_expr_int = IntVal(rvalue[3])
            false_expr = Int2BV(false_expr_int, 32)
        # TODO: i cant add it to the pc bc this a bool sort ... not a bitvec one and it will throw an error
        #s.pc.add(If((cond == one_bv), true_expr, false_expr))
        
        return result