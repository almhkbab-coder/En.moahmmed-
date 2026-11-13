import os

env_setting = os.getenv('DJANGO_ENV', 'development')
if env_setting == 'production':
    from .production import *
elif env_setting == 'staging' or os.getenv('RENDER'):
    from .staging import *
else:
    from .development import *

