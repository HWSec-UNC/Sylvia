# Sylvia - A Software-Style Symbolic Execution Engine for Verilog

## Setup

Download
--------------------
1. Clone this repo. `git clone https://github.com/kakiryan/Sylvia`
2. `cd Sylvia`
3. Run the dependency install script, this will install all system-wide and python module dependencies. `./sylviaInstall.sh`


Running Sylvia
---------------------
The following command should get you started with a basic run of symbolic execution:

`python3 -m main 1 designs/test-designs/updowncounter.v > out.txt`

The expected usage of Sylvia is:

python3 -m main {num_cycles} {list of verilog files}

`python3 -m main 1 designs/test-designs/test.v designs/test-designs/test_2.v  > out.txt` for example is a command 
with two example verilog files.

You can run:

`python3 -m main --help` for information about the different flags you can run Sylvia with. -B will display the initial & final symbolic store and path condition for each clock cycle during the run. 

How to Cite
---------------------


Please cite our FMCAD paper when using Sylvia!

@inproceedings{Ryan2023Sylvia,
author = {Ryan, Kaki and Sturton, Cynthia},
title = {Sylvia: Countering the Path Explosion Problem in the Symbolic Execution of Hardware Designs},
year = {2023},
isbn = {978-3-85448-060-0},
publisher = {TU Wien Academic Press},
address = {New York, NY, USA},
url = {https://repositum.tuwien.at/handle/20.500.12708/188806 },
booktitle = {Proceedings of the 23rd Conference on Formal Methods in Computer-Aided Design (FMCAD)},
pages = {110--121},
numpages = {12},
series = {FMCAD}
}
