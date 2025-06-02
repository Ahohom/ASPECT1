from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField, MDTextFieldHelperText
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.metrics import dp
import sqlite3
from kivy.animation import Animation
from kivy.properties import NumericProperty
from db_utils import get_db_path,get_session_path
from kivymd.app import MDApp

class PhoneNumberInput(MDTextField):
    max_length = NumericProperty(11)  # Максимальная длина для номера телефона

    def insert_text(self, substring, from_undo=False):
        # Разрешаем ввод только цифр
        if not substring.isdigit():
            return

        # Проверяем максимальную длину
        if len(self.text) + len(substring) > self.max_length:
            return

        return super().insert_text(substring, from_undo)


class RegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]  # Белый фон
        self.error_label = None
        self.password_visible = False  # Флаг видимости пароля
        self.build_ui()

    def build_ui(self):
        # Метка для ошибки (изначально скрыта)
        self.error_label = MDLabel(
            text="",
            pos_hint={'center_x': 0.5, 'center_y': 0.88},
            size_hint_x=0.8,
            theme_text_color="Error",
            halign="center",
            opacity=0,
        )
        self.add_widget(self.error_label)

        # Метка для поля ФИО
        full_name_label = MDLabel(
            text="Фамилия Имя:",
            pos_hint={'center_x': 0.55, 'center_y': 0.825},
            size_hint_x=0.8,
            theme_text_color="Primary"
        )
        self.add_widget(full_name_label)

        self.full_name = MDTextField(
            hint_text="Введите ФИО",
            pos_hint={'center_x': 0.5, 'center_y': 0.77},
            size_hint_x=0.7
        )
        self.full_name.add_widget(MDTextFieldHelperText(
            text="Пример: Иванов Иван",
            mode="on_focus"
        ))

        # Метка для поля логина
        login_label = MDLabel(
            text="Логин:",
            pos_hint={'center_x': 0.5, 'center_y': 0.675},
            size_hint_x=0.7,
            theme_text_color="Primary"
        )
        self.add_widget(login_label)

        self.login = MDTextField(
            hint_text="Введите логин",
            pos_hint={'center_x': 0.5, 'center_y': 0.62},
            size_hint_x=0.7
        )
        self.login.add_widget(MDTextFieldHelperText(
            text="Пример: user123",
            mode="on_focus"
        ))

        # Метка для поля пароля
        password_label = MDLabel(
            text="Пароль:",
            pos_hint={'center_x': 0.5, 'center_y': 0.525},
            size_hint_x=0.7,
            theme_text_color="Primary"
        )
        self.add_widget(password_label)

        # Контейнер для поля пароля и кнопки
        password_container = MDFloatLayout(size_hint_x=0.78)

        self.password = MDTextField(
            hint_text="Введите пароль",
            password=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint_x=0.9,
            on_text=self.on_password_text  # Обработчик изменения текста
        )
        self.password.add_widget(MDTextFieldHelperText(
            text="Минимум 6 символов",
            mode="on_focus"
        ))

        # Кнопка для показа/скрытия пароля
        self.toggle_password_btn = MDIconButton(
            icon="eye-off",
            pos_hint={'center_x': 0.9, 'center_y': 0.5},
            opacity=0,  # Изначально невидима
            on_release=self.toggle_password_visibility
        )

        password_container.add_widget(self.password)
        password_container.add_widget(self.toggle_password_btn)

        # Позиционируем контейнер
        password_container.pos_hint = {'center_x': 0.5, 'center_y': 0.47}
        self.add_widget(password_container)  # Добавляем контейнер на экран

        # Метка для поля телефона
        phone_label = MDLabel(
            text="Телефон:",
            pos_hint={'center_x': 0.5, 'center_y': 0.375},
            size_hint_x=0.7,
            theme_text_color="Primary"
        )
        self.add_widget(phone_label)

        self.phone = PhoneNumberInput(
            hint_text="Введите номер телефона",
            pos_hint={'center_x': 0.5, 'center_y': 0.32},
            size_hint_x=0.7,
        )
        self.phone.add_widget(MDTextFieldHelperText(
            text="Пример: 79991234567",
            mode="on_focus"
        ))

        # Кнопка "Зарегистрироваться"
        self.register_button = MDButton(
            MDButtonText(
                text="Зарегистрироваться",
            ),
            style="outlined",
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            size_hint=(None, None),
            width=dp(300),
            height=dp(40),
            on_release=self.register
        )

        # Кнопка "Назад"
        self.back_button = MDButton(
            MDButtonText(
                text="Назад",
            ),
            style="outlined",
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
            size_hint=(None, None),
            width=dp(300),
            height=dp(40),
            on_release=self.go_to_login
        )

        self.add_widget(self.full_name)
        self.add_widget(self.login)
        self.add_widget(self.phone)
        self.add_widget(self.register_button)
        self.add_widget(self.back_button)

    def on_password_text(self, instance, value):
        """Обработчик изменения текста в поле пароля"""
        print(f"Password text changed: {value}")  # Отладочная печать

        # Показываем/скрываем кнопку в зависимости от наличия текста
        if value.strip():  # Если есть текст (удаляем пробелы)
            anim = Animation(opacity=1, duration=0.2)
            self.toggle_password_btn.disabled = False
        else:  # Если поле пустое
            anim = Animation(opacity=0, duration=0.2)
            self.toggle_password_btn.disabled = True
            # Возвращаем скрытый пароль, если он был показан
            if not self.password.password:
                self.toggle_password_visibility()

        anim.start(self.toggle_password_btn)

    def toggle_password_visibility(self, *args):
        """Переключает видимость пароля"""
        self.password_visible = not self.password_visible
        self.password.password = not self.password_visible
        self.toggle_password_btn.icon = "eye" if self.password_visible else "eye-off"

    def register(self, *args):
        # Сначала скрываем предыдущее сообщение об ошибке
        self.error_label.opacity = 0

        # Проверка заполненности всех полей
        if not all([self.full_name.text, self.login.text, self.password.text, self.phone.text]):
            self.show_error("Все поля должны быть обязательно заполнены")
            return

        # Проверка длины пароля
        if len(self.password.text) < 6:
            self.show_error("Пароль должен состоять не меньше 6 символов")
            return

        # Проверка валидности телефона
        if not self.phone.text.isdigit() or len(self.phone.text) != 11:
            self.show_error("Телефон должен содержать 11 цифр")
            return

        # Проверка уникальности логина и телефона
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()

        try:
            # Проверка уникальности логина
            c.execute("SELECT id FROM users WHERE login=?", (self.login.text,))
            if c.fetchone():
                self.show_error("Пользователь с таким логином уже существует")
                return

            # Проверка уникальности телефона
            c.execute("SELECT id FROM users WHERE phone=?", (self.phone.text,))
            if c.fetchone():
                self.show_error("Пользователь с таким телефоном уже существует")
                return

            # Регистрация пользователя
            c.execute("""
                INSERT INTO users (full_name, login, password_hash, phone, role_id)
                VALUES (?, ?, ?, ?, 2)
            """, (self.full_name.text, self.login.text, self.password.text, self.phone.text))

            user_id = c.lastrowid
            conn.commit()
            conn.close()

            session_file = get_session_path()
            with open(session_file, "w") as f:
                f.write(str(user_id))

            app = MDApp.get_running_app()  # Получаем экземпляр приложения
            app.current_user = {'id': user_id, 'role_id': 2}
            # Обновляем зависимые экраны через приложение
            app.update_user_dependent_screens()
            self.manager.current = 'apartments'

        except Exception as e:
            self.show_error(f"Ошибка при регистрации: {str(e)}")
        finally:
            conn.close()

    def show_error(self, message):
        """Показывает сообщение об ошибке над полем ФИО"""
        self.error_label.text = message
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.error_label)

    def go_to_login(self, *args):
        """Переключает на экран логина."""
        self.error_label.opacity = 0  # Скрываем сообщение об ошибке
        self.manager.current = 'login'