from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import json
import shutil
import uuid
"""
run with this one -> 'uvicorn API.sylvia_api:app --host 127.0.0.1 --port 8001` and open on `http://localhost:8001/docs` or `http://127.0.0.1:8001/docs`
"""

app = FastAPI()

script_dir = os.path.dirname(__file__)
#UPLOAD_DIR = os.path.join(script_dir, "..", "uploads")  # Directory to store uploaded files
#OUTPUT_JSON = os.path.join(script_dir, "sylvia_tree.json")
UPLOAD_DIR = "/tmp/uploads"
OUTPUT_JSON = "/tmp/sylvia_tree.json"
ALLOWED_DOMAINS = ["https://veriviz-backend-dept-hwsecurity.cloudapps.unc.edu", 
                   "https://localhost:8000"
                   ]
# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_DOMAINS,
    allow_credentials=True,
    allow_methods=["*"],  # 🔥 Ensure POST is allowed
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_verilog(file: UploadFile = File(...), clock_cycles: int = Form(...)):
    try:
        # Generate unique file path
        file_ext = os.path.splitext(file.filename)[-1]
        file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{file_ext}")

        # Save uploaded file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Run Sylvia with the specified clock cycles
        out_file = "out.txt"
        sylvia_command = f"python3 -m main -B {clock_cycles} {file_path} > {out_file}"
        subprocess.run(sylvia_command, shell=True, check=True)

        # Run parse_sylvia_output.py
        in_txt  = os.path.abspath("out.txt")
        out_json = OUTPUT_JSON  # already defined above as script_dir/sylvia_tree.json
        parse_script = os.path.join(script_dir, "parse_sylvia_output.py")

        parse_command = [
            "python3",
            parse_script,
            in_txt,
            out_json
        ]
        subprocess.run(parse_command, check=True)

        # Read the generated JSON output
        if os.path.exists(OUTPUT_JSON):
            with open(OUTPUT_JSON, "r") as json_file:
                result_json = json.load(json_file)
        else:
            return {"error": "Output JSON file not found."}

        # Read the out.txt file for debugging
        output_text = ""
        if os.path.exists(out_file):
            with open(out_file, "r") as out_file_obj:
                output_text = out_file_obj.read()

        # Clean up uploaded file (optional)
        os.remove(file_path)

        return {"json_data": result_json, "output_text": output_text}

    except subprocess.CalledProcessError as e:
        return {"error": f"Error running Sylvia: {e}"}
    except Exception as e:
        return {"error": str(e)}
