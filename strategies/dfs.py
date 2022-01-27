"""Depth First Traversal of the AST."""
from .template import Search
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
            # print("Inital state:")
            print(s.store)
            

        for item in module.items:
            if isinstance(item, Value):
                self.visit_expr(m, s, item)
            else:
                self.visit_stmt(m, s, item, modules)

        if m.ignore:
            # print("infeasible path...")
            ...
        
        if not m.is_child and not m.init_run_flag and not m.ignore:
        #if not m.is_child and m.assertion_violation:
            # print("Final state:")
            print(s.store)
       
            # print("Final path condition:")
            # print(s.pc)
            
        elif m.ignore:
            #print("Path abandoned")
            m.abandon = False
            m.ignore = False
            return

    def visit_stmt(self, m: ExecutionManager, s: SymbolicState, stmt: Node, modules: Optional):
        "Traverse the statements in a hardware design"
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
                s.store[m.curr_module][stmt.name] = init_symbol()
        elif isinstance(stmt, Always):
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
                                prev_symbol = m.updates[m.dependencies[module][signal]][1]
                                new_symbol = s.store[module][m.dependencies[module][signal]]
                                s.store[module][signal] = s.store[module][signal].replace(prev_symbol, new_symbol)
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
                self.visit_stmt(m, s, item, modules)
        elif isinstance(stmt, Initial):
            self.visit_stmt(m, s, stmt.statement,  modules)
        elif isinstance(stmt, IfStatement):
            m.curr_level += 1
            self.cond = True
            bit_index = len(m.path_code) - m.curr_level
            if (m.path_code[len(m.path_code) - m.curr_level] == '1'):
                self.branch = True

                # check if i am the final thing/no more conditionals after me
                # basically, we never want me to be true again after this bc we are wasting time reexploring this

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
                        s.store[m.curr_module][str(port.argname)] = init_symbol()
                        s.store[stmt.module][str(port.portname)] = s.store[m.curr_module][str(port.argname)]
                    else:
                        s.store[stmt.module][str(port.portname)] = s.store[m.curr_module][str(port.argname)]
                m.opt_1 = False
                if m.opt_1:
                    if m.seen_mod[stmt.module][m.config[stmt.module]] == {}:
                        #print("hello")
                        self.execute_child(modules[stmt.module], s, m)
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
                    self.execute_child(modules[stmt.module], s, m)
        elif isinstance(stmt, CaseStatement):
            m.curr_level += 1
            self.cond = True
            bit_index = len(m.path_code) - m.curr_level

            if (m.path_code[len(m.path_code) - m.curr_level] == '1'):
                self.branch = True

                # check if i am the final thing/no more conditionals after me
                # basically, we never want me to be true again after this bc we are wasting time reexploring this

                self.visit_expr(m, s, stmt.comp)
                if (m.abandon):
 
                    #print("Abandoning this path!")
                    return
                # m.curr_level == (32 - bit_index) this is always true
                #if nested_ifs == 0 and m.curr_level < 2 and self.seen_all_cases(m, bit_index, nested_ifs):
                self.visit_stmt(m, s, stmt.caselist, modules)
            else:
                self.branch = False
                self.visit_expr(m, s, stmt.comp)
                if (m.abandon):
                    #print("Abandoning this path!")

                    return
                self.visit_stmt(m, s, stmt.caselist, modules)

    def visit_expr(self, m: ExecutionManager, s: SymbolicState, expr: Value) -> None:
        """Traverse the expressions in a hardware design."""
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
                    #print("Abandoning infeasible path")
                    m.abandon = True
                    m.ignore  = True
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