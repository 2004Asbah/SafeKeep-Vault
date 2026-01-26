from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    ngo_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FileRecord(Base):
    __tablename__ = "files"
    id = Column(String, primary_key=True)   # file_123... style
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)

    original_size = Column(Integer, nullable=False)
    compressed_size = Column(Integer, nullable=False)
    compression_ratio = Column(Float, nullable=False)
    compression_method = Column(String, nullable=False)

    uploaded_by = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    s3_key = Column(String, nullable=False)
    status = Column(String, default="active")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user = Column(String, nullable=False)
    action = Column(String, nullable=False)
    target = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    ip = Column(String, nullable=True)
