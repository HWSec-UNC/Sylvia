"""Depth First Traversal of the AST."""
from .template import Search
from z3 import Solver, Int, BitVec, Int2BV, IntVal, Concat
from engine.execution_manager import ExecutionManager
from engine.symbolic_state import SymbolicState
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement, SingleStatement, And, Constant, Rvalue, Plus, Input, Output
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block, SystemCall, Land, InstanceList, IntConst, Partselect, Ioport
from pyverilog.vparser.ast import Value, Reg, Initial, Eq, Identifier, Initial,  NonblockingSubstitution, Decl, Always, Assign, NotEql, Case
from pyverilog.vparser.ast import Concat, BlockingSubstitution, Parameter, StringConst, Wire, PortArg, Cond, Pointer, IdentifierScope, Operator, ForStatement
from pyverilog.vparser.ast import Repeat 
from helpers.utils import init_symbol
from typing import Optional
from helpers.rvalue_parser import tokenize, parse_tokens, evaluate, resolve_dependency, count_nested_cond, cond_options, str_to_int, str_to_bool, simpl_str_exp, conjunction_with_pointers
from helpers.rvalue_to_z3 import parse_expr_to_Z3, solve_pc, parse_concat_to_Z3
from helpers.utils import to_binary
from itertools import product, permutations
import os
import copy
import time


