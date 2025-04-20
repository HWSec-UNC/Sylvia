#!/usr/bin/env python3
"""
Run:  python3 API/parse_sylvia_output.py out.txt API/sylvia_tree.json
to test: python3 -m http.server 8000 and view on http://localhost:8000/tree_view.html
You may have to use WSL on windows
"""
#!/usr/bin/env python3
import json
import re
import sys
import pathlib
import ast

# —— Regex definitions —— 
DELIM           = re.compile(r"^-{4,}$")  # “----” ends one path’s block
CYCLE_RE        = re.compile(
    r"\*\*\s*path\s+(\d+)\s+clock\s+cycle\s+(\d+)\s*\*\*", re.I
)
PATH_COND_RE    = re.compile(r"Path condition:", re.I)
BRACKET_CONTENT = re.compile(r"\[(.*?)\]", re.S)
ASSERT_RE       = re.compile(r"Assertion violation", re.I)
DICT_RE         = re.compile(r"(\{.*\})")
STATE_RE        = re.compile(r"state:", re.I)

def parse(input_path: pathlib.Path, output_path: pathlib.Path):
    lines = input_path.read_text().splitlines()
    root = { "name": "Execution", "children": [] }
    last_cycle = {}       # maps path_idx → its last cycle node
    curr_cycle = None
    curr_assertion = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # — reset on “----”
        if DELIM.match(line):
            curr_cycle = None
            curr_assertion = None
            i += 1
            continue

        # — new “** path N clock cycle C **” header
        m = CYCLE_RE.match(line)
        if m:
            path_idx  = int(m.group(1))
            cycle_num = int(m.group(2))
            name      = f"path {path_idx} clock cycle {cycle_num}"

            node = { "name": name, "path_condition": [], "children": [] }
            if cycle_num == 0:
                root["children"].append(node)
            else:
                (last_cycle.get(path_idx) or root)["children"].append(node)

            last_cycle[path_idx] = node
            curr_cycle = node
            curr_assertion = None

            # —— capture the very first state dict to build our mapping
            mapping = {}
            for j in range(i+1, len(lines)-1):
                if STATE_RE.search(lines[j]):
                    if dm := DICT_RE.search(lines[j+1]):
                        try:
                            full_dict = ast.literal_eval(dm.group(1))
                            # we expect a single outer key → inner dict
                            inner = next(iter(full_dict.values()))
                            # build random_string → var_name map
                            mapping = {val: key for key, val in inner.items()}
                        except Exception:
                            mapping = {}
                    break
            curr_cycle["mapping"] = mapping

            i += 1
            continue

        # — path-condition block; translate each entry via mapping
        if curr_cycle and PATH_COND_RE.search(line):
            buf = ""
            # if it’s all on one line
            if "[" in line and "]" in line:
                buf = line
            else:
                j = i + 1
                while j < len(lines) and "]" not in lines[j]:
                    buf += lines[j].strip()
                    j += 1
                if j < len(lines):
                    buf += lines[j].strip()
                i = j

            if bc := BRACKET_CONTENT.search(buf):
                raw = [c.strip() for c in bc.group(1).split(",") if c.strip()]
                mapped = []
                for cond in raw:
                    # replace all random tokens with their var‑names
                    for rand, varname in curr_cycle.get("mapping", {}).items():
                        cond = cond.replace(rand, varname)
                    mapped.append(cond)
                curr_cycle["path_condition"] = mapped

            curr_assertion = None
            i += 1
            continue

        # — assertion‑violation node
        if curr_cycle and ASSERT_RE.search(line):
            a = {
                "name":           "Assertion violation",
                "path_condition": curr_cycle.get("path_condition", []),
                "state":          {},
                "children":       []
            }
            curr_cycle["children"].append(a)
            curr_assertion = a
            i += 1
            continue

        # — dict after an assertion → fill in a['state']
        if curr_assertion and (dm := DICT_RE.search(line)):
            try:
                curr_assertion["state"] = ast.literal_eval(dm.group(1))
            except Exception:
                curr_assertion["state"] = dm.group(1)
            curr_assertion = None
            i += 1
            continue

        # — skip everything else
        i += 1

    # write JSON
    output_path.write_text(json.dumps(root, indent=2))
    print(f"[OK] wrote {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: parse_sylvia_output.py out.txt API/sylvia_tree.json")
    parse(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))



