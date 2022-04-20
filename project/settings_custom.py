"""
Put your custom settings here, not in settings.py

Settings structure:

- settings.py         : Defaults from Django, do not edit
- settings_ansible.py : Generated by Ansible (not committed)
- settings_custom.py  : Your custom project settings, edit this one
"""

# Standard Library
from socket import getfqdn

# Requirements
from dotenv import load_dotenv

# Project
from project.settings_ansible import *


# Load environment variables
load_dotenv(f'{BASE_DIR}/.envrc')

# Applications
def replace(l, a, b):
    return [b if x == a else x for x in l]

INSTALLED_APPS = replace(INSTALLED_APPS, 'django.contrib.admin', 'apps.myadmin')
INSTALLED_APPS += [
    # Requirements
    'django_vite',
    'strawberry.django',
    # For testing Svelte integration
    'apps.boot',
    'apps.demo',
]

# Static files
STATICFILES_DIRS = [
    BASE_DIR / 'project' / 'static',
]

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'project' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Emails
ADMINS = ()
MANAGERS = ADMINS

fqdn = getfqdn()
DEFAULT_FROM_EMAIL = 'webmaster@' + fqdn
SERVER_EMAIL = 'root@' + fqdn

# Vite
DJANGO_VITE_ASSETS_PATH = BASE_DIR / 'project' / 'static' / 'build'
DJANGO_VITE_DEV_MODE = DEBUG
