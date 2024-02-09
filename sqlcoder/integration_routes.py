from fastapi import APIRouter, Request
import json
import os
from defog import Defog

DEFOG_API_KEY = "NULL_VALUE" # placeholder, doesn't matter for any of the function here

home_dir = os.path.expanduser("~")
defog_path = os.path.join(home_dir, ".defog")

router = APIRouter()

def convert_nested_dict_to_list(table_metadata):
    metadata = []
    for key in table_metadata:
        table_name = key
        for item in table_metadata[key]:
            item["table_name"] = table_name
            if "column_description" not in item:
                item["column_description"] = ""
            metadata.append(item)
    return metadata

@router.post("/integration/get_tables_db_creds")
async def get_tables_db_creds(request: Request):
    try:
        defog = Defog()
    except:
        return {"error": "no defog instance found"}

    try:
        with open(os.path.join(defog_path, "tables.json"), "r") as f:
            table_names = json.load(f)
    except:
        table_names = []

    try:
        with open(os.path.join(defog_path, "selected_tables.json"), "r") as f:
            selected_table_names = json.load(f)
    except:
        selected_table_names = []

    db_type = defog.db_type
    db_creds = defog.db_creds
    
    return {
        "tables": table_names,
        "db_creds": db_creds,
        "db_type": db_type,
        "selected_tables": selected_table_names
    }

@router.post("/integration/get_metadata")
async def get_metadata(request: Request):
    try:
        with open(os.path.join(defog_path, "metadata.json"), "r") as f:
            table_metadata = json.load(f)
        
        metadata = convert_nested_dict_to_list(table_metadata)
        return {"metadata": metadata}
    except:
        return {"error": "no metadata found"}

@router.post("/integration/generate_tables")
async def generate_tables(request: Request):
    params = await request.json()
    db_type = params.get("db_type")
    db_creds = params.get("db_creds")
    for k in ["api_key", "db_type"]:
        if k in db_creds:
            del db_creds[k]

    defog = Defog(DEFOG_API_KEY, db_type, db_creds)
    table_names = defog.generate_db_schema(tables=[], return_tables_only=True)

    with open(os.path.join(defog_path, "tables.json"), "w") as f:
        json.dump(table_names, f)

    return {"tables": table_names}

@router.post("/integration/generate_metadata")
async def generate_metadata(request: Request):
    params = await request.json()
    tables = params.get("tables")

    with open(os.path.join(defog_path, "selected_tables.json"), "w") as f:
        json.dump(tables, f)

    defog = Defog()
    metadata = defog.generate_db_schema(
        tables=tables, upload=False
    )
    
    with open(os.path.join(defog_path, "metadata.json"), "w") as f:
        json.dump(metadata, f)
    
    metadata = convert_nested_dict_to_list(metadata)
    return {"metadata": metadata}

@router.post("/integration/update_metadata")
async def update_metadata(request: Request):
    params = await request.json()
    metadata = params.get("metadata")

    # convert metadata to nested dictionary
    table_metadata = {}
    for item in metadata:
        table_name = item["table_name"]
        if table_name not in table_metadata:
            table_metadata[table_name] = []
        table_metadata[table_name].append(
            {
                "column_name": item["column_name"],
                "data_type": item["data_type"],
                "column_description": item["column_description"],
            }
        )
    
    with open(os.path.join(defog_path, "metadata.json"), "w") as f:
        json.dump(table_metadata, f)
    
    return {"status": "success"}