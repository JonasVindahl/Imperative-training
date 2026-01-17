# TrueNAS SCALE Deployment - Quick Guide

## 🚀 Deploy to TrueNAS SCALE 24.10

### Step 1: Build Docker Image for AMD64

On your Mac, run:

```bash
chmod +x build-for-truenas.sh
./build-for-truenas.sh
```

This builds a **linux/amd64** image compatible with TrueNAS (not ARM64).

### Step 2: Deploy Custom App

In TrueNAS Web UI:

1. **Apps** → **Discover Apps** or **Available Applications**
2. Click **Launch Docker Image** or **Custom App**
3. Fill in the form:

   **Application Name**: `c-programming-practice`

   **Image Repository**: `ghcr.io/jonasvindahl/imperative-training`

   **Image Tag**: `latest`

   **Container Port**: `8000`

   **Node Port** (Host Port): `8000` (or any port like 18000, 28000, etc.)

4. **Optional - Add Storage** (for persistent database):
   - **Host Path**: `/mnt/MainPool/Apps/c-practice-data`
   - **Mount Path**: `/app/instance`
   - **Type**: Host Path

5. Click **Install** or **Deploy**

### Step 3: Access the Application

Open your browser to:

```
http://TRUENAS_IP:8000
```

(Or use the host port you chose, e.g., `http://TRUENAS_IP:18000`)

---

## 📊 Quick Verification

```bash
# SSH to TrueNAS
ssh root@TRUENAS_IP

# Check if container is running
docker ps | grep programming

# View logs
docker logs c-programming-practice

# Test locally
curl http://localhost:8000
```

---

## 🎓 First Use

1. Navigate to `http://TRUENAS_IP:8000`
2. Click **Register** to create an account
3. Login with your new account
4. Select a question category
5. Start practicing with **620 questions**!

---

## 🔧 Management Commands

```bash
# Restart
docker restart c-programming-practice

# Stop
docker stop c-programming-practice

# Start
docker start c-programming-practice

# View logs in real-time
docker logs -f c-programming-practice

# Remove and redeploy
docker stop c-programming-practice
docker rm c-programming-practice
# Then redeploy via TrueNAS Web UI
```

---

## 📈 System Resources

**Recommended**:
- CPU: 1-2 cores
- RAM: 1-2 GB
- Storage: 2 GB

**Handles**:
- 1-5 users: Minimum specs
- 5-20 users: Recommended specs
- 20+ users: 2-4 cores, 4 GB RAM

---

## 🔐 Security Notes

- The app runs on port 8000 (HTTP)
- For production: Use NGINX reverse proxy with SSL
- For local network use: HTTP is fine
- Database is SQLite (stored in `/app/instance/practice.db`)
- User passwords are hashed with werkzeug

---

## 📁 Data Persistence

If you mounted storage:
- Database: `/app/instance/practice.db`
- Backup: `cp /mnt/MainPool/Apps/c-practice-data/practice.db backup.db`

Without mounted storage:
- Data is inside container (lost on removal)
- To persist: Add Host Path mount as shown in Step 2

---

## ❓ Troubleshooting

**Port already in use?**
- Use a different host port (e.g., 18000, 28000)
- Or stop the conflicting service

**Can't access from browser?**
```bash
# Check container status
docker ps | grep programming

# Check if port is listening
netstat -an | grep 8000

# Test from TrueNAS itself
curl http://localhost:8000
```

**Container won't start?**
```bash
# Check logs for errors
docker logs c-programming-practice

# Verify image was pulled
docker images | grep imperative

# Try pulling manually
docker pull ghcr.io/jonasvindahl/imperative-training:latest
```

**Database errors?**
```bash
# Reset database (WARNING: Deletes all user data)
docker exec c-programming-practice rm /app/instance/practice.db
docker restart c-programming-practice
```

---

## 🌐 Access from Internet (Advanced)

### Option 1: Port Forward
1. Forward port 8000 on your router to TrueNAS IP
2. Access via: `http://YOUR_PUBLIC_IP:8000`
3. ⚠️ **Not recommended without SSL!**

### Option 2: NGINX Proxy Manager (Recommended)
1. Install NGINX Proxy Manager from TrueNAS Apps
2. Configure proxy host:
   - Domain: `cpractice.yourdomain.com`
   - Forward to: `truenas-ip:8000`
   - Enable SSL with Let's Encrypt
3. Access via: `https://cpractice.yourdomain.com`

---

## ✅ Success Checklist

- [x] Built Docker image with `build-for-truenas.sh`
- [x] Deployed Custom App in TrueNAS
- [x] Container is running (`docker ps`)
- [x] Can access at `http://TRUENAS_IP:8000`
- [x] Can register and login
- [x] Questions load correctly
- [x] Database persists after restart (if mounted storage)

---

**Deployment Complete!** 🎉

You now have **620 C programming questions** running on TrueNAS SCALE!
