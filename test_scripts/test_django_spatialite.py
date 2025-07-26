#!/usr/bin/env python
import os
import sys
sys.path.insert(0, '/app')
os.environ['DJANGO_SETTINGS_MODULE'] = 'find_artek.settings'

import django
from django.conf import settings

print("Django version:", django.VERSION)
print("Settings configured:", settings.configured)

# Test database connection
from django.db import connection
print('Database backend:', connection.settings_dict['ENGINE'])
print('Database file:', connection.settings_dict['NAME'])

# Test database connection
cursor = connection.cursor()
cursor.execute('SELECT sqlite_version()')
version = cursor.fetchone()[0]
print('Connected to SQLite version:', version)

# Test if spatialite extension can be loaded
try:
    cursor.execute('SELECT load_extension("spatialite")')
    print('SpatiaLite extension loaded successfully!')
    cursor.execute('SELECT spatialite_version()')
    spatialite_version = cursor.fetchone()[0]
    print('SpatiaLite version:', spatialite_version)
    print('SUCCESS: SpatiaLite is working!')
except Exception as e:
    print('SpatiaLite test failed:', str(e))
    print('Error type:', type(e).__name__)
