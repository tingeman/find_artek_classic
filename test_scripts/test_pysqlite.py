#!/usr/bin/env python
"""Test script for pysqlite2 with SpatiaLite integration"""

import sys

try:
    from pysqlite2 import dbapi2 as Database
    print('pysqlite2 version: ' + Database.version)
    print('SQLite version: ' + Database.sqlite_version)
    
    conn = Database.connect(':memory:')
    print('enable_load_extension available: ' + str(hasattr(conn, 'enable_load_extension')))
    
    if hasattr(conn, 'enable_load_extension'):
        conn.enable_load_extension(True)
        cursor = conn.cursor()
        cursor.execute('SELECT load_extension(?)', ['/usr/local/lib/mod_spatialite'])
        cursor.execute('SELECT spatialite_version()')
        result = cursor.fetchone()
        print('SpatiaLite version via pysqlite2: ' + result[0])
        print('SUCCESS: pysqlite2 can load SpatiaLite!')
        cursor.close()
        conn.close()
    else:
        print('ERROR: enable_load_extension not available')
        sys.exit(1)

except ImportError as e:
    print('ERROR: Could not import pysqlite2: ' + str(e))
    sys.exit(1)
except Exception as e:
    print('ERROR: Test failed: ' + str(e))
    sys.exit(1)
