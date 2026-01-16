# TrueNAS SCALE 24.10 - Deploy via Apps (Easiest Method)

Complete guide for deploying C Programming Practice System using TrueNAS SCALE 24.10's native Apps system.

---

## Method 1: Custom App (Recommended - No SSH Needed!) ⭐

### Step 1: Create Dataset for App Storage

1. **Navigate to Storage**
   - Go to **Storage** → **Create Dataset** (or right-click your pool)
   - **Name**: `c-practice`
   - **Dataset Preset**: Generic
   - Click **Save**

2. **Create Sub-datasets** (for organization)
   - Create dataset: `c-practice/app` (application files)
   - Create dataset: `c-practice/data` (database/instance)

### Step 2: Upload Application Files

**Option A: Using SMB Share (Easiest for Mac)**

1. **Create SMB Share:**
   - Go to **Shares** → **Windows Shares (SMB)** → **Add**
   - **Path**: Browse to `/mnt/YOUR_POOL/c-practice/app`
   - **Name**: `c-practice-app`
   - Click **Save**
   - **Enable Service**: Toggle **SMB** service on

2. **Connect from Mac:**
   - Open **Finder** → **Go** → **Connect to Server** (⌘K)
   - Enter: `smb://YOUR_TRUENAS_IP/c-practice-app`
   - Login with your TrueNAS credentials
   - Copy the entire project folder (`7_imperative_exam`) to the share

**Option B: Using SSH/SCP**

```bash
# From your Mac terminal:
scp -r /Users/jonasvindahl/Documents/projects/7_imperative_exam \
    root@YOUR_TRUENAS_IP:/mnt/YOUR_POOL/c-practice/app/
```

### Step 3: Deploy Custom App via Web UI

1. **Go to Apps Section:**
   - Click **Apps** in left sidebar
   - Click **Discover Apps** (top right)

2. **Install Custom App:**
   - Scroll down and click **Custom App**
   - Fill in the form:

#### Application Name
```
c-programming-practice
```

#### Image Configuration

**Image Repository:**
```
python:3.11-slim
```

**Image Pull Policy:**
```
If not present
```

#### Container Configuration

**Container Command:**
```bash
/bin/bash
```

**Container Args:**
```bash
-c
cd /app && apt-get update && apt-get install -y gcc build-essential && pip install -r requirements.txt && python app.py
```

**Container Environment Variables:**
Click **Add** for each:

| Name | Value |
|------|-------|
| `FLASK_SECRET_KEY` | `change-this-to-random-string-abc123` |
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | `sqlite:///instance/practice.db` |
| `MAX_CODE_EXECUTION_TIME` | `3` |
| `MAX_MEMORY_MB` | `50` |

#### Networking

**Add Port:**
- **Container Port**: `5067`
- **Node Port**: `5067`
- **Protocol**: `TCP`

#### Storage

**Host Path Volumes** - Click **Add** for each:

**Volume 1 - Application Files:**
- **Host Path**: `/mnt/YOUR_POOL/c-practice/app/7_imperative_exam`
- **Mount Path**: `/app`
- **Read Only**: ❌ (unchecked)

**Volume 2 - Database/Instance:**
- **Host Path**: `/mnt/YOUR_POOL/c-practice/data`
- **Mount Path**: `/app/instance`
- **Read Only**: ❌ (unchecked)

#### Resources (Optional but Recommended)

**CPU Limit:**
```
2
```

**Memory Limit:**
```
2Gi
```

#### Security

**Privileged Mode**: ❌ Leave unchecked

**Capabilities**: Leave default

3. **Deploy:**
   - Scroll to bottom
   - Click **Install**
   - Wait for deployment (2-5 minutes for first time)

### Step 4: Verify Deployment

1. **Check App Status:**
   - Go to **Apps** → **Installed**
   - You should see `c-programming-practice` with status **Running**

