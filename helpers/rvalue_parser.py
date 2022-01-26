"""Utilities to parse the rvalues of pyverilog, which are specified in prefix notation, evaluate them,
and update our symbolic state. This may not be exhaustive and needs to be updated as we hit more 
cases in the designs we evaluate. Please open a Github issue if you run into a design with an 
rvalue not handled by this."""

import sys
from pyverilog.vparser.ast import Rvalue
from engine.execution_manager import ExecutionManager
from engine.symbolic_state import SymbolicState

# Mapping from PyVerilog Operands to Z3 approximations (for later)
BINARY_OPS = ("Plus", "Minus")
op_map = {"Plus": "+", "Minus": "-"}

def tokenize(rvalue):
    """Takes a PyVerilog Rvalue expression and splits it into Tokens."""
    print(rvalue)
    str_rvalue = str(rvalue)
    tokens = []
    str_rvalue = str_rvalue.replace("(","( ").replace(")"," )").replace("  "," ")
    tokens = str_rvalue.split(" ")
    return tokens

def parse_tokens(tokens):
    print(tokens)
    l = []
    iterat = iter(tokens)
    next(iterat) 
    while True:
	    l += (parser_helper(iterat),)
	    if (next(iterat, None) == None):
		    break
    print(l)
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
    print(parsedList)
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

def eval_rvalue(i, s: SymbolicState, m: ExecutionManager) -> str:
    """Takes in an AST and should return the new symbolic expression for the symbolic state."""
    if i[0] in BINARY_OPS:
        return evaluate_binary_op(i[1], i[2], op_map[i[0]], s, m)