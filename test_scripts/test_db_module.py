#!/usr/bin/env python
"""Test script for Django database module selection"""

import os
import sys

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'django.conf.global_settings'

try:
    from pysqlite2 import dbapi2 as Database
    print('Django will use pysqlite2')
    print('Database API version: ' + Database.apilevel)
    print('Thread safety: ' + str(Database.threadsafety))
except ImportError:
    print('Fallback to sqlite3')
    import sqlite3 as Database

print('Final Database module: ' + Database.__name__)
