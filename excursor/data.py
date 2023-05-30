"""
Data ingestion, cleaning, transformation and writing are all included in this module
"""

from dataclasses import dataclass
from pathlib import Path

from datasets import load_dataset

@dataclass
class Reader:
    path: list[str] | list[Path]


ds = load_dataset("json", data_files="excursor/example_ds/data1.ndjson", split="train")
flattened_ds = ds.flatten()
