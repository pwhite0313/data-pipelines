import logging
import os
import io
import pandas as pd
from datetime import datetime
from src.utils import RAW_DATA_DIR

logger = logging.getLogger(__name__)


def load_records(records, output_path=None) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output_{timestamp}.csv"
    bucket = os.getenv("S3_BUCKET")

    if bucket:
        import boto3
        s3_key = f"raw/{filename}"
        csv_buffer = io.StringIO()
        records.to_csv(csv_buffer, index=False)
        boto3.client("s3").put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=csv_buffer.getvalue().encode("utf-8"),
        )
        logger.info("Wrote %s records to s3://%s/%s", len(records), bucket, s3_key)
        return f"s3://{bucket}/{s3_key}"

    if output_path is None:
        output_path = RAW_DATA_DIR / filename

    logger.info("Writing %s records to %s", len(records), output_path)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        records.to_csv(f, index=False)

    return str(output_path)