2. **View Logs:**
   - Click the app name
   - Click **Logs** button
   - You should see Flask starting up

3. **Access the Application:**
   - Open browser: `http://YOUR_TRUENAS_IP:5067`
   - You should see the login/register page

---

## Method 2: Using Docker Compose via Apps (Alternative)

TrueNAS SCALE 24.10 can also run docker-compose directly!

### Step 1: Prepare Files (Same as Method 1, Steps 1-2)

### Step 2: Enable SSH and Deploy

```bash
# SSH to TrueNAS
ssh root@YOUR_TRUENAS_IP

# Navigate to app directory
cd /mnt/YOUR_POOL/c-practice/app/7_imperative_exam

# Run deployment script
./deploy.sh

# Or manually with docker-compose
docker-compose up -d
```

This uses the native Docker that comes with SCALE!

---

## Method 3: Using Portainer (Advanced Users)

### Step 1: Install Portainer from Apps

1. Go to **Apps** → **Discover Apps**
2. Search for "**Portainer**"
3. Click **Install**
4. Configure:
   - **Web Port**: `9000`
   - **Storage**: Create dataset `/mnt/YOUR_POOL/portainer-data`
5. Click **Install**

### Step 2: Access Portainer

1. Open `http://YOUR_TRUENAS_IP:9000`
2. Create admin account
3. Select **Docker** environment

### Step 3: Deploy Stack

1. Go to **Stacks** → **Add Stack**
2. **Name**: `c-programming-practice`
3. **Web editor** - Paste docker-compose.yml content:

```yaml
version: '3.8'

services:
  c-practice:
    image: python:3.11-slim
    container_name: c-programming-practice
    command: >
      bash -c "apt-get update &&
               apt-get install -y gcc build-essential &&
               cd /app &&
               pip install -r requirements.txt &&
               python app.py"
    ports:
      - "5067:5067"
    volumes:
      - /mnt/YOUR_POOL/c-practice/app/7_imperative_exam:/app
      - /mnt/YOUR_POOL/c-practice/data:/app/instance
    environment:
      - FLASK_SECRET_KEY=change-me-to-random-string
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///instance/practice.db
      - MAX_CODE_EXECUTION_TIME=3
      - MAX_MEMORY_MB=50
    restart: unless-stopped
```

4. Click **Deploy the stack**

---

## Comparison of Methods

| Method | Difficulty | SSH Needed | Best For |
|--------|-----------|------------|----------|
| **Custom App** | ⭐ Easy | ❌ No | Beginners, GUI lovers |
| **Docker Compose** | ⭐⭐ Medium | ✅ Yes | Power users, automation |
| **Portainer** | ⭐⭐⭐ Advanced | ❌ No | Managing multiple containers |

---

## Managing Your App

### Via TrueNAS Apps Interface

**Start/Stop:**
1. Go to **Apps** → **Installed**
2. Click the three dots (⋮) next to your app
3. Select **Start** or **Stop**

**View Logs:**
1. Click the app name
2. Click **Logs** tab
3. See real-time application logs

**Edit Configuration:**
1. Click three dots (⋮)
2. Select **Edit**
3. Modify settings
4. Click **Save** (will restart container)

**Delete:**
1. Click three dots (⋮)
2. Select **Delete**
3. Confirm

### Via SSH (for Docker Compose method)

```bash
ssh root@YOUR_TRUENAS_IP
cd /mnt/YOUR_POOL/c-practice/app/7_imperative_exam

# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Logs
docker-compose logs -f

# Update
git pull  # if using git
docker-compose up -d --build
```

---

## Accessing from Other Devices

### Local Network
Simply use: `http://TRUENAS_IP:5067`

### From Internet (Optional - Requires Router Setup)

1. **Port Forwarding on Router:**
   - Forward external port `5067` → TrueNAS IP `5067`

2. **Use Dynamic DNS** (if home IP changes):
   - Services like No-IP, DuckDNS, or Cloudflare
   - Point domain to your home IP

