import json
import pandas as pd
from datetime import datetime
from utils import RAW_DATA_DIR

def load_records(records, output_path) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    # output_path = RAW_DATA_DIR / f"records_{timestamp}.csv" # Commented out to use with DAG

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        records.to_csv(f, index=False)
        # json.dump(records, f, indent=2)

    return str(output_path)