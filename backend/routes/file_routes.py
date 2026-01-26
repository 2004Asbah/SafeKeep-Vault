from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models import FileRecord, AuditLog
from datetime import datetime
import time

from compression_engine import compress_pdf_with_ghostscript, compress_image_really
from s3_service import upload_bytes_to_s3

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload")
async def upload_file(
    request: Request,
    category: str = Form(...),
    compression_level: str = Form("medium"),
    user_email: str = Form(...),
    upload: UploadFile = File(...)
    ,db: Session = Depends(get_db)
):
    file_name = upload.filename
    file_bytes = await upload.read()
    original_size = len(file_bytes)

    ext = file_name.lower().split(".")[-1]

    # ==== YOUR COMPRESSION LOGIC ====
    if ext == "pdf":
        compressed_data, method, ratio = compress_pdf_with_ghostscript(file_bytes, compression_level.lower())
        content_type = "application/pdf"
    elif ext in ["jpg", "jpeg", "png", "gif", "bmp", "tiff"]:
        compressed_data, method, ratio = compress_image_really(file_bytes, compression_level.lower())
        content_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
    else:
        compressed_data = file_bytes
        method = "No Compression"
        ratio = 0
        content_type = "application/octet-stream"

    compressed_size = len(compressed_data)

    # Upload compressed to S3
    metadata = {
        "original-size": original_size,
        "compressed-size": compressed_size,
        "compression-ratio": f"{ratio:.1f}",
        "compression-method": method,
        "original-filename": file_name,
        "compression-level": compression_level,
        "upload-date": datetime.utcnow().isoformat()
    }

    s3_key, s3_path = upload_bytes_to_s3(
        data=compressed_data,
        filename=file_name,
        category=category,
        metadata=metadata,
        content_type=content_type
    )

    file_id = f"file_{int(time.time())}"
    rec = FileRecord(
        id=file_id,
        name=file_name,
        category=category,
        original_size=original_size,
        compressed_size=compressed_size,
        compression_ratio=ratio,
        compression_method=method,
        uploaded_by=user_email,
        s3_key=s3_key,
        status="active"
    )

    db.add(rec)

    # Audit log
    db.add(AuditLog(
        user=user_email,
        action="UPLOAD",
        target=file_name,
        status="Success",
        ip=request.client.host if request.client else None
    ))

    db.commit()

    return {
        "id": rec.id,
        "name": rec.name,
        "category": rec.category,
        "original_size": rec.original_size,
        "compressed_size": rec.compressed_size,
        "compression_ratio": rec.compression_ratio,
        "compression_method": rec.compression_method,
        "uploaded_by": rec.uploaded_by,
        "uploaded_at": rec.uploaded_at.isoformat() if rec.uploaded_at else datetime.utcnow().isoformat(),
        "s3_path": s3_path
    }

@router.get("")
def list_files(db: Session = Depends(get_db)):
    files = db.query(FileRecord).filter(FileRecord.status=="active").order_by(FileRecord.uploaded_at.desc()).all()
    return [{
        "id": f.id,
        "name": f.name,
        "category": f.category,
        "original_size": f.original_size,
        "compressed_size": f.compressed_size,
        "compression_ratio": f.compression_ratio,
        "uploaded_by": f.uploaded_by,
        "uploaded_at": f.uploaded_at.isoformat() if f.uploaded_at else None,
        "s3_path": f"s3_key"
    } for f in files]

@router.delete("/{file_id}")
def delete_file(file_id: str, user_email: str, request: Request, db: Session = Depends(get_db)):
    rec = db.query(FileRecord).filter(FileRecord.id==file_id).first()
    if not rec:
        raise HTTPException(404, "File not found")
    rec.status="deleted"
    db.add(AuditLog(user=user_email, action="DELETE", target=rec.name, status="Success",
                   ip=request.client.host if request.client else None))
    db.commit()
    return {"ok": True}
