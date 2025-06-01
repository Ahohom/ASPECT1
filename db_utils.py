import os
import sqlite3
from kivy.utils import platform

def get_db_path():
    if platform == 'android':
        try:
            from android.storage import app_storage_path
            db_dir = app_storage_path()
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            return os.path.join(db_dir, 'Rieltor.db')
        except ImportError:
            return 'Rieltor.db'
    else:
        return 'Rieltor.db'