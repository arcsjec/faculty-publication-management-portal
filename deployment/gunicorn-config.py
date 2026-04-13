# Gunicorn Configuration File for SJEC Publications Portal
# Place this in: /opt/sjec-publications/gunicorn_config.py

import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = 3
worker_class = "sync"
worker_connections = 1000
threads = 2
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "sjecportal"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn/sjecportal.pid"
user = "SJEC"
group = "SJEC"
umask = 0o007

# SSL (for future HTTPS support)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Server hooks
def on_starting(server):
    print("🚀 SJEC Publications Portal starting...")

def on_reload(server):
    print("🔄 Reloading SJEC Publications Portal...")

def when_ready(server):
    print("✅ SJEC Publications Portal is ready!")
    print(f"   Workers: {workers}")
    print(f"   Listening on: {bind}")

def on_exit(server):
    print("👋 SJEC Publications Portal shutting down...")
