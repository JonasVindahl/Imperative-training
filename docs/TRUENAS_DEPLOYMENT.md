# TrueNAS Deployment Guide

Complete guide for hosting the C Programming Practice System on TrueNAS.

---

## Quick Start - Which Method?

**TrueNAS SCALE** (recommended) → Use **Docker** (easiest)
**TrueNAS CORE** → Use **Jail** or **VM**

Not sure which you have?
- SCALE = newer, Linux-based, has "Apps" menu
- CORE = FreeBSD-based, has "Jails" menu

---

## Method 1: Docker on TrueNAS SCALE (EASIEST) ⭐

### Prerequisites
- TrueNAS SCALE installed
- Access to TrueNAS web interface
- Dataset for app storage

### Step 1: Create Dataset
1. Go to **Storage** → **Pools**
2. Click your pool → **Add Dataset**
3. Name: `c-practice-app`
4. Click **Save**

### Step 2: Upload Files to TrueNAS

**Option A: Using Web Interface (SMB/NFS)**
1. Create SMB share for the dataset
2. From your Mac, connect to the share
3. Copy the entire project folder to the share

**Option B: Using SSH/SCP**
```bash
# From your Mac, in the project directory
scp -r /Users/jonasvindahl/Documents/projects/7_imperative_exam \
    root@YOUR_TRUENAS_IP:/mnt/tank/c-practice-app/
```

### Step 3: Deploy with Docker Compose

**SSH into TrueNAS:**
```bash
ssh root@YOUR_TRUENAS_IP
```

**Navigate to project:**
```bash
cd /mnt/tank/c-practice-app/7_imperative_exam
```

**Start the application:**
```bash
docker-compose up -d
```

**Check status:**
```bash
docker-compose ps
docker-compose logs -f
```

### Step 4: Access the Application

Open browser: `http://YOUR_TRUENAS_IP:5067`

### Managing the Container

**Stop:**
```bash
docker-compose down
```

**Restart:**
```bash
docker-compose restart
```

**View logs:**
```bash
docker-compose logs -f c-practice
```

**Update after changes:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Method 2: TrueNAS SCALE Custom App

### Step 1: Install Portainer (Optional but Recommended)

1. Go to **Apps** → **Discover Apps**
2. Search for "Portainer"
3. Click **Install**
4. Configure and deploy

### Step 2: Create Custom App via Portainer

1. Open Portainer web interface
2. Go to **Stacks** → **Add Stack**
3. Name: `c-programming-practice`
4. Paste the docker-compose.yml content
5. Click **Deploy**

---

## Method 3: Docker CLI on TrueNAS SCALE

### Build and Run Manually

**SSH into TrueNAS:**
```bash
ssh root@YOUR_TRUENAS_IP
cd /mnt/tank/c-practice-app/7_imperative_exam
```

**Build image:**
```bash
docker build -t c-practice-app .
```

**Run container:**
```bash
docker run -d \
  --name c-programming-practice \
  -p 5067:5067 \
  -v /mnt/tank/c-practice-app/7_imperative_exam/instance:/app/instance \
  -e FLASK_SECRET_KEY=your-secret-key-change-me \
  --restart unless-stopped \
  c-practice-app
```

**Check logs:**
```bash
docker logs -f c-programming-practice
```

---

## Method 4: TrueNAS CORE with Jail

### Step 1: Create Jail

1. Go to **Jails** → **Add**
2. Name: `c-practice`
3. Release: Choose latest FreeBSD version
4. Click **Save**
5. Start the jail

### Step 2: Install Dependencies

**Enter jail console:**
```bash
iocage console c-practice
```

**Install packages:**
```bash
pkg update
pkg install python39 py39-pip gcc git
```

### Step 3: Copy Application Files

**From TrueNAS shell (not in jail):**
```bash
# Create dataset
zfs create tank/c-practice-data

# Copy files to jail
cp -r /mnt/tank/c-practice-app/7_imperative_exam/* \
     /mnt/tank/iocage/jails/c-practice/root/home/
```

### Step 4: Setup Application in Jail

