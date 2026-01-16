# TrueNAS SCALE 24.10 - Deploy with YAML

Quick deployment guide using the YAML configuration file.

---

## Method 1: Using Docker Compose YAML (Recommended)

TrueNAS SCALE 24.10 has native Docker support. Use the YAML file directly!

### Step 1: Prepare Storage

**SSH into TrueNAS:**
```bash
ssh root@YOUR_TRUENAS_IP
```

**Create directories:**
```bash
# Create directories for app and data
mkdir -p /mnt/MainPool/Apps/c-practice
mkdir -p /mnt/MainPool/Apps/c-practice-data

# Set permissions
chmod 755 /mnt/MainPool/Apps/c-practice
chmod 755 /mnt/MainPool/Apps/c-practice-data
```

### Step 2: Upload Application Files

**Option A: Using SCP (from your Mac):**
```bash
# Copy entire project to TrueNAS
scp -r /Users/jonasvindahl/Documents/projects/7_imperative_exam/* \
    root@YOUR_TRUENAS_IP:/mnt/MainPool/Apps/c-practice/
```

**Option B: Using SMB Share:**
1. Create SMB share pointing to `/mnt/MainPool/Apps/c-practice`
2. Connect from Mac: `smb://YOUR_TRUENAS_IP/Apps`
3. Copy all project files to the share

### Step 3: Deploy with YAML

**SSH into TrueNAS:**
```bash
ssh root@YOUR_TRUENAS_IP
cd /mnt/MainPool/Apps/c-practice
```

**Deploy using docker-compose:**
```bash
docker compose -f truenas-scale-app.yaml up -d
```

**Or if docker-compose is separate command:**
```bash
docker-compose -f truenas-scale-app.yaml up -d
```

### Step 4: Verify Deployment

**Check status:**
```bash
docker ps
```

You should see `c-programming-practice` with status "Up".

**View logs:**
```bash
docker logs -f c-programming-practice
```

Look for:
```
Database initialized!
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5067
```

### Step 5: Access the Application

Open browser: **http://YOUR_TRUENAS_IP:5067**

---

## Method 2: Import via TrueNAS Apps UI (If Supported)

Some versions of SCALE allow importing compose files via the UI.

### Try This:

1. **Go to Apps** → **Discover Apps**
2. Look for **"Launch Docker Image"** or **"Custom App"**
3. If there's an option to **import YAML/compose file**, select it
4. Upload `truenas-scale-app.yaml`
5. Adjust paths if needed
6. Deploy

**Note:** If this option doesn't exist, use Method 1 (CLI).

---

## Managing the Application

### Start/Stop/Restart

```bash
# Stop
docker compose -f /mnt/MainPool/Apps/c-practice/truenas-scale-app.yaml down

# Start
docker compose -f /mnt/MainPool/Apps/c-practice/truenas-scale-app.yaml up -d

# Restart
docker compose -f /mnt/MainPool/Apps/c-practice/truenas-scale-app.yaml restart

# View logs
docker logs -f c-programming-practice

# Check status
docker ps | grep c-programming
```

### Update Application

```bash
# Stop container
docker compose -f /mnt/MainPool/Apps/c-practice/truenas-scale-app.yaml down

# Update files (if using git)
cd /mnt/MainPool/Apps/c-practice
git pull

# Or manually copy new files via SCP/SMB

# Rebuild and start
docker compose -f /mnt/MainPool/Apps/c-practice/truenas-scale-app.yaml up -d --build
```

---

## YAML Configuration Explained

The `truenas-scale-app.yaml` file contains:

### Image
```yaml
image: python:3.11-slim
```
Base Python image with slim OS.

### Command
```yaml
command:
  - /bin/bash
  - -c
  - |
    set -e
    apt-get update
    apt-get install -y gcc build-essential
    cd /app
    pip install --no-cache-dir -r requirements.txt
    python app.py
```
Multi-line command that:
1. Updates package manager
2. Installs GCC compiler
3. Installs Python dependencies
4. Starts the Flask app

### Environment Variables
```yaml
environment:
  - FLASK_SECRET_KEY=change-this-to-random-string
  - FLASK_ENV=production
  - DATABASE_URL=sqlite:///instance/practice.db
  - TZ=Europe/Copenhagen
```

