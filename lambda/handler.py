import boto3
from PIL import Image
import io
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Identify file type
    extension = key.split('.')[-1].lower()
    new_key = key.replace('incoming/', 'uploads/', 1)
    
    try:
        # CASE 1: IMAGES (Compress)
        if extension in ['jpg', 'jpeg', 'png']:
            print(f"Optimizing image: {key}")
            response = s3.get_object(Bucket=bucket, Key=key)
            img = Image.open(io.BytesIO(response['Body'].read()))
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=60, optimize=True)
            buffer.seek(0)
            
            s3.put_object(Bucket=bucket, Key=new_key, Body=buffer, ContentType='image/jpeg')
            
        # CASE 2: DOCUMENTS (Move only)
        else:
            print(f"Moving non-image document: {key}")
            s3.copy_object(
                Bucket=bucket,
                CopySource={'Bucket': bucket, 'Key': key},
                Key=new_key
            )
        
        # CLEANUP: Delete from incoming
        s3.delete_object(Bucket=bucket, Key=key)
        
    except Exception as e:
        print(f"Error processing {key}: {str(e)}")
        # If it fails, we keep it in incoming so we can see the error in logs
        raise e

    return {"status": "success"}