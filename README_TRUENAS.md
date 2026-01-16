# Deploy to TrueNAS SCALE 24.10 - Quick Guide

## 🎯 Super Simple 3-Step Deployment

### Step 1: Copy Files to TrueNAS

**From your Mac:**
```bash
scp -r /Users/jonasvindahl/Documents/projects/7_imperative_exam \
    root@YOUR_TRUENAS_IP:/mnt/MainPool/Apps/c-practice
```

Change `MainPool` to your actual pool name.

### Step 2: Run Deploy Script

**SSH to TrueNAS:**
```bash
ssh root@YOUR_TRUENAS_IP
cd /mnt/MainPool/Apps/c-practice/7_imperative_exam
./DEPLOY_TRUENAS_SIMPLE.sh
```

### Step 3: Access Your App

Open browser: **http://YOUR_TRUENAS_IP:5067**

**Done!** 🎉

---

## 📁 What You Have

### Deployment Files

✅ **`truenas-scale-app.yaml`**
- Docker Compose configuration
- Ready to use with TrueNAS SCALE 24.10
- Sets up Python + GCC environment
- Configures ports, volumes, environment

✅ **`DEPLOY_TRUENAS_SIMPLE.sh`**
- Automated deployment script
- Creates directories
- Generates secret key
- Deploys container
- Shows status

✅ **`TRUENAS_SCALE_YAML_DEPLOY.md`**
- Complete documentation
- Troubleshooting guide
- Management commands
- Backup strategies

---

## 🔧 Managing Your App

### Common Commands

**View logs:**
```bash
docker logs -f c-programming-practice
```

**Restart:**
```bash
docker restart c-programming-practice
```

**Stop:**
```bash
cd /mnt/MainPool/Apps/c-practice/7_imperative_exam
docker compose -f truenas-scale-app.yaml down
```

**Start:**
```bash
cd /mnt/MainPool/Apps/c-practice/7_imperative_exam
docker compose -f truenas-scale-app.yaml up -d
```

**Check status:**
```bash
docker ps | grep c-programming
```

---

## 📊 Your Data

**Application files:**
```
/mnt/MainPool/Apps/c-practice/7_imperative_exam/
```

**Database & user data:**
```
/mnt/MainPool/Apps/c-practice-data/
└── practice.db
```

**Questions (edit anytime):**
```
/mnt/MainPool/Apps/c-practice/7_imperative_exam/questions/
├── memory_management.json
├── pointers.json
├── fill_blanks.json
└── ... (20 questions each)
```

---

## 🛡️ Backups

### Quick Backup

```bash
# Backup database
cp /mnt/MainPool/Apps/c-practice-data/practice.db \
   /mnt/MainPool/Apps/c-practice-data/practice.db.backup
```

### TrueNAS Snapshots (Recommended)

1. **Data Protection** → **Periodic Snapshot Tasks**
2. **Add** → Select dataset: `Apps/c-practice`
3. **Schedule**: Daily at 2 AM
4. **Lifetime**: 7 days

---

## 🔄 Updates

### Update Application

```bash
# SSH to TrueNAS
ssh root@YOUR_TRUENAS_IP

# Navigate to app
cd /mnt/MainPool/Apps/c-practice/7_imperative_exam

# Pull updates (if using git)
git pull

# Or copy new files via SCP

# Redeploy
./DEPLOY_TRUENAS_SIMPLE.sh
```

### Add More Questions

Just edit the JSON files in `questions/` directory:

```bash
# Via SSH
nano /mnt/MainPool/Apps/c-practice/7_imperative_exam/questions/memory_management.json

# Or via SMB share (easier)
# Connect from Mac, edit with text editor
```

Restart app to reload:
```bash
docker restart c-programming-practice
```

---

## 🌐 Access from Internet (Optional)

### Port Forward on Router

1. Login to your router
2. Add port forwarding rule:
   - **External Port**: 5067
   - **Internal IP**: Your TrueNAS IP
   - **Internal Port**: 5067
   - **Protocol**: TCP

3. Access via your public IP: `http://YOUR_PUBLIC_IP:5067`

**⚠️ Security Warning:** Use HTTPS/reverse proxy for internet access!

