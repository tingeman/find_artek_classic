#!/usr/bin/env python
"""
Custom Django spatialite backend that works around missing enable_load_extension
"""
import sys
from ctypes.util import find_library
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.backends.sqlite3.base import (Database,
    DatabaseWrapper as SQLiteDatabaseWrapper, SQLiteCursorWrapper)
from django.contrib.gis.db.backends.spatialite.client import SpatiaLiteClient
from django.contrib.gis.db.backends.spatialite.creation import SpatiaLiteCreation
from django.contrib.gis.db.backends.spatialite.introspection import SpatiaLiteIntrospection
from django.contrib.gis.db.backends.spatialite.operations import SpatiaLiteOperations
from django.utils import six

class DatabaseWrapper(SQLiteDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        # Before we get too far, make sure pysqlite 2.5+ is installed.
        if Database.version_info < (2, 5, 0):
            raise ImproperlyConfigured('Only versions of pysqlite 2.5+ are '
                                       'compatible with SpatiaLite and GeoDjango.')
        
        # Try to find mod_spatialite instead of spatialite
        self.spatialite_lib = getattr(settings, 'SPATIALITE_LIBRARY_PATH', 
                                      '/usr/local/lib/mod_spatialite')
        if not self.spatialite_lib:
            # Fallback to finding libspatialite
            self.spatialite_lib = find_library('spatialite')
        
        if not self.spatialite_lib:
            raise ImproperlyConfigured('Unable to locate the SpatiaLite library. '
                                       'Make sure it is in your library path, or set '
                                       'SPATIALITE_LIBRARY_PATH in your settings.')
        
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.ops = SpatiaLiteOperations(self)
        self.client = SpatiaLiteClient(self)
        self.creation = SpatiaLiteCreation(self)
        self.introspection = SpatiaLiteIntrospection(self)

    def get_new_connection(self, conn_params):
        conn = super(DatabaseWrapper, self).get_new_connection(conn_params)
        
        # Try to enable extension loading if available
        try:
            conn.enable_load_extension(True)
            extension_loading_enabled = True
        except AttributeError:
            # enable_load_extension not available, but we can still try to load extensions
            # This is a workaround for custom compiled Python without enable_load_extension
            extension_loading_enabled = False
            print("Warning: enable_load_extension not available, attempting direct loading")
        
        # Create cursor and try to load SpatiaLite
        cur = conn.cursor(factory=SQLiteCursorWrapper)
        try:
            # Try loading the extension
            cur.execute("SELECT load_extension(%s)", (self.spatialite_lib,))
            print("SpatiaLite extension loaded successfully")
        except Exception as msg:
            if not extension_loading_enabled:
                # If enable_load_extension wasn't available, this might be expected
                # Let's try a different approach or give a more helpful error
                new_msg = (
                    'Unable to load the SpatiaLite library extension '
                    '"%s" because: %s. This might be due to enable_load_extension '
                    'not being available in this Python build. SQLite version: %s'
                    ) % (self.spatialite_lib, msg, Database.sqlite_version)
            else:
                new_msg = (
                    'Unable to load the SpatiaLite library extension '
                    '"%s" because: %s') % (self.spatialite_lib, msg)
            six.reraise(ImproperlyConfigured, ImproperlyConfigured(new_msg), sys.exc_info()[2])
        
        cur.close()
        return conn
