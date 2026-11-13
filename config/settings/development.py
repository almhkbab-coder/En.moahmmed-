from .base import *

DEBUG = True

# In local development, if postgres isn't running or encounters errors, provide graceful database fallback option
# But our base.py already points to PostgreSQL configured in .env

