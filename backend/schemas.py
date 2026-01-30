from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    ngo_name: str
    email: str
    password: str

class AuthResponse(BaseModel):
    token: str
    email: str
    name: str
    ngo: str

class UploadResponse(BaseModel):
    id: str
    name: str
    category: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_method: str
    uploaded_by: str
    s3_path: str
