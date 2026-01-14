import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def load_json(filename: str):
    """Loads a JSON file from the data directory."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return {} # Return empty dict/list if file missing to avoid crash
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def get_schools():
    return load_json("schools.json")

def get_courses():
    return load_json("courses.json")

def get_scholarships():
    return load_json("scholarships.json")

def get_campus():
    return load_json("campus.json")

def get_placements():
    return load_json("placements.json")

def get_cocurricular():
    return load_json("cocurricular.json")
