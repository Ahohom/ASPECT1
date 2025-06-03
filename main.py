from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import MDSnackbar
import sqlite3
from kivy.logger import Logger
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem, MDNavigationItemIcon
from kivy.metrics import dp
import os
from kivy.utils import platform
from kivy.config import Config
from screens.favourites_screen import FavouritesScreen
from screens.login_screen import LoginScreen
from screens.profile_screen import ProfileScreen
from screens.register_screen import RegisterScreen
from screens.apartments_screen import ApartmentsScreen
from screens.realtor_constructor_screen import RealtorConstructorScreen
from db_utils import get_db_path, get_db_connection, get_session_path

# Фиксируем минимальную ширину в 490dp
MIN_WIDTH_DP = 490
TARGET_HEIGHT_DP = 800

# Настройки окна для разных платформ
if platform == 'android':
    try:
        from android.storage import app_storage_path
        from jnius import autoclass
        from android.runnable import run_on_ui_thread
    except ImportError:
        app_storage_path = None
        autoclass = lambda x: None
        run_on_ui_thread = lambda f: f()
else:
    # Настройки для ПК
    Window.size = (dp(MIN_WIDTH_DP), dp(TARGET_HEIGHT_DP))
    Config.set('graphics', 'resizable', False)
    Config.set('graphics', 'width', str(dp(MIN_WIDTH_DP)))
    Config.set('graphics', 'height', str(dp(TARGET_HEIGHT_DP)))

KV = '''
MDNavigationLayout:
    ScreenManager:
        id: screen_manager

        ApartmentsScreen:
            name: 'apartments'

    MDNavigationDrawer:
        id: nav_drawer
        BoxLayout:
            orientation: 'vertical'
            MDTopAppBar:
                title: "Фильтры"
                left_action_items: [["close", lambda x: nav_drawer.set_state("close")]]

            ScrollView:
                MDList:
                    MDListItem:
                        MDListItemLeadingIcon:
                            icon: "city"
                        MDListItemHeadlineText:
                            text: "Город"

                    MDListItem:
                        MDListItemLeadingIcon:
                            icon: "tag"
                        MDListItemHeadlineText:
                            text: "Категория"

                    MDListItem:
                        MDListItemLeadingIcon:
                            icon: "currency-rub"
                        MDListItemHeadlineText:
                            text: "Цена"

<ApartmentsScreen>:
    name: 'apartments'
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Поиск"
            left_action_items: [["menu", lambda x: root.open_navigation_drawer()]]
            right_action_items: [["dots-vertical", lambda x: app.open_menu(x)]]
            elevation: 2

        MDScrollView:
            pos_hint: {'top': 0.95, 'bottom': 0.1}
            do_scroll_x: False
            MDGridLayout:
                id: card_grid
                cols: 2
                padding: 10
                spacing: 10
                size_hint_y: None
                height: self.minimum_height
'''


def get_db_path():
    if platform == 'android':
        try:
            db_dir = app_storage_path()
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            return os.path.join(db_dir, 'Rieltor.db')
        except:
            return 'Rieltor.db'
    else:
        return 'Rieltor.db'


class AspectApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.initialize_database()

        menu_items = [
            {
                "text": f"Item {i}",
                "on_release": lambda x=f"Item {i}": self.menu_callback(x),
            } for i in range(5)
        ]
        self.menu = MDDropdownMenu(items=menu_items)

    def initialize_database(self):
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = c.fetchall()
            Logger.info(f"Database: Найдены таблицы: {tables}")
            conn.close()
        except Exception as e:
            Logger.error(f"Database: Ошибка инициализации: {str(e)}")
            MDSnackbar(text="Ошибка базы данных - переустановите приложение").open()

    def build(self):
        # Создаем корневой макет с масштабированием
        self.root_layout = MDFloatLayout()

        # Настройка масштабирования для маленьких экранов
        self.setup_window_scaling()

        # Загружаем KV-строку
        Builder.load_string(KV)

        # Создаем ScreenManager
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(ApartmentsScreen(name='apartments'))
        self.sm.add_widget(FavouritesScreen(name='favourites'))
        self.sm.add_widget(ProfileScreen(name='profile'))

        if self.current_user:
            self.sm.add_widget(RealtorConstructorScreen(name='realtor_constructor'))

        # Создаем Navigation Bar
        self.nav_bar = MDNavigationBar(
            size_hint=(1, None),
            height=dp(30),
            pos_hint={'center_x': 0.5, 'y': 0},
            md_bg_color=(0.95, 0.95, 0.95, 1),
            elevation=1,
            opacity=0,
            disabled=True
        )

        # Кнопки навигации
        self.nav_item_apartments = MDNavigationItem(
            MDNavigationItemIcon(icon="home"),
            on_release=lambda x: self.set_screen('apartments')
        )
        self.nav_item_favorites = MDNavigationItem(
            MDNavigationItemIcon(icon="heart"),
            on_release=lambda x: self.set_screen('favourites')
        )
        self.nav_item_profile = MDNavigationItem(
            MDNavigationItemIcon(icon="account"),
            on_release=lambda x: self.set_screen('profile')
        )

        self.nav_bar.add_widget(self.nav_item_apartments)
        self.nav_bar.add_widget(self.nav_item_favorites)
        self.nav_bar.add_widget(self.nav_item_profile)

        # Добавляем виджеты
        self.root_layout.add_widget(self.sm)
        self.root_layout.add_widget(self.nav_bar)
        self.sm.bind(current=self.on_current_screen)

        return self.root_layout

    def setup_window_scaling(self):
        if Window.width < dp(MIN_WIDTH_DP):
            scale_factor = Window.width / dp(MIN_WIDTH_DP)
            self.root_layout.scale = (scale_factor, scale_factor)
            self.root_layout.size_hint = (None, None)
            self.root_layout.size = (dp(MIN_WIDTH_DP), Window.height)
            self.root_layout.pos_hint = {'center_x': 0.5}

            if platform == 'android':
                self.fix_android_window_size()

    def fix_android_window_size(self):
        @run_on_ui_thread
        def _fix_android_window_size():
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                activity = PythonActivity.mActivity
                window = activity.getWindow()
                params = window.getAttributes()
                params.width = int(dp(MIN_WIDTH_DP))
                window.setAttributes(params)
            except Exception as e:
                Logger.error(f"Android window size error: {str(e)}")

        _fix_android_window_size()

    def on_current_screen(self, instance, value):
        hidden_screens = ['login', 'register']
        if value in hidden_screens:
            self.nav_bar.opacity = 0
            self.nav_bar.disabled = True
        else:
            self.nav_bar.opacity = 1
            self.nav_bar.disabled = False

    def set_screen(self, screen_name):
        if screen_name in self.sm.screen_names:
            self.sm.current = screen_name

    def on_start(self):
        if self.check_saved_session():
            self.sm.current = 'apartments'
            if 'realtor_constructor' not in self.sm.screen_names and self.current_user:
                self.sm.add_widget(RealtorConstructorScreen(name='realtor_constructor'))

    def check_saved_session(self):
        try:
            session_file = get_session_path()
            if not os.path.exists(session_file):
                return False

            with open(session_file, "r") as f:
                user_id = f.read().strip()
                if not user_id:
                    return False

            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT id, role_id FROM users WHERE id=?", (user_id,))
            user = c.fetchone()
            conn.close()

            if user:
                self.current_user = {'id': user[0], 'role_id': user[1]}
                self.update_user_dependent_screens()
                return True
        except Exception as e:
            Logger.error(f"Session check error: {str(e)}")
        return False

    def update_user_dependent_screens(self):
        if hasattr(self, 'sm'):
            if 'profile' in self.sm.screen_names:
                profile_screen = self.sm.get_screen('profile')
                if hasattr(profile_screen, 'build_ui'):
                    profile_screen.build_ui()

            if 'favourites' in self.sm.screen_names:
                favourites_screen = self.sm.get_screen('favourites')
                if hasattr(favourites_screen, 'load_favorite_apartments'):
                    favourites_screen.load_favorite_apartments()

    def logout(self, *args):
        self.current_user = None
        try:
            session_file = get_session_path()
            if os.path.exists(session_file):
                os.remove(session_file)
        except Exception as e:
            Logger.error(f"Error removing session: {str(e)}")
        self.sm.current = 'login'

    def open_menu(self, button):
        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, text_item):
        self.menu.dismiss()
        MDSnackbar(text=text_item).open()


if __name__ == '__main__':
    AspectApp().run()