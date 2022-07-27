import pytest


def run_tests(initial_symbolic_state, final_symbolic_state, pc):
    print("hello")
    print(final_symbolic_state)
    print(pc)
    assert initial_symbolic_state["updowncounter"]["clock"] != final_symbolic_state["updowncounter"]["clock"]
    assert initial_symbolic_state["updowncounter"]["reset"] != 1
    assert initial_symbolic_state["updowncounter"]["value"] == final_symbolic_state["updowncounter"]["value"]


#TODO: write the unit test to check that the clocks are the same
#TODO: write the calls to the test functions
