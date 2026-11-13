"""
Gunicorn configuration for Dr. Mohammed Ahmed Al-Sayyad Medical Website & Clinic Management System.
"""
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2

# Logging
accesslog = "/var/log/gunicorn/alsayyad_access.log"
errorlog = "/var/log/gunicorn/alsayyad_error.log"
loglevel = "info"

# Security & Process Naming
proc_name = "alsayyad_clinic_gunicorn"
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

