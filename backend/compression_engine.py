import os
import io
import sys
import shutil
import tempfile
import subprocess
import zlib

import boto3
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

# --- AWS INITIALIZATION ---
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'safekeep-ngo-vault-149575e8')
s3 = boto3.client('s3')

def find_ghostscript():
    possible_paths = ['gs', 'gswin64c.exe', 'gswin32c.exe',
                      'C:\\Program Files\\gs\\gs10.00.0\\bin\\gswin64c.exe',
                      'C:\\Program Files (x86)\\gs\\gs9.53.3\\bin\\gswin32c.exe',
                      '/usr/local/bin/gs', '/usr/bin/gs']
    for path in possible_paths:
        try:
            if shutil.which(path):
                print(f"COMPRESSION: Found Ghostscript at {path}")
                return path
        except Exception: # pylint: disable=broad-except
            pass
    if sys.platform == 'win32':
        program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
        for root, _, files in os.walk(program_files):
            if 'gswin64c.exe' in files:
                return os.path.join(root, 'gswin64c.exe')
            if 'gswin32c.exe' in files:
                return os.path.join(root, 'gswin32c.exe')
    print("COMPRESSION: Ghostscript NOT found!")
    return None

def verify_ghostscript():
    gs_path = find_ghostscript()
    if not gs_path:
        return False, "Ghostscript not found"
    try:
        result = subprocess.run(
            [gs_path, '--version'],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        if result.returncode == 0:
            return True, f"Ghostscript {result.stdout.strip()} ready"
        return False, "Ghostscript failed to run"
    except Exception as e: # pylint: disable=broad-except
        return False, f"Error: {str(e)}"

def compress_pdf_fallback(pdf_bytes):
    """Fallback PDF compression using pikepdf (better than PyPDF2)"""
    original_size = len(pdf_bytes)
    print(f"COMPRESSION: Using pikepdf fallback for {original_size} bytes")
    
    try:
        import pikepdf
        
        # Open PDF from bytes
        input_pdf = io.BytesIO(pdf_bytes)
        output_pdf = io.BytesIO()
        
        with pikepdf.open(input_pdf) as pdf:
            # Remove unreferenced resources
            pdf.remove_unreferenced_resources()
            
            # Save with aggressive compression
            pdf.save(
                output_pdf,
                compress_streams=True,
                stream_decode_level=pikepdf.StreamDecodeLevel.generalized,
                object_stream_mode=pikepdf.ObjectStreamMode.generate,
                recompress_flate=True,
                deterministic_id=True
            )
        
        compressed_data = output_pdf.getvalue()
        compressed_size = len(compressed_data)
        
        # Calculate actual savings
        if compressed_size < original_size:
            saved_bytes = original_size - compressed_size
            ratio = (saved_bytes / original_size) * 100
            print(f"COMPRESSION: pikepdf SUCCESS - Original: {original_size}, Compressed: {compressed_size}, Saved: {ratio:.1f}%")
            return (compressed_data, "pikepdf Optimized", ratio)
        else:
            print(f"COMPRESSION: pikepdf - No improvement (Original: {original_size}, Result: {compressed_size})")
            return (pdf_bytes, "Already Optimized", 0)
        
    except Exception as e: # pylint: disable=broad-except
        print(f"COMPRESSION: pikepdf failed: {str(e)}, trying PyPDF2...")
        
        # Final fallback to PyPDF2
        try:
            from PyPDF2 import PdfReader, PdfWriter
            reader = PdfReader(io.BytesIO(pdf_bytes))
            writer = PdfWriter()
            
            for page in reader.pages:
                page.compress_content_streams()
                writer.add_page(page)
            
            output = io.BytesIO()
            writer.write(output)
            compressed_data = output.getvalue()
            compressed_size = len(compressed_data)
            
            if compressed_size < original_size:
                ratio = ((original_size - compressed_size) / original_size) * 100
                print(f"COMPRESSION: PyPDF2 fallback - Saved: {ratio:.1f}%")
                return (compressed_data, "PyPDF2 Optimized", ratio)
            return (pdf_bytes, "Already Optimized", 0)
        except Exception as e2:
            print(f"COMPRESSION: All methods failed: {str(e2)}")
            return pdf_bytes, "Compression Failed", 0

def compress_pdf_with_ghostscript(pdf_bytes, quality_level="medium"): # pylint: disable=too-many-locals
    original_size = len(pdf_bytes)
    size_mb = original_size / (1024 * 1024)
    print(f"COMPRESSION: Starting PDF compression for {size_mb:.1f} MB, quality={quality_level}")
    
    # Skip very small files (under 100KB) - not worth compressing
    if original_size < 100 * 1024:
        print(f"COMPRESSION: File too small ({original_size} bytes), skipping")
        return pdf_bytes, "Too Small", 0
    
    # Log warning for large files
    if size_mb > 10:
        print(f"COMPRESSION: Large file ({size_mb:.1f} MB) - this may take several minutes...")
    
    gs_path = find_ghostscript()
    if not gs_path:
        print("COMPRESSION: Ghostscript not found, using fallback")
        return compress_pdf_fallback(pdf_bytes)
    
    temp_dir = tempfile.mkdtemp()
    input_path, output_path = (
        os.path.join(temp_dir, "input.pdf"),
        os.path.join(temp_dir, "output.pdf")
    )
    
    try:
        with open(input_path, 'wb') as f:
            f.write(pdf_bytes)
        
        q_map = {"low": ("/printer", 200), "medium": ("/ebook", 150), "high": ("/screen", 72)}
        pdf_settings, dpi = q_map.get(quality_level, ("/ebook", 150))
        
        gs_command = [gs_path, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                      f'-dPDFSETTINGS={pdf_settings}', f'-dColorImageResolution={dpi}',
                      f'-dGrayImageResolution={dpi}', f'-dMonoImageResolution={dpi}',
                      '-dColorConversionStrategy=/sRGB', '-dProcessColorModel=/DeviceRGB',
                      '-dConvertCMYKImagesToRGB=true', '-dEmbedAllFonts=true',
                      '-dSubsetFonts=true', '-dCompressFonts=true', '-dAutoRotatePages=/None',
                      '-dDetectDuplicateImages=true', '-dCompressPages=true',
                      '-dDoThumbnails=false', '-dCreateJobTicket=false',
                      '-dPreserveEPSInfo=false', '-dPreserveOPIComments=false',
                      '-dPreserveOverprintSettings=false', '-dUCRandBGInfo=/Remove',
                      '-dUseCIEColor=false', '-dNOSAFER', '-dNOPAUSE', '-dBATCH', '-dQUIET',
                      f'-sOutputFile={output_path}', input_path]
        
        print(f"COMPRESSION: Running Ghostscript with command: {' '.join(gs_command[:5])}...")
        import time
        start_time = time.time()
        result = subprocess.run(gs_command, capture_output=True, text=True, timeout=300, check=False)
        elapsed = time.time() - start_time
        print(f"COMPRESSION: Ghostscript completed in {elapsed:.1f} seconds, return code: {result.returncode}")
        
        if result.returncode == 0 and os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                compressed_data = f.read()
            
            compressed_size = len(compressed_data)
            ratio = ((original_size - compressed_size) / original_size) * 100
            
            print(f"COMPRESSION: Ghostscript SUCCESS - Original: {original_size}, Compressed: {compressed_size}, Ratio: {ratio:.1f}%")
            
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Return compressed if any improvement
            if ratio > 0 and compressed_size < original_size:
                return (compressed_data, f"Ghostscript {quality_level}", ratio)
            return (pdf_bytes, "Already Optimized", 0)
        
        print(f"COMPRESSION: Ghostscript failed with code {result.returncode}")
        if result.stderr:
            print(f"COMPRESSION: Ghostscript stderr: {result.stderr[:1000]}")
        if result.stdout:
            print(f"COMPRESSION: Ghostscript stdout: {result.stdout[:1000]}")
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        return compress_pdf_fallback(pdf_bytes)
        
    except subprocess.TimeoutExpired:
        print(f"COMPRESSION: Ghostscript TIMEOUT after 300 seconds!")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        return compress_pdf_fallback(pdf_bytes)
        
    except Exception as e: # pylint: disable=broad-except
        print(f"COMPRESSION: Exception during Ghostscript: {str(e)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        return compress_pdf_fallback(pdf_bytes)

def compress_image_really(image_bytes, quality_level="medium"):
    original_size = len(image_bytes)
    print(f"COMPRESSION: Starting image compression for {original_size} bytes, quality={quality_level}")
    
    try:
        img = Image.open(io.BytesIO(image_bytes))
        print(f"COMPRESSION: Image format={img.format}, size={img.size}, mode={img.mode}")
        
        # Skip very small images
        if original_size < 50 * 1024:
            print(f"COMPRESSION: Image too small ({original_size} bytes), skipping")
            return image_bytes, "Too Small", 0
        
        q = {"low": 85, "medium": 70, "high": 50}.get(quality_level, 70)
        
        output = io.BytesIO()
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as optimized JPEG
        img.save(output, format='JPEG', quality=q, optimize=True)
        compressed_data = output.getvalue()
        
        compressed_size = len(compressed_data)
        ratio = ((original_size - compressed_size) / original_size) * 100
        
        print(f"COMPRESSION: Image result - Original: {original_size}, Compressed: {compressed_size}, Ratio: {ratio:.1f}%")
        
        # Return compressed if any improvement
        if ratio > 0 and compressed_size < original_size:
            return (compressed_data, f"Image {quality_level}", ratio)
        return (image_bytes, "Already Optimized", 0)
        
    except Exception as e: # pylint: disable=broad-except
        print(f"COMPRESSION: Image compression failed: {str(e)}")
        return image_bytes, "Compression Failed", 0