class DepthFirst(Search):

    def visit_module(self, m: ExecutionManager, s: SymbolicState, module: ModuleDef, modules: Optional):
        """Traverse the module of a hardware design, depth first."""
        m.currLevel = 0
        params = module.paramlist.params
        ports = module.portlist.ports

        for param in params:
            if isinstance(param.list[0], Parameter):
                if m.curr_module in m.instances_loc:
                    containing_module = m.instances_loc[m.curr_module]
                    s.store[m.curr_module][param.list[0].name] = s.store[containing_module][param.list[0].name]

        for port in ports:
            if isinstance(port, Ioport):
                if str(port.first.name) not in s.store[m.curr_module]:
                    s.store[m.curr_module][str(port.first.name)] = init_symbol()
            else:
                if m.curr_module in m.instances_loc:
                    containing_module = m.instances_loc[m.curr_module]
                    if not port.name in s.store[containing_module]: 
                        s.store[m.curr_module][port.name] = init_symbol()
                    else:
                        s.store[m.curr_module][port.name] = s.store[containing_module][port.name]
                if port.name not in s.store[m.curr_module]:
                    s.store[m.curr_module][port.name] = init_symbol()

        
        if not m.is_child and not m.init_run_flag and not m.ignore:
            m.initial_store = copy.deepcopy(s.store) 

        for item in module.items:
            if isinstance(item, Value):
                self.visit_expr(m, s, item)
            else:
                continue
                # This should be handled by exploration in always blocks
                # self.visit_stmt(m, s, item, modules)
        

        # simpl / collapsing step
        
        for module in m.cond_assigns:
            for signal in m.cond_assigns[module]:
                res = m.cond_assigns[module][signal]
                if str(signal) in s.store[module] and str(s.store[module][str(signal)]).startswith("If("):
                    cond = str(s.store[module][str(signal)])[3:].split(",")[0][:-1]
                    if str_to_bool(cond, s, m):
                        if isinstance(m.cond_assigns[module][signal][cond], Operator):
                            parsed_cond = evaluate(parse_tokens(tokenize(m.cond_assigns[module][signal][cond], s, m)), s, m)
                            int_cond = None
                            if parsed_cond.split(" ")[0].isdigit():
                                #TODO: get correct width here
                                int_cond = str_to_int(parsed_cond, s, m, 32)
                            if not int_cond is None:
                                s.store[module][str(signal)] = int_cond
                            else:
                                s.store[module][str(signal)] = parsed_cond
                        else:
                            s.store[module][str(signal)] = s.store[module][str(m.cond_assigns[module][signal][cond])]
                    else:
                        s.store[module][str(signal)] = m.cond_assigns[module][signal]["default"]
                        

        if m.ignore:
            ...
        
    

    def visit_stmt(self, m: ExecutionManager, s: SymbolicState, stmt: Node, modules: Optional[dict], direction: Optional[int]):
        "Traverse the statements in a hardware design"
        if m.ignore:
            return
        if isinstance(stmt, Decl):
            for item in stmt.list:
                if isinstance(item, Value):
                    self.visit_expr(m, s, item)
                else:
                    self.visit_stmt(m, s, item, modules, direction)
                # ref_name = item.name
                # ref_width = int(item.width.msb.value) + 1
                #  dont want to actually call z3 here, just when looking at PC
                # x = BitVec(ref_name, ref_width)
            
        elif isinstance(stmt, Parameter):
            if isinstance(stmt.value.var, IntConst):
                s.store[m.curr_module][stmt.name] = stmt.value.var
            elif isinstance(stmt.value.var, Identifier):
                s.store[m.curr_module][stmt.name] = s.store[m.curr_module][str(stmt.value.var)]
            else:
                if m.cycle == 0:
                    s.store[m.curr_module][stmt.name] = init_symbol()
        elif isinstance(stmt, Always):
            m.in_always = True
            sens_list = stmt.sens_list
            if m.opt_3:
                if stmt in m.blocks_of_interest:
                    sub_stmt = stmt.statement
                    m.in_always = True
                    self.visit_stmt(m, s, sub_stmt, modules, direction)
                    for module in m.dependencies:
                        for signal in m.dependencies[module]:
                            if m.dependencies[module][signal] in m.updates:
                                if m.updates[m.dependencies[module][signal]][0] == 1:
                                    prev_symbol = m.updates[m.dependencies[module][signal]][1]

                                    if m.dependencies[module][signal] in m.cond_assigns[module]:
                                        m.cond_assigns[m.curr_module][signal] = m.cond_assigns[module][m.dependencies[module][signal]]

                                    if signal in s.store[m.curr_module] and '[' in str(s.store[m.curr_module][signal]):
                                        
                                        parts = s.store[m.curr_module][signal].partition("[")

                                        new_symbol = s.store[m.curr_module][m.dependencies[module][signal]]
                                        if isinstance(new_symbol, dict):
                                            first_parts = {}
                                            for sig_name in new_symbol:
                                                first_parts[sig_name] = parts[0].replace(parts[0], new_symbol[sig_name])
                                                for i in range(1, len(parts)):
                                                    new_symbol[sig_name] += parts[i]
                                                s.store[m.curr_module][sig_name] = new_symbol[sig_name]
                                        else:
                                            first_part = parts[0].replace(parts[0], new_symbol)
                                            for i in range(1, len(parts)):
                                                new_symbol += parts[i]

                                            s.store[m.curr_module][signal] = new_symbol

                                    else:
                                        if signal in m.dependencies[module] and signal in s.store[m.curr_module] and m.dependencies[module][signal] in s.store[m.curr_module]:
                                            new_symbol = s.store[m.curr_module][m.dependencies[module][signal]]
                                            s.store[m.curr_module][signal] = str(s.store[m.curr_module][signal]).replace(prev_symbol, new_symbol)
                                        else:
                                            # the signal was updated, but something trivial happened like it was just written with a constant
                                            pass
                            for lhs in m.cond_assigns[module]:
                                if lhs in m.dependencies[module] and isinstance(m.updates[lhs], tuple) and m.updates[lhs][0] == 1:
                                    prev_symbol = str(m.updates[lhs][1])
                                    if not prev_symbol.isdigit() and prev_symbol in s.store[m.curr_module]: 
                                        prev_symbol = s.store[m.curr_module][prev_symbol]
                                    if lhs in s.store[module] and '[' in str(s.store[module][lhs]):
                                        
                                        parts = s.store[module][lhs].partition("[")

                                        new_symbol = s.store[module][str(m.dependencies[module][lhs])]
                                        first_part = parts[0].replace(parts[0], new_symbol)
                                        for i in range(1, len(parts)):
                                            new_symbol += parts[i]

                                        s.store[module][lhs] = new_symbol
                                    else:
                                        # do a simpl pass?
                                        if lhs in s.store[module]:
                                            s.store[module][lhs] = s.store[module][lhs]
                                    m.updates[lhs] = 0 

            else: 
                sub_stmt = stmt.statement
                m.in_always = True
                #self.visit_stmt(m, s, sub_stmt, modules, direction)
                for module in m.dependencies:
                    for signal in m.dependencies[module]:
                        if m.dependencies[module][signal] in m.updates:
                            if m.updates[m.dependencies[module][signal]][0] == 1:
                                prev_symbol = m.updates[m.dependencies[module][signal]][1]

                                if m.dependencies[module][signal] in m.cond_assigns[module]:
                                    m.cond_assigns[m.curr_module][signal] = m.cond_assigns[module][m.dependencies[module][signal]]

                                if signal in s.store[m.curr_module] and '[' in str(s.store[m.curr_module][signal]):
                                    
                                    parts = s.store[m.curr_module][signal].partition("[")

                                    new_symbol = s.store[m.curr_module][m.dependencies[module][signal]]
                                    if isinstance(new_symbol, dict):
                                        first_parts = {}
                                        for sig_name in new_symbol:
                                            first_parts[sig_name] = parts[0].replace(parts[0], new_symbol[sig_name])
                                            for i in range(1, len(parts)):
                                                new_symbol[sig_name] += parts[i]
                                            s.store[m.curr_module][sig_name] = new_symbol[sig_name]
                                    else:
                                        first_part = parts[0].replace(parts[0], new_symbol)
                                        for i in range(1, len(parts)):
                                            new_symbol += parts[i]

                                        s.store[m.curr_module][signal] = new_symbol

                                else:
                                    if signal in m.dependencies[module] and signal in s.store[m.curr_module] and m.dependencies[module][signal] in s.store[m.curr_module]:
                                        new_symbol = s.store[m.curr_module][m.dependencies[module][signal]]
                                        s.store[m.curr_module][signal] = str(s.store[m.curr_module][signal]).replace(prev_symbol, new_symbol)
                                    else:
                                        # the signal was updated, but something trivial happened like it was just written with a constant
                                        pass
                        for lhs in m.cond_assigns[module]:
                            if lhs in m.dependencies[module] and isinstance(m.updates[lhs], tuple) and m.updates[lhs][0] == 1:
                                prev_symbol = str(m.updates[lhs][1])
                                if not prev_symbol.isdigit() and prev_symbol in s.store[m.curr_module]: 
                                    prev_symbol = s.store[m.curr_module][prev_symbol]
                                if lhs in s.store[module] and '[' in str(s.store[module][lhs]):
                                    
                                    parts = s.store[module][lhs].partition("[")

                                    new_symbol = s.store[module][str(m.dependencies[module][lhs])]
                                    first_part = parts[0].replace(parts[0], new_symbol)
                                    for i in range(1, len(parts)):
                                        new_symbol += parts[i]

                                    s.store[module][lhs] = new_symbol
                                else:
                                    # do a simpl pass?
                                    if lhs in s.store[module]:
                                        s.store[module][lhs] = s.store[module][lhs]
                                m.updates[lhs] = 0 
                        # simplificiation / collapsing step
            m.in_always = False               
        elif isinstance(stmt, Assign):
            if isinstance(stmt.left.var, Identifier) and stmt.left.var.name in m.reg_decls and m.cycle > 0:
                ...
            elif isinstance(stmt.right.var, IntConst):
                if isinstance(stmt.left.var, Pointer):
                    s.store[m.curr_module][f"{stmt.left.var.var}[{stmt.left.var.ptr}]"] = stmt.right.var.value
                elif isinstance(stmt.left.var, Partselect):
                    s.store[m.curr_module][f"{stmt.left.var.var.name}[{stmt.left.var.msb}:{stmt.left.var.lsb}]"] = stmt.right.var.value
                else:
                    s.store[m.curr_module][stmt.left.var.name] = stmt.right.var.value
            elif isinstance(stmt.right.var, Identifier):
                if isinstance(stmt.left.var, Pointer):
                    s.store[m.curr_module][f"{stmt.left.var.var}[{stmt.left.var.ptr}]"] = s.store[m.curr_module][stmt.right.var.name]
                elif isinstance(stmt.left.var, Partselect):
                    s.store[m.curr_module][f"{stmt.left.var.var.name}[{stmt.left.var.msb}:{stmt.left.var.lsb}]"] = s.store[m.curr_module][stmt.right.var.name]
                else:

                    if isinstance(stmt.left.var, Concat):
                        for sub_item in stmt.left.var.list:
                            s.store[m.curr_module][sub_item.name] = s.store[m.curr_module][stmt.right.var.name]
                    else:
                        s.store[m.curr_module][stmt.left.var.name] = s.store[m.curr_module][stmt.right.var.name]
            elif isinstance(stmt.right.var, Partselect):

                if isinstance(stmt.left.var, Partselect):
                    s.store[m.curr_module][stmt.left.var.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.msb}:{stmt.right.var.lsb}]"
                    m.dependencies[m.curr_module][stmt.left.var.var.name] = stmt.right.var.var.name
                    m.updates[stmt.left.var.var.name] = 0
                else:
                    new_msb = evaluate(parse_tokens(tokenize(stmt.right.var.msb, s, m)), s, m)
                    new_lsb = evaluate(parse_tokens(tokenize(stmt.right.var.lsb, s, m)), s, m)
                    #TODO : cases
                    if not new_msb is None and not new_lsb is None:
                        s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{new_msb}:{new_lsb}]"
                    elif not new_msb is None:
                        s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{new_msb}:{stmt.right.var.lsb}]"
                    elif not new_lsb is None: 
                        s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.msb}:{new_lsb}]"
                    else:
                        s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.msb}:{stmt.right.var.lsb}]"
                    m.dependencies[m.curr_module][stmt.left.var.name] = stmt.right.var.var.name
                    m.updates[stmt.left.var.name] = 0
            
            elif isinstance(stmt.right.var, Concat):
                if isinstance(stmt.left.var, Concat):
                    for sub_item in stmt.left.var.list:
                        for item in stmt.right.var.list:
                            if isinstance(item, Partselect):
                                s.store[m.curr_module][sub_item.name] = f"{s.store[m.curr_module][item.var.name]}[{item.msb}:{item.lsb}]"
                            elif isinstance(item, IntConst):
                                s.store[m.curr_module][sub_item.name] = item.value
                            else:
                                s.store[m.curr_module][sub_item.name] = s.store[m.curr_module][item.name]
                                # items match 1:1:
                else:
                    s.store[m.curr_module][stmt.left.var.name] = {}
                    for item in stmt.right.var.list:
                        # TODO: concatenation is more nuanced potentially than this...
                        # see line 237 of or1200_except
                        str_item = evaluate(parse_tokens(tokenize(item, s, m)), s, m)
                        s.store[m.curr_module][stmt.left.var.name][str_item] = str_item
                        #s.store[m.curr_module][stmt.left.var.name][item.name] = s.store[m.curr_module][item.name]
            elif isinstance(stmt.right.var, Cond):
                if isinstance(stmt.left.var, Pointer):
                    m.dependencies[m.curr_module][f"{stmt.left.var.var}[{stmt.left.var.ptr}]"] = resolve_dependency(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m)
                    opts = cond_options(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m, {})
                    m.cond_assigns[m.curr_module][f"{stmt.left.var.var}[{stmt.left.var.ptr}]"] = opts
                    # complexity is how many nested conditonals we have on the rhs
                    complexity = count_nested_cond(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m)
                    new_r_value = evaluate(parse_tokens(tokenize(stmt.right.var, s, m)), s, m)
                    if str(stmt.right.var.cond) in opts:
                        new_cond = new_r_value[3:].split(",")[0][:-1]

                        opts[new_cond] = opts.pop(str(stmt.right.var.cond))
                    s.store[m.curr_module][f"{stmt.left.var.var}[{stmt.left.var.ptr}]"] = new_r_value
                elif isinstance(stmt.left.var, Partselect):
                    m.dependencies[m.curr_module][f"{stmt.left.var.var.name}[{stmt.left.var.msb}:{stmt.left.var.lsb}]"] = resolve_dependency(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m)
                    opts = cond_options(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m, {})
                    m.cond_assigns[m.curr_module][f"{stmt.left.var.var.name}[{stmt.left.var.msb}:{stmt.left.var.lsb}]"] = opts
                    # complexity is how many nested conditonals we have on the rhs
                    complexity = count_nested_cond(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m)
                    new_r_value = evaluate(parse_tokens(tokenize(stmt.right.var, s, m)), s, m)
                    if str(stmt.right.var.cond) in opts:
                        new_cond = new_r_value[3:].split(",")[0][:-1]
                        opts[new_cond] = opts.pop(str(stmt.right.var.cond))
                    s.store[m.curr_module][f"{stmt.left.var.var.name}[{stmt.left.var.msb}:{stmt.left.var.lsb}]"] = new_r_value
                else:
                    m.dependencies[m.curr_module][stmt.left.var.name] = resolve_dependency(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m)
                    opts = cond_options(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m, {})
                    m.cond_assigns[m.curr_module][stmt.left.var.name] = opts
                    # complexity is how many nested conditonals we have on the rhs
                    complexity = count_nested_cond(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m)
                    new_r_value = evaluate(parse_tokens(tokenize(stmt.right.var, s, m)), s, m)
                    if str(stmt.right.var.cond) in opts:
                        new_cond = new_r_value[3:].split(",")[0][:-1]
                        opts[new_cond] = opts.pop(str(stmt.right.var.cond))
                    s.store[m.curr_module][stmt.left.var.name] = new_r_value
            elif isinstance(stmt.right.var, Pointer):
                expr_in_brackets = evaluate(parse_tokens(tokenize(stmt.right.var.ptr, s, m)), s, m)
                if not expr_in_brackets is None:
                    s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[ {expr_in_brackets} ]"
                else:
                    s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.ptr}]"
                m.dependencies[m.curr_module][stmt.left.var.name] = stmt.right.var.var.name
                m.updates[stmt.left.var.name] = 0
            else:
                new_r_value = evaluate(parse_tokens(tokenize(stmt.right.var, s, m)), s, m)
                if new_r_value != None:
                    s.store[m.curr_module][stmt.left.var.name] = new_r_value
                else:
                    s.store[m.curr_module][stmt.left.var.name] = s.store[m.curr_module][stmt.right.var.name]

            if isinstance(stmt.left.var, Pointer):
                if f"{stmt.left.var.var}[{stmt.left.var.ptr}]" in s.store[m.curr_module]:
                    prev_symbol = s.store[m.curr_module][f"{stmt.left.var.var}[{stmt.left.var.ptr}]"]
                else:
                    prev_symbol = s.store[m.curr_module][f"{stmt.left.var.var}"]
            elif isinstance(stmt.left.var, Partselect):
                if f"{stmt.left.var.var.name}[{stmt.left.var.msb}:{stmt.left.var.lsb}]" in s.store[m.curr_module]:
                    prev_symbol = s.store[m.curr_module][f"{stmt.left.var.var.name}[{stmt.left.var.msb}:{stmt.left.var.lsb}]"]
                else:
                    prev_symbol = s.store[m.curr_module][f"{stmt.left.var.var.name}"]
            else:
                if isinstance(stmt.left.var, Concat):
                    #TODO: loop over all prev symbols
                    prev_symbol = s.store[m.curr_module][str(stmt.left.var.list[0])]
                else:
                    prev_symbol = s.store[m.curr_module][stmt.left.var.name]

            if isinstance(stmt.left.var, Concat):
                for sub_item in stmt.left.var.list:
                    m.updates[sub_item.name] = (1, prev_symbol)
            elif isinstance(stmt.left.var, Pointer):
                m.updates[f"{stmt.left.var.var}[{stmt.left.var.ptr}]"]= (1, prev_symbol)
            elif isinstance(stmt.left.var, Partselect):
                m.updates[f"{stmt.left.var.var.name}[{stmt.left.var.msb}:{stmt.left.var.lsb}]"] = (1, prev_symbol)
            else:
                m.updates[stmt.left.var.name] = (1, prev_symbol)
        elif isinstance(stmt, NonblockingSubstitution):
            reg_width = 0
            if isinstance(stmt.left.var, Identifier):
                if stmt.left.var.name in m.reg_decls:
                    #TODO: This is bad
                    if stmt.left.var.name in m.reg_widths:
                        reg_width = m.reg_widths[stmt.left.var.name]
                    else:
                        reg_width = 4294967296
            if isinstance(stmt.right.var, IntConst):
                if isinstance(stmt.left.var, Pointer):
                    s.store[m.curr_module][stmt.left.var.var.name] = stmt.right.var.value
                else:
                    s.store[m.curr_module][stmt.left.var.name] = stmt.right.var.value
            elif isinstance(stmt.right.var, Identifier):
                if isinstance(stmt.left.var, Pointer):
                    s.store[m.curr_module][f"{stmt.left.var.var}[{stmt.left.var.ptr}]"] = s.store[m.curr_module][stmt.right.var.name]
                else:
                    s.store[m.curr_module][stmt.left.var.name] = s.store[m.curr_module][stmt.right.var.name]
            elif isinstance(stmt.right.var, Concat):
                # TODO make this a real concat
                if isinstance(stmt.left.var, Concat):
                    for sub_item in stmt.left.var.list:
                        for item in stmt.right.var.list:
                            if isinstance(item, Partselect):
                                s.store[m.curr_module][sub_item.name] = f"{s.store[m.curr_module][item.var.name]}[{item.msb}:{item.lsb}]"
                            elif isinstance(item, IntConst):
                                s.store[m.curr_module][sub_item.name] = item.value
                            else:
                                s.store[m.curr_module][sub_item.name] = s.store[m.curr_module][item.name]
                                # items match 1:1:
                
                else:
                    s.store[m.curr_module][stmt.left.var.name] = {}
                    for item in stmt.right.var.list:
                        if isinstance(item, Partselect):
                            s.store[m.curr_module][stmt.left.var.name][item.var.name] = f"{s.store[m.curr_module][item.var.name]}[{item.msb}:{item.lsb}]"
                        elif isinstance(item, IntConst):
                            s.store[m.curr_module][stmt.left.var.name][item.value] = item.value
                        elif isinstance(item, Repeat):
                            new_r_value = evaluate(parse_tokens(tokenize(stmt.right.var, s, m)), s, m)
                            s.store[m.curr_module][stmt.left.var.name][item.value] = new_r_value
                        else:
                            s.store[m.curr_module][stmt.left.var.name][item.name] = s.store[m.curr_module][item.name]
            elif isinstance(stmt.right.var, StringConst):
                if "'h" in stmt.right.var.value or "'b" in stmt.right.var.value or "'d" in stmt.right.var.value:
                    s.store[m.curr_always][stmt.left.var.name] = stmt.right.var.value.split("'")[1][1:]
                else:
                    s.store[m.curr_module][stmt.left.var.name] = stmt.right.var.value
            elif isinstance(stmt.right.var, Partselect):
                # TODO make sure the width is still enforced correctly though
                if stmt.right.var.var.name in m.cond_assigns[m.curr_module]:
                    m.cond_assigns[m.curr_module][stmt.left.var.name] = m.cond_assigns[m.curr_module][stmt.right.var.var.name]
                elif isinstance(stmt.left.var, Partselect):
                    s.store[m.curr_module][stmt.left.var.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.msb}:{stmt.right.var.lsb}]"
                else:
                    s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.msb}:{stmt.right.var.lsb}]"
            elif isinstance(stmt.right.var, Pointer):
                expr_in_brackets = evaluate(parse_tokens(tokenize(stmt.right.var.ptr, s, m)), s, m)
                if isinstance(stmt.left.var, Pointer):
                    if not expr_in_brackets is None:
                        s.store[m.curr_module][stmt.left.var.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[ {expr_in_brackets} ]"
                    else:
                        s.store[m.curr_module][stmt.left.var.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.ptr.value}]"
                else:
                    if not expr_in_brackets is None:
                        s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[ {expr_in_brackets} ]"
                    else: 
                         s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.ptr.value}]"
            else:
                new_r_value = evaluate(parse_tokens(tokenize(stmt.right.var, s, m)), s, m)
                if new_r_value != None:
                    if new_r_value.split(" ")[0].isdigit():
                        int_r_value = str_to_int(new_r_value, s, m, reg_width)
                        if not int_r_value is None:
                            s.store[m.curr_module][stmt.left.var.name] = str(int_r_value)
                        else:
                            s.store[m.curr_module][stmt.left.var.name] = new_r_value
                    else:
                        s.store[m.curr_module][stmt.left.var.name] = new_r_value
                else:
                    s.store[m.curr_module][stmt.left.var.name] = s.store[m.curr_module][stmt.right.var.name]

        elif isinstance(stmt, BlockingSubstitution):
            if isinstance(stmt.left.var, Partselect):
                prev_symbol = s.store[m.curr_module][stmt.left.var.var.name]
            else:
                prev_symbol = s.store[m.curr_module][stmt.left.var.name]
            if isinstance(stmt.right.var, IntConst):
                if isinstance(stmt.left.var, Partselect):
                    s.store[m.curr_module][stmt.left.var.var.name] = stmt.right.var.value
                else:
                    s.store[m.curr_module][stmt.left.var.name] = stmt.right.var.value
            elif isinstance(stmt.right.var, Identifier):
                s.store[m.curr_module][stmt.left.var.name] = s.store[m.curr_module][stmt.right.var.name]
            elif isinstance(stmt.right.var, Concat):
                s.store[m.curr_module][stmt.left.var.name] = {}
                for item in stmt.right.var.list:
                    if isinstance(item, Partselect):
                        s.store[m.curr_module][stmt.left.var.name][item.var.name] = f"{s.store[m.curr_module][item.var.name]}[{item.msb}:{item.lsb}]"
                    else:
                        s.store[m.curr_module][stmt.left.var.name][item.name] = s.store[m.curr_module][item.name]
            elif isinstance(stmt.right.var, StringConst):
                if "'h" in stmt.right.var.value or "'b" in stmt.right.var.value or "'d" in stmt.right.var.value:
                    s.store[m.curr_always][stmt.left.var.name] = stmt.right.var.value.split("'")[1][1:]
                else:
                    s.store[m.curr_module][stmt.left.var.name] = stmt.right.var.value
            elif isinstance(stmt.right.var, Partselect):
                if isinstance(stmt.left.var, Partselect):
                    s.store[m.curr_module][stmt.left.var.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.msb}:{stmt.right.var.lsb}]"
                    m.dependencies[m.curr_module][stmt.left.var.var.name] = stmt.right.var.var.name
                    m.updates[stmt.left.var.var.name] = 0
                else:
                    s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.msb}:{stmt.right.var.lsb}]"
                    m.dependencies[m.curr_module][stmt.left.var.name] = stmt.right.var.var.name
                    m.updates[stmt.left.var.name] = 0
            else:
                new_r_value = evaluate(parse_tokens(tokenize(stmt.right.var, s, m)), s, m)
                if  new_r_value != None:
                    s.store[m.curr_module][stmt.left.var.name] = new_r_value
                else:
                    s.store[m.curr_module][stmt.left.var.name] = s.store[m.curr_module][stmt.right.var.name]
            if isinstance(stmt.left.var, Partselect):
                m.updates[stmt.left.var.var.name] = (1, prev_symbol)
            else:
                m.updates[stmt.left.var.name] = (1, prev_symbol)
        elif isinstance(stmt, Block):
            if m.opt_2:
                for item in stmt.statements: 
                    self.visit_stmt(m, s, item, modules, direction)
            else:
                all_orderings = list(permutations(stmt.statements))
                for ordering in all_orderings:
                    for item in ordering: 
                        self.visit_stmt(m, s, item, modules, direction)
            
        elif isinstance(stmt, Initial):
            self.visit_stmt(m, s, stmt.statement,  modules)
        elif isinstance(stmt, IfStatement):
            m.curr_level += 1
            self.cond = True
            bit_index = m.curr_level
            if (direction):
                self.branch = True

                for lhs in m.cond_assigns[m.curr_module]:
                    if str(stmt.cond) in m.cond_assigns[m.curr_module][lhs]:
                        m.updates[lhs] = (1, m.cond_assigns[m.curr_module][lhs][str(stmt.cond)])

                solver_start = time.process_time()
                self.visit_expr(m, s, stmt.cond)
                solver_end = time.process_time()
                m.solver_time += solver_end - solver_start
                if (m.abandon and m.debug):
                    print("Abandoning this path!")
                    return
                nested_ifs = m.count_conditionals_2(m, stmt.true_statement)
                diff = 32 - bit_index
                # m.curr_level == (32 - bit_index) this is always true
                #if nested_ifs == 0 and m.curr_level < 2 and self.seen_all_cases(m, bit_index, nested_ifs):
                if m.seen_all_cases(m, bit_index, nested_ifs):
                    m.completed.append(bit_index)
                #self.visit_stmt(m, s, stmt.true_statement,  modules, direction)
            else:
                m.count_conditionals_2(m, stmt.true_statement)
                self.branch = False
                for lhs in m.cond_assigns[m.curr_module]:
                    if str(stmt.cond) in m.cond_assigns[m.curr_module][lhs]:
                        m.updates[lhs] = (1, m.cond_assigns[m.curr_module][lhs]["default"])
                
                solver_start = time.process_time()
                self.visit_expr(m, s, stmt.cond)
                solver_end = time.process_time()
                m.solver_time += solver_end - solver_start
                if (m.abandon and m.debug):
                    print("Abandoning this path!")

                    return
                #self.visit_stmt(m, s, stmt.false_statement,  modules, direction)
        elif isinstance(stmt, ForStatement):
            print("FOR")
            m.curr_level += 1
            self.cond = True
            bit_index = len(m.path_code) - m.curr_level
            if (direction):
                self.branch = True

                for lhs in m.cond_assigns[m.curr_module]:
                    if str(stmt.cond) in m.cond_assigns[m.curr_module][lhs]:
                        m.updates[lhs] = (1, m.cond_assigns[m.curr_module][lhs][str(stmt.cond)])

                solver_start = time.process_time()
                self.visit_expr(m, s, stmt.cond)
                solver_start = time.process_time()
                m.solver_time += solver_end - solver_start
                if (m.abandon and m.debug):
                    print("Abandoning this path!")
                    return
                nested_ifs = m.count_conditionals_2(m, stmt.statement)
                diff = 32 - bit_index
                # m.curr_level == (32 - bit_index) this is always true
                #if nested_ifs == 0 and m.curr_level < 2 and self.seen_all_cases(m, bit_index, nested_ifs):
                s.store[m.curr_module][str(stmt.pre.left.var.name)] = stmt.pre.right.var.value
                while str_to_bool(evaluate(parse_tokens(tokenize(stmt.cond, s, m)), s, m), s, m):
                    print("bey")
                    self.visit_stmt(m, s, stmt.statement,  modules)
                    r = evaluate(parse_tokens(tokenize(stmt.post.right.var, s, m)), s, m)
                    s.store[m.curr_module][stmt.pre.left.var.name] = str_to_int(evaluate(parse_tokens(tokenize(stmt.post.right.var, s, m)), s, m), s, m)
            else:
                m.count_conditionals_2(m, stmt.statement)
                self.branch = False
                for lhs in m.cond_assigns[m.curr_module]:
                    if str(stmt.cond) in m.cond_assigns[m.curr_module][lhs]:
                        m.updates[lhs] = (1, m.cond_assigns[m.curr_module][lhs]["default"])
                #self.visit_stmt(m, s, stmt.pre,  modules)
                s.store[m.curr_module][str(stmt.pre.left.var.name)] = stmt.pre.right.var.value
                
                solver_start = time.process_time()
                self.visit_expr(m, s, stmt.cond)
                solver_start = time.process_time()
                m.solver_time += solver_end - solver_start
                while str_to_bool(evaluate(parse_tokens(tokenize(stmt.cond, s, m)), s, m), s, m):
                    self.visit_stmt(m, s, stmt.statement,  modules)
                    print("hi")
                    s.store[m.curr_module][stmt.pre.left.var.name] = str_to_int(evaluate(parse_tokens(tokenize(stmt.post.right.var, s, m)), s, m), s, m)

                if (m.abandon and m.debug):
                    print("Abandoning this path!")

                    return
                self.visit_stmt(m, s, stmt.statement,  modules, direction)
        elif isinstance(stmt, SystemCall):
            m.assertion_violation = True
        elif isinstance(stmt, SingleStatement):
            self.visit_stmt(m, s, stmt.statement,  modules, direction)
        elif isinstance(stmt, InstanceList):
            if not stmt.module in m.instances_seen:
                m.instances_seen[stmt.module] = 1
            instance_index = m.instances_seen[stmt.module]
            m.instances_seen[stmt.module] += 1 % m.instance_count[stmt.module]
            m.instances_loc[f"{stmt.module}_{instance_index}"] = m.curr_module
            if stmt.module in modules:
                for port in stmt.instances[0].portlist:
                    if str(port.argname) not in s.store[f"{stmt.module}_{instance_index}"]:
                        if f"{stmt.module}_{instance_index}" in m.instances_loc:
                            containing_module = m.instances_loc[f"{stmt.module}_{instance_index}"]
                            if str(port.argname) in s.store[containing_module]:
                                s.store[f"{stmt.module}_{instance_index}"][str(port.portname)] = s.store[containing_module][str(port.argname)]
                                m.intermodule_dependencies[containing_module][str(port.argname)] = (f"{stmt.module}_{instance_index}", str(port.portname))
                            else:
                                s.store[containing_module][str(port.argname)] = init_symbol()
                                s.store[f"{stmt.module}_{instance_index}"][str(port.portname)] = s.store[containing_module][str(port.argname)]
                                m.intermodule_dependencies[containing_module][str(port.argname)] = (f"{stmt.module}_{instance_index}", str(port.portname))
                    else:
                        s.store[f"{stmt.module}_{instance_index}"][str(port.portname)] = s.store[f"{stmt.module}_{instance_index}"][str(port.argname)]

                if m.opt_1:
                    if m.config[m.curr_module] in m.seen_mod[stmt.module]:
                        self.execute_child(modules[stmt.module], s, m, f"{stmt.module}_{instance_index}")
                    elif m.seen_mod[f"{stmt.module}_{instance_index}"][m.config[f"{stmt.module}_{instance_index}"]] == {}:
                        #print("hello")
                        self.execute_child(modules[stmt.module], s, m, f"{stmt.module}_{instance_index}")
                    else:
                        #TODO: Instead of another self.execute, we can just go and grab that state and bring it over int our own
                        m.merge_states(s, s.store, True, f"{stmt.module}_{instance_index}")
                        # this loop updates all the signals in the top level module
                        # so that the param connections seem like cont. assigns
                        for port in stmt.instances[0].portlist:
                            s.store[f"{stmt.module}_{instance_index}"][str(port.argname)] = s.store[f"{stmt.module}_{instance_index}"][str(port.portname)]
                else:
                    for port in stmt.instances[0].portlist:
                        if f"{stmt.module}_{instance_index}" in m.instances_loc:
                            containing_module = m.instances_loc[f"{stmt.module}_{instance_index}"]
                            s.store[f"{stmt.module}_{instance_index}"][str(port.portname)] = s.store[containing_module][str(port.argname)]
                            m.intermodule_dependencies[containing_module][str(port.argname)] = (f"{stmt.module}_{instance_index}", str(port.portname))

                    self.execute_child(modules[stmt.module], s, m, f"{stmt.module}_{instance_index}")
        elif isinstance(stmt, Case):
            m.curr_level += 1
            self.cond = True
            bit_index = len(m.path_code) - m.curr_level

            if (direction):
                self.branch = True
                for lhs in m.cond_assigns[m.curr_module]:
                    if str(stmt.cond) in m.cond_assigns[m.curr_module][lhs]:
                        m.updates[lhs] = (1, m.cond_assigns[m.curr_module][lhs][str(stmt.cond)])
                

                solver_start = time.process_time()
                if stmt.cond is None:
                    self.visit_expr(m, s, stmt.cond)
                else:
                    self.visit_expr(m, s, stmt.cond[0])
                solver_end = time.process_time()
                m.solver_time += solver_end - solver_start
                if (m.abandon and m.debug):
 
                    print("Abandoning this path!")
                    return
                # m.curr_level == (32 - bit_index) this is always true
                #if nested_ifs == 0 and m.curr_level < 2 and self.seen_all_cases(m, bit_index, nested_ifs):
            else:
                self.branch = False
                for lhs in m.cond_assigns[m.curr_module]:
                    if str(stmt.cond) in m.cond_assigns[m.curr_module][lhs]:
                        m.updates[lhs] = (1, m.cond_assigns[m.curr_module][lhs]["default"])


                solver_start = time.process_time()
                if stmt.cond is None:
                    self.visit_expr(m, s, stmt.cond)
                else:
                    self.visit_expr(m, s, stmt.cond[0])
                solver_end = time.process_time()
                m.solver_time += solver_end - solver_start
                if (m.abandon and m.debug):
                    print("Abandoning this path!")

                    return

        elif isinstance(stmt, CaseStatement):
            m.curr_case = stmt.comp
            for case in stmt.caselist:
                self.visit_stmt(m, s, case, modules, direction)

    def visit_expr(self, m: ExecutionManager, s: SymbolicState, expr: Value) -> None:
        """Traverse the expressions in a hardware design."""
        if isinstance(expr, Reg):
            if not expr.name in m.reg_writes:
                if m.cycle == 0:
                    #print(expr.name)
                    s.store[m.curr_module][expr.name] = init_symbol()
                m.reg_writes.add(expr.name)
                m.reg_decls.add(expr.name)
                if not expr.width is None: 
                    if isinstance(expr.width.msb, Operator):
                        val = str_to_int(evaluate(parse_tokens(tokenize(expr.width.msb, s, m)), s, m), s, m)
                        if not val is None:
                            m.reg_widths[expr.name] = 2 ** (val + 1)
                        else:
                            val = simpl_str_exp(evaluate(parse_tokens(tokenize(expr.width.msb, s, m)), s, m), s, m)
                            m.reg_widths[expr.name] = val
                else:
                    m.reg_widths[expr.name] = 4294967296
            else: 
                # do nothing because we don't want to overwrite the previous state of the register
                ...
        elif isinstance(expr, Wire):
            if m.cycle == 0:
                s.store[m.curr_module][expr.name] = init_symbol()
            return 
        elif isinstance(expr, Eq):
            # assume left is identifier
            #parse_expr_to_Z3(expr, s, m)
            if isinstance(expr.left, Partselect):                      
                x = BitVec(s.store[m.curr_module][expr.left.var.name], 32)
            elif (s.store[m.curr_module][expr.left.name]).isdigit():
                int_val = IntVal(int(s.store[m.curr_module][expr.left.name]))
                x = Int2BV(int_val, 32)
            elif (s.store[m.curr_module][expr.left.name]).split(" ")[0].isdigit():
                x = Int2BV(IntVal(str_to_int(s.store[m.curr_module][expr.left.name], s, m)), 32)
            else: 
                x = BitVec(s.store[m.curr_module][expr.left.name], 32)
            
            if isinstance(expr.right, IntConst):
                if "'h" in str(expr.right.value) or "'b" in str(expr.right.value) or "'d" in str(expr.right.value):
                    int_val = IntVal(int(str(expr.right.value.split("'")[1][1:])))
                else:
                    int_val = IntVal(expr.right.value)
                y = Int2BV(int_val, 32)
            else:
                y = BitVec(expr.right.name, 32)
            if self.branch:
                s.pc.push()
                s.pc.add(x==y)
                if not solve_pc(s.pc):
                    s.pc.pop()
                    m.abandon = True
                    m.ignore  = True
                    return
            else: 
                s.pc.push()
                s.pc.add(x != y)
                if not solve_pc(s.pc):
                    s.pc.pop()
                    m.abandon = True
                    m.ignore = True
                    return
               
        elif isinstance(expr, Identifier):
            # change this to one since inst is supposed to just be 1 bit width
            # and the identifier class actually doesn't have a width param
            symbol = s.store[m.curr_module][expr.name]
            if "'h" in s.store[m.curr_module][expr.name] or "'b" in s.store[m.curr_module][expr.name] or "'d" in s.store[m.curr_module][expr.name]:
                symbol = s.store[m.curr_module][expr.name].split("'")[1][1:]
                s.store[m.curr_module][expr.name] = symbol
                if not symbol.isdigit():
                    x = BitVec(s.store[m.curr_module][expr.name], 1)
                else:
                    x = Int2BV(IntVal(int(symbol)), 1)
            elif isinstance(symbol, dict):
                bit_vec_list = parse_concat_to_Z3(symbol, s, m)
                #TODO: get the right widths
                x = BitVec(Concat(bit_vec_list), 1)
            else:
                x = BitVec(s.store[m.curr_module][expr.name], 1)
            y = BitVec(1, 1)
            one = IntVal(1)
            zero = IntVal(0)
            one_bv = Int2BV(one, 1)
            zero_bv = Int2BV(zero, 1)
            if self.branch:
                s.pc.push()
                s.pc.add(x==one_bv)
                if not solve_pc(s.pc):
                    s.pc.pop()
                    #print("Abandoning infeasible path")
                    m.abandon = True
                    m.ignore = True
                    return
            else: 
                s.pc.push()
                s.pc.add(x != one_bv)
                if not solve_pc(s.pc):
                    s.pc.pop()
                    #print("Abandoning infeasible path")
                    m.abandon = True
                    m.ignore = True
                    time.process_time()
                    return

        # Handling Assertions
        elif isinstance(expr, NotEql):
            print("assertion")
            parse_expr_to_Z3(expr, s, m)
            # x = BitVec(expr.left.name, 32)
            # y = BitVec(int(expr.right.value), 32)
            # if self.branch:
            #     s.pc.add(x != y)
            # else: 
            #     s.pc.add(x == y)
        elif isinstance(expr, Land):
            parse_expr_to_Z3(expr, s, m)
        elif isinstance(expr, tuple):
            cond = expr[0]
            base = (str(cond.value)[0:1])
            if base == "b'":
                value = (int(cond.value.split("'")[1], 2))
            elif base == "h'":
                value = (int(cond.value.split("'")[1], 16))
            elif isinstance(cond, IntConst):
                if "'b" in str(cond.value):
                    width = int(cond.value.split("'")[0])
                    value = (int(cond.value.split("'")[1][1:], 2))
                elif base == "'h"  in str(cond.value):
                    width = int(cond.value.split("'")[0])
                    value = (int(cond.value.split("'")[1][1:], 16))
                else:   
                    value = int(cond.value)
                y = Int2BV(IntVal(value), width)
            else:
                value = s.store[m.curr_module][cond]

            symbol = s.store[m.curr_module][str(m.curr_case)]
            if isinstance(symbol, dict):
                bit_vec_list = parse_concat_to_Z3(symbol, s, m)
                #TODO: get the right widths
                if len(bit_vec_list) == 2:
                    x = Concat(BitVec(str(bit_vec_list[0]), width // 2), BitVec(str(bit_vec_list[1]), width //2))
                else:
                    raise Exception
            else:
                x = BitVec(s.store[m.curr_module][str(m.curr_case)], width)

            if self.branch:
                s.pc.push()
                s.pc.add(x==y)
                if not solve_pc(s.pc):
                    s.pc.pop()
                    #print("Abandoning infeasible path")
                    m.abandon = True
                    m.ignore = True
                    return
            else: 
                s.pc.push()
                s.pc.add(x != y)
                if not solve_pc(s.pc):
                    s.pc.pop()
                    #print("Abandoning infeasible path")
                    m.abandon = True
                    m.ignore = True
                    return
        elif isinstance(expr, Operator):
            #TODO Fix?
            new_val = simpl_str_exp(evaluate(parse_tokens(tokenize(expr, s, m)),s,m), s, m)
            x = BitVec(new_val, 1)
            one = IntVal(1)
            one_bv = Int2BV(one, 1)
            if self.branch:
                s.pc.push()
                s.pc.add(x==one_bv)
                if not solve_pc(s.pc):
                    s.pc.pop()
                    #print("Abandoning infeasible path")
                    m.abandon = True
                    m.ignore = True
                    return
            else: 
                s.pc.push()
                s.pc.add(x != one_bv)
                if not solve_pc(s.pc):
                    s.pc.pop()
                    #print("Abandoning infeasible path")
                    m.abandon = True
                    m.ignore = True
                    time.process_time()
                    return
        elif isinstance(expr, Decl):
            #print("here")
            ...
        else:   
            return None

    def execute_child(self, ast: ModuleDef, state: SymbolicState, parent_manager: Optional[ExecutionManager], instance) -> None:
        """Drives symbolic execution of child modules."""
        # different manager
        # same state
        # dont call pc solve
        manager_sub = ExecutionManager()
        manager_sub.is_child = True
        manager_sub.curr_module = instance
        parent_manager.init_run(manager_sub, ast)
        manager_sub.path_code = parent_manager.config[instance]
        manager_sub.seen = parent_manager.seen

        # mark this exploration of the submodule as seen and store the state so we don't have to explore it again.
        if parent_manager.seen_mod[instance][manager_sub.path_code] == {}:
            parent_manager.seen_mod[instance][manager_sub.path_code] = state.store
        else:
            ...
            #print("already seen this")
        # i'm pretty sure we only ever want to do 1 loop here
        for i in range(1):
        #for i in range(manager_sub.num_paths):
            manager_sub.path_code = parent_manager.config[instance]
            self.visit_module(manager_sub, state, ast, parent_manager.modules)

            containing_module = parent_manager.instances_loc[instance]
            deps = parent_manager.intermodule_dependencies[containing_module]
            for parent_signal in deps:
                child = deps[parent_signal]
                # propagate back up unless changed in top
                if not parent_signal in parent_manager.updates and child[1] in state.store[child[0]]:
                    state.store[containing_module][parent_signal] = state.store[child[0]][child[1]]
            if (parent_manager.assertion_violation):
                print("Assertion violation")
                parent_manager.assertion_violation = False
                solver_start = time.process_time()
                solve_pc(state.pc)
                solver_end = time.process_time()
                parent_manager.solver_time += solver_end - solver_start
            parent_manager.curr_level = 0
            #state.pc.reset()
        #manager.path_code = to_binary(0)
        #print(f" finishing {ast.name}")
        if manager_sub.ignore:
            parent_manager.ignore = True

        #manager.is_child = False
        ## print(state.store)