3. **Access via:**
   - `http://your-domain.com:5067`

**⚠️ Security Warning:** Exposing to internet without HTTPS is not recommended. See Reverse Proxy section below.

---

## Adding HTTPS with Reverse Proxy

### Method: Using NGINX Proxy Manager (Recommended)

1. **Install NGINX Proxy Manager:**
   - Go to **Apps** → **Discover Apps**
   - Search "nginx proxy manager"
   - Install with default settings
   - Access at `http://TRUENAS_IP:81`

2. **Add Proxy Host:**
   - Login (default: `admin@example.com` / `changeme`)
   - Go to **Hosts** → **Proxy Hosts** → **Add Proxy Host**
   - **Domain Names**: `practice.yourdomain.com`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `TRUENAS_IP`
   - **Forward Port**: `5067`
   - Click **Save**

3. **Add SSL Certificate:**
   - Edit the proxy host
   - Go to **SSL** tab
   - Select **Request a new SSL Certificate**
   - Enable **Force SSL**
   - Click **Save**

4. **Access with HTTPS:**
   - `https://practice.yourdomain.com`

---

## Backups

### Method 1: TrueNAS Snapshots (Easiest)

1. **Create Snapshot Task:**
   - Go to **Data Protection** → **Periodic Snapshot Tasks**
   - Click **Add**
   - **Dataset**: Select `c-practice`
   - **Recursive**: ✅ Enabled
   - **Schedule**: Daily at 2:00 AM
   - **Lifetime**: 7 days
   - Click **Save**

### Method 2: Manual Backup

**Via Web UI:**
1. Go to **Storage**
2. Select `c-practice` dataset
3. Click **Create Snapshot** button
4. Name it: `c-practice-backup-DATE`

**Via SSH:**
```bash
# Backup database
cd /mnt/YOUR_POOL/c-practice/data
cp practice.db practice.db.backup-$(date +%Y%m%d)

# Or backup entire dataset
tar -czf /mnt/YOUR_POOL/backups/c-practice-$(date +%Y%m%d).tar.gz \
  /mnt/YOUR_POOL/c-practice/
```

### Restore from Snapshot

1. Go to **Storage**
2. Select dataset → **Snapshots**
3. Find snapshot → Click **Rollback**
4. Confirm
5. Restart app

---

## Updating Questions

Questions are in the volume, so you can edit them directly:

**Via SMB Share:**
1. Connect to SMB share (from Step 2)
2. Navigate to `7_imperative_exam/questions/`
3. Edit JSON files with any text editor
4. Save
5. Changes take effect immediately (or restart app)

**Via SSH:**
```bash
ssh root@YOUR_TRUENAS_IP
cd /mnt/YOUR_POOL/c-practice/app/7_imperative_exam/questions
nano memory_management.json
# Edit and save
```

**Restart app to reload questions:**
```bash
# Via Apps UI: Stop → Start
# Or via SSH:
docker restart c-programming-practice
```

---

## Monitoring & Performance

### Check App Resources

**Via Apps Interface:**
1. Go to **Apps** → **Installed**
2. Click app name
3. See CPU, Memory, Network stats

**Via SSH:**
```bash
# Container stats
docker stats c-programming-practice

# Detailed info
docker inspect c-programming-practice
```

### View Application Logs

**Via Apps UI:**
1. Click app → **Logs** tab

**Via SSH:**
```bash
docker logs -f c-programming-practice
```

---

## Troubleshooting

### App Won't Start

1. **Check Logs:**
   - Apps → Click app → Logs
   - Look for error messages

2. **Common Issues:**
   - **Port in use**: Change port in configuration
   - **Path not found**: Verify dataset paths are correct
   - **Permission denied**: Check dataset permissions

### Can't Access from Browser

1. **Verify app is running:**
   - Apps → Installed → Check status is "Running"

