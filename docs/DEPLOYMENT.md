# 🚀 Deployment Guide

This guide covers deploying Safekeep NGO Vault to **Render.com** using their free tier.

---

## 📋 Prerequisites

- GitHub account
- Render.com account (sign up with GitHub)
- AWS account (for S3 storage only)

---

## 🌐 Render.com Deployment (Recommended)

### Why Render?

- ✅ **Free tier** for backend, frontend, and PostgreSQL
- ✅ **Auto-deploy** from GitHub
- ✅ **Zero configuration** for SSL/HTTPS
- ✅ **Built-in PostgreSQL** database
- ✅ **Simple environment variables** management

---

## Step 1: Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Ensure you have these files:**
   - `Dockerfile.backend` - Backend API container
   - `Dockerfile.frontend` - Frontend Streamlit container
   - `.streamlit/config.toml` - Streamlit production config

---

## Step 2: Set Up AWS S3 (File Storage)

Render provides compute, but we use AWS S3 for file storage.

1. **Create S3 Bucket:**
   ```bash
   aws s3 mb s3://your-bucket-name
   ```

2. **Create IAM User** with S3 permissions:
   - Go to AWS Console → IAM → Users → Create User
   - Attach policy: `AmazonS3FullAccess`
   - Save **Access Key ID** and **Secret Access Key**

3. **Configure CORS** (optional, for presigned URLs):
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "PUT", "POST"],
       "AllowedOrigins": ["*"],
       "ExposeHeaders": []
     }
   ]
   ```

---

## Step 3: Deploy Backend to Render

1. **Go to [Render Dashboard](https://dashboard.render.com)**

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository**

4. **Configure Backend Service:**
   ```
   Name: safekeep-backend
   Environment: Docker
   Dockerfile Path: Dockerfile.backend
   Branch: main
   Instance Type: Free
   ```

5. **Add Environment Variables:**
   ```bash
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   S3_BUCKET_NAME=your-bucket-name
   AWS_REGION=us-east-1
   JWT_SECRET=your-random-secret-key-here
   DATABASE_URL=<automatically provided by Render>
   ```

6. **Click "Create Web Service"**

7. **Wait for deployment** (~5-10 minutes)

8. **Copy your backend URL:** `https://safekeep-backend.onrender.com`

---

## Step 4: Deploy Frontend to Render

1. **Click "New +" → "Web Service"** again

2. **Connect same GitHub repository**

3. **Configure Frontend Service:**
   ```
   Name: safekeep-frontend
   Environment: Docker
   Dockerfile Path: Dockerfile.frontend
   Branch: main
   Instance Type: Free
   ```

4. **Add Environment Variable:**
   ```bash
   SAFEKEEP_API_URL=https://safekeep-backend.onrender.com
   ```
   (Use your actual backend URL from Step 3)

5. **Click "Create Web Service"**

6. **Wait for deployment** (~5-10 minutes)

---

## Step 5: Create PostgreSQL Database

1. **Click "New +" → "PostgreSQL"**

2. **Configure Database:**
   ```
   Name: safekeep-db
   Database: safekeep
   User: safekeep
   Region: Same as your services
   Instance Type: Free
   ```

3. **Click "Create Database"**

4. **Copy the Internal Database URL**

5. **Update Backend Service:**
   - Go to backend service → Environment
   - Update `DATABASE_URL` with the internal database URL

---

## Step 6: Test Your Deployment

1. **Visit your frontend URL:**
   ```
   https://safekeep-frontend.onrender.com
   ```

2. **Register a test NGO:**
   - NGO Name: Test Organization
   - Email: admin@test.org
   - Password: test123

3. **Test features:**
   - ✅ Upload a file
   - ✅ View dashboard
   - ✅ Check audit logs
   - ✅ Generate share link

---

## 🔧 Environment Variables Reference

### Backend (`safekeep-backend`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `AWS_ACCESS_KEY_ID` | AWS IAM access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `S3_BUCKET_NAME` | S3 bucket name | `safekeep-vault-files` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `JWT_SECRET` | Secret for JWT tokens | `your-random-secret-key` |

### Frontend (`safekeep-frontend`)

| Variable | Description | Example |
|----------|-------------|---------|
| `SAFEKEEP_API_URL` | Backend API URL | `https://safekeep-backend.onrender.com` |

---

## 🐛 Troubleshooting

### Backend won't start

**Check logs:**
- Go to backend service → Logs
- Look for errors

**Common issues:**
- Missing environment variables
- Invalid DATABASE_URL
- AWS credentials incorrect

### Frontend can't connect to backend

**Verify:**
1. `SAFEKEEP_API_URL` is set correctly
2. Backend is showing "Live" status
3. Visit `https://your-backend.onrender.com/docs` - should show API docs

### Database connection errors

**Fix:**
1. Ensure `DATABASE_URL` uses the **Internal Database URL** from Render
2. Check database is running (should show "Available")
3. Restart backend service

### Files not uploading

**Check:**
1. AWS credentials are correct
2. S3 bucket exists and is accessible
3. IAM user has S3 permissions

---

## 💰 Cost Estimate

### Free Tier (Current Setup)

| Service | Cost | Limitations |
|---------|------|-------------|
| Backend (Render) | **$0/month** | 750 hours/month, sleeps after 15min inactivity |
| Frontend (Render) | **$0/month** | 750 hours/month, sleeps after 15min inactivity |
| PostgreSQL (Render) | **$0/month** | 1GB storage, expires after 90 days |
| S3 Storage (AWS) | **~$0.50/month** | First 5GB free, then $0.023/GB |

**Total: ~$0.50/month** (just S3 storage)

### Production Tier (Recommended for real use)

| Service | Cost | Benefits |
|---------|------|----------|
| Backend (Render) | **$7/month** | Always on, 512MB RAM |
| Frontend (Render) | **$7/month** | Always on, 512MB RAM |
| PostgreSQL (Render) | **$7/month** | 1GB storage, persistent |
| S3 Storage (AWS) | **~$5/month** | 100GB storage |

**Total: ~$26/month**

---

## 🔒 Security Best Practices

1. **Use strong JWT secrets** (generate with `openssl rand -hex 32`)
2. **Rotate AWS credentials** regularly
3. **Enable S3 bucket encryption**
4. **Use HTTPS only** (Render provides this automatically)
5. **Set up monitoring** via Render dashboard

---

## 📊 Monitoring

### Render Dashboard

- **Logs:** Real-time application logs
- **Metrics:** CPU, memory, response times
- **Events:** Deployment history

### Health Checks

- Backend: `https://your-backend.onrender.com/docs`
- Frontend: `https://your-frontend.onrender.com`

---

## 🔄 Continuous Deployment

Render automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render will:
1. ✅ Pull latest code
2. ✅ Build Docker images
3. ✅ Run health checks
4. ✅ Deploy new version
5. ✅ Zero downtime

---

## 📞 Support

- **Render Docs:** https://render.com/docs
- **AWS S3 Docs:** https://docs.aws.amazon.com/s3/
- **Project Issues:** https://github.com/2004Asbah/SafeKeep-Vault/issues

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] S3 bucket created
- [ ] AWS credentials configured
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Render
- [ ] PostgreSQL database created
- [ ] Environment variables set
- [ ] Test registration works
- [ ] Test file upload works
- [ ] Test file sharing works
- [ ] Live demo link added to README

**Congratulations! Your app is live! 🎉**
