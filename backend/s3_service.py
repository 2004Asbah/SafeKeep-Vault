from datetime import datetime
import boto3
from config import S3_BUCKET_NAME, AWS_REGION

s3 = boto3.client("s3", region_name=AWS_REGION)

def upload_bytes_to_s3(
    data: bytes, filename: str, category: str, metadata: dict, content_type: str
):
    safe_category = category.lower()
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    key = f"{safe_category}/{ts}_{filename}"

    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=data,
        ContentType=content_type,
        Metadata={k: str(v) for k, v in metadata.items()}
    )

    return key, f"s3://{S3_BUCKET_NAME}/{key}"
