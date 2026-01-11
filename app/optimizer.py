import boto3 
from PLI import IMAGE 
import os
import io

#CONFIGURATION
BUCKET_name ="safekeep-ngo-vault-149575e8"
s3_client=boto3.client('s3')

def compress_and_upload(filepath):
    """Compresses an image and uploads it to the NGO Vault."""
    file_name = os.path.basename(file_path)

    print(f"🔄 Processing: {file_name}")


# 1. Open and Compress the image
    with Image.open(file_path) as img:
        # Convert to RGB (to ensure JPEG compatibility)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Save compressed image to memory (BytesIO) instead of disk
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", optimize=True, quality=50)
        buffer.seek(0)


        # Calculate size reduction for the NGO dashboard
        original_size = os.path.getsize(file_path) / 1024
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
