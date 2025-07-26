#!/usr/bin/env python
"""Test script for Django with SpatiaLite integration"""

import sys
import os

# Ensure our custom SQLite library is loaded first
os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib:/usr/lib/x86_64-linux-gnu:/usr/lib'

# Set up Django environment  
sys.path.insert(0, '/app/app-classic/find_artek')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'find_artek.settings')

try:
    import django
    from django.conf import settings
    
    print('Django version: ' + django.get_version())
    print('Testing Django spatialite backend...')
    
    # Try to import basic database functionality (avoid GIS imports for now)
    from django.db import connections
    
    print('Django database connections imported successfully')
    print('Database backends configured:')
    for alias, config in settings.DATABASES.items():
        print('  ' + alias + ': ' + config.get("ENGINE", "unknown"))
    
    # Test basic database connection
    default_db = connections['default']
    cursor = default_db.cursor()
    cursor.execute("SELECT sqlite_version()")
    sqlite_version = cursor.fetchone()[0]
    print('SQLite version from Django: ' + sqlite_version)
    
    # Test SpatiaLite loading
    cursor.execute("SELECT spatialite_version()")
    spatialite_version = cursor.fetchone()[0]
    print('SpatiaLite version from Django: ' + spatialite_version)
    
    cursor.close()
    print('SUCCESS: Django can connect and use SpatiaLite!')

except ImportError as e:
    print('ERROR: Could not import Django modules: ' + str(e))
    sys.exit(1)
except Exception as e:
    print('ERROR: Django test failed: ' + str(e))
    sys.exit(1)
