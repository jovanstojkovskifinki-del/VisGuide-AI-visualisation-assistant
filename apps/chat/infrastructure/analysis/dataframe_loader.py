from typing import Any

import pandas as pd


def load_dataframe(dataset: Any) -> pd.DataFrame:
    file_type = str(dataset.file_type).lower()
    with dataset.file.open("rb") as f:
        if "csv" in file_type:
            return pd.read_csv(f)
        if "xls" in file_type or "excel" in file_type:
            return pd.read_excel(f)
    raise ValueError(f"Unsupported file type: {dataset.file_type}")