**Back in jail console:**
```bash
cd /home/7_imperative_exam

# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python app.py &
# Wait 5 seconds then Ctrl+C
```

### Step 5: Create Service (Auto-start)

**Create rc script:**
```bash
cat > /usr/local/etc/rc.d/cpractice << 'EOF'
#!/bin/sh
# PROVIDE: cpractice
# REQUIRE: DAEMON
# KEYWORD: shutdown

. /etc/rc.subr

name=cpractice
rcvar=cpractice_enable
command="/usr/local/bin/python3.9"
command_args="/home/7_imperative_exam/app.py"
pidfile="/var/run/cpractice.pid"

load_rc_config $name
run_rc_command "$1"
EOF

chmod +x /usr/local/etc/rc.d/cpractice
```

**Enable service:**
```bash
echo 'cpractice_enable="YES"' >> /etc/rc.conf
service cpractice start
```

### Step 6: Configure Firewall/NAT

In TrueNAS web interface:
1. Go to **Jails** → Select `c-practice`
2. Click **Edit**
3. Add port forwarding: Host `5067` → Jail `5067`
4. Save

---

## Method 5: TrueNAS VM (Any Version)

### Step 1: Create Ubuntu VM

1. Download Ubuntu Server ISO
2. Go to **Virtual Machines** → **Add**
3. Configure:
   - Name: `c-practice-vm`
   - OS: Linux
   - CPUs: 2
   - RAM: 2GB
   - Disk: 20GB
   - Network: Bridge
4. Install Ubuntu

### Step 2: Install Docker in VM

**SSH into VM and run:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y
```

### Step 3: Deploy Application

**Copy files to VM** (from your Mac):
```bash
scp -r /Users/jonasvindahl/Documents/projects/7_imperative_exam \
    user@VM_IP:~/
```

**In VM:**
```bash
cd ~/7_imperative_exam
sudo docker-compose up -d
```

---

## Reverse Proxy Setup (Optional)

### Using TrueNAS SCALE + Traefik

**Add labels to docker-compose.yml:**
```yaml
services:
  c-practice:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.c-practice.rule=Host(`practice.yourdomain.com`)"
      - "traefik.http.services.c-practice.loadbalancer.server.port=5067"
```

### Using NGINX Proxy Manager

1. Install NGINX Proxy Manager from TrueNAS Apps
2. Add proxy host:
   - Domain: `practice.yourdomain.com`
   - Forward to: `localhost:5067`
3. Enable SSL with Let's Encrypt

---

## Environment Variables

Create `.env` file in project directory:

```bash
# Security
FLASK_SECRET_KEY=change-this-to-random-string

# Database
DATABASE_URL=sqlite:///instance/practice.db

# Code execution limits
MAX_CODE_EXECUTION_TIME=3
MAX_MEMORY_MB=50

# Flask settings
FLASK_ENV=production
FLASK_DEBUG=False
```

**Generate secure secret key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Persistence & Backups

### Important Directories to Backup

```
7_imperative_exam/
├── instance/          # SQLite database (user data, progress)
├── questions/         # Question bank (static)
└── .env              # Configuration (if created)
```

### TrueNAS Snapshot Schedule

1. Go to **Tasks** → **Periodic Snapshot Tasks**
2. Add task for dataset `c-practice-app`
3. Schedule: Daily at 2 AM
4. Retention: 7 days

### Manual Backup

```bash
# From TrueNAS shell
tar -czf c-practice-backup-$(date +%Y%m%d).tar.gz \
  /mnt/tank/c-practice-app/7_imperative_exam/instance
```

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Check if port is in use
netstat -an | grep 5067

# Restart container
docker-compose restart
```

### Can't access from browser
```bash
# Check if container is running
docker ps

# Check firewall
# On TrueNAS SCALE, firewall is usually permissive

# Test from TrueNAS itself
curl http://localhost:5067
```

### Database locked errors
```bash
# Stop container
docker-compose down

# Check database file permissions
ls -la instance/practice.db

# Restart
docker-compose up -d
```

