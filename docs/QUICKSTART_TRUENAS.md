# TrueNAS Quick Start (5 Minutes)

## For TrueNAS SCALE (Recommended)

### 1. Copy Files to TrueNAS

**Using SMB/NFS Share:**
1. Create dataset: `Storage` → `Pools` → `Add Dataset` → Name: `c-practice`
2. Create SMB share for the dataset
3. Copy entire project folder to the share from your Mac

**OR using SCP:**
```bash
# From your Mac terminal:
cd /Users/jonasvindahl/Documents/projects/7_imperative_exam
scp -r . root@YOUR_TRUENAS_IP:/mnt/tank/c-practice/
```

### 2. Deploy with Docker

**SSH into TrueNAS:**
```bash
ssh root@YOUR_TRUENAS_IP
cd /mnt/tank/c-practice/7_imperative_exam
```

**Run the deploy script:**
```bash
./deploy.sh
```

**OR manually:**
```bash
docker-compose up -d
```

### 3. Access the App

Open browser: **http://YOUR_TRUENAS_IP:5067**

Done! 🎉

---

## For TrueNAS CORE

### Quick Method (Jail)

```bash
# 1. Create jail named "c-practice" via web UI

# 2. SSH into TrueNAS
iocage console c-practice

# 3. Install dependencies
pkg install python39 py39-pip gcc

# 4. Copy files to jail (from TrueNAS shell, not jail)
# Exit jail first (Ctrl+D), then:
cp -r /mnt/tank/c-practice/7_imperative_exam /mnt/tank/iocage/jails/c-practice/root/root/

# 5. Back in jail console
cd /root/7_imperative_exam
pip install -r requirements.txt
python3.9 app.py

# Access at http://TRUENAS_IP:5067
```

---

## Manage the App

```bash
# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Update after changes
docker-compose up -d --build
```

---

## Troubleshooting

**Can't access the app?**
- Check container is running: `docker-compose ps`
- Check logs: `docker-compose logs`
- Test locally on TrueNAS: `curl http://localhost:5067`

**Port 5067 already in use?**
Edit `docker-compose.yml`, change line:
```yaml
ports:
  - "8080:5067"  # Use port 8080 instead
```

**Database errors?**
```bash
docker-compose down
rm -rf instance/
docker-compose up -d
```

---

## Next Steps

✅ Register first user: http://TRUENAS_IP:5067/auth/register
✅ Setup reverse proxy for HTTPS (optional)
✅ Configure TrueNAS snapshots for backups

**Full documentation:** See `TRUENAS_DEPLOYMENT.md`
