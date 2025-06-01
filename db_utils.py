import os
import sqlite3
from kivy.utils import platform
from kivy.logger import Logger


def get_db_path():
    db_name = 'Rieltor.db'

    if platform == 'android':
        try:
            from android.storage import app_storage_path
            db_dir = app_storage_path()
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, db_name)

            # Если базы нет или она повреждена, копируем из assets
            if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
                Logger.info(f"Database: Copying from assets to {db_path}")

                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                asset_manager = context.getAssets()

                # Читаем базу из assets
                try:
                    input_stream = asset_manager.open(db_name)
                    with open(db_path, 'wb') as f:
                        while True:
                            chunk = input_stream.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    input_stream.close()
                    Logger.info("Database: Copied successfully")
                except Exception as e:
                    Logger.error(f"Database: Error copying from assets: {str(e)}")
                    return db_name  # fallback

            return db_path
        except Exception as e:
            Logger.error(f"Database: Android storage error: {str(e)}")
            return db_name  # fallback
    else:
        return db_name