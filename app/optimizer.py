import boto3
from PIL import Image
import os
import io

#CONFIGURATION
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
s3_client = boto3.client('s3')

def compress_and_upload(filepath):
    """Compresses an image and uploads it to the NGO Vault."""
    file_name = os.path.basename(filepath)

    print(f"🔄 Processing: {file_name}")

    if not BUCKET_NAME:
        print("❌ Error: S3_BUCKET_NAME environment variable not set.")
        return

# 1. Open and Compress the image
    with Image.open(filepath) as img:
        # Convert to RGB (to ensure JPEG compatibility)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Save compressed image to memory (BytesIO) instead of disk
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", optimize=True, quality=50)
        buffer.seek(0)


        # Calculate size reduction for the NGO dashboard
        original_size = os.path.getsize(filepath) / 1024
        compressed_size = buffer.getbuffer().nbytes / 1024
        reduction = 100 * (1 - compressed_size / original_size)

        print(f"📉 Size: {original_size:.1f}KB -> {compressed_size:.1f}KB ({reduction:.1f}% saved)")


        # 2. Upload to S3
        try:
            s3_client.upload_fileobj(
                buffer, 
                BUCKET_NAME, 
                f"uploads/{file_name}",
                ExtraArgs={'ContentType': 'image/jpeg'}
            )
            print(f"✅ Successfully uploaded {file_name} to {BUCKET_NAME}")
        except Exception as e:
            print(f"❌ Upload failed: {e}")



# --- TEST IT ---
if __name__ == "__main__":
    # Put a sample image (e.g. test.jpg) in your project folder to test!
    test_image = "test.jpg" 
    if os.path.exists(test_image):
        compress_and_upload(test_image)
    else:
        print("Please place a 'test.jpg' file in the folder to test.")            
