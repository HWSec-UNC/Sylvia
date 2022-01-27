"""Template for a search strategy."""
from abc import ABC, abstractmethod
from z3 import Solver, Int, BitVec
from engine.execution_manager import ExecutionManager
from engine.symbolic_state import SymbolicState
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement, SingleStatement, And, Constant, Rvalue, Plus, Input, Output
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block, SystemCall, Land, InstanceList, IntConst, Partselect, Ioport
from pyverilog.vparser.ast import Value, Reg, Initial, Eq, Identifier, Initial,  NonblockingSubstitution, Decl, Always, Assign, NotEql, Case
from pyverilog.vparser.ast import Concat, BlockingSubstitution, Parameter, StringConst, Wire, PortArg
from helpers.utils import init_symbol
from typing import Optional
from helpers.rvalue_parser import tokenize, parse_tokens, evaluate
from helpers.rvalue_to_z3 import parse_expr_to_Z3, solve_pc


class Search:
    """The base methods needed to implement a search strategy
    Can add as many more as you need, of course."""

    @abstractmethod
    def visit_module(self, m: ExecutionManager, s: SymbolicState, module: ModuleDef, modules: Optional):
        """Traverse the modules of a hardware design."""
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

        for item in module.items:
            if isinstance(item, Value):
                #TODO: Visit expression?
                pass
            else:
                #TODO: Visit statement?
                pass
        

    @abstractmethod
    def visit_stmt(self, m: ExecutionManager, s: SymbolicState, stmt: Node, modules):
        """Traverse the statements within a module."""
        if isinstance(stmt, Decl):
            for item in stmt.list:
                #TODO
                pass
        elif isinstance(stmt, Parameter):
            if isinstance(stmt.value.var, IntConst):
                s.store[m.curr_module][stmt.name] = stmt.value.var
            elif isinstance(stmt.value.var, Identifier):
                s.store[m.curr_module][stmt.name] = s.store[m.curr_module][stmt.value.var]
            else:
                s.store[m.curr_module][stmt.name] = init_symbol()
        elif isinstance(stmt, Always):
            sens_list = stmt.sens_list
            #TODO
            pass
        elif isinstance(stmt, Assign):
            if isinstance(stmt.right.var, IntConst):
                s.store[m.curr_module][stmt.left.var.name] = stmt.right.var.value
            elif isinstance(stmt.right.var, Identifier):
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
                s.store[m.curr_module][stmt.left.var.name] = {}
                for item in stmt.right.var.list:
                    s.store[m.curr_module][stmt.left.var.name][item.name] = s.store[m.curr_module][item.name]
            else:
                new_r_value = evaluate(parse_tokens(tokenize(str(stmt.right.var))), s, m)
                if new_r_value != None:
                    s.store[m.curr_module][stmt.left.var.name] = new_r_value
                else:
                    s.store[m.curr_module][stmt.left.var.name] = s.store[m.curr_module][stmt.right.var.name]
        elif isinstance(stmt, NonblockingSubstitution):
            prev_symbol = s.store[m.curr_module][stmt.left.var.name]
            if isinstance(stmt.right.var, IntConst):
                s.store[m.curr_module][stmt.left.var.name] = stmt.right.var.value
            elif isinstance(stmt.right.var, Identifier):
                s.store[m.curr_module][stmt.left.var.name] = s.store[m.curr_module][stmt.right.var.name]
            elif isinstance(stmt.right.var, Concat):
                s.store[m.curr_module][stmt.left.var.name] = {}
                for item in stmt.right.var.list:
                    s.store[m.curr_module][stmt.left.var.name][item.name] = s.store[m.curr_module][item.name]
            elif isinstance(stmt.right.var, StringConst):
                s.store[m.curr_module][stmt.left.var.name] = stmt.right.var.value
            else:
                new_r_value = evaluate(parse_tokens(tokenize(str(stmt.right.var))), s, m)
                if new_r_value != None:
                    s.store[m.curr_module][stmt.left.var.name] = new_r_value
                else:
                    s.store[m.curr_module][stmt.left.var.name] = s.store[m.curr_module][stmt.right.var.name]
            m.updates[stmt.left.var.name] = (1, prev_symbol)
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
                s.store[m.curr_module][stmt.left.var.name] = stmt.right.var.value
            else:
                new_r_value = evaluate(parse_tokens(tokenize(str(stmt.right.var))), s, m)
                if  new_r_value != None:
                    s.store[m.curr_module][stmt.left.var.name] = new_r_value
                else:
                    s.store[m.curr_module][stmt.left.var.name] = s.store[m.curr_module][stmt.right.var.name]
            m.updates[stmt.left.var.name] = (1, prev_symbol)
        elif isinstance(stmt, Block):
            for item in stmt.statements: 
                #TODO: Visit each statement in the Block Statement
                pass
        elif isinstance(stmt, Initial):
            #TODO: Visit each statement in the Initial block
            pass
        elif isinstance(stmt, IfStatement):
            m.curr_level += 1
            self.cond = True
            bit_index = len(m.path_code) - m.curr_level
            if (m.path_code[len(m.path_code) - m.curr_level] == '1'):
                self.branch = True

                #TODO: May want to visit the expression. Access it using stmt.cond self
                if (m.abandon):

                    return
                nested_ifs = m.count_conditionals_2(m, stmt.true_statement)
                diff = 32 - bit_index
                # m.curr_level == (32 - bit_index) this is always true
                #if nested_ifs == 0 and m.curr_level < 2 and self.seen_all_cases(m, bit_index, nested_ifs):
                if m.seen_all_cases(m, bit_index, nested_ifs):
                     m.completed.append(bit_index)
                
                #TODO: Visit the then block?
            else:
                self.branch = False
                #TODO: May want to visit the expression. Access it using stmt.cond self
                if (m.abandon):
                    #print("Abandoning this path!")

                    return
                #TODO: Visit the else block?
        elif isinstance(stmt, SystemCall):
            m.assertion_violation = True
        elif isinstance(stmt, SingleStatement):
            # TODO: Visit that single statement?
            pass
        elif isinstance(stmt, InstanceList):
            if stmt.module in modules:
                for port in stmt.instances[0].portlist:
                    if str(port.argname) not in s.store[m.curr_module]:
                        s.store[m.curr_module][str(port.argname)] = init_symbol()
                        s.store[stmt.module][str(port.portname)] = s.store[m.curr_module][str(port.argname)]
                    else:
                        s.store[stmt.module][str(port.portname)] = s.store[m.curr_module][str(port.argname)]
                m.opt_1 = False
                if m.opt_1:
                    if m.seen_mod[stmt.module][m.config[stmt.module]] == {}:
                        #print("hello")
                        # TODO: Visit child module. See helper execute_child in DFS strategy.
                        pass
                    else:
                        #TODO: Instead of another self.execute, we can just go and grab that state and bring it over int our own
                        #print("ho")
                        m.merge_states(m, s, m.seen_mod[stmt.module][m.config[stmt.module]])
                        # this loop updates all the signals in the top level module
                        # so that the param connections seem like cont. assigns
                        for port in stmt.instances[0].portlist:
                            s.store[m.curr_module][str(port.argname)] = s.store[stmt.module][str(port.portname)]
                else:
                    #print("hey")
                    for port in stmt.instances[0].portlist:
                        s.store[m.curr_module][str(port.argname)] = s.store[stmt.module][str(port.portname)]
                    # TODO: Visit child module. See helper execute_child in DFS strategy.
        elif isinstance(stmt, CaseStatement):
            m.curr_level += 1
            self.cond = True
            bit_index = len(m.path_code) - m.curr_level

            if (m.path_code[len(m.path_code) - m.curr_level] == '1'):
                self.branch = True

                # check if i am the final thing/no more conditionals after me
                # basically, we never want me to be true again after this bc we are wasting time reexploring this

                # TODO: May want to visit the case expr. Can access using stmt.comp
                if (m.abandon):
 
                    #print("Abandoning this path!")
                    return
                # m.curr_level == (32 - bit_index) this is always true
                #if nested_ifs == 0 and m.curr_level < 2 and self.seen_all_cases(m, bit_index, nested_ifs):
                #TODO: Visit case list? 
            else:
                self.branch = False
                # TODO: May want to visit the case expr. Can access using stmt.comp
                if (m.abandon):
                    #print("Abandoning this path!")

                    return
                #TODO: Visit case list? 


    @abstractmethod
    def visit_expr(self, m: ExecutionManager, s: SymbolicState, expr: Value):
        """Traverse the expressions within a statement."""
        if isinstance(expr, Reg):
            s.store[m.curr_module][expr.name] = init_symbol()
        elif isinstance(expr, Wire):
            s.store[m.curr_module][expr.name] = init_symbol()
        elif isinstance(expr, Eq):
            # assume left is identifier
            x = BitVec(s.store[m.curr_module][expr.left.name], 32)
            
            if isinstance(expr.right, IntConst):
                y = BitVec(expr.right.value, 32)
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
            x = BitVec(s.store[m.curr_module][expr.name], 1)
            y = BitVec(1, 1)
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