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

from screens.favourites_screen import FavouritesScreen
from screens.login_screen import LoginScreen
from screens.profile_screen import ProfileScreen
from screens.register_screen import RegisterScreen
from screens.apartments_screen import ApartmentsScreen
from screens.realtor_constructor_screen import RealtorConstructorScreen
import os
from kivy.utils import platform
from db_utils import get_db_path, get_db_connection
#Для пк
Window.size = (360, 640)

try:
    from android.storage import app_storage_path
    from jnius import autoclass
except ImportError:
    # Заглушки для разработки на ПК
    app_storage_path = None
    autoclass = lambda x: None

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
            from android.storage import app_storage_path
            db_dir = app_storage_path()
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            return os.path.join(db_dir, 'Rieltor.db')
        except ImportError:
            # Заглушка для разработки на ПК
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

        # Создаем меню
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
        # Загружаем KV-строку
        Builder.load_string(KV)
        #Размер экрана Для андройда----------------
        #Window.size = (Window.width, Window.height)
        #Window.fullscreen = 'auto'
        #------------------------------------------
        # Создаем главный макет
        self.root_layout = MDFloatLayout()

        # Создаем ScreenManager
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(ApartmentsScreen(name='apartments'))
        self.sm.add_widget(FavouritesScreen(name='favourites'))
        self.sm.add_widget(ProfileScreen(name='profile'))

        if self.current_user:
            self.sm.add_widget(RealtorConstructorScreen(name='realtor_constructor'))

        # Создаем Navigation Bar - изначально невидимый
        self.nav_bar = MDNavigationBar(
            size_hint=(1, None),
            height=dp(30),
            pos_hint={'center_x': 0.5, 'y': 0},
            md_bg_color=(0.95, 0.95, 0.95, 1),
            elevation=1,
            opacity=0,  # Изначально невидим
            disabled=True,  # Изначально отключен

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

        # Добавляем виджеты в корневой макет
        self.root_layout.add_widget(self.sm)
        self.root_layout.add_widget(self.nav_bar)

        # Привязываем обработчик изменения экрана
        self.sm.bind(current=self.on_current_screen)

        return self.root_layout

    def on_current_screen(self, instance, value):
        """Обработчик изменения текущего экрана - управляет видимостью Navigation Bar"""
        # Список экранов, где не нужно показывать Navigation Bar
        hidden_screens = ['login', 'register']

        if value in hidden_screens:
            self.nav_bar.opacity = 0
            self.nav_bar.disabled = True
        else:
            self.nav_bar.opacity = 1
            self.nav_bar.disabled = False

    def set_screen(self, screen_name):
        """Метод для переключения экранов"""
        if screen_name in self.sm.screen_names:
            self.sm.current = screen_name

    def on_start(self):
        if self.check_saved_session():
            self.sm.current = 'apartments'
            if 'realtor_constructor' not in self.sm.screen_names and self.current_user:
                self.sm.add_widget(RealtorConstructorScreen(name='realtor_constructor'))

    def check_saved_session(self):
        try:
            with open("session.txt", "r") as f:
                user_id = f.read().strip()
                conn = sqlite3.connect('Rieltor.db')
                c = conn.cursor()
                c.execute("SELECT id, role_id FROM users WHERE id=?", (user_id,))
                user = c.fetchone()
                conn.close()
                if user:
                    self.current_user = {'id': user[0], 'role_id': user[1]}
                    return True
        except:
            return False
        return False

    def logout(self, *args):
        self.current_user = None
        try:
            os.remove("session.txt")
        except:
            pass
        self.sm.current = 'login'

    def goto_apartments(self, nav_drawer):
        self.sm.current = 'apartments'
        nav_drawer.set_state("close")

    def goto_profile(self, nav_drawer):
        self.sm.current = 'profile'
        nav_drawer.set_state("close")

    def goto_realtor_constructor(self, nav_drawer):
        if self.current_user and self.current_user['role_id'] in [1, 3]:
            self.sm.current = 'realtor_constructor'
            nav_drawer.set_state("close")

    def goto_favorites(self, nav_drawer):
        self.sm.current = 'favorites'
        nav_drawer.set_state("close")

    def goto_users(self, nav_drawer):
        if self.current_user and self.current_user['role_id'] == 1:
            self.sm.current = 'users'
            nav_drawer.set_state("close")

    def goto_settings(self, nav_drawer):
        self.sm.current = 'settings'
        nav_drawer.set_state("close")

    def open_menu(self, button):
        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, text_item):
        self.menu.dismiss()
        MDSnackbar(text=text_item).open()


if __name__ == '__main__':
    AspectApp().run()
