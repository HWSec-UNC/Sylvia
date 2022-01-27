"""Functions of interest for the COI analysis optimization."""
from pyverilog.vparser.ast import Description, ModuleDef, Node, IfStatement, SingleStatement, And, Constant, Rvalue, Plus, Input, Output
from pyverilog.vparser.ast import WhileStatement, ForStatement, CaseStatement, Block, SystemCall, Land, InstanceList, IntConst, Partselect, Ioport
from pyverilog.vparser.ast import Value, Reg, Initial, Eq, Identifier, Initial,  NonblockingSubstitution, Decl, Always, Assign, NotEql, Case
from pyverilog.vparser.ast import Concat, BlockingSubstitution, Parameter, StringConst, Wire, PortArg
from engine.execution_manager import ExecutionManager
from engine.symbolic_state import SymbolicState

def lhs_signals(self, m: ExecutionManager, items):
    """Take stock of which signals are written to in which always blocks for COI analysis."""
    stmts = items
    if isinstance(items, Block):
        stmts = items.statements
        items.cname = "Block"
    if hasattr(stmts, '__iter__'):
        for item in stmts:
            if isinstance(item, IfStatement) or isinstance(item, CaseStatement):
                if isinstance(item, IfStatement):
                    self.lhs_signals(m, item.true_statement)
                    self.lhs_signals(m, item.false_statement)
                if isinstance(item, CaseStatement):
                    for case in item.caselist:
                        self.lhs_signals(m, case.statement)
            if isinstance(item, Block):
                self.lhs_signals(m, item.items)
            elif isinstance(item, Always):
                m.curr_always = item
                m.always_writes[item] = []
                self.lhs_signals(m, item.statement)             
            elif isinstance(item, Initial):
                self.lhs_signals(m, item.statement)
            elif isinstance(item, Case):
                self.lhs_signals(m, item.statement)
            elif isinstance(item, Assign):
                if isinstance(item.left.var, Partselect):
                    if m.curr_always is not None and item.left.var.var.name not in m.always_writes[m.curr_always]:
                        m.always_writes[m.curr_always].append(item.left.var.var.name)
                elif m.curr_always is not None and item.left.var.name not in m.always_writes[m.curr_always]:
                    m.always_writes[m.curr_always].append(item.left.var.name)
            elif isinstance(item, NonblockingSubstitution):
                if isinstance(item.left.var, Partselect):
                    if m.curr_always is not None and item.left.var.var.name not in m.always_writes[m.curr_always]:
                        m.always_writes[m.curr_always].append(item.left.var.var.name)
                elif m.curr_always is not None and item.left.var.name not in m.always_writes[m.curr_always]:
                    m.always_writes[m.curr_always].append(item.left.var.name)
            elif isinstance(item, BlockingSubstitution):
                if isinstance(item.left.var, Partselect):
                    if m.curr_always is not None and item.left.var.var.name not in m.always_writes[m.curr_always]:
                        m.always_writes[m.curr_always].append(item.left.var.var.name)
                elif m.curr_always is not None and item.left.var.name not in m.always_writes[m.curr_always]:
                    m.always_writes[m.curr_always].append(item.left.var.name)
    elif items != None:
        if isinstance(items, IfStatement):
            self.lhs_signals(m, items.true_statement)
            self.lhs_signals(m, items.false_statement)
        if isinstance(items, CaseStatement):
            for case in items.caselist:
                self.lhs_signals(m, case.statement)
        elif isinstance(items, Assign):
            if m.curr_always is not None and items.left.var.name not in m.always_writes[m.curr_always]:
                m.always_writes[m.curr_always].append(items.left.var.name)
        elif isinstance(items, NonblockingSubstitution):
            if m.curr_always is not None and items.left.var.name not in m.always_writes[m.curr_always]:
                m.always_writes[m.curr_always].append(items.left.var.name)
        elif isinstance(items, BlockingSubstitution):
            if m.curr_always is not None and items.left.var.name not in m.always_writes[m.curr_always]:
                m.always_writes[m.curr_always].append(items.left.var.name)


def get_assertions(self, m: ExecutionManager, items):
    """Traverse the AST and get the assertion violating conditions."""
    stmts = items
    if isinstance(items, Block):
        stmts = items.statements
        items.cname = "Block"
    if hasattr(stmts, '__iter__'):
        for item in stmts:
            if isinstance(item, IfStatement) or isinstance(item, CaseStatement):
                if isinstance(item, IfStatement):
                    # starting to check for the assertions
                    if isinstance(item.true_statement, Block):
                        if isinstance(item.true_statement.statements[0], SingleStatement):
                            if isinstance(item.true_statement.statements[0].statement, SystemCall) and "ASSERTION" in item.true_statement.statements[0].statement.args[0].value:
                                m.assertions.append(item.cond)
                                print("assertion found")
                    else:     
                        return 
                        #self.get_assertions(m, item.true_statement)
                        #self.get_assertions(m, item.false_statement)
                if isinstance(item, CaseStatement):
                    for case in item.caselist:
                        self.get_assertions(m, case.statement)
            elif isinstance(item, Block):
                self.get_assertions(m, item.items)
            elif isinstance(item, Always):
                self.get_assertions(m, item.statement)             
            elif isinstance(item, Initial):
                self.get_assertions(m, item.statement)
            elif isinstance(item, Case):
                self.get_assertions(m, item.statement)
    elif items != None:
        if isinstance(items, IfStatement):
            self.get_assertions(m, items.true_statement)
            self.get_assertions(m, items.false_statement)
        if isinstance(items, CaseStatement):
            for case in items.caselist:
                self.get_assertions(m, case.statement)

def map_assertions_signals(self, m: ExecutionManager):
    """Map the assertions to a list of relevant signals."""
    signals = []
    for assertion in m.assertions:
        if isinstance(assertion.left, Identifier):
            signals.append(assertion.left.name)
    return signals

def assertions_always_intersect(self, m: ExecutionManager):
    """Get the always blocks that have the signals relevant to the assertions."""
    signals_of_interest = self.map_assertions_signals(m)
    blocks_of_interest = []
    for block in m.always_writes:
        for signal in signals_of_interest:
            if signal in m.always_writes[block]:
                blocks_of_interest.append(block)
    m.blocks_of_interest = blocks_of_interest