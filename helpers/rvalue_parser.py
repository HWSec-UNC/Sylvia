"""Utilities to parse the rvalues of pyverilog, which are specified in prefix notation, evaluate them,
and update our symbolic state. This may not be exhaustive and needs to be updated as we hit more 
cases in the designs we evaluate. Please open a Github issue if you run into a design with an 
rvalue not handled by this."""

import sys
from pyverilog.vparser.ast import Rvalue, Eq, Cond, Pointer, UnaryOperator, Operator, IdentifierScope, Identifier, StringConst, Partselect
from pyverilog.vparser.ast import Concat
from engine.execution_manager import ExecutionManager
from engine.symbolic_state import SymbolicState
from z3 import If, BitVec, IntVal, Int2BV, BitVecVal

# Mapping from PyVerilog Operands to Z3 approximations (for later)
BINARY_OPS = ("Plus", "Minus", "Power", "Times", "Divide", "Mod", "Sll", "Srl", "Sla", "Sra", "LessThan",
"GreaterThan", "LessEq", "GreaterEq", "Eq", "NotEq", "Eql", "NotEql", "And", "Xor",
"Xnor", "Or", "Land", "Lor")

UNARY_OPS = ("Unot", "Ulnot", "Unor", "Uor")

op_map = {"Plus": "+", "Minus": "-", "Power": "**", "Times": "*", "Divide": "/", "Mod": "%", "Sll": "<<", "Srl": ">>>",
"Sra": ">>", "LessThan": "<", "GreaterThan": ">", "LessEq": "<=", "GreaterEq": ">=", "Eq": "==", "NotEq": "!=", "Eql": "===", "NotEql": "!==",
"And": "&", "Xor": "^", "Or": "|", "Land": "&&", "Lor": "||", "Unot": "!", "Ulnot": "!", "Unor": "!", "Uor": "|"}

def conjunction_with_pointers(rvalue, s: SymbolicState, m: ExecutionManager) -> str: 
    """Convert the compound rvalue into proper string representation with pointers taken into account."""
    if isinstance(rvalue, UnaryOperator):
        operator = str(rvalue).split(" ")[0][1:]
        if isinstance(rvalue.right, Pointer):
            new_right = f"({operator} {rvalue.right.var}[{rvalue.right.ptr}])"
            return new_right
        else: 
            return f"({operator} {conjunction_with_pointers(rvalue.right, s, m)})"
    elif isinstance(rvalue, Cond):
        if isinstance(rvalue.false_value, Pointer):
            ptr_access = f"{rvalue.false_value.var}[{rvalue.false_value.ptr}]"
            s.store[m.curr_module][ptr_access] = s.store[m.curr_module][rvalue.false_value.var.name]
            return f"(Cond {rvalue.cond} {rvalue.true_value} {ptr_access})"
        else:
            return f"(Cond {rvalue.cond} {rvalue.true_value} {rvalue.false_value})"
    elif isinstance(rvalue, Operator):
        operator = str(rvalue).split(" ")[0][1:]
        if isinstance(rvalue.left, Pointer):
            new_left = f"{rvalue.left.var}[{rvalue.left.ptr}]"
            s.store[m.curr_module][new_left] = s.store[m.curr_module][rvalue.left.var.name]
            # make a new value in store for the pointer
            return f"({operator} {new_left} {conjunction_with_pointers(rvalue.right, s, m)})"
        elif isinstance(rvalue.right, Pointer):
            new_right = f"{rvalue.right.var}[{rvalue.right.ptr}]"
            s.store[m.curr_module][new_right] = s.store[m.curr_module][rvalue.right.var.name]
            # make a new value in the store for the pointer
            return f"({operator} {conjunction_with_pointers(rvalue.left, s, m)} {new_right})"
        elif isinstance(rvalue.right, Partselect):
            new_right = f"{rvalue.right.var.name}[{rvalue.right.msb}:{rvalue.right.lsb}]"
            return f"({operator} {conjunction_with_pointers(rvalue.left, s, m)} {new_right})"
        elif isinstance(rvalue.left, Partselect):
            new_left = f"{rvalue.left.var.name}[{rvalue.left.msb}:{rvalue.left.lsb}]"
            return f"({operator} {new_left} {conjunction_with_pointers(rvalue.right, s, m)} )"
        elif isinstance(rvalue.left, Identifier):
            module_name = ""
            if not rvalue.left.scope is None:
                module_name = rvalue.left.scope.labellist[0].name
            new_left = f"{rvalue.left.name}"
            if module_name != "":
                return f"({operator} {module_name}.{new_left} {conjunction_with_pointers(rvalue.right, s, m)})"
            else: 
                return f"({operator} {new_left} {conjunction_with_pointers(rvalue.right, s, m)})"
        else: 
            return f"({operator} {conjunction_with_pointers(rvalue.left, s, m)} {conjunction_with_pointers(rvalue.right, s, m)})" 
    elif isinstance(rvalue, Pointer):
        return f"{rvalue.var}[{rvalue.ptr}]"
    elif isinstance(rvalue, Concat):
        accumulate = "{ "
        for sub_item in rvalue.list:
            accumulate += sub_item.name + " "
        return accumulate + " }"
    else:
        return rvalue

