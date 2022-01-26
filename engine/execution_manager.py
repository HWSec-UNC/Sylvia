class ExecutionManager:
    num_paths: int = 1
    curr_level: int = 0
    path_code: str = "0" * 12
    ast_str: str = ""
    debugging: bool = False
    abandon: bool = False
    assertion_violation: bool = False
    in_always: bool = False
    modules = {}
    dependencies = {}
    updates = {}
    seen = {}
    final = False
    completed = []
    is_child: bool = False
    # Map of module name to path nums for child module
    child_num_paths = {}    
    # Map of module name to path code for child module
    child_path_codes = {}
    paths = []
    config = {}
    names_list = []
    instance_count = {}
    seen_mod = {}
    opt_1: bool = True
    curr_module: str = ""
    piece_wise: bool = False
    child_range: range = None
    always_writes = {}
    curr_always = None
    opt_2: bool = True
    opt_3: bool = False
    assertions = []
    blocks_of_interest = []
    init_run: bool = False
    ignore = False
    inital_state = {}