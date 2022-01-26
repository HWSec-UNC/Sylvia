import z3
from z3 import Solver, Int, BitVec, BitVecSort

class SymbolicState:
    pc = Solver()
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
        return self.store[module_name][var_name]