**⚠️ IMPORTANT:** Change `FLASK_SECRET_KEY` to something random!

Generate secure key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Volumes
```yaml
volumes:
  - /mnt/MainPool/Apps/c-practice:/app:rw
  - /mnt/MainPool/Apps/c-practice-data:/app/instance:rw
```

Maps host directories to container paths.

### Ports
```yaml
ports:
  - 5067:5067
```

Exposes port 5067 on host.

### Resources
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

Limits CPU and RAM usage.

---

## Customization

### Change Port

Edit `truenas-scale-app.yaml`:
```yaml
ports:
  - 8080:5067  # External:Internal
```

Access at: `http://TRUENAS_IP:8080`

### Change Paths

If your storage is different:
```yaml
volumes:
  - /mnt/YOUR_POOL/your-path:/app:rw
  - /mnt/YOUR_POOL/your-data:/app/instance:rw
```

### Change Resource Limits

For more/less resources:
```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # More CPU
      memory: 4G     # More RAM
```

### Change Timezone

```yaml
environment:
  - TZ=America/New_York  # Or your timezone
```

---

## Auto-Start on Boot

The YAML includes `restart: unless-stopped` which means:
- ✅ Auto-starts when TrueNAS boots
- ✅ Restarts if crashes
- ⏸️ Stays stopped if you manually stop it

To change behavior:
```yaml
restart: always        # Always restart
restart: on-failure    # Only restart on errors
restart: "no"          # Never restart
```

---

## Backups

### Backup Database

```bash
# Manual backup
cp /mnt/MainPool/Apps/c-practice-data/practice.db \
   /mnt/MainPool/Apps/c-practice-data/practice.db.backup-$(date +%Y%m%d)
```

### Backup Entire App

```bash
# Create tarball
tar -czf /mnt/MainPool/Backups/c-practice-$(date +%Y%m%d).tar.gz \
  /mnt/MainPool/Apps/c-practice \
  /mnt/MainPool/Apps/c-practice-data
```

### TrueNAS Snapshots (Recommended)

1. Go to **Data Protection** → **Periodic Snapshot Tasks**
2. Add task for dataset `Apps/c-practice`
3. Schedule: Daily
4. Retention: 7 days

---

## Monitoring

### Check Container Health

```bash
# Container stats
docker stats c-programming-practice

# Detailed info
docker inspect c-programming-practice

# Check health status
docker inspect c-programming-practice | grep -A 5 Health
```

### View Logs

```bash
# Real-time logs
docker logs -f c-programming-practice

# Last 100 lines
docker logs --tail 100 c-programming-practice

# Since specific time
docker logs --since 1h c-programming-practice
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker logs c-programming-practice

# Check if port is in use
netstat -an | grep 5067

# Try starting manually to see errors
docker compose -f truenas-scale-app.yaml up
```

### Permission Errors

```bash
# Fix permissions
chown -R 1000:1000 /mnt/MainPool/Apps/c-practice
chown -R 1000:1000 /mnt/MainPool/Apps/c-practice-data
chmod -R 755 /mnt/MainPool/Apps/c-practice
```

### Database Locked

```bash
# Stop container
docker compose -f /mnt/MainPool/Apps/c-practice/truenas-scale-app.yaml down

# Check database file
ls -la /mnt/MainPool/Apps/c-practice-data/practice.db

# Remove lock file if exists
rm -f /mnt/MainPool/Apps/c-practice-data/practice.db-wal
rm -f /mnt/MainPool/Apps/c-practice-data/practice.db-shm

# Restart
docker compose -f /mnt/MainPool/Apps/c-practice/truenas-scale-app.yaml up -d
```

### Can't Access from Browser

```bash
# Test locally on TrueNAS
curl http://localhost:5067

# Check if container is running
docker ps | grep c-programming

# Check container IP
docker inspect c-programming-practice | grep IPAddress

# Try accessing via container IP
curl http://CONTAINER_IP:5067
```

### GCC Compilation Fails

