# Quick Start - Ubuntu Deployment

## 📋 Prerequisites
- Ubuntu 24.04 Desktop installed
- Internet connection
- IP: 192.168.111.79 (already configured)
- User: SJEC

---

## 🚀 Quick Deployment Steps

### 1️⃣ On Ubuntu: Initial Setup (5 minutes)

```bash
# Transfer the setup script to Ubuntu
# Then run:
cd /tmp
sudo bash setup_ubuntu.sh
```

### 2️⃣ Transfer Files from Windows (2 minutes)

**Option A - Using SCP (from Windows PowerShell):**
```powershell
scp -r "C:\Users\shalt\.vscode\ProgramFiles\Faculty Publication Portal" SJEC@192.168.111.79:/tmp/portal/
```

**Option B - Using USB drive:**
- Copy entire project folder to USB
- Mount on Ubuntu and copy to `/tmp/portal/`

### 3️⃣ On Ubuntu: Move Files & Configure (3 minutes)

```bash
# Move to final location
sudo mkdir -p /opt/sjec-publications
sudo cp -r /tmp/portal/* /opt/sjec-publications/
sudo chown -R SJEC:SJEC /opt/sjec-publications

# Run configuration
cd /opt/sjec-publications
sudo bash deployment/configure_services.sh
```

### 4️⃣ Test Access (1 minute)

Open browser on any device on Staff WiFi:
- `http://publications.local`
- `http://192.168.111.79`

---

## ✅ That's It! Portal is Live!

### Daily Usage:

**Check Status:**
```bash
bash deployment/manage.sh status
```

**View Logs:**
```bash
bash deployment/manage.sh logs
```

**Restart Service:**
```bash
bash deployment/manage.sh restart
```

**Create Backup:**
```bash
bash deployment/manage.sh backup
```

---

## 🔄 Updating Code from Windows

### Via VS Code Remote SSH:
1. Open VS Code
2. Connect to `SJEC@192.168.111.79`
3. Edit files directly
4. In terminal: `sudo systemctl restart sjecportal`

### Via SSH Command Line:
```bash
ssh SJEC@192.168.111.79
cd /opt/sjec-publications
# Edit files
sudo systemctl restart sjecportal
```

---

## 📞 Need Help?

See full guide: `deployment/DEPLOYMENT_GUIDE.md`

Contact:
- testpublicationportal@gmail.com
- 23g56.shalton@sjec.ac.in
- 23g31.luke@sjec.ac.in
