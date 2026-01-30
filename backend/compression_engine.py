import os
import io
import sys
import shutil
import tempfile
import subprocess
from datetime import datetime
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
    return None

def verify_ghostscript():
    gs_path = find_ghostscript()
    if not gs_path:
        return False, "Ghostscript not found"
    try:
        result = subprocess.run([gs_path, '--version'], capture_output=True, text=True, timeout=5, check=False)
        if result.returncode == 0:
            return True, f"Ghostscript {result.stdout.strip()} ready"
        return False, "Ghostscript failed to run"
    except Exception as e: # pylint: disable=broad-except
        return False, f"Error: {str(e)}"

def compress_pdf_fallback(pdf_bytes):
    original_size = len(pdf_bytes)
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        if reader.metadata:
            writer.add_metadata(reader.metadata)
        output = io.BytesIO()
        writer.write(output)
        compressed_data = output.getvalue()
        ratio = ((original_size - len(compressed_data)) / original_size) * 100
        return (compressed_data, "PyPDF2 Basic", ratio) if ratio > 2 else (pdf_bytes, "Already Optimized", 0)
    except Exception: # pylint: disable=broad-except
        return pdf_bytes, "Compression Failed", 0

def compress_pdf_with_ghostscript(pdf_bytes, quality_level="medium"): # pylint: disable=too-many-locals
    original_size = len(pdf_bytes)
    if original_size < 100 * 1024:
        return pdf_bytes, "Already Optimized", 0
    gs_path = find_ghostscript()
    if not gs_path:
        return compress_pdf_fallback(pdf_bytes)
    temp_dir = tempfile.mkdtemp()
    input_path, output_path = os.path.join(temp_dir, "input.pdf"), os.path.join(temp_dir, "output.pdf")
    try:
        with open(input_path, 'wb') as f:
            f.write(pdf_bytes)
        q_map = {"low": ("/printer", 200), "medium": ("/ebook", 150), "high": ("/screen", 100)}
        pdf_settings, dpi = q_map[quality_level]
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
        result = subprocess.run(gs_command, capture_output=True, text=True, timeout=60, check=False)
        if result.returncode == 0 and os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                compressed_data = f.read()
            ratio = min(70, ((original_size - len(compressed_data)) / original_size) * 100)
            shutil.rmtree(temp_dir, ignore_errors=True)
            return (compressed_data, f"Ghostscript {quality_level}", ratio) if ratio > 5 else (pdf_bytes, "Already Optimized", 0)
        shutil.rmtree(temp_dir, ignore_errors=True)
        return compress_pdf_fallback(pdf_bytes)
    except Exception: # pylint: disable=broad-except
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        return compress_pdf_fallback(pdf_bytes)

def compress_image_really(image_bytes, quality_level="medium"):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        original_size = len(image_bytes)
        if original_size < 50 * 1024:
            return image_bytes, "Already Optimized", 0
        q = {"low": 85, "medium": 75, "high": 65}[quality_level]
        output = io.BytesIO()
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(output, format='JPEG', quality=q, optimize=True)
        compressed_data = output.getvalue()
        ratio = ((original_size - len(compressed_data)) / original_size) * 100
        return (compressed_data, f"Image {quality_level}", ratio) if ratio > 10 else (image_bytes, "Already Optimized", 0)
    except Exception: # pylint: disable=broad-except
        return image_bytes, "Compression Failed", 0