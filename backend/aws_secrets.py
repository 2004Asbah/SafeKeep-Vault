import json
import boto3
from botocore.exceptions import ClientError
import os

def get_secret(secret_name: str, region_name: str = None):
    """
    Retrieves a secret from AWS Secrets Manager.
    
    Args:
        secret_name (str): The name or ARN of the secret.
        region_name (str, optional): The AWS region. Defaults to AWS_REGION env var.
    
    Returns:
        dict: The secret key-value pairs as a dictionary.
        None: If the secret cannot be retrieved or found.
    """
    if not region_name:
        region_name = os.getenv("AWS_REGION", "eu-north-1")

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For this specific app, we'll just print the error and return None
        # In production, you might want to raise specific exceptions or log errors
        print(f"Error retrieving secret {secret_name}: {e}")
        return None

    # Decrypts secret using the associated KMS key.
    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
        try:
            return json.loads(secret)
        except json.JSONDecodeError:
            return {"raw_value": secret}
            
    return None
