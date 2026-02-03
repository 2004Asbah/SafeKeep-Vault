# API Documentation

## Base URL
- **Local**: `http://localhost:8000`
- **Production**: `https://your-api-url.com`

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### Authentication

#### Register Organization
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "admin@ngo.org",
  "password": "securepassword",
  "ngo_name": "My NGO",
  "role": "admin"
}
```

**Response:**
```json
{
  "ok": true
}
```

#### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "admin@ngo.org",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "email": "admin@ngo.org",
  "name": "My NGO",
  "ngo": "My NGO",
  "role": "admin"
}
```

---

### Files

#### Upload File
```http
POST /files/upload
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `upload`: File (binary)
- `category`: String (Finance|Donors|Compliance|Programs)
- `compression_level`: String (low|medium|high)
- `user_email`: String

**Response:**
```json
{
  "id": "file_1234567890",
  "name": "document.pdf",
  "category": "Finance",
  "original_size": 1048576,
  "compressed_size": 524288,
  "compression_ratio": 0.5,
  "compression_method": "Ghostscript",
  "uploaded_by": "admin@ngo.org",
  "uploaded_at": "2024-01-15T10:30:00",
  "s3_path": "s3://bucket/finance/20240115_103000_document.pdf"
}
```

#### List Files
```http
GET /files
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "file_1234567890",
    "name": "document.pdf",
    "category": "Finance",
    "original_size": 1048576,
    "compressed_size": 524288,
    "compression_ratio": 0.5,
    "uploaded_by": "admin@ngo.org",
    "uploaded_at": "2024-01-15T10:30:00",
    "s3_path": "finance/20240115_103000_document.pdf"
  }
]
```

#### Download File
```http
GET /files/{file_id}/download?user_email=admin@ngo.org
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** Binary file stream

#### Share File
```http
POST /files/{file_id}/share
```

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `expiration`: Integer (seconds, default: 3600)

**Response:**
```json
{
  "share_url": "https://s3.amazonaws.com/bucket/file?X-Amz-Algorithm=...",
  "expires_in": 3600
}
```

#### Delete File
```http
DELETE /files/{file_id}?user_email=admin@ngo.org
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "ok": true
}
```

---

### Audit Logs

#### List Audit Logs
```http
GET /audit?limit=100
```

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit`: Integer (default: 100)

**Response:**
```json
[
  {
    "timestamp": "2024-01-15T10:30:00",
    "user": "admin@ngo.org",
    "action": "LOGIN",
    "target": "System",
    "status": "Success",
    "ip_address": "127.0.0.1"
  }
]
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid credentials"
}
```

### 404 Not Found
```json
{
  "detail": "File not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

- **Limit**: 100 requests per minute per IP
- **Headers**:
  - `X-RateLimit-Limit`: 100
  - `X-RateLimit-Remaining`: 95
  - `X-RateLimit-Reset`: 1642252800

---

## Interactive Documentation

Visit `/docs` for Swagger UI or `/redoc` for ReDoc documentation.

**Example:**
```
http://localhost:8000/docs
```
