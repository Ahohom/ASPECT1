from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivy.metrics import dp
import sqlite3
from kivy.animation import Animation
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon, MDTextFieldHintText, MDTextFieldTrailingIcon
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from io import BytesIO
from PIL import Image as PILImage
import logging
from kivy.graphics import Color, RoundedRectangle
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
import re
logging.basicConfig(level=logging.DEBUG)
import tempfile
import os
from kivy.core.image import Image as CoreImage
from PIL import ImageDraw
from kivymd.uix.swiper import MDSwiper, MDSwiperItem
from kivy.core.window import Window
from kivymd.uix.navigationbar import MDNavigationBar,  MDNavigationItem, MDNavigationItemIcon
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.screen import MDScreen
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivy.clock import Clock
import sqlite3
from kivy.properties import NumericProperty
from kivy.uix.image import Image, AsyncImage
from io import BytesIO
from PIL import Image as PILImage
import tempfile
import os
from kivy.core.image import Image as CoreImage
from PIL import ImageDraw
from kivymd.uix.swiper import MDSwiper, MDSwiperItem
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.stencilview import StencilView
from db_utils import get_db_path

class PhotoSwiper(MDSwiper):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = dp(300)
        self.pos_hint = {'top': 0.9}
        self.current_photos = []
        self.temp_files = []
        self.apartment_id = None

    def load_photos(self, apartment_id):
        """Загружает все фото для конкретной квартиры"""
        if self.apartment_id == apartment_id and self.current_photos:
            return  # Уже загружены

        self.clear_photos()  # Очищаем предыдущие фото
        self.apartment_id = apartment_id

        try:
            conn = sqlite3.connect(get_db_path())
            c = conn.cursor()

            # Загружаем все доступные фото (от 1 до 10)
            for i in range(1, 11):
                c.execute(
                    f"SELECT Photo_{i} FROM apartment_photos WHERE apartment_id = ?",
                    (apartment_id,)
                )
                photo_data = c.fetchone()
                if photo_data and photo_data[0]:
                    self._load_single_photo(photo_data[0])

            conn.close()

            if not self.current_photos:
                self._add_placeholder("Нет фотографий")

        except Exception as e:
            print(f"Ошибка загрузки фото: {e}")
            self._add_placeholder("Ошибка загрузки")

    def _load_single_photo(self, photo_data):
        """Загружает и отображает одну фотографию"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp_filename = tmp.name
                self.temp_files.append(tmp_filename)

            # Сохраняем изображение во временный файл
            with open(tmp_filename, 'wb') as f:
                f.write(photo_data)

            swiper_item = MDSwiperItem()
            img = AsyncImage(
                source=tmp_filename,
                size_hint=(1, 1),
                keep_ratio=False,
                allow_stretch=True
            )
            swiper_item.add_widget(img)
            self.add_widget(swiper_item)
            self.current_photos.append(photo_data)

        except Exception as e:
            print(f"Ошибка обработки фото: {e}")
            self._add_placeholder("Ошибка фото")

    def clear_photos(self):
        """Очищает все фото и временные файлы"""
        self.clear_widgets()
        self._cleanup_temp_files()
        self.current_photos = []

    def _cleanup_temp_files(self):
        """Удаляет временные файлы"""
        for file in self.temp_files:
            try:
                if os.path.exists(file):
                    os.unlink(file)
            except Exception as e:
                print(f"Ошибка удаления временного файла: {e}")
        self.temp_files = []

    def _add_placeholder(self, text):
        """Заглушка, если фото нет"""
        item = MDSwiperItem()
        item.add_widget(MDLabel(text=text, halign='center'))
        self.add_widget(item)

class ApartmentDescriptionScreen(MDScreen):
    apartment_id = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]
        self.photo_swiper = None
        self.current_apartment_id = None
        self.favorite_button = None
        self.build_ui()

    def build_ui(self):
        """Создание интерфейса"""
        self.main_layout = MDFloatLayout()

        # Top App Bar
        self.top_app_bar = MDTopAppBar(
            title="Описание квартиры",
            pos_hint={'top': 1},
            elevation=2,
            md_bg_color=(0.2, 0.6, 1, 1),
            size_hint=(1, None),
            height=dp(40)
        )

        # Back button
        self.back_button = MDIconButton(
            icon="arrow-left",
            pos_hint={'x': 0.02, 'top': 0.98},
            size=(dp(48), dp(48)),
            on_release=self.go_back
        )

        # Favorite button
        self.favorite_button = FavoriteButton(
            pos_hint={'right': 0.98, 'top': 0.98},
            size=(dp(48), dp(48)),
            apartment_id=self.apartment_id
        )

        # Info Card с фиксированной высотой
        self.info_card = MDCard(
            size_hint=(1, None),
            height=dp(400),  # Фиксированная высота карточки
            pos_hint={'top': 0.55},
            padding=dp(16),
            spacing=dp(16),
            elevation=2,
            radius=[15],
            md_bg_color=(0.2, 0.6, 1, 1)
        )

        # Основной контейнер для контента
        self.info_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
        )
        self.info_card.add_widget(self.info_content)

        # Assemble UI
        self.main_layout.add_widget(self.top_app_bar)
        self.main_layout.add_widget(self.back_button)
        self.main_layout.add_widget(self.favorite_button)
        self.main_layout.add_widget(self.info_card)
        self.add_widget(self.main_layout)

    def on_enter(self):
        """Загружает данные при открытии экрана"""
        if self.apartment_id:
            # Очищаем предыдущий PhotoSwiper
            self.clear_photo_swiper()

            # Создаем новый PhotoSwiper
            self.photo_swiper = PhotoSwiper()
            self.main_layout.add_widget(self.photo_swiper)

            # Загружаем данные
            self.load_apartment_data(self.apartment_id)
            self.photo_swiper.load_photos(self.apartment_id)

    def on_leave(self):
        """Очищает фото при закрытии экрана"""
        self.clear_photo_swiper()

    def on_apartment_id(self, instance, value):
        """Обновляет данные при изменении apartment_id"""
        if value == self.current_apartment_id:
            return

        self.current_apartment_id = value
        if self.favorite_button:
            self.favorite_button.apartment_id = value
            Clock.schedule_once(lambda dt: self.favorite_button.check_favorite_state())

        # Очищаем предыдущий PhotoSwiper
        self.clear_photo_swiper()

        # Создаем новый PhotoSwiper
        self.photo_swiper = PhotoSwiper()
        self.main_layout.add_widget(self.photo_swiper)

        # Загружаем данные
        self.load_apartment_data(value)
        self.photo_swiper.load_photos(value)

    def load_apartment_data(self, apartment_id):
        """Загружает данные квартиры из БД"""
        try:
            conn = sqlite3.connect(get_db_path())
            c = conn.cursor()

            c.execute("""
                SELECT a.description, a.address, c.name, a.price, 
                       a.area, rc.room_count, a.full_description, 
                       u.phone, u.full_name, cat.name
                FROM apartments a
                JOIN cities c ON a.city_id = c.id
                JOIN room_counts rc ON a.room_count_id = rc.id
                JOIN users u ON a.realtor_id = u.id
                JOIN categories cat ON a.category_id = cat.id
                WHERE a.id = ?
            """, (apartment_id,))

            apartment_data = c.fetchone()
            conn.close()

            self._update_info(apartment_data)

        except Exception as e:
            print(f"Ошибка загрузки данных квартиры: {e}")
            self._show_error()

    def _update_info(self, apartment_data):
        """Обновляет информацию о квартире"""
        self.info_content.clear_widgets()

        if not apartment_data:
            self.info_content.add_widget(MDLabel(
                text="Данные не найдены",
                halign='center',
                size_hint_y=None,
                height=dp(20)
            ))
            return

        # 1. Краткое описание
        self.info_content.add_widget(MDLabel(
            text=apartment_data[0] or "Нет описания",
            size_hint_y=None,
            height=dp(20),
            bold=True,
            halign='left'
        ))

        # 2. Категория и цена
        category_price_row = MDBoxLayout(
            size_hint_y=None,
            height=dp(30),
            spacing=dp(20))
        category_text = f"Категория: {apartment_data[9]}" if apartment_data[9] else "Категория не указана"
        category_price_row.add_widget(MDLabel(
            text=category_text,
            size_hint_x=0.6,
            halign='left'
        ))

        price_text = f"Цена:{int(apartment_data[3]):,} ₽".replace(",", " ") if apartment_data[3] else "Цена не указана"
        category_price_row.add_widget(MDLabel(
            text=price_text,
            size_hint_x=0.55,
            halign='right',
            theme_text_color="Primary"
        ))
        self.info_content.add_widget(category_price_row)

        # 3. Город и адрес
        city_address_text = f"{apartment_data[2]}, {apartment_data[1]}" if apartment_data[2] and apartment_data[
            1] else "Адрес не указан"
        self.info_content.add_widget(MDLabel(
            text=city_address_text,
            size_hint_y=None,
            height=dp(30),
            halign='left',
            theme_text_color="Secondary"
        ))

        # 4. Площадь и комнаты
        area_rooms_text = f"Площадь: {apartment_data[4]} м², комнат: {apartment_data[5]}" if apartment_data[4] and \
                                                                                             apartment_data[
                                                                                                 5] else "Площадь и комнаты не указаны"
        self.info_content.add_widget(MDLabel(
            text=area_rooms_text,
            size_hint_y=None,
            height=dp(20),
            halign='left'
        ))

        # Разделитель
        self.info_content.add_widget(MDLabel(
            text="____________________________________________",
            size_hint_y=None,
            height=dp(5),
            halign='center',
            theme_text_color="Secondary"
        ))

        # 5. Информация о риелторе
        realtor_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(2)
        )
        realtor_name = f"Риелтор: {apartment_data[8]}" if apartment_data[8] else "Риелтор не указан"
        realtor_box.add_widget(MDLabel(
            text=realtor_name,
            size_hint_y=None,
            height=dp(20),
            halign='left'
        ))

        phone_text = apartment_data[7] if apartment_data[7] else "не указан"
        realtor_box.add_widget(MDLabel(
            text=f"Раб.Тел: {phone_text}",
            size_hint_y=None,
            height=dp(20),
            halign='left'
        ))
        self.info_content.add_widget(realtor_box)

        # Разделитель
        self.info_content.add_widget(MDLabel(
            text="____________________________________________",
            size_hint_y=None,
            height=dp(10),
            halign='center',
            theme_text_color="Secondary"
        ))

        # 6. Полное описание
        full_desc = apartment_data[6] or "Полное описание отсутствует"
        self.info_content.add_widget(MDLabel(
            text=f"Описание:\n{full_desc}",
            size_hint_y=None,
            height=dp(150),
            halign='left',
            valign='top'
        ))

    def _show_error(self):
        """Показывает сообщение об ошибке"""
        self.info_card.clear_widgets()
        self.info_card.add_widget(MDLabel(
            text="Ошибка загрузки данных",
            halign='center',
            theme_text_color="Error"
        ))

    def clear_photo_swiper(self):
        """Очищает текущий PhotoSwiper и удаляет его из интерфейса"""
        if self.photo_swiper:
            self.photo_swiper.clear_photos()
            self.main_layout.remove_widget(self.photo_swiper)
            self.photo_swiper = None

    def go_back(self, *args):
        """Возврат на предыдущий экран"""
        self.manager.current = 'apartments'

class FavoritesManager:
    _instance = None
    _favorites_state = {}
    _callbacks = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def is_favorite(self, user_id, apartment_id):
        key = (user_id, apartment_id)
        if key not in self._favorites_state:
            self._check_db_state(user_id, apartment_id)
        return self._favorites_state.get(key, False)

    def toggle_favorite(self, user_id, apartment_id):
        try:
            conn = sqlite3.connect(get_db_path())
            c = conn.cursor()

            key = (user_id, apartment_id)
            if self._favorites_state.get(key, False):
                c.execute("""
                    DELETE FROM favorites 
                    WHERE user_id = ? AND apartment_id = ?
                """, (user_id, apartment_id))
                self._favorites_state[key] = False
            else:
                c.execute("""
                    INSERT INTO favorites (user_id, apartment_id)
                    VALUES (?, ?)
                """, (user_id, apartment_id))
                self._favorites_state[key] = True

            conn.commit()
            conn.close()

            # Важно: уведомляем ВСЕХ подписчиков для этого apartment_id
            self._notify_subscribers(apartment_id)

            return self._favorites_state[key]
        except Exception as e:
            print(f"Ошибка обновления избранного: {e}")
            return None

    def _check_db_state(self, user_id, apartment_id):
        try:
            conn = sqlite3.connect(get_db_path())
            c = conn.cursor()
            c.execute("""
                SELECT 1 FROM favorites 
                WHERE user_id = ? AND apartment_id = ?
            """, (user_id, apartment_id))
            self._favorites_state[(user_id, apartment_id)] = c.fetchone() is not None
            conn.close()
        except Exception as e:
            print(f"Ошибка проверки избранного: {e}")
            self._favorites_state[(user_id, apartment_id)] = False

    def subscribe(self, apartment_id, callback):
        if apartment_id not in self._callbacks:
            self._callbacks[apartment_id] = []
        self._callbacks[apartment_id].append(callback)

    def unsubscribe(self, apartment_id, callback):
        if apartment_id in self._callbacks and callback in self._callbacks[apartment_id]:
            self._callbacks[apartment_id].remove(callback)

    def _notify_subscribers(self, apartment_id):
        if apartment_id in self._callbacks:
            for callback in self._callbacks[apartment_id]:
                callback()


class FavoriteButton(MDIconButton, TouchBehavior):
    is_favorite = BooleanProperty(False)
    apartment_id = NumericProperty(None)
    scale = NumericProperty(1.0)

    def __init__(self, **kwargs):
        # Инициализация всех необходимых атрибуты перед вызовом super()
        self.favorites_manager = FavoritesManager()
        self._anim = None  # Инициализируем _anim здесь

        # Затем вызов родительского __init__
        super().__init__(**kwargs)

        self.theme_text_color = "Custom"
        self.text_color = (0.5, 0.5, 0.5, 1)
        self.icon = "heart-outline"
        self.size_hint = (None, None)
        self.size = (dp(36), dp(36))
        self.user_font_size = dp(24)

        # Принудительная проверка состояния после создания
        Clock.schedule_once(lambda dt: self._finish_init())

    def _finish_init(self, dt=None):
        """Завершаем инициализацию после создания виджета"""
        self.bind(
            apartment_id=self.on_apartment_id,
            is_favorite=self.update_icon
        )
        # Проверяем состояние сразу
        self.check_favorite_state()
        # Принудительно обновляем иконку без анимации
        self.update_icon(self, self.is_favorite, force=True)

    def on_apartment_id(self, instance, value):
        """Обрабатываем изменение apartment_id"""
        # Отписываемся от старого ID
        if instance.apartment_id:
            self.favorites_manager.unsubscribe(instance.apartment_id, self.check_favorite_state)

        # Подписываемся на новый ID
        if value:
            self.favorites_manager.subscribe(value, self.check_favorite_state)

        # Немедленно проверяем состояние
        self.check_favorite_state()

    def check_favorite_state(self, *args):
        """Проверяет состояние избранного"""
        if not self.apartment_id:
            return

        user_id = self.get_current_user_id()
        if not user_id:
            self.is_favorite = False
            return

        self.is_favorite = self.favorites_manager.is_favorite(user_id, self.apartment_id)

    def update_icon(self, instance, value, force=False):
        """Обновляет иконку с анимацией или без"""
        if hasattr(self, '_anim') and self._anim:
            self._anim.cancel(self)

        if value:
            self.icon = "heart"
            if force:
                self.text_color = (1, 0, 0, 1)  # Красный цвет без анимации
            else:
                self._anim = Animation(text_color=(1, 0, 0, 1), duration=0.2)
                self._anim.start(self)
        else:
            self.icon = "heart-outline"
            if force:
                self.text_color = (0.5, 0.5, 0.5, 1)  # Серый цвет без анимации
            else:
                self._anim = Animation(text_color=(0.5, 0.5, 0.5, 1), duration=0.2)
                self._anim.start(self)


    def toggle_favorite(self):
        """Переключает состояние избранного"""
        user_id = self.get_current_user_id()
        if not user_id:
            print("Пользователь не авторизован")
            return

        new_state = self.favorites_manager.toggle_favorite(user_id, self.apartment_id)
        if new_state is not None:
            self.is_favorite = new_state

    def get_current_user_id(self):
        """Получает ID текущего пользователя"""
        try:
            with open("session.txt", "r") as f:
                return int(f.read().strip())
        except:
            return None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.toggle_favorite()
            return True
        return super().on_touch_down(touch)

class ApartmentsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]
        self.filters = {}
        self.city_menu = None
        self.category_menu = None
        self.room_count_menu = None
        self.search_active = BooleanProperty(False)
        self.current_user_id = None
        self.load_current_user()
        self.build_ui()

    def show_apartment_details(self, apartment_id):
        if not hasattr(self, 'description_screen'):
            self.description_screen = ApartmentDescriptionScreen(name='apartment_description')
            self.manager.add_widget(self.description_screen)

        self.description_screen.apartment_id = apartment_id
        self.manager.current = 'apartment_description'

    def load_current_user(self):
        """Загружает ID текущего пользователя из session.txt"""
        try:
            with open("session.txt", "r") as f:
                self.current_user_id = int(f.read().strip())
        except:
            self.current_user_id = None

    def build_ui(self):
        # Основной контейнер
        main_layout = MDFloatLayout()

        # Простой аппбар
        self.top_app_bar = MDTopAppBar(
            title="",
            pos_hint={'top': 1},
            elevation=0,
            md_bg_color=(1, 1, 1, 0)
        )

        # Кнопка меню фильтров
        self.filter_menu_button = MDIconButton(
            icon="menu",
            pos_hint={'x': 0.02, 'top': 0.98},
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            on_release=self.open_navigation_drawer
        )
        # Кнопка очистки
        self.clear_search_btn = MDIconButton(
            icon="close",
            pos_hint={'x': 1, 'top': 1.3},
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            theme_text_color="Primary",
            opacity=0
        )
        # Контейнер для поиска
        search_container = MDBoxLayout(
            orientation='horizontal',
            size_hint=(0.8, None),
            height=dp(50),  # Фиксированная высота контейнера
            pos_hint={'center_x': 0.55, 'top': 0.99},
            padding=[dp(0), dp(0)],  # Уменьшенные отступы
            spacing=dp(0),
            md_bg_color=(1, 1, 1, 0),
            radius=[18]
        )
        # Поле поиска
        self.search_field = MDTextField(
            MDTextFieldLeadingIcon(
                icon="magnify",
            ),
            MDTextFieldHintText(
                text="Поиск",
            ),
            mode="outlined",
            size_hint_x=0.9,
            height=dp(40),  # Высота поля
            font_size='12sp',
            line_color_focus=(0.2, 0.6, 1, 1),
            fill_color_normal=(0, 0, 0, 0),
            fill_color_focus=(1, 1, 1, 1),
            radius=[18],
        )
        self.search_field.bind(on_text_validate=self.on_search_enter)

        # Сборка элементов поиска
        search_container.add_widget(self.search_field)
        search_container.add_widget(self.clear_search_btn)

        # Обработчики событий для поисковой системы в аппбаре
        self.search_field.bind(text=self.on_search_text_change)
        self.clear_search_btn.bind(on_release=self.clear_search)

        # Навигационный drawer
        self.nav_drawer = MDNavigationDrawer()
        self.nav_drawer_box = MDBoxLayout(orientation='vertical')

        self.nav_drawer_top_bar = MDTopAppBar(
            #title="Фильтры",
            left_action_items=[["close", lambda x: self.nav_drawer.set_state("close")]]
        )
        self.nav_drawer_box.add_widget(self.nav_drawer_top_bar)

        self.filter_list = MDBoxLayout(orientation='vertical', spacing=dp(1), padding=dp(1))

        # Элементы фильтров (город, категория, комнаты)
        self.city_item = MDListItem(
            MDListItemLeadingIcon(icon="city"),
            MDListItemHeadlineText(text="Город")
        )
        self.city_item.bind(on_release=self.open_city_menu)
        self.filter_list.add_widget(self.city_item)

        self.category_item = MDListItem(
            MDListItemLeadingIcon(icon="tag"),
            MDListItemHeadlineText(text="Категория")
        )
        self.category_item.bind(on_release=self.open_category_menu)
        self.filter_list.add_widget(self.category_item)

        self.room_count_item = MDListItem(
            MDListItemLeadingIcon(icon="bed"),
            MDListItemHeadlineText(text="Количество комнат")
        )
        self.room_count_item.bind(on_release=self.open_room_count_menu)
        self.filter_list.add_widget(self.room_count_item)

        # Поля для цены
        price_from_label = MDLabel(
            text="Цена от",
            size_hint_x=0.9,
            pos_hint={'center_x': 0.5},
            theme_text_color="Primary",
            font_size="16sp"
        )
        self.filter_list.add_widget(price_from_label)

        self.price_from_input = MDTextField(
            hint_text="Введите цену от",
            mode="outlined",
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(30),
            pos_hint={'center_x': 0.5}
        )
        self.filter_list.add_widget(self.price_from_input)

        price_to_label = MDLabel(
            text="Цена до",
            size_hint_x=0.9,
            pos_hint={'center_x': 0.5},
            theme_text_color="Primary",
            font_size="16sp"
        )
        self.filter_list.add_widget(price_to_label)

        self.price_to_input = MDTextField(
            hint_text="Введите цену до",
            mode="outlined",
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(30),
            pos_hint={'center_x': 0.5}
        )
        self.filter_list.add_widget(self.price_to_input)

        # Поля для площади
        area_from_label = MDLabel(
            text="Площадь от",
            size_hint_x=0.9,
            pos_hint={'center_x': 0.5},
            theme_text_color="Primary",
            font_size="16sp"
        )
        self.filter_list.add_widget(area_from_label)

        self.area_from_input = MDTextField(
            hint_text="Введите площадь от",
            mode="outlined",
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(30),
            pos_hint={'center_x': 0.5}
        )
        self.filter_list.add_widget(self.area_from_input)

        area_to_label = MDLabel(
            text="Площадь до",
            size_hint_x=0.9,
            pos_hint={'center_x': 0.5},
            theme_text_color="Primary",
            font_size="16sp"
        )
        self.filter_list.add_widget(area_to_label)

        self.area_to_input = MDTextField(
            hint_text="Введите площадь до",
            mode="outlined",
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(30),
            pos_hint={'center_x': 0.5}
        )
        self.filter_list.add_widget(self.area_to_input)

        # Кнопки применения/сброса фильтров
        button_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(70))

        self.apply_filters_button = MDIconButton(
            icon="check",
            on_release=self.apply_filters_from_inputs,
            theme_text_color="Custom",
            md_bg_color=(1, 1, 1, 0),
        )
        button_box.add_widget(self.apply_filters_button)

        self.reset_filters_button = MDIconButton(
            icon="close",
            on_release=self.reset_filters,
            theme_text_color="Custom",
            md_bg_color=(1, 1, 1, 0),
        )
        button_box.add_widget(self.reset_filters_button)

        self.filter_list.add_widget(button_box)
        # Добавляем пустой блок для поднятия элементов выше
        empty_space = MDBoxLayout(
            size_hint_y=None,
            height=dp(265)  # Высота пустого блока
        )
        self.filter_list.add_widget(empty_space)

        self.nav_drawer_scroll = MDScrollView()
        self.nav_drawer_scroll.add_widget(self.filter_list)
        self.nav_drawer_box.add_widget(self.nav_drawer_scroll)
        self.nav_drawer.add_widget(self.nav_drawer_box)

        # ScrollView с карточками
        self.scroll_view = MDScrollView(
            pos_hint={'top': 0.9, 'bottom': 0.1},
            do_scroll_x=False
        )
        self.card_grid = MDGridLayout(
            cols=2,
            padding=dp(15),
            spacing=dp(9),
            size_hint_y=None,
            height=dp(500)
        )
        self.scroll_view.add_widget(self.card_grid)

        # сборка всех элементов
        main_layout.add_widget(self.top_app_bar)
        main_layout.add_widget(self.filter_menu_button)
        main_layout.add_widget(search_container)
        main_layout.add_widget(self.scroll_view)
        main_layout.add_widget(self.nav_drawer)

        self.add_widget(main_layout)
        self.load_apartments()

    def on_search_enter(self, instance):
        # Вызов поиска при нажатии Enter
        self.perform_search(instance)

    def on_search_text_change(self, instance, value):
        self.clear_search_btn.opacity = 1 if value else 0

    def clear_search(self, *args):
        self.search_field.text = ""
        self.clear_search_btn.opacity = 0
        self.perform_search(self.search_field)

    def open_navigation_drawer(self, *args):
        self.nav_drawer.set_state("open")

    def perform_search(self, instance):
        search_text = instance.text.strip().lower()
        self.clear_search_btn.opacity = 1 if search_text else 0

        self.card_grid.clear_widgets()
        self.card_grid.height = 0

        if not hasattr(self, 'all_apartments'):
            self.load_apartments()
            return

        filtered_apartments = []
        for apt in self.all_apartments:
            include = True

            # Фильтр по городу
            if 'city' in self.filters and self.filters['city']:
                if apt[2] != self.filters['city']:
                    include = False

            # Фильтр по категории
            if include and 'category' in self.filters and self.filters['category']:
                if apt[3] != self.filters['category']:
                    include = False

            # Фильтр по количеству комнат
            if include and 'room_count' in self.filters and self.filters['room_count']:
                if len(apt) > 8 and apt[8] != self.filters['room_count']:
                    include = False

            # Фильтр по цене (от)
            if include and 'price_min' in self.filters and self.filters['price_min']:
                try:
                    price_min = float(self.filters['price_min'])
                    if apt[4] is None or float(apt[4]) < price_min:
                        include = False
                except ValueError:
                    pass

            # Фильтр по цене (до)
            if include and 'price_max' in self.filters and self.filters['price_max']:
                try:
                    price_max = float(self.filters['price_max'])
                    if apt[4] is None or float(apt[4]) > price_max:
                        include = False
                except ValueError:
                    pass

            # Фильтр по площади (от)
            if include and 'area_min' in self.filters and self.filters['area_min']:
                try:
                    area_min = float(self.filters['area_min'])
                    if apt[7] is None or float(apt[7]) < area_min:
                        include = False
                except ValueError:
                    pass

            # Фильтр по площади (до)
            if include and 'area_max' in self.filters and self.filters['area_max']:
                try:
                    area_max = float(self.filters['area_max'])
                    if apt[7] is None or float(apt[7]) > area_max:
                        include = False
                except ValueError:
                    pass

            if include:
                filtered_apartments.append(apt)

        # Дополнительная фильтрация по поисковой строке
        if search_text:
            search_terms = [term for term in re.findall(r'\b\w{3,}\b', search_text) if term]
            if search_terms:
                final_filtered = []
                for apt in filtered_apartments:
                    search_fields = []
                    description = (apt[5] or "").lower()
                    address = (apt[1] or "").lower()

                    if 'city' not in self.filters or not self.filters['city']:
                        city = (apt[2] or "").lower()
                        search_fields.append(city)

                    if 'category' not in self.filters or not self.filters['category']:
                        category = (apt[3] or "").lower()
                        search_fields.append(category)

                    search_fields.extend([description, address])

                    matches_all = True
                    for term in search_terms:
                        found = False
                        for field in search_fields:
                            if term in field:
                                found = True
                                break
                        if not found:
                            matches_all = False
                            break

                    if matches_all:
                        final_filtered.append(apt)
                filtered_apartments = final_filtered

        for apt in filtered_apartments:
            self.card_grid.add_widget(self.create_apartment_card(apt))
            self.card_grid.height += dp(220)

    def open_city_menu(self, *args):
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute("SELECT name FROM cities")
        cities = c.fetchall()
        conn.close()

        city_items = [
            {
                "text": city[0],
                "on_release": lambda x=city[0]: self.set_city(x),
                "right_icon": "check" if self.filters.get('city') == city[0] else ""
            } for city in cities
        ]
        self.city_menu = MDDropdownMenu(
            caller=self.city_item,
            items=city_items,
            width_mult=4
        )
        self.city_menu.open()

    def set_city(self, city):
        self.filters['city'] = city
        self.city_item.children[1].text = f"Город: {city}"
        self.city_menu.dismiss()
        self.perform_search(self.search_field)

    def open_category_menu(self, *args):
        category_items = [
            {
                "text": "Аренда",
                "on_release": lambda x="Аренда": self.set_category(x),
                "right_icon": "check" if self.filters.get('category') == "Аренда" else ""
            },
            {
                "text": "Продажа",
                "on_release": lambda x="Продажа": self.set_category(x),
                "right_icon": "check" if self.filters.get('category') == "Продажа" else ""
            }
        ]
        self.category_menu = MDDropdownMenu(
            caller=self.category_item,
            items=category_items,
            width_mult=4
        )
        self.category_menu.open()

    def set_category(self, category):
        self.filters['category'] = category
        self.category_item.children[1].text = f"Категория: {category}"
        self.category_menu.dismiss()
        self.perform_search(self.search_field)

    def open_room_count_menu(self, *args):
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute("SELECT room_count FROM room_counts")
        room_counts = c.fetchall()
        conn.close()

        room_count_items = [
            {
                "text": str(room_count[0]),
                "on_release": lambda x=room_count[0]: self.set_room_count(x),
                "right_icon": "check" if self.filters.get('room_count') == room_count[0] else ""
            } for room_count in room_counts
        ]
        self.room_count_menu = MDDropdownMenu(
            caller=self.room_count_item,
            items=room_count_items,
            width_mult=4
        )
        self.room_count_menu.open()

    def set_room_count(self, room_count):
        self.filters['room_count'] = room_count
        self.room_count_item.children[1].text = f"Количество комнат: {room_count}"
        self.room_count_menu.dismiss()
        if hasattr(self, 'search_field'):
            self.perform_search(self.search_field)

    def apply_filters_from_inputs(self, *args):
        self.filters['price_min'] = self.price_from_input.text.strip() if self.price_from_input.text.strip() else None
        self.filters['price_max'] = self.price_to_input.text.strip() if self.price_to_input.text.strip() else None
        self.filters['area_min'] = self.area_from_input.text.strip() if self.area_from_input.text.strip() else None
        self.filters['area_max'] = self.area_to_input.text.strip() if self.area_to_input.text.strip() else None

        self.perform_search(self.search_field)

    def reset_filters(self, *args):
        self.filters = {}
        self.city_item.children[1].text = "Город"
        self.category_item.children[1].text = "Категория"
        self.room_count_item.children[1].text = "Количество комнат"
        self.price_from_input.text = ""
        self.price_to_input.text = ""
        self.area_from_input.text = ""
        self.area_to_input.text = ""
        self.perform_search(self.search_field)

    def load_apartments(self):
        self.card_grid.clear_widgets()
        self.card_grid.height = 0

        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()

        query = """
            SELECT a.id, a.address, c.name, cat.name, a.price, a.description, 
                   ap.Photo_1, a.area, a.room_count_id
            FROM apartments a 
            JOIN cities c ON a.city_id = c.id 
            JOIN categories cat ON a.category_id = cat.id
            LEFT JOIN apartment_photos ap ON a.id = ap.apartment_id
        """

        c.execute(query)
        self.all_apartments = c.fetchall()
        conn.close()

        filtered_apartments = []
        for apt in self.all_apartments:
            include = True

            if 'city' in self.filters and self.filters['city']:
                if apt[2] != self.filters['city']:
                    include = False

            if include and 'category' in self.filters and self.filters['category']:
                if apt[3] != self.filters['category']:
                    include = False

            if include and 'room_count' in self.filters and self.filters['room_count']:
                if len(apt) > 8 and apt[8] != self.filters['room_count']:
                    include = False

            if include:
                filtered_apartments.append(apt)

        for apt in filtered_apartments:
            self.card_grid.add_widget(self.create_apartment_card(apt))
            self.card_grid.height += dp(220)

    def create_apartment_card(self, apartment_data):
        """Создает карточку квартиры с обрезанием фотографии по границам"""
        # Основные параметры карточки
        card = MDCard(
            size_hint=(None, None),
            size=(dp(225), dp(310)),
            padding=dp(5),
            elevation=0,
            md_bg_color=[0.95, 0.95, 0.95, 1],
            radius=[15],
        )
        card.apartment_id = apartment_data[0]

        # Главный контейнер
        main_layout = MDFloatLayout(
            size_hint_y=None,
            height=dp(300)
        )

        # Контейнер для изображения (теперь просто MDCard)
        image_container = MDCard(
            size_hint=(1, None),
            height=dp(220),
            pos_hint={'top': 1, 'center_x': 0.5},
            radius=[12],
            elevation=0,
            padding=dp(-1)
        )

        # Загрузка изображения
        if apartment_data[6]:  # Проверяем наличие фото в данных
            try:
                # Создаем временный файл
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                    tmp_filename = tmp.name
                    tmp.write(apartment_data[6])  # Записываем данные сразу

                # Создаем изображение с правильными параметрами
                img = AsyncImage(
                    source=tmp_filename,
                    size_hint=(1, 1),
                    keep_ratio=False,
                    allow_stretch=True,
                    pos_hint={'center_x': 0.5, 'center_y': 0.5}
                )

                # Добавляем изображение в контейнер
                image_container.add_widget(img)

                # Удаляем временный файл через 5 секунд
                Clock.schedule_once(lambda dt: os.unlink(tmp_filename) if os.path.exists(tmp_filename) else None, 5)

            except Exception as e:
                logging.error(f"Ошибка загрузки изображения: {e}")
                image_container.add_widget(MDLabel(
                    text="Ошибка загрузки",
                    halign='center',
                    theme_text_color="Error"
                ))
        else:
            image_container.add_widget(MDLabel(
                text="Фото отсутствует",
                halign='center',
                theme_text_color="Secondary"
            ))

        # Кнопка избранного
        favorite_btn = FavoriteButton(
            pos_hint={'right': 0.98, 'top': 0.98},
            size=(dp(36), dp(36)),
            apartment_id=apartment_data[0]
        )
        Clock.schedule_once(lambda dt: favorite_btn.check_favorite_state())

        # Текстовый блок
        text_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(3),
            size_hint_y=None,
            height=dp(93),
            pos_hint={'top': 0.3, 'center_x': 0.5}
        )

        # Краткое описание
        description = MDLabel(
            text=f"{apartment_data[5] if apartment_data[5] else 'Нет описания'}",
            size_hint_y=None,
            height=dp(25),
            theme_text_color="Primary",
            font_size="11sp",
            halign='left',
            shorten=True,
            max_lines=1
        )

        # Категория и площадь
        category_area = MDLabel(
            text=f"{apartment_data[3] if apartment_data[3] else 'Кат. не указана'} • {apartment_data[7] if apartment_data[7] else '?'} м²",
            size_hint_y=None,
            height=dp(25),
            theme_text_color="Primary",
            font_size="11sp",
            halign='left'
        )

        # Форматирование цены
        price_value = apartment_data[4]
        if price_value is not None:
            try:
                price_text = f"{int(price_value):,} ₽".replace(",", " ")
            except (ValueError, TypeError):
                price_text = "Цена не указана"
        else:
            price_text = "Цена не указана"

        price = MDLabel(
            text=price_text,
            size_hint_y=None,
            height=dp(25),
            theme_text_color="Secondary",
            font_size="12sp",
            halign='left',
            bold=True
        )

        # Сборка текстового блока
        text_layout.add_widget(description)
        text_layout.add_widget(category_area)
        text_layout.add_widget(price)

        # Сборка всех элементов
        main_layout.add_widget(image_container)
        main_layout.add_widget(favorite_btn)
        main_layout.add_widget(text_layout)

        # Добавление в карточку
        card.add_widget(main_layout)

        # Привязка события нажатия
        card.bind(on_release=lambda x: self.show_apartment_details(apartment_data[0]))

        return card