```bash
# Enter container
docker exec -it c-programming-practice bash

# Manually install GCC
apt-get update
apt-get install -y gcc build-essential

# Test GCC
gcc --version

# Exit
exit

# Restart container
docker restart c-programming-practice
```

---

## Upgrading

### Update to New Version

```bash
# Navigate to app directory
cd /mnt/MainPool/Apps/c-practice

# Pull latest changes (if using git)
git pull

# Or copy new files via SCP/SMB

# Rebuild and restart
docker compose -f truenas-scale-app.yaml down
docker compose -f truenas-scale-app.yaml up -d --build

# Check logs
docker logs -f c-programming-practice
```

---

## Remove/Uninstall

```bash
# Stop and remove container
docker compose -f /mnt/MainPool/Apps/c-practice/truenas-scale-app.yaml down

# Remove image (optional)
docker rmi python:3.11-slim

# Remove data (if you want to start fresh)
rm -rf /mnt/MainPool/Apps/c-practice
rm -rf /mnt/MainPool/Apps/c-practice-data
```

---

## Integration with TrueNAS Apps UI

### Make It Appear in Apps UI

TrueNAS SCALE 24.10 may not automatically show docker-compose deployed apps in the Apps UI. They're managed via CLI only.

**To see it in Apps UI, you'd need to:**
1. Create a full TrueNAS app chart (complex)
2. Or use the Custom App feature in UI (as shown in previous guide)

**Recommendation:** Use CLI for this deployment method. It's simpler and more direct.

---

## Quick Reference Commands

```bash
# Start
cd /mnt/MainPool/Apps/c-practice && docker compose -f truenas-scale-app.yaml up -d

# Stop
cd /mnt/MainPool/Apps/c-practice && docker compose -f truenas-scale-app.yaml down

# Restart
docker restart c-programming-practice

# Logs
docker logs -f c-programming-practice

# Status
docker ps | grep c-programming

# Enter container
docker exec -it c-programming-practice bash

# Rebuild
cd /mnt/MainPool/Apps/c-practice && docker compose -f truenas-scale-app.yaml up -d --build
```

---

## Complete Deployment Script

Create this as `deploy-on-truenas.sh` on TrueNAS:

```bash
#!/bin/bash
# Quick deployment script for TrueNAS SCALE

set -e

APP_DIR="/mnt/MainPool/Apps/c-practice"
DATA_DIR="/mnt/MainPool/Apps/c-practice-data"
YAML_FILE="$APP_DIR/truenas-scale-app.yaml"

echo "🚀 Deploying C Programming Practice System..."

# Create directories
mkdir -p "$APP_DIR"
mkdir -p "$DATA_DIR"

# Set permissions
chmod 755 "$APP_DIR"
chmod 755 "$DATA_DIR"

# Navigate to app directory
cd "$APP_DIR"

# Stop if already running
if docker ps | grep -q c-programming-practice; then
    echo "⏹️  Stopping existing container..."
    docker compose -f "$YAML_FILE" down
fi

# Start container
echo "🔨 Starting container..."
docker compose -f "$YAML_FILE" up -d

# Wait for startup
echo "⏳ Waiting for application to start..."
sleep 10

# Check status
if docker ps | grep -q c-programming-practice; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "Access at: http://$(hostname -I | awk '{print $1}'):5067"
    echo ""
    echo "View logs: docker logs -f c-programming-practice"
else
    echo ""
    echo "❌ Deployment failed. Check logs:"
    echo "docker logs c-programming-practice"
fi
```

Make it executable:
```bash
chmod +x deploy-on-truenas.sh
```

Run it:
```bash
./deploy-on-truenas.sh
```

---

## Summary

**Files to use:**
- ✅ `truenas-scale-app.yaml` - Main deployment file
- ✅ All project files in `/mnt/MainPool/Apps/c-practice/`

**Commands to remember:**
```bash
# Deploy
docker compose -f truenas-scale-app.yaml up -d

# Manage
docker logs -f c-programming-practice
docker restart c-programming-practice
docker compose -f truenas-scale-app.yaml down
```

**Access:**
- `http://YOUR_TRUENAS_IP:5067`

That's it! Simple, clean, works perfectly with TrueNAS SCALE 24.10. 🎉
