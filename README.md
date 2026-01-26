# 💎 Safekeep NGO Vault

**Safekeep NGO Vault** is a secure, cloud-native file management system designed for Non-Governmental Organizations (NGOs). It combines a modern, multi-tenant frontend with a robust, serverless backend architecture.

---

## 🚀 Key Features

### 🔐 Security & Isolation
- **Multi-Tenant Architecture**: Strict data isolation ensures one NGO never accesses another's data.
- **Role-Based Access Control (RBAC)**: Distinct portals for **Admins** and **Staff**.
- **Audit Logging**: Immutable logs for all critical actions (Login, Upload, Delete).
- **Secure File Storage**: 
    - **Local Dev**: Encrypted storage in `data/uploads/`.
    - **Production**: AWS S3 with strict public access blocks and lifecycle policies.

### 👥 User Management
- **Self-Service Registration**: NGOs can register their own tenant organization.
- **Staff Management**: Admins can easily add and manage staff members (`pages/5_User_Management.py`).

### ☁️ Cloud & DevOps (Production Ready)
- **Infrastructure as Code**: Full AWS setup defined in **Terraform**.
- **Serverless Compute**: AWS Lambda for automated image processing.
- **Containerization**: Multi-stage **Docker** builds including a hardened Distroless image for maximum security.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit (Python) |
| **Backend** | Python 3.11, AWS Lambda |
| **Infrastructure** | Terraform (IaC) |
| **Container** | Docker (Distroless) |
| **Storage** | AWS S3 (Production) / Local JSON (Dev) |

---

## ⚡ Quick Start (Local Development)

### 1. Installation
```bash
git clone <repository-url>
cd safekeep-vault

# Create virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r frontendd/requirements.txt
```

### 2. Running the App
The application uses local JSON persistence by default for development.

```bash
cd frontendd
streamlit run app.py
```
Access the app at `http://localhost:8501`.

---

## ☁️ Cloud Infrastructure (DevOps)

### 🐳 Docker Deployment
The project includes a multi-stage `Dockerfile` supporting three targets:
1. **Simple**: Standard Python image.
2. **Optimized**: Slim image with user permissions.
3. **Secure (Distroless)**: Hardened production image using Google's Distroless base.

**Build & Run:**
```bash
# Build the secure image
docker build --target secure -t safekeep-vault:secure .

# Run the container
docker run -p 8501:8501 safekeep-vault:secure
```

### 🏗️ Terraform Provisioning
We use Terraform to provision the AWS infrastructure (S3, Lambda, IAM).

**Resources Created:**
- **AWS S3 Bucket**: Private bucket for vault storage (`safekeep-ngo-vault-*`).
- **Lifecycle Rules**: Auto-archive to Glacier after 30 days.
- **AWS Lambda**: `safekeep-image-processor` for handling uploads.
- **IAM Roles**: Least-privilege policies for secure access.

**Deploy Infrastructure:**
```bash
cd terraform
terraform init
terraform apply
```

---

## 📖 Usage Guide

### 1. Registering an Organization
- Launch the app -> **"Register NGO"**.
- Enter NGO name & Admin details to create your secure tenant.

### 2. Admin Dashboard
- **Admin Portal**: Login to view storage stats, recent activity, and audit logs.
- **User Management**: Add staff members to your organization.

### 3. Staff Access
- **Staff Portal**: Secure access for employees to upload and view files.
- **Vault Explorer**: Search, filter, and download files (Persisted locally in Dev).

---

## 📁 Project Structure

```
safekeep-vault/
├── frontendd/              # Streamlit Frontend Application
│   ├── app.py              # Main Entry Point
│   ├── services.py         # Business Logic Layer
│   ├── data.py             # Data Persistence Layer
│   ├── components.py       # Shared UI Components
│   ├── styles.css          # Glassmorphism CSS
│   ├── requirements.txt    # Python Dependencies
│   ├── pages/              # Application Modules
│   │   ├── 1_Dashboard.py
│   │   ├── 2_Upload_Center.py
│   │   ├── 3_Vault_Explorer.py
│   │   ├── 4_Audit_Logs.py
│   │   └── 5_User_Management.py
│   └── data/               # Local Database (Runtime)
│       ├── users.json
│       ├── files.json
│       └── uploads/
│
├── terraform/              # Infrastructure as Code
│   ├── main.tf             # AWS Configuration
│   └── ...
│
├── backend/                # Fast API Backend
├── lambda/                 # AWS Lambda Functions
├── Dockerfile              # Container Configuration
└── README.md               # Documentation
```

---
*Safekeep NGO Vault - Secure. Scalable. Serverless.*
