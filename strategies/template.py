"""Template for a search strategy."""
from abc import ABC, abstractmethod


class Search:
    """The base methods needed to implement a search strategy
    Can add as many more as you need, of course."""

    @abstractmethod
    def visit_module(self):
        """Traverse the modules of a hardware design."""
        pass

    @abstractmethod
    def visit_stmt(self):
        """Traverse the statements within a module."""
        pass

    @abstractmethod
    def visit_expr(self):
        """Traverse the expressions within a statement."""
        pass