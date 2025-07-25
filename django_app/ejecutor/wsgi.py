"""
WSGI config for ejecutor project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'django_app'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ejecutor.settings')

application = get_wsgi_application()
