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

            # Копируем базу из assets если её нет
            if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
                Logger.info(f"Database: Копирую базу в {db_path}")
                copy_db_from_assets(db_name, db_path)

            return db_path
        except Exception as e:
            Logger.error(f"Database: Ошибка на Android: {str(e)}")
            return db_name  # запасной вариант
    else:
        return db_name


def copy_db_from_assets(db_name, db_path):
    """Копирует базу из assets"""
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        asset_manager = context.getAssets()

        input_stream = asset_manager.open(db_name)
        with open(db_path, 'wb') as f:
            while True:
                chunk = input_stream.read(1024)
                if not chunk:
                    break
                f.write(chunk)
        input_stream.close()
        Logger.info("Database: База успешно скопирована")
    except Exception as e:
        Logger.error(f"Database: Ошибка копирования: {str(e)}")
        raise  # Перебрасываем исключение


def get_db_connection():
    """Создает соединение с базой с обработкой ошибок"""
    db_path = get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        # Проверяем что это валидная база
        conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return conn
    except sqlite3.Error as e:
        Logger.error(f"Database: Ошибка открытия базы {db_path}: {str(e)}")
        if platform == 'android':
            # Пробуем восстановить базу
            try:
                os.remove(db_path)
                copy_db_from_assets('Rieltor.db', db_path)
                return sqlite3.connect(db_path)
            except Exception as e:
                Logger.error(f"Database: Восстановление не удалось: {str(e)}")
                raise
        raise

Logger.info(f"Путь к базе: {get_db_path()}")
Logger.info(f"База существует: {os.path.exists(get_db_path())}")
Logger.info(f"Размер базы: {os.path.getsize(get_db_path())}")