def tokenize(rvalue, s: SymbolicState, m: ExecutionManager):
    """Takes a PyVerilog Rvalue expression and splits it into Tokens."""
    rvalue_converted = conjunction_with_pointers(rvalue, s, m)
    str_rvalue = str(rvalue_converted)
    tokens = []
    str_rvalue = str_rvalue.replace("(","( ").replace(")"," )").replace("  "," ")
    tokens = str_rvalue.split(" ")
    return tokens

def parse_tokens(tokens):
    if len(tokens) == 1 and tokens[0].isalpha():
        return tokens
    l = []
    iterat = iter(tokens)
    next(iterat) 
    while True:
	    l += (parser_helper(iterat),)
	    if (next(iterat, None) == None):
		    break
    return l

def parser_helper(token):
    tup = ()
    for char in token:
        #print(char)
        if char == "(":
            tup += ( parser_helper(token), )
        elif char.isdigit():
            tup += (int(char),)
        elif char == ")":
            return tup
        elif char == "<":
            print("HELP")
        else:
            tup += (char,)

def evaluate(parsedList, s: SymbolicState, m: ExecutionManager):
    #print(parsedList)
    for i in parsedList:
	    res = eval_rvalue(i, s, m)
    return res

def evaluate_unary_op(expr, op, s: SymbolicState, m: ExecutionManager) -> str:
    """Helper function to resolve unary symbolic expression."""
    # convert hex strings into ints
    if isinstance(expr, str) and not expr.isdigit():
        if "'h" in expr or "'b" in expr or "'d" in expr:
            expr = int(expr.split("'")[1][1:])

    if (isinstance(expr,tuple)):
        return f"{op} {eval_rvalue(expr, s, m)}"
    else:
        if (isinstance(expr ,str) and not expr.isdigit()):
            return f" {op} {s.get_symbolic_expr(m.curr_module, expr)}"
        else: 
            return f"{op} {str(expr)}"

def evaluate_binary_op(lhs, rhs, op, s: SymbolicState, m: ExecutionManager) -> str: 
    """Helper function to resolve binary symbolic expressions."""
    # convert hex strings into ints
    if isinstance(rhs, str) and not rhs.isdigit():
        if "'h" in rhs or "'b" in rhs or "'d" in rhs:
            rhs = int(rhs.split("'")[1][1:])

    if isinstance(lhs, str) and not lhs.isdigit():
        if "'h" in lhs or "'b" in lhs or "'d" in lhs:
            lhs = int(lhs.split("'")[1][1:])

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
    #print("evaluating cond expression")
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
            #TODO: this a temporary fix need to exapnd for all cases
            if isinstance(cond, tuple):
                new_cond = evaluate_binary_op(cond[1], cond[2], op_map[cond[0]], s, m)
                if not new_cond is None:
                    return f"If({new_cond}), {s.store[m.curr_module][true_expr]}, {false_expr})"
                else:
                    return f"If({s.store[m.curr_module][cond[1]]}, {s.store[m.curr_module][true_expr]}, {false_expr})"
            else:
                return f"If({s.store[m.curr_module][cond]}, {s.store[m.curr_module][true_expr]}, {false_expr})"
        else:
            return f"If({s.store[m.curr_module][cond]}, {s.store[m.curr_module][true_expr]}, {s.store[m.curr_module][false_expr]})"

