# CompilerX - Gunicorn Production Server Configuration
# This file configures the web server for Render deployment
# You do NOT need to edit this file

import multiprocessing

# Bind to all interfaces on port 10000 (Render's default)
bind = "0.0.0.0:10000"

# Number of worker processes
# Formula: (2 x CPU cores) + 1
workers = 2

# Worker class - sync is stable and simple
worker_class = "sync"

# Timeout in seconds
timeout = 120

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Restart workers after this many requests (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Preload app for faster startup
preload_app = True
