from fastapi import APIRouter, Request
import os
import sys
import json
from defog import Defog
from defog.query import execute_query_once
from huggingface_hub import hf_hub_download

router = APIRouter()

device_type = None
generate_function = None

DEFOG_API_KEY = "NULL_VALUE" # placeholder, doesn't matter for any of the function here

home_dir = os.path.expanduser("~")
defog_path = os.path.join(home_dir, ".defog")

# stuff that we need to do only once, before everything is loaded

if os.popen("lspci | grep -i nvidia").read():
    device_type = "gpu"
elif sys.platform == "darwin" and os.uname().machine == "arm64":
    device_type = "apple_silicon"
else:
    device_type = "cpu"

if device_type == "gpu":
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

    model = AutoModelForCausalLM.from_pretrained(
        "defog/sqlcoder-7b-2",
        device_map="auto",
        torch_dtype=torch.float16
    )
    tokenizer = AutoTokenizer.from_pretrained("defog/sqlcoder-7b-2")
    pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer)
    generate_function = lambda prompt: pipe(
        prompt,
        max_new_tokens=512,
        do_sample=False,
        num_beams=3,
        num_return_sequences=1,
        return_full_text=False,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
    )[0]["generated_text"].split(";")[0].split("```")[0].strip() + ";"
else:
    from llama_cpp import Llama
    home_dir = os.path.expanduser("~")
    filepath = os.path.join(home_dir, ".defog", "sqlcoder-7b-q5_k_m.gguf")

    if not os.path.exists(filepath):
        print(
            "Downloading the SQLCoder-7b GGUF file. This is a 4GB file and may take a long time to download. But once it's downloaded, it will be saved on your machine and you won't have to download it again."
        )

        # download the gguf file from the internet and save it
        hf_hub_download(repo_id="defog/sqlcoder-7b-2", filename="sqlcoder-7b-q5_k_m.gguf", local_dir=defog_path)
    
    if device_type == "apple_silicon":
        llm = Llama(model_path=filepath, n_gpu_layers=-1, n_ctx=4096)
    else:
        llm = Llama(model_path=filepath, n_ctx=4096)

    generate_function = lambda prompt: llm(
        prompt,
        max_tokens=512,
        temperature=0,
        top_p=1,
        echo=False,
        repeat_penalty=1.0
    )["choices"][0]["text"].split(";")[0].split("```")[0].strip() + ";"

def convert_metadata_to_ddl(metadata):
    # metadata is a dictionary of a table
    master_ddl = ""
    for table_name, columns in metadata.items():
        ddl = f"CREATE TABLE {table_name} (\n"
        for column in columns:
            ddl += f"    {column['column_name']} {column['data_type']},\n"
        ddl = ddl[:-2] + "\n);"
        master_ddl += ddl + "\n\n"
    return master_ddl

@router.post("/get_device_type")
async def get_device_type():
    return {"device_type": device_type}

@router.post("/query")
async def query(request: Request):
    body = await request.json()
    question = body.get("question")

    with open(os.path.join(defog_path, "metadata.json"), "r") as f:
        metadata = json.load(f)
    
    ddl = convert_metadata_to_ddl(metadata)

    prompt = f"""### Task
Generate a SQL query to answer [QUESTION]{question}[/QUESTION]

### Instructions
- If you cannot answer the question with the available database schema, return 'I do not know'

### Database Schema
The query will run on a database with the following schema:
{ddl}

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{question}[/QUESTION]
[SQL]
"""
    query = generate_function(prompt)
    
    defog = Defog()
    db_type = defog.db_type or "postgres"
    db_creds = defog.db_creds
    columns, data = execute_query_once(db_type, db_creds, query)

    return {
        "query_generated": query,
        "data": data,
        "columns": columns,
        "ran_successfully": True
    }