def eval_rvalue(rvalue, s: SymbolicState, m: ExecutionManager) -> str:
    """Takes in an AST and should return the new symbolic expression for the symbolic state."""
    #print(rvalue)
    if not rvalue is None:
        if rvalue[0] in BINARY_OPS:
            return evaluate_binary_op(rvalue[1], rvalue[2], op_map[rvalue[0]], s, m)
        elif rvalue[0] in UNARY_OPS:
            return evaluate_unary_op(rvalue[1], op_map[rvalue[0]], s, m)
        elif rvalue[0] == "Cond":
            # TODO this is not good  need to handle in z3 parser
            result = evaluate_cond_expr(rvalue[1], rvalue[2], rvalue[3], s, m)
            # if rvalue[0] in op_map:
            #     parsed_cond = evaluate_binary_op(rvalue[0], rvalue[1], rvalue[2], s, m)
            # else:
            #     parsed_cond = ""
            # print(parsed_cond)
            parsed_cond = ""
            if isinstance(rvalue[1], tuple):
                parsed_cond = str(rvalue[1][1]) +  " & " + str(rvalue[1][2])
            if parsed_cond != "":
                cond = BitVec(parsed_cond, 1)
            else:
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
        else:
            return s.store[m.curr_module][str(rvalue)]

        

def str_to_int(symbolic_exp: str, s: SymbolicState, m: ExecutionManager, reg_width=4294967296) -> int:
    """Takes in a symbolic expression as a string that is only ints and evaluates it down to a single int.
    This is a special case."""
    tokens = symbolic_exp.split(" ")
    result: int = int(tokens[0])
    try: 
        for i in range(1, len(tokens)):
            #TODO: apply operator using HOF or something
            if tokens[i] == "+":
                result += int(tokens[i + 1]) % reg_width
        return result % reg_width
    except Exception:
        return None

def str_to_bool(symbolic_exp: str, s: SymbolicState, m: ExecutionManager, reg_width=4294967296) -> int:
    """Takes in a symbolic expression as a string that is only ints and evaluates it down to a single int.
    This is a special case."""
    tokens = symbolic_exp.split(" ")
    if tokens[0].isnumeric():
        lhs = int(tokens[0])
    else:
        lhs = tokens[0]
    rhs: int = 1
    flag = 0
    op = ""
    try: 
        for i in range(1, len(tokens)):
            #TODO: apply operator using HOF or something
            if tokens[i] == "+" and flag == 0:
                lhs += int(tokens[i + 1]) % reg_width
            elif tokens[i] == "==":
                op = "eq"
                flag = 1
            elif tokens[i] == "+" and flag == 1: 
                rhs += int(tokens[i + 1]) % reg_width
            elif flag == 1:
                rhs = int(tokens[i])
        if op == "eq":
            return lhs == rhs
        elif len(tokens) == 1:
            assertions = s.pc.assertions()
            for assertion in assertions:
                if lhs in str(assertion) and "!= int2bv(1)" in str(assertion):
                    return False
                elif lhs in str(assertion) and "== int2bv(1)" in str(assertion):
                    return True
        return lhs == rhs
    except Exception:
        return None

def resolve_dependency(cond, true_value, false_value, s: SymbolicState, m: ExecutionManager) -> str:
    if isinstance(cond, Operator):
        return true_value
    else:
        # TODO: make sure this works
        return cond.name

def cond_options(cond, true_value, false_value, s: SymbolicState, m: ExecutionManager, res):
    """Returns a mapping from conditionals and their resultant values."""
    if isinstance(false_value, Cond):
        res[cond.name] = true_value
        return cond_options(false_value, false_value.true_value, false_value.false_value, s, m, res)
    elif isinstance(cond, Operator):
        res[str(cond)] = true_value
        res["default"] = false_value
    else: 
        res[cond.name] = true_value
        res["default"] = false_value
    return res

def count_nested_cond(cond, true_value, false_value, s: SymbolicState, m: ExecutionManager) -> str:
    """Calculating the number of branches represented within a conditoinal expression."""
    if isinstance(true_value, Cond):
        return 1 + count_nested_cond(true_value, true_value.true_value, true_value.false_value, s, m)

    elif isinstance(false_value, Cond):
        return 1 + count_nested_cond(false_value, false_value.true_value, false_value.false_value, s, m)

    else:
        return 1
    


        