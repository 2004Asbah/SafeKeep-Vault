# 🚀 Deploy to Render.com - Step-by-Step Guide

## 📋 What You'll Need
- ✅ GitHub account with repository pushed
- ✅ AWS S3 bucket (already created via Terraform)
- ✅ Render.com account (free - create at [render.com](https://render.com))

**Time Required**: ~20 minutes

---

## Step 1: Sign Up for Render

1. Go to [render.com](https://render.com)
2. Click "Get Started"
3. Sign up with GitHub (recommended - easier integration)
4. Authorize Render to access your repositories

---

## Step 2: Create PostgreSQL Database

1. **Dashboard** → Click "New +" → Select "PostgreSQL"

2. **Configure Database**:
   ```
   Name: safekeep-db
   Database: safekeep
   User: safekeep
   Region: Oregon (US West)
   PostgreSQL Version: 15
   Instance Type: Free
   ```

3. Click **"Create Database"**

4. **IMPORTANT**: Copy the **Internal Database URL**
   - It looks like: `postgresql://safekeep:xxxxx@dpg-xxxxx/safekeep`
   - You'll need this in Step 3

---

## Step 3: Deploy Backend API

1. **Dashboard** → Click "New +" → Select "Web Service"

2. **Connect Repository**:
   - Select your GitHub repository: `2004Asbah/safekeep-vault`
   - Click "Connect"

3. **Configure Service**:
   ```
   Name: safekeep-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave empty)
   Environment: Docker
   Instance Type: Free
   ```

4. **Add Environment Variables** (click "Advanced"):
   
   Click "Add Environment Variable" for each:
   
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | Paste the Internal Database URL from Step 2 |
   | `AWS_ACCESS_KEY_ID` | Your AWS access key |
   | `AWS_SECRET_ACCESS_KEY` | Your AWS secret key |
   | `AWS_REGION` | `eu-north-1` |
   | `S3_BUCKET_NAME` | Your S3 bucket name (from Terraform output) |
   | `JWT_SECRET` | Generate random string (e.g., `openssl rand -hex 32`) |

5. Click **"Create Web Service"**

6. **Wait for deployment** (~5-10 minutes)
   - Watch the logs in real-time
   - Should see "Build successful" then "Deploy live"

7. **Copy Backend URL**:
   - Will be something like: `https://safekeep-backend.onrender.com`
   - You'll need this for Step 4

---

## Step 4: Deploy Frontend

1. **Dashboard** → Click "New +" → Select "Web Service"

2. **Connect Repository**:
   - Select same repository: `2004Asbah/safekeep-vault`

3. **Configure Service**:
   ```
   Name: safekeep-frontend
   Region: Oregon (US West)
   Branch: main
   Root Directory: frontendd
   Environment: Docker
   Instance Type: Free
   ```

4. **Add Environment Variable**:
   
   | Key | Value |
   |-----|-------|
   | `SAFEKEEP_API_URL` | Paste backend URL from Step 3 |

5. Click **"Create Web Service"**

6. **Wait for deployment** (~5-10 minutes)

---

## Step 5: Initialize Database

1. Go to **safekeep-backend** service page

2. Click **"Shell"** tab (top right)

3. Run this command:
   ```bash
   python reset_database.py
   ```

4. You should see:
   ```
   ✅ Database reset complete!
   Tables created: users, files, audit_logs
   ```

---

## Step 6: Test Your Deployment! 🎉

1. **Open Frontend URL**:
   - Go to your frontend service
   - Click the URL (e.g., `https://safekeep-frontend.onrender.com`)

2. **Register Test NGO**:
   - Click "Register NGO"
   - Fill in details
   - Login

3. **Upload Test File**:
   - Go to Upload Center
   - Upload a PDF or image
   - Watch compression in action

4. **Verify S3**:
   - Check your S3 bucket
   - File should be there!

---

## Step 7: Update Your README

Add the live demo link to your README.md:

```markdown
🔗 **[Live Demo](https://safekeep-frontend.onrender.com)** | 📖 **[Documentation](docs/)**
```

Commit and push:
```bash
git add README.md
git commit -m "docs: Add live demo link"
git push
```

---

## 🎯 What You've Accomplished

✅ **Live Application** - Running on Render.com  
✅ **PostgreSQL Database** - Production-ready  
✅ **AWS S3 Integration** - Cloud file storage  
✅ **Free Hosting** - $0/month (forever)  
✅ **Auto-Deploy** - Updates on every git push  
✅ **Professional URL** - Share with recruiters  

---

## 📊 Your Architecture Now

```
GitHub → Render (Auto-Deploy) → PostgreSQL + Docker
                ↓
              AWS S3 (File Storage)
```

**Resume Line**:
> "Deployed multi-tenant SaaS application with Docker, PostgreSQL, and AWS S3 on Render with automated CI/CD from GitHub"

---

## ⚠️ Important Notes

### Free Tier Limitations
- **Spin down after 15 min inactivity** (cold start ~30 sec)
- **750 hours/month** (enough for demos)
- **512MB RAM** per service

### Keeping It Awake (Optional)
Use a service like [UptimeRobot](https://uptimerobot.com) to ping your app every 5 minutes.

---

## 🐛 Troubleshooting

### Backend Won't Start
- Check environment variables are set correctly
- View logs: Backend service → "Logs" tab
- Verify DATABASE_URL format

### Frontend Can't Connect
- Verify `SAFEKEEP_API_URL` is correct
- Should be `https://` not `http://`
- Check backend is running (green status)

### Database Connection Error
- Verify DATABASE_URL is the **Internal** URL, not External
- Check database is running

### S3 Upload Fails
- Verify AWS credentials are correct
- Check S3 bucket exists
- Verify bucket region matches `AWS_REGION`

---

## 🎉 Next Steps

1. ✅ Share live URL with recruiters
2. ✅ Add to resume/portfolio
3. ✅ Monitor Render dashboard
4. ✅ Set up custom domain (optional, $0 on Render)

**Your app is now LIVE!** 🚀
