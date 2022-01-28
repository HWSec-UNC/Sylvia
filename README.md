# Sylvia - A Software-Style Symbolic Execution Engine for Verilog

## Setup

Requirements
--------------------
- Python3: 3.8 or later
- z3: run `python3 -m pip install z3-solver`
- Icarus Verilog: 10.1 or later: run `sudo apt install iverilog`
- Jinja 2.10 or later: run `python3 -m pip install jinja2`
- PLY 3.4 or later: run `python3 -m pip install ply`
- PyVerilog: run `python3 -m pip install pyverilog`

Download
--------------------
git clone https://github.com/kakiryan/Sylvia

cd Sylvia

Running Sylvia
---------------------
The following command should get you started with a basic run of symbolic execution:

`python3 -m main 1 designs/test-designs/updowncounter.v > out.txt`

The expected usage of Sylvia is:

python3 -m engine {num_cycles} {list of verilog files}

`python3 -m main 1 designs/test-designs/test.v designs/test-designs/test_2.v  > out.txt` for example is a command 
with two example verilog files.