"""Depth First Traversal of the AST."""
from .template import Search
from z3 import Solver, Int, BitVec, Int2BV, IntVal, Concat
from engine.execution_manager import ExecutionManager
from engine.symbolic_state import SymbolicState
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement, SingleStatement, And, Constant, Rvalue, Plus, Input, Output
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block, SystemCall, Land, InstanceList, IntConst, Partselect, Ioport
from pyverilog.vparser.ast import Value, Reg, Initial, Eq, Identifier, Initial,  NonblockingSubstitution, Decl, Always, Assign, NotEql, Case
from pyverilog.vparser.ast import Concat, BlockingSubstitution, Parameter, StringConst, Wire, PortArg, Cond, Pointer, IdentifierScope, Operator
from helpers.utils import init_symbol
from typing import Optional
from helpers.rvalue_parser import tokenize, parse_tokens, evaluate, resolve_dependency, count_nested_cond, cond_options, str_to_int, str_to_bool
from helpers.rvalue_to_z3 import parse_expr_to_Z3, solve_pc, parse_concat_to_Z3
from helpers.utils import to_binary
import os


class DepthFirst(Search):

    def visit_module(self, m: ExecutionManager, s: SymbolicState, module: ModuleDef, modules: Optional):
        """Traverse the module of a hardware design, depth first."""
        m.currLevel = 0
        params = module.paramlist.params
        ports = module.portlist.ports



        for param in params:
            if isinstance(param.list[0], Parameter):
                if param.list[0].name not in s.store[m.curr_module]:
                    s.store[m.curr_module][param.list[0].name] = init_symbol()

        for port in ports:
            if isinstance(port, Ioport):
                if str(port.first.name) not in s.store[m.curr_module]:
                    s.store[m.curr_module][str(port.first.name)] = init_symbol()
            else:
                if port.name not in s.store[m.curr_module]:
                    s.store[m.curr_module][port.name] = init_symbol()


        if not m.is_child and not m.init_run_flag and not m.ignore:
            print("Inital state:")
            print(s.store)
            ...
            

        for item in module.items:
            if isinstance(item, Value):
                self.visit_expr(m, s, item)
            else:
                self.visit_stmt(m, s, item, modules)

        # simpl / collapsing step
        for module in m.cond_assigns:
            for signal in m.cond_assigns[module]:
                res = m.cond_assigns[module][signal]
                if s.store[m.curr_module][str(signal)].startswith("If("):
                    cond = s.store[m.curr_module][str(signal)][3:].split(",")[0][:-1]
                    if str_to_bool(cond, s, m):
                        s.store[m.curr_module][str(signal)] = s.store[m.curr_module][str(m.cond_assigns[m.curr_module][signal][cond])]
                    else:
                        s.store[m.curr_module][str(signal)] = m.cond_assigns[m.curr_module][signal]["default"]

        if m.ignore:
            # print("infeasible path...")
            ...
        
        if not m.is_child and not m.init_run_flag and not m.ignore and not m.abandon:
        #if not m.is_child and m.assertion_violation and not m.ignore and not m.abandon:
            print(f"Cycle {m.cycle} final state:")
            print(s.store)
       
            print(f"Cycle {m.cycle} final path condition:")
            print(s.pc)
    

    def visit_stmt(self, m: ExecutionManager, s: SymbolicState, stmt: Node, modules: Optional):
        "Traverse the statements in a hardware design"
        if m.ignore:
            return
        if isinstance(stmt, Decl):
            for item in stmt.list:
                if isinstance(item, Value):
                    self.visit_expr(m, s, item)
                else:
                    self.visit_stmt(m, s, item, modules)
                # ref_name = item.name
                # ref_width = int(item.width.msb.value) + 1
                #  dont want to actually call z3 here, just when looking at PC
                # x = BitVec(ref_name, ref_width)
        elif isinstance(stmt, Parameter):
            if isinstance(stmt.value.var, IntConst):
                s.store[m.curr_module][stmt.name] = stmt.value.var
            elif isinstance(stmt.value.var, Identifier):
                s.store[m.curr_module][stmt.name] = s.store[m.curr_module][stmt.value.var]
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
                    self.visit_stmt(m, s, sub_stmt, modules)
                    for signal in m.dependencies:
                        if m.dependencies[m.curr_module][signal] in m.updates:
                            if m.updates[m.dependencies[m.curr_module][signal]][0] == 1:
                                prev_symbol = m.updates[m.dependencies[m.curr_module][signal]][1]
                            
                                if '[' in s.store[m.curr_module][signal]:
                                    
                                    parts = s.store[m.curr_module][signal].partition("[")

                                    new_symbol = s.store[m.curr_module][m.dependencies[m.curr_module][signal]]
                                    first_part = parts[0].replace(parts[0], new_symbol)
                                    for i in range(1, len(parts)):
                                        new_symbol += parts[i]

                                    s.store[m.curr_module][signal] = new_symbol
                                else:
                                    new_symbol = s.store[m.curr_module][m.dependencies[m.curr_module][signal]]
                                    s.store[m.curr_module][signal] = s.store[m.curr_module][signal].replace(prev_symbol, new_symbol)
            else: 
                # print(sens_list.list[0].sig) # clock
                # print(sens_list.list[0].type) # posedge
                sub_stmt = stmt.statement
                m.in_always = True
                self.visit_stmt(m, s, sub_stmt, modules)
                for module in m.dependencies:
                    for signal in m.dependencies[module]:
                        if m.dependencies[module][signal] in m.updates:
                            if m.updates[m.dependencies[module][signal]][0] == 1:
                                print(f"dirty {m.updates[m.dependencies[module][signal]][0]}")
                                prev_symbol = m.updates[m.dependencies[module][signal]][1]

                                if '[' in s.store[module][signal]:
                                    
                                    parts = s.store[module][signal].partition("[")

                                    new_symbol = s.store[module][m.dependencies[module][signal]]
                                    first_part = parts[0].replace(parts[0], new_symbol)
                                    for i in range(1, len(parts)):
                                        new_symbol += parts[i]

                                    s.store[module][signal] = new_symbol
                                else:
                                    new_symbol = s.store[module][m.dependencies[module][signal]]
                                    s.store[module][signal] = s.store[module][signal].replace(prev_symbol, new_symbol)
                        for lhs in m.cond_assigns[module]:
                            if lhs in m.dependencies[module] and isinstance(m.updates[lhs], tuple) and m.updates[lhs][0] == 1:
                                prev_symbol = str(m.updates[lhs][1])
                                if not prev_symbol.isdigit() and prev_symbol in s.store[m.curr_module]: 
                                    prev_symbol = s.store[m.curr_module][prev_symbol]
                                if '[' in s.store[module][lhs]:
                                    
                                    parts = s.store[module][lhs].partition("[")

                                    new_symbol = s.store[module][m.dependencies[module][lhs]]
                                    first_part = parts[0].replace(parts[0], new_symbol)
                                    for i in range(1, len(parts)):
                                        new_symbol += parts[i]

                                    s.store[module][lhs] = new_symbol
                                else:
                                    s.store[module][lhs] = prev_symbol
                                m.updates[lhs] = 0 
                        # simplificiation / collapsing step
            m.in_always = False               
        elif isinstance(stmt, Assign):
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
                m.dependencies[m.curr_module][stmt.left.var.name] = resolve_dependency(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m)
                opts = cond_options(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m, {})
                m.cond_assigns[m.curr_module][stmt.left.var.name] = opts
                # complexity is how many nested conditonals we have on the rhs
                complexity = count_nested_cond(stmt.right.var.cond, stmt.right.var.true_value, stmt.right.var.false_value, s, m)
                #print(complexity)
                new_r_value = evaluate(parse_tokens(tokenize(stmt.right.var, s, m)), s, m)
                if str(stmt.right.var.cond) in opts:
                    new_cond = new_r_value[3:].split(",")[0][:-1]
                    #print(f"new r {new_r_value}")

                    opts[new_cond] = opts.pop(str(stmt.right.var.cond))
                s.store[m.curr_module][stmt.left.var.name] = new_r_value
            elif isinstance(stmt.right.var, Pointer):
                s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.ptr.value}]"
                m.dependencies[m.curr_module][stmt.left.var.name] = stmt.right.var.var.name
                m.updates[stmt.left.var.name] = 0
            else:
                new_r_value = evaluate(parse_tokens(tokenize(stmt.right.var, s, m)), s, m)
                if new_r_value != None:
                    s.store[m.curr_module][stmt.left.var.name] = new_r_value
                else:
                    s.store[m.curr_module][stmt.left.var.name] = s.store[m.curr_module][stmt.right.var.name]
            if isinstance(stmt.left.var, Pointer):
                m.updates[f"{stmt.left.var.var}[{stmt.left.var.ptr}]"]= (1, prev_symbol)
            elif isinstance(stmt.left.var, Partselect):
                m.updates[f"{stmt.left.var.var.name}[{stmt.left.var.msb}:{stmt.left.var.lsb}]"] = (1, prev_symbol)
            else:

                if isinstance(stmt.left.var, Concat):
                    for sub_item in stmt.left.var.list:
                        m.updates[sub_item.name] = (1, prev_symbol)
                else:
                    m.updates[stmt.left.var.name] = (1, prev_symbol)
        elif isinstance(stmt, NonblockingSubstitution):
            reg_width = 0
            if isinstance(stmt.left.var, Identifier):
                if stmt.left.var.name in m.reg_decls:
                    #print(m.reg_widths)
                    reg_width = m.reg_widths[stmt.left.var.name]
            if isinstance(stmt.right.var, IntConst):
                s.store[m.curr_module][stmt.left.var.name] = stmt.right.var.value
            elif isinstance(stmt.right.var, Identifier):
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
                        else:
                            s.store[m.curr_module][stmt.left.var.name][item.name] = s.store[m.curr_module][item.name]
            elif isinstance(stmt.right.var, StringConst):
                if "'h" in stmt.right.var.value or "'b" in stmt.right.var.value or "'d" in stmt.right.var.value:
                    s.store[m.curr_always][stmt.left.var.name] = stmt.right.var.value.split("'")[1][1:]
                else:
                    s.store[m.curr_module][stmt.left.var.name] = stmt.right.var.value
            elif isinstance(stmt.right.var, Partselect):
                s.store[m.curr_module][stmt.left.var.name] = f"{s.store[m.curr_module][stmt.right.var.var.name]}[{stmt.right.var.msb}:{stmt.right.var.lsb}]"
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
            #print(s.store)
            #m.updates[stmt.left.var.name] = (1, prev_symbol)
        elif isinstance(stmt, BlockingSubstitution):
            prev_symbol = s.store[m.curr_module][stmt.left.var.name]
            if isinstance(stmt.right.var, IntConst):
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
            m.updates[stmt.left.var.name] = (1, prev_symbol)
        elif isinstance(stmt, Block):
            for item in stmt.statements: 
                self.visit_stmt(m, s, item, modules)
        elif isinstance(stmt, Initial):
            self.visit_stmt(m, s, stmt.statement,  modules)
        elif isinstance(stmt, IfStatement):
            m.curr_level += 1
            self.cond = True
            bit_index = len(m.path_code) - m.curr_level
            if (m.path_code[len(m.path_code) - m.curr_level] == '1'):
                self.branch = True

                for lhs in m.cond_assigns[m.curr_module]:
                    if str(stmt.cond) in m.cond_assigns[m.curr_module][lhs]:
                        m.updates[lhs] = (1, m.cond_assigns[m.curr_module][lhs][str(stmt.cond)])

                self.visit_expr(m, s, stmt.cond)
                if (m.abandon):
                    #print("Abandoning this path!")
                    return
                nested_ifs = m.count_conditionals_2(m, stmt.true_statement)
                diff = 32 - bit_index
                # m.curr_level == (32 - bit_index) this is always true
                #if nested_ifs == 0 and m.curr_level < 2 and self.seen_all_cases(m, bit_index, nested_ifs):
                if m.seen_all_cases(m, bit_index, nested_ifs):
                    m.completed.append(bit_index)
                self.visit_stmt(m, s, stmt.true_statement,  modules)
            else:
                self.branch = False

                for lhs in m.cond_assigns[m.curr_module]:
                    if str(stmt.cond) in m.cond_assigns[m.curr_module][lhs]:
                        m.updates[lhs] = (1, m.cond_assigns[m.curr_module][lhs]["default"])
                        
                self.visit_expr(m, s, stmt.cond)
                if (m.abandon):
                    #print("Abandoning this path!")

                    return
                self.visit_stmt(m, s, stmt.false_statement,  modules)
        elif isinstance(stmt, SystemCall):
            m.assertion_violation = True
        elif isinstance(stmt, SingleStatement):
            self.visit_stmt(m, s, stmt.statement,  modules)
        elif isinstance(stmt, InstanceList):
            if stmt.module in modules:
                for port in stmt.instances[0].portlist:
                    if str(port.argname) not in s.store[m.curr_module]:
                        if m.cycle == 0:
                            s.store[m.curr_module][str(port.argname)] = init_symbol()
                            s.store[stmt.module][str(port.portname)] = s.store[m.curr_module][str(port.argname)]
                    else:
                        s.store[stmt.module][str(port.portname)] = s.store[m.curr_module][str(port.argname)]
                if m.opt_1:
                    if m.seen_mod[stmt.module][m.config[stmt.module]] == {}:
                        #print("hello")
                        self.execute_child(modules[stmt.module], s, m)
                    else:
                        #TODO: Instead of another self.execute, we can just go and grab that state and bring it over int our own
                        print("already seen")
                        m.merge_states(s, s.store[stmt.module])
                        # this loop updates all the signals in the top level module
                        # so that the param connections seem like cont. assigns
                        for port in stmt.instances[0].portlist:
                            s.store[m.curr_module][str(port.argname)] = s.store[stmt.module][str(port.portname)]
                else:
                    #print("hey")
                    for port in stmt.instances[0].portlist:
                        s.store[m.curr_module][str(port.argname)] = s.store[stmt.module][str(port.portname)]
                    self.execute_child(modules[stmt.module], s, m)
        elif isinstance(stmt, Case):
            m.curr_level += 1
            self.cond = True
            bit_index = len(m.path_code) - m.curr_level

            if (m.path_code[len(m.path_code) - m.curr_level] == '1'):
                self.branch = True
                for lhs in m.cond_assigns[m.curr_module]:
                    if str(stmt.cond) in m.cond_assigns[m.curr_module][lhs]:
                        m.updates[lhs] = (1, m.cond_assigns[m.curr_module][lhs][str(stmt.cond)])
                self.visit_expr(m, s, stmt.cond)
                if (m.abandon):
 
                    #print("Abandoning this path!")
                    return
                # m.curr_level == (32 - bit_index) this is always true
                #if nested_ifs == 0 and m.curr_level < 2 and self.seen_all_cases(m, bit_index, nested_ifs):
            else:
                self.branch = False
                for lhs in m.cond_assigns[m.curr_module]:
                    if str(stmt.cond) in m.cond_assigns[m.curr_module][lhs]:
                        m.updates[lhs] = (1, m.cond_assigns[m.curr_module][lhs]["default"])

                self.visit_expr(m, s, stmt.cond)
                if (m.abandon):
                    #print("Abandoning this path!")

                    return

        elif isinstance(stmt, CaseStatement):
            m.curr_case = stmt.comp
            for case in stmt.caselist:
                self.visit_stmt(m, s, case, modules)

    def visit_expr(self, m: ExecutionManager, s: SymbolicState, expr: Value) -> None:
        """Traverse the expressions in a hardware design."""
        if isinstance(expr, Reg):
            if not expr.name in m.reg_writes:
                if m.cycle == 0: 
                    s.store[m.curr_module][expr.name] = init_symbol()
                m.reg_writes.add(expr.name)
                m.reg_decls.add(expr.name)
                if not expr.width is None: 
                    if isinstance(expr.width.msb, Operator):
                        val = str_to_int(evaluate(parse_tokens(tokenize(expr.width.msb, s, m)), s, m), s, m)
                        m.reg_widths[expr.name] = 2 ** (val + 1)
                    else:
                        m.reg_widths[expr.name] = 2 ** (int(expr.width.msb.value) + 1)
                else:
                    m.reg_widths[expr.name] = 4294967296
            else: 
                # do nothing because we don't want to overwrite the previous state of the register
                ...
        elif isinstance(expr, Wire):
            if m.cycle == 0:
                s.store[m.curr_module][expr.name] = init_symbol()
        elif isinstance(expr, Eq):
            # assume left is identifier
            #parse_expr_to_Z3(expr, s, m)
            if (s.store[m.curr_module][expr.left.name]).isdigit():
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
        return None

    def execute_child(self, ast: ModuleDef, state: SymbolicState, parent_manager: Optional[ExecutionManager]) -> None:
        """Drives symbolic execution of child modules."""
        # different manager
        # same state
        # dont call pc solve
        manager_sub = ExecutionManager()
        manager_sub.is_child = True
        manager_sub.curr_module = ast.name
        parent_manager.init_run(manager_sub, ast)
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

        #manager.is_child = False
        ## print(state.store)