2. **Test locally on TrueNAS:**
   ```bash
   ssh root@YOUR_TRUENAS_IP
   curl http://localhost:5067
   ```

3. **Check firewall:**
   - TrueNAS SCALE usually has no firewall by default
   - Check your router/network firewall

### Database Errors

1. **Stop app**
2. **Delete database:**
   ```bash
   ssh root@YOUR_TRUENAS_IP
   rm /mnt/YOUR_POOL/c-practice/data/practice.db
   ```
3. **Start app** (will create fresh database)
4. **Register new users**

### GCC Not Working

If C code compilation fails:

1. **Rebuild container:**
   - Stop app
   - Delete app
   - Redeploy (it will reinstall GCC)

2. **Or install manually:**
   ```bash
   docker exec -it c-programming-practice bash
   apt-get update
   apt-get install -y gcc build-essential
   ```

---

## Security Best Practices

### 1. Change Secret Key

Generate secure key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Update in app configuration:
- Edit app → Environment Variables → `FLASK_SECRET_KEY`

### 2. Use HTTPS

Set up NGINX Proxy Manager as shown above.

### 3. Restrict Access

**By IP (if you don't need public access):**
- Only access from local network
- Don't port forward on router

**By Authentication:**
- App requires login by default
- Use strong passwords

### 4. Regular Updates

```bash
# Update application code
cd /mnt/YOUR_POOL/c-practice/app/7_imperative_exam
git pull  # if using git

# Restart app
docker restart c-programming-practice
```

---

## Performance Tuning

### For Many Users (10+ concurrent)

Increase resources in app configuration:

**Edit app → Resources:**
- **CPU Limit**: `4`
- **Memory Limit**: `4Gi`

### Use PostgreSQL Instead of SQLite

For production with many users:

1. **Install PostgreSQL from Apps**

2. **Update app environment:**
   ```
   DATABASE_URL=postgresql://user:pass@postgres-host:5432/practice
   ```

3. **Update requirements.txt:**
   Add `psycopg2-binary`

---

## Quick Reference Card

| Task | How To |
|------|--------|
| **Start app** | Apps → Installed → Click ▶️ |
| **Stop app** | Apps → Installed → Click ⏸️ |
| **View logs** | Apps → Click app name → Logs |
| **Edit config** | Apps → Click ⋮ → Edit |
| **Update code** | Edit files in SMB share → Restart app |
| **Backup** | Storage → Dataset → Create Snapshot |
| **Access app** | `http://TRUENAS_IP:5067` |

---

## Complete Example Walkthrough

### From Zero to Running (15 minutes)

1. **Create dataset:**
   - Storage → Create Dataset → Name: `c-practice`

2. **Upload files via SMB:**
   - Shares → Add SMB share → Point to `c-practice`
   - Connect from Mac
   - Copy project folder

3. **Deploy Custom App:**
   - Apps → Discover → Custom App
   - Fill in:
     - Image: `python:3.11-slim`
     - Command: Install script (see above)
     - Port: `5067:5067`
     - Volume: `/mnt/pool/c-practice/app/7_imperative_exam:/app`
   - Install

4. **Wait for deployment** (2-3 min)

5. **Access:** `http://TRUENAS_IP:5067`

6. **Register user and start practicing!**

---

## Getting Help

**Check logs first:**
- Apps → Click app → Logs

**Test connectivity:**
```bash
ssh root@YOUR_TRUENAS_IP
curl http://localhost:5067
```

**Restart app:**
- Apps → Click ⋮ → Stop → Start

**Nuclear option (fresh start):**
1. Delete app
2. Delete datasets
3. Start over

---

## What's Next?

✅ Deploy the app
✅ Register admin account
✅ Test all question types
✅ Set up HTTPS (optional)
✅ Configure backups
✅ Share with students!

Enjoy your C Programming Practice System on TrueNAS SCALE! 🚀
