"""
WSGI config for ecommerce project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

# application = get_wsgi_application()
import sys
import os

# Replace with your path
path = '/home/balajibalajik/Django_Ecommerce'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ecommerce.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
