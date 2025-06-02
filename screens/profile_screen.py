from kivymd.uix.screen import MDScreen
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem, MDNavigationItemIcon
from kivy.metrics import dp
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.utils import platform
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelHeader, MDExpansionPanelContent
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
import sqlite3
import os
from kivy.uix.image import Image
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from db_utils import get_db_path, get_session_path

class ProfileScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]
        self.build_ui()

    def build_ui(self):
        self.main_layout = MDFloatLayout()

        # Карточка пользователя
        user_card = MDCard(
            size_hint=(0.9, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.94},
            radius=[15],
            elevation=2
        )

        user_data = self.get_user_data()
        user_info_layout = MDFloatLayout()

        profile_icon = MDListItemLeadingIcon(
            icon="account",
            theme_icon_color="Custom",
            icon_color=(0.26, 0.63, 0.28, 1),
            pos_hint={'center_x': 0.1, 'center_y': 0.55}
        )

        full_name = MDLabel(
            text=user_data.get('full_name', "Неизвестный пользователь") if user_data else "Неизвестный пользователь",
            pos_hint={'center_x': 0.6, 'center_y': 0.7},
            size_hint_x=0.8,
            font_size="20sp",
            bold=True
        )

        phone = MDLabel(
            text=user_data.get('phone', "Телефон не указан") if user_data else "Телефон не указан",
            pos_hint={'center_x': 0.6, 'center_y': 0.3},
            size_hint_x=0.8,
            font_size="16sp"
        )

        user_info_layout.add_widget(profile_icon)
        user_info_layout.add_widget(full_name)
        user_info_layout.add_widget(phone)
        user_card.add_widget(user_info_layout)
        self.main_layout.add_widget(user_card)

        # Меню
        menu_items = [
            {"text": "Политика конфиденциальности", "icon": "shield-lock",
             "on_release": lambda x: self.open_screen("privacy")},
            {"text": "Страхование имущества", "icon": "home", "on_release": lambda x: self.open_screen("insurance")},
            {"text": "FAQ - Частые вопросы", "icon": "help-circle", "on_release": lambda x: self.open_screen("faq")},
            {"text": "О приложении", "icon": "information", "on_release": lambda x: self.open_screen("about")}
        ]

        for i, item in enumerate(menu_items):
            list_item = MDListItem(
                MDListItemLeadingIcon(icon=item["icon"]),
                MDListItemHeadlineText(text=item["text"]),
                pos_hint={'center_x': 0.5, 'top': 0.83 - i * 0.1},
                size_hint=(0.9, None),
                height=dp(56),
                on_release=item["on_release"]
            )
            self.main_layout.add_widget(list_item)

        logout_button = MDButton(
            MDButtonText(text="Выйти из аккаунта", theme_text_color="Custom", text_color=(1, 0, 0, 1)),
            MDListItemLeadingIcon(icon="logout", theme_icon_color="Custom", icon_color=(1, 0, 0, 1)),
            style="text",
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
            size_hint=(0.9, None),
            height=dp(40),
            on_release=self.logout
        )
        self.main_layout.add_widget(logout_button)

        self.add_widget(self.main_layout)

    def get_user_data(self):
        try:
            session_file = get_session_path()
            with open(session_file, 'r') as f:
                user_id = f.read().strip()
                if user_id:
                    conn = sqlite3.connect(get_db_path())
                    c = conn.cursor()
                    c.execute("SELECT full_name, phone FROM users WHERE id=?", (user_id,))
                    user = c.fetchone()
                    conn.close()
                    if user:
                        return {'full_name': str(user[0]), 'phone': str(user[1])}
        except Exception as e:
            print(f"Error getting user data: {e}")
        return None

    def open_screen(self, screen_type):
        if not self.manager.has_screen(screen_type):
            if screen_type == "privacy":
                self.manager.add_widget(PrivacyPolicyScreen(name=screen_type))
            elif screen_type == "insurance":
                self.manager.add_widget(PropertyInsuranceScreen(name=screen_type))
            elif screen_type == "about":
                self.manager.add_widget(AboutAppScreen(name=screen_type))
            elif screen_type == "faq":
                self.manager.add_widget(FAQScreen(name=screen_type))
        self.manager.current = screen_type

    def logout(self, *args):
        try:
            session_file = get_session_path()
            with open(session_file, 'w') as f:
                f.write('')
        except Exception as e:
            print(f"Error clearing session: {e}")
        self.manager.current = 'login'

class AboutAppScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]
        self.build_ui()

    def build_ui(self):
        layout = MDFloatLayout()

        # Кнопка назад с иконкой стрелки в левом верхнем углу
        back_button = MDIconButton(
            icon="arrow-left",
            pos_hint={'x': 0.02, 'top': 0.98},
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=lambda x: setattr(self.manager, 'current', 'profile')
        )

        title = MDLabel(
            text="О приложении:",
            pos_hint={'center_x': 0.5, 'top': 1.446},
            font_size="24sp",
            halign="center",
            bold=True
        )

        content = MDLabel(
            text="Версия приложения: \n\nBeta 0.5.1\n\nИдентификатор сборки: \n\n1206334\n\nООО'АСПЕКТ'все права защищены©",
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.9, 0.7),
            halign="center",
            font_size="16sp"
        )

        layout.add_widget(back_button)
        layout.add_widget(title)
        layout.add_widget(content)
        self.add_widget(layout)

class PrivacyPolicyScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]
        self.build_ui()

    def build_ui(self):
        layout = MDFloatLayout()
        privacy_policy_text = """
ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ
приложения "Аспект" для поиска недвижимости

1. Общие положения
1.1. Приложение "Аспект" (далее - Приложение) предназначено для помощи пользователям в поиске жилой недвижимости (квартир) для аренды или покупки, с возможностью связи с ответственными риелторами.
1.2. Используя Приложение, вы соглашаетесь с условиями данной Политики конфиденциальности.

2. Собираемые данные
2.1. При регистрации мы собираем:
- Фамилию, имя, отчество
- Номер телефона
- Логин и пароль (хранится в зашифрованном виде)
2.2. В процессе использования:
- История просмотров квартир
- Избранные объявления
- Данные о взаимодействии с риелторами

3. Цели использования данных
3.1. Данные используются для:
- Предоставления доступа к функционалу Приложения
- Персонализации пользовательского опыта
- Связи с риелторами по выбранным объявлениям
- Улучшения качества сервиса
- Информирования о новых предложениях (только с согласия пользователя)

4. Защита данных
4.1. Мы применяем следующие меры защиты:
- Шифрование передаваемых данных
- Защищенные соединения (HTTPS)
- Ограниченный доступ к персональным данным
- Регулярное обновление систем безопасности

5. Передача данных третьим лицам
5.1. Ваши данные могут передаваться:
- Риелторам, отвечающим за конкретные объявления, которые вас заинтересовали
- Техническим сервис-провайдерам для обеспечения работы Приложения
5.2. Мы не продаем и не передаем данные в рекламные сети без вашего согласия.

6. Хранение данных
6.1. Данные хранятся:
- На защищенных серверах
- В течение срока, необходимого для целей их обработки
- До момента удаления вашего аккаунта

7. Права пользователей
7.1. Вы имеете право:
- Запросить доступ к своим данным
- Внести изменения в данные
- Удалить свой аккаунт
- Отозвать согласие на обработку данных

8. Контакты
8.1. По вопросам обработки данных обращайтесь:
Email: privacy@aspekt-app.ru
Телефон: +7 (999) 445-23-39 

Дата последнего обновления: 12.05.2025

ООО'АСПЕКТ'все права защищены© 2025г.
        """

        # Кнопка назад с иконкой стрелки
        back_button = MDIconButton(
            icon="arrow-left",
            pos_hint={'x': 0.02, 'top': 0.98},
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=lambda x: setattr(self.manager, 'current', 'profile')
        )

        title = MDLabel(
            text="Политика конфиденциальности",
            pos_hint={'center_x': 0.5, 'top': 1.446},
            font_size="24sp",
            halign="center",
            bold=True
        )

        # Создаем контейнер для текста с прокруткой
        scroll_container = MDScrollView(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.98, 0.8)
        )

        content = MDLabel(
            text=privacy_policy_text,
            size_hint_y=None,
            height=dp(1880),  # Примерная высота для всего текста
            halign="left",
            valign="top",
            padding=(20, 30),
            font_size="12sp"
        )

        scroll_container.add_widget(content)

        layout.add_widget(back_button)
        layout.add_widget(title)
        layout.add_widget(scroll_container)
        self.add_widget(layout)

class PropertyInsuranceScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]
        self.build_ui()


    def build_ui(self):
        layout = MDFloatLayout()
        insurance_text = """
УСЛУГИ СТРАХОВАНИЯ ИМУЩЕСТВА
от компании "Аспект"

1. Наши страховые продукты

1.1. Страхование квартиры:
- Полная защита от повреждений
- Защита от затопления, пожара, стихийных бедствий
- Страхование отделки и инженерных коммуникаций
- Защита от противоправных действий третьих лиц

1.2. Страхование гражданской ответственности:
- На случай причинения вреда соседям
- При аренде жилья

2. Преимущества страхования у нас

2.1. Специальные условия для клиентов приложения:
- Скидка 15% при оформлении онлайн
- Быстрое оформление - от 15 минут
- Гибкие тарифные планы

2.2. Дополнительные сервисы:
- Консультация по снижению страховых рисков
- Помощь в оценке стоимости имущества
- Круглосуточная поддержка клиентов

3. Как оформить страховку

3.1. Процедура оформления:
1. Выберите тип страховки в приложении
2. Заполните простую форму
3. Получите индивидуальный расчет
4. Оплатите удобным способом
5. Получите полис на email

4. Условия выплат

4.1. Мы гарантируем:
- Прозрачные условия договора
- Быстрое рассмотрение страховых случаев
- Выплаты в течение 10 рабочих дней после предоставления всех документов

5. Наши партнеры

5.1. Мы сотрудничаем с ведущими страховыми компаниями:
- СОГАЗ
- АльфаСтрахование
- Ингосстрах
- ВТБ Страхование

6. Контакты

По вопросам страхования:
Телефон: +7 (999) 445-23-39
Email: insurance@aspekt-app.ru

*Подробные условия страхования указаны в договоре.
            """
        # Кнопка назад с иконкой стрелки
        back_button = MDIconButton(
            icon="arrow-left",
            pos_hint={'x': 0.02, 'top': 0.98},
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=lambda x: setattr(self.manager, 'current', 'profile')
        )

        title = MDLabel(
            text="Страхование имущества",
            pos_hint={'center_x': 0.5, 'top': 1.446},
            font_size="24sp",
            halign="center",
            bold=True
        )

        # Создаем контейнер для текста с прокруткой
        scroll_container = MDScrollView(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.98, 0.8)
        )

        content = MDLabel(
            text=insurance_text,
            size_hint_y=None,
            height=dp(1600),  # Подберите высоту под ваш текст
            halign="left",
            valign="top",
            padding=(20, 30),
            font_size="14sp"
        )

        scroll_container.add_widget(content)

        layout.add_widget(back_button)
        layout.add_widget(title)
        layout.add_widget(scroll_container)
        self.add_widget(layout)


class FAQScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]
        self.build_ui()

    def build_ui(self):
        layout = MDFloatLayout()

        # Кнопка назад с иконкой стрелки
        back_button = MDIconButton(
            icon="arrow-left",
            pos_hint={'x': 0.02, 'top': 0.98},
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=lambda x: setattr(self.manager, 'current', 'profile')
        )

        title = MDLabel(
            text="FAQ - Частые вопросы",
            pos_hint={'center_x': 0.5, 'top': 1.446},
            font_size="24sp",
            halign="center",
            bold=True
        )

        # Создаем контейнер для текста с прокруткой
        scroll_container = MDScrollView(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.98, 0.8)
        )

        # Содержимое FAQ
        faq_text = """
1. Как найти подходящую квартиру?
- Используйте фильтры для уточнения параметров
- Сохраняйте понравившиеся варианты в избранное
- В полной информации о квартире указаны все основные характеристики, а так же контакты риелтора который сможет вам помочь 

2. Как связаться с риелтором?
- На экране с полной информацией о квартире указан н.т. отвечающего Риелтора за эту квартиру 
- Позвоните по указанному номеру телефона

3. Как работает страхование имущества?
- Свяжитесь с нами по телефону или email
- Предоставьте почту нашему сотруднику
- Следуйте инструкциям в письме
- Получите полис на email в течение 15 минут

4. Как удалить аккаунт?
- Напишите запрос на support@aspekt-app.ru
- Укажите ваш номер телефона
- Аккаунт будет удален в течение 3 рабочих дней

5. Почему не отображаются контакты риелтора?
- Возможно, требуется обновить приложение
- Проверьте подключение к интернету
- Если проблема сохраняется, напишите в поддержку

6. Как получить скидку на услуги?
- Оформляйте страховку онлайн - скидка 15%
- Приводите друзей - получите бонусы

7. Как восстановить пароль?
- Напишите нам support@aspekt-app.ru
- Следуйте инструкциям в письме

8. Какие гарантии безопасности?
- Все данные передаются по защищенному соединению
- Пароли хранятся в зашифрованном виде
- Мы не передаем ваши данные третьим лицам без согласия

9. Как оставить отзыв?
- Оцените приложение в магазине приложений
- Поделитесь мнением в соцсетях с хештегом #АспектОтзыв

Техническая поддержка:
Телефон: +7 (999) 445-23-39
Email: support@aspekt-app.ru
        """

        content = MDLabel(
            text=faq_text,
            size_hint_y=None,
            height=dp(1600),
            halign="left",
            valign="top",
            padding=(20, 20),
            font_size="14sp"
        )

        scroll_container.add_widget(content)

        layout.add_widget(back_button)
        layout.add_widget(title)
        layout.add_widget(scroll_container)
        self.add_widget(layout)