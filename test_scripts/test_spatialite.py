import sqlite3

# Create connection
conn = sqlite3.connect(':memory:')

# Test if we can enable extension loading
try:
    conn.enable_load_extension(True)
    print('SUCCESS: enable_load_extension works!')
    
    # Try to load SpatiaLite
    try:
        conn.load_extension('/usr/local/lib/libspatialite.so')
        print('SUCCESS: SpatiaLite loaded via load_extension!')
        
        # Test a spatial function
        result = conn.execute('SELECT spatialite_version()').fetchone()
        print('SpatiaLite version:', result[0])
        
    except Exception as e:
        print('FAILED to load via load_extension:', e)
        
except AttributeError as e:
    print('FAILED: enable_load_extension not available:', e)
    
except Exception as e:
    print('FAILED: enable_load_extension error:', e)

# Try alternative approach - direct loading
try:
    conn.load_extension('/usr/local/lib/libspatialite.so', 'sqlite3_modSpatiaLite_init')
    print('SUCCESS: SpatiaLite loaded via modSpatiaLite_init!')
    result = conn.execute('SELECT spatialite_version()').fetchone()
    print('SpatiaLite version:', result[0])
except Exception as e:
    print('FAILED modSpatiaLite_init:', e)

conn.close()
