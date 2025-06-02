from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField, MDTextFieldHelperText
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
import sqlite3
from kivymd.uix.dialog import MDDialog
from db_utils import get_db_path, get_session_path
from kivymd.app import MDApp

class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]  # Белый фон
        self.error_label = None  # Для хранения ссылки на метку ошибки
        self.build_ui()

    def build_ui(self):
        # Метка для ошибки (изначально скрыта)
        self.error_label = MDLabel(
            text="Логин или пароль не совпадают, попробуйте ещё раз",
            pos_hint={'center_x': 0.5, 'center_y': 0.7},
            size_hint_x=0.8,
            theme_text_color="Error",
            halign="center",
            opacity=0  # Начальная прозрачность 0 (невидима)
        )
        self.add_widget(self.error_label)

        # Метка для поля логина (смещена ниже из-за добавления error_label)
        login_label = MDLabel(
            text="Логин:",
            pos_hint={'center_x': 0.5, 'center_y': 0.64},
            size_hint_x=0.8,
            theme_text_color="Primary"
        )
        self.add_widget(login_label)

        self.login_input = MDTextField(
            hint_text="Введите логин",
            pos_hint={'center_x': 0.5, 'center_y': 0.58},
            size_hint_x=0.8
        )
        self.login_input.add_widget(MDTextFieldHelperText(
            text="Пример: user123",
            mode="on_focus"
        ))

        # Метка для поля пароля
        password_label = MDLabel(
            text="Пароль:",
            pos_hint={'center_x': 0.5, 'center_y': 0.48},
            size_hint_x=0.8,
            theme_text_color="Primary"
        )
        self.add_widget(password_label)

        self.password_input = MDTextField(
            hint_text="Введите пароль",
            password=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.42},
            size_hint_x=0.8
        )
        self.password_input.add_widget(MDTextFieldHelperText(
            text="Минимум 6 символов",
            mode="on_focus"
        ))

        # Кнопка "Войти"
        self.login_button = MDButton(
            MDButtonText(
                text="Войти",
            ),
            style="outlined",
            pos_hint={'center_x': 0.5, 'center_y': 0.25},
            size_hint=(None, None),
            width=dp(300),
            height=dp(40),
            on_release=self.login
        )

        # Кнопка "Регистрация"
        self.register_button = MDButton(
            MDButtonText(
                text="Регистрация",
            ),
            style="outlined",
            pos_hint={'center_x': 0.5, 'center_y': 0.15},
            size_hint=(None, None),
            width=dp(300),
            height=dp(40),
            on_release=self.go_to_register
        )

        self.add_widget(self.login_input)
        self.add_widget(self.password_input)
        self.add_widget(self.login_button)
        self.add_widget(self.register_button)

    def login(self, *args):
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE login=? AND password_hash=?",
                  (self.login_input.text, self.password_input.text))
        user = c.fetchone()
        conn.close()

        if user:
            self.error_label.opacity = 0
            app = MDApp.get_running_app()  # Получаем экземпляр приложения
            app.current_user = {
                'id': user[0],
                'role_id': user[5]
            }
            # Записываем сессию
            session_file = get_session_path()
            with open(session_file, "w") as f:
                f.write(str(user[0]))

            # Обновляем зависимые экраны через приложение
            app.update_user_dependent_screens()
            self.manager.current = 'apartments'
        else:
            self.error_label.opacity = 1
            from kivy.animation import Animation
            anim = Animation(opacity=1, duration=0.3) + Animation(opacity=0.8, duration=0.1) + Animation(opacity=1,
                                                                                                         duration=0.1)
            anim.start(self.error_label)

    def go_to_register(self, *args):
        """Переключает на экран регистрации."""
        self.error_label.opacity = 0  # Скрываем сообщение об ошибке при переходе
        self.manager.current = 'register'