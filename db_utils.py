import os
import sqlite3
from kivy.utils import platform
from kivy.logger import Logger
import requests
from kivy.network.urlrequest import UrlRequest  # Альтернатива для Kivy


def get_db_path():
    db_name = 'Rieltor.db'

    if platform == 'android':
        try:
            from android.storage import app_storage_path
            db_dir = app_storage_path()
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, db_name)

            # Если базы нет или она пустая - скачиваем с GitHub
            if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
                Logger.info(f"Database: Загружаю базу с GitHub...")
                download_db_from_github(db_path)

            return db_path
        except Exception as e:
            Logger.error(f"Database: Ошибка на Android: {str(e)}")
            return db_name  # запасной вариант
    else:
        # Для десктопной версии используем локальную базу
        return db_name


def download_db_from_github(db_path):
    """Скачивает базу данных с GitHub"""
    try:
        # Прямая ссылка на raw-версию файла в GitHub
        db_url = "https://github.com/Ahohom/ASPECT1/raw/main/Rieltor.db"

        Logger.info(f"Database: Начинаю загрузку с {db_url}")

        # Вариант 1: Используем requests (более надежный)
        response = requests.get(db_url, stream=True)
        if response.status_code == 200:
            with open(db_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB chunks
                    if chunk:
                        f.write(chunk)
            Logger.info(f"Database: Успешно загружено {os.path.getsize(db_path)} байт")
        else:
            raise Exception(f"HTTP ошибка: {response.status_code}")

    except Exception as e:
        Logger.error(f"Database: Ошибка загрузки: {str(e)}")
        raise


def get_db_connection():
    """Создает соединение с базой с обработкой ошибок"""
    db_path = get_db_path()
    max_retries = 3
    retry_delay = 1  # секунда

    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(db_path)
            # Проверяем что это валидная база
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            Logger.info("Database: Соединение с базой установлено")
            return conn

        except sqlite3.Error as e:
            Logger.error(f"Database: Попытка {attempt + 1}: Ошибка открытия базы: {str(e)}")

            if attempt == max_retries - 1:
                Logger.error("Database: Все попытки подключения провалились")
                raise

            # Удаляем поврежденную базу и пробуем снова
            if platform == 'android':
                try:
                    if os.path.exists(db_path):
                        os.remove(db_path)
                        Logger.info("Database: Удалена поврежденная база")
                    download_db_from_github(db_path)
                except Exception as e:
                    Logger.error(f"Database: Ошибка восстановления: {str(e)}")
                    raise

            import time
            time.sleep(retry_delay)


# Тестовый вывод информации о базе
if __name__ == "__main__":
    try:
        db_path = get_db_path()
        Logger.info(f"Database: Путь к базе: {db_path}")
        Logger.info(f"Database: База существует: {os.path.exists(db_path)}")
        if os.path.exists(db_path):
            Logger.info(f"Database: Размер базы: {os.path.getsize(db_path)} байт")

        # Тест подключения
        conn = get_db_connection()
        if conn:
            Logger.info("Database: Тест подключения успешен")
            conn.close()
    except Exception as e:
        Logger.error(f"Database: Критическая ошибка: {str(e)}")