### Add HTTPS (Recommended)

Install **NGINX Proxy Manager** from TrueNAS Apps:

1. **Apps** → **Discover** → Search "nginx proxy manager"
2. Install
3. Access at `http://TRUENAS_IP:81`
4. Add proxy host pointing to `localhost:5067`
5. Enable Let's Encrypt SSL
6. Access via `https://yourdomain.com`

---

## ❓ Troubleshooting

### App won't start?

```bash
# Check logs
docker logs c-programming-practice

# Check if port is in use
netstat -an | grep 5067

# Recreate container
cd /mnt/MainPool/Apps/c-practice/7_imperative_exam
docker compose -f truenas-scale-app.yaml down
docker compose -f truenas-scale-app.yaml up -d
```

### Can't access from browser?

```bash
# Test locally
curl http://localhost:5067

# Check container is running
docker ps | grep c-programming

# Check TrueNAS firewall (usually disabled by default)
```

### Database errors?

```bash
# Stop app
docker stop c-programming-practice

# Remove database
rm /mnt/MainPool/Apps/c-practice-data/practice.db

# Start app (creates new database)
docker start c-programming-practice
```

### Need more help?

Check the full guide: `TRUENAS_SCALE_YAML_DEPLOY.md`

---

## 📈 System Requirements

**Minimum:**
- TrueNAS SCALE 24.10
- 1 CPU core
- 512MB RAM
- 2GB storage

**Recommended:**
- 2 CPU cores
- 2GB RAM
- 5GB storage

**Concurrent users:**
- Light use (1-5 users): Minimum specs OK
- Medium (5-20 users): Recommended specs
- Heavy (20+ users): 4 cores, 4GB RAM

---

## 📚 Documentation

**Quick Start:**
- This file (README_TRUENAS.md)
- DEPLOY_TRUENAS_SIMPLE.sh

**Detailed Guides:**
- TRUENAS_SCALE_YAML_DEPLOY.md - Complete YAML deployment guide
- TRUENAS_SCALE_APPS_DEPLOY.md - GUI deployment method
- TRUENAS_DEPLOYMENT.md - All deployment methods

**Application:**
- NEW_FEATURES.md - Feature overview
- QUESTION_EXPANSION_REPORT.md - Question bank details
- TEST_REPORT.md - Testing documentation

---

## 🎓 First Time Setup

After deployment:

1. **Access the app**: `http://TRUENAS_IP:5067`
2. **Register admin account**: Click "Register"
3. **Create account** with strong password
4. **Start practicing!** Select a category

**Share with students:**
- Give them the URL: `http://TRUENAS_IP:5067`
- They register their own accounts
- Track their progress in the database

---

## 💾 Storage Usage

**Typical usage:**
- Application files: ~50MB
- Database (per user): ~1MB
- Total for 50 users: ~100MB

**Growth:**
- Database grows slowly with usage
- Mostly static files
- 1GB dataset is plenty

---

## ✅ Feature Checklist

Current features:
- ✅ 264 questions across 11 categories
- ✅ 5 question types (MC, fill-blanks, drag-drop, recursive trace)
- ✅ Bilingual (English + Danish)
- ✅ User authentication
- ✅ Progress tracking
- ✅ Adaptive learning
- ✅ Safe C code compilation
- ✅ Instant feedback
- ✅ Detailed explanations

---

## 🚀 Quick Command Reference

```bash
# Deploy
./DEPLOY_TRUENAS_SIMPLE.sh

# Status
docker ps | grep c-programming

# Logs
docker logs -f c-programming-practice

# Restart
docker restart c-programming-practice

# Stop
docker stop c-programming-practice

# Start
docker start c-programming-practice

# Remove
docker compose -f truenas-scale-app.yaml down

# Backup DB
cp /mnt/MainPool/Apps/c-practice-data/practice.db backup.db

# Update
git pull && ./DEPLOY_TRUENAS_SIMPLE.sh
```

---

## 🎉 You're All Set!

Your C Programming Practice System is ready to use on TrueNAS SCALE 24.10.

**Need help?** Check the detailed guides in the documentation folder.

**Questions?** All settings are in `truenas-scale-app.yaml`

**Enjoy!** 🚀
