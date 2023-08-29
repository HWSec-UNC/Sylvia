"""The Symbolic State is comprised of the path condition and the symbolic store. There 
are some other methods here that may be helpful, too."""

import z3
from z3 import Solver, Int, BitVec, BitVecSort
from pyverilog.vparser.ast import Pointer

class SymbolicState:
    pc = Solver()
    assertion_counter = 0
    sort = BitVecSort(32)
    clock_cycle: int = 0
    #TODO need to change to be a nested mapping of module names to dictionaries
    # can be initalized at the beginning of the run 
    store = {}

    # set to true when evaluating a conditoin so that
    # evaluating the expression knows to add the expr to the
    # PC, set to false after
    cond: bool = False

    def get_symbolic_expr(self, module_name: str, var_name: str) -> str:
        """Just looks up a symbolic expression associated with a specific variable name
        in that particular module."""
        if '[' in var_name:
            name = var_name.split("[")[0]
            return self.store[module_name][name]
        elif '.' in var_name:
            real_module_name = var_name.split(".")[0]
            real_var_name = var_name.split(".")[1]
            return self.store[real_module_name][real_var_name]
        return self.store[module_name][var_name]

    def get_symbols(self):
        """Returns a list of all the symbols present in the symbolic state.
        This is useful in the parsing to z3 phase because we need to know what symbols to declare as constants."""
        symbols_list = []
        for module in self.store:
            for signal in self.store[module]:
                symbolic_expression = self.store[module][signal]
                symbols_list += symbolic_expression.split(" ")
        res = []
        for sym in symbols_list:
            if sym.isalnum():
                res.append(sym)
        return res
