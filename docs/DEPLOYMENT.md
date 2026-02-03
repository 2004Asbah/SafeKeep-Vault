# Deployment Guide

This guide covers deploying Safekeep NGO Vault to various platforms.

## Table of Contents
- [AWS Deployment](#aws-deployment)
- [Render.com Deployment](#rendercom-deployment)
- [Railway Deployment](#railway-deployment)
- [Environment Variables](#environment-variables)

---

## AWS Deployment

### Prerequisites
- AWS Account
- Terraform installed
- AWS CLI configured

### Step 1: Provision Infrastructure

```bash
cd terraform
terraform init
terraform apply
```

This creates:
- S3 bucket for file storage
- Lambda function for image processing
- IAM roles and policies

### Step 2: Deploy Application

**Option A: EC2**
```bash
# Launch EC2 t2.micro instance
# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Clone repository
git clone https://github.com/your-username/safekeep-vault.git
cd safekeep-vault

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start

# Run application
docker-compose up -d
```

**Option B: ECS/Fargate**
```bash
# Build and push to ECR
aws ecr create-repository --repository-name safekeep-vault
docker build -t safekeep-vault .
docker tag safekeep-vault:latest <account-id>.dkr.ecr.<region>.amazonaws.com/safekeep-vault:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/safekeep-vault:latest

# Deploy to ECS (use AWS Console or CLI)
```

---

## Render.com Deployment

### Prerequisites
- GitHub account
- Render.com account (free)

### Step 1: Prepare Repository

1. Push code to GitHub
2. Ensure `Dockerfile` and `docker-compose.yml` are in root

### Step 2: Create Services

**Backend Service:**
1. Go to Render Dashboard → New → Web Service
2. Connect GitHub repository
3. Settings:
   - **Name**: `safekeep-backend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `Dockerfile`
   - **Instance Type**: Free
4. Add environment variables (see below)
5. Deploy

**Frontend Service:**
1. New → Web Service
2. Settings:
   - **Name**: `safekeep-frontend`
   - **Build Command**: `pip install -r frontendd/requirements.txt`
   - **Start Command**: `streamlit run frontendd/app.py --server.port=$PORT`
3. Deploy

**Database:**
1. New → PostgreSQL
2. Name: `safekeep-db`
3. Copy `DATABASE_URL` to backend environment variables

---

## Railway Deployment

### Prerequisites
- GitHub account
- Railway account

### Deployment Steps

1. Go to Railway.app
2. New Project → Deploy from GitHub
3. Select repository
4. Railway auto-detects Docker configuration
5. Add environment variables
6. Deploy

---

## Environment Variables

### Required Variables

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=eu-north-1
S3_BUCKET_NAME=your-bucket-name

# Application
JWT_SECRET=your-super-secret-key-change-this

# Database (Production)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# API URL (Frontend)
SAFEKEEP_API_URL=http://backend-url:8000
```

### Optional Variables

```bash
# AWS Secrets Manager (if using)
# AWS_SECRET_NAME=safekeep/production

# Debug
DEBUG=false
```

---

## Post-Deployment

### 1. Initialize Database

```bash
# SSH into server or use Render shell
python reset_database.py
```

### 2. Test Application

1. Visit frontend URL
2. Register a test NGO
3. Upload a file
4. Check S3 bucket for uploaded file
5. Verify audit logs

### 3. Set Up Custom Domain (Optional)

**Render:**
- Dashboard → Service → Settings → Custom Domain

**AWS:**
- Route 53 → Create hosted zone
- Add A record pointing to EC2/Load Balancer

---

## Troubleshooting

### Database Connection Issues
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection
python -c "from backend.database import engine; print(engine.connect())"
```

### S3 Access Issues
```bash
# Verify AWS credentials
aws s3 ls s3://your-bucket-name

# Check IAM permissions
```

### Container Issues
```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

---

## Monitoring

### Application Logs
- **Render**: Dashboard → Service → Logs
- **AWS**: CloudWatch Logs
- **Railway**: Dashboard → Deployments → Logs

### Metrics
- **AWS**: CloudWatch Metrics
- **Render**: Built-in metrics dashboard

---

## Scaling

### Horizontal Scaling
- **Render**: Upgrade to paid plan, increase instances
- **AWS**: Use Auto Scaling Groups with ECS

### Database Scaling
- **Render**: Upgrade PostgreSQL plan
- **AWS**: Use RDS with read replicas

---

## Security Checklist

- [ ] Environment variables set (no hardcoded secrets)
- [ ] S3 bucket is private
- [ ] JWT secret is strong and unique
- [ ] HTTPS enabled
- [ ] Database backups configured
- [ ] Audit logs enabled

---

## Cost Estimates

### AWS (After Free Tier)
- EC2 t2.micro: ~$8/month
- S3 (5GB): ~$0.50/month
- **Total**: ~$10/month

### Render (Free Tier)
- Web Services: Free (with limitations)
- PostgreSQL: Free (512MB)
- **Total**: $0/month

### Railway
- $5 free credit/month
- Typical usage: ~$5/month

---

For more help, see [GitHub Issues](https://github.com/your-username/safekeep-vault/issues) or contact the maintainers.
