import os
import sqlite3
from kivy.utils import platform


def get_db_path():
    if platform == 'android':
        try:
            # Сначала пробуем найти в папке приложения
            from android.storage import app_storage_path
            db_dir = app_storage_path()
            db_path = os.path.join(db_dir, 'Rieltor.db')

            # Если базы нет, копируем из assets
            if not os.path.exists(db_path):
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                asset_manager = context.getAssets()

                # Читаем базу из assets
                input_stream = asset_manager.open('Rieltor.db')
                with open(db_path, 'wb') as f:
                    f.write(input_stream.read())
                input_stream.close()

            return db_path
        except Exception as e:
            print(f"Error handling DB path on Android: {e}")
            return 'Rieltor.db'
    else:
        return 'Rieltor.db'