### GCC compilation errors in container
```bash
# Rebuild container with fresh image
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Performance Tuning

### For Many Concurrent Users

**Increase resources in docker-compose.yml:**
```yaml
services:
  c-practice:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
```

### Use PostgreSQL Instead of SQLite

**Add PostgreSQL service:**
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: practice
      POSTGRES_USER: practice
      POSTGRES_PASSWORD: secure-password
    volumes:
      - postgres-data:/var/lib/postgresql/data

  c-practice:
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgresql://practice:secure-password@postgres:5432/practice

volumes:
  postgres-data:
```

---

## Security Hardening

### 1. Change Default Port

In `docker-compose.yml`:
```yaml
ports:
  - "8080:5067"  # External:Internal
```

### 2. Use Strong Secret Key

```bash
# Generate and set in .env
FLASK_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### 3. Enable HTTPS

Use reverse proxy (NGINX Proxy Manager or Traefik) with Let's Encrypt SSL.

### 4. Restrict Network Access

**Docker network isolation:**
```yaml
networks:
  internal:
    internal: true
  external:

services:
  c-practice:
    networks:
      - external
```

### 5. Run as Non-Root User

Add to Dockerfile:
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

---

## Monitoring

### Container Health

```bash
# Docker stats
docker stats c-programming-practice

# Resource usage
docker inspect c-programming-practice | grep -A 10 Resources
```

### Application Logs

```bash
# Real-time logs
docker-compose logs -f --tail=100

# Save logs to file
docker-compose logs > app-logs-$(date +%Y%m%d).log
```

---

## Updates & Maintenance

### Update Application

```bash
# Stop container
docker-compose down

# Pull latest code (if using git)
git pull

# Rebuild
docker-compose build --no-cache

# Start with new version
docker-compose up -d
```

### Update Questions

```bash
# Questions are in volumes, just edit files
# Changes reflect immediately (no restart needed for question changes)
nano questions/memory_management.json

# Restart to reload question cache (if needed)
docker-compose restart
```

---

## Recommended Setup: TrueNAS SCALE + Docker Compose

**Why this is best:**
✅ Easy to deploy
✅ Easy to update
✅ Isolated environment
✅ Built-in health checks
✅ Automatic restart
✅ Volume persistence
✅ Clean uninstall

**Complete setup in 5 minutes:**

```bash
# 1. SSH to TrueNAS
ssh root@truenas-ip

# 2. Create directory
mkdir -p /mnt/tank/apps/c-practice
cd /mnt/tank/apps/c-practice

# 3. Copy files (from your Mac)
# Use SCP or SMB share

# 4. Create .env file
cat > .env << EOF
FLASK_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=sqlite:///instance/practice.db
EOF

# 5. Deploy
docker-compose up -d

# 6. Check
docker-compose ps
curl http://localhost:5067

# Done! Access at http://truenas-ip:5067
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start | `docker-compose up -d` |
| Stop | `docker-compose down` |
| Restart | `docker-compose restart` |
| Logs | `docker-compose logs -f` |
| Status | `docker-compose ps` |
| Rebuild | `docker-compose build --no-cache` |
| Update | `git pull && docker-compose up -d --build` |
| Backup DB | `cp instance/practice.db instance/practice.db.backup` |

---

## Support

**Check logs first:**
```bash
docker-compose logs -f c-practice
```

**Common issues:**
- Port 5067 in use → Change port in docker-compose.yml
- Permission denied → Check file ownership: `chown -R 1000:1000 instance/`
- Database locked → Stop container, check instance/practice.db permissions
- Can't compile C code → Rebuild container: `docker-compose build --no-cache`

**Test manually:**
```bash
# Enter container
docker exec -it c-programming-practice bash

# Test GCC
gcc --version

# Test Python
python app.py
```

---

## Next Steps

1. ✅ Deploy using preferred method
2. ✅ Access app at `http://truenas-ip:5067`
3. ✅ Register first user account
4. ✅ Test practice sessions
5. ✅ Setup reverse proxy (optional)
6. ✅ Enable SSL (optional)
7. ✅ Configure backups

Enjoy your C Programming Practice System! 🚀
