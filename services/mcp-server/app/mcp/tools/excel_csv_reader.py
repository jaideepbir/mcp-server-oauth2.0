# python
import os
import csv
from fastapi import HTTPException


def read_csv(path: str, max_rows: int = 1000):
    if not os.path.exists(path):
        raise HTTPException(status_code=400, detail="File not found")
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            rows.append(row)
    return rows
