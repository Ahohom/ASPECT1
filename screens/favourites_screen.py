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
from screens.apartments_screen import PhotoSwiper
from screens.apartments_screen import FavoriteButton
from screens.apartments_screen import FavoritesManager
logging.basicConfig(level=logging.DEBUG)
from kivy.uix.image import Image, AsyncImage
from db_utils import get_db_path

class FavoriteApartmentDescriptionScreen(MDScreen):
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
            if self.photo_swiper:
                self.main_layout.remove_widget(self.photo_swiper)
                self.photo_swiper = None

            # Создаем новый PhotoSwiper
            self.photo_swiper = PhotoSwiper()
            self.main_layout.add_widget(self.photo_swiper)

            # Загружаем данные
            self.load_apartment_data(self.apartment_id)
            self.photo_swiper.load_photos(self.apartment_id)

    def on_leave(self):
        """Очищает ресурсы при закрытии экрана"""
        if self.photo_swiper:
            self.photo_swiper.clear_photos()
            self.main_layout.remove_widget(self.photo_swiper)
            self.photo_swiper = None

    def on_apartment_id(self, instance, value):
        """Обновляет данные при изменении apartment_id"""
        if value == self.current_apartment_id and self.photo_swiper is not None:
            return

        self.current_apartment_id = value
        if self.favorite_button:
            self.favorite_button.apartment_id = value
            Clock.schedule_once(lambda dt: self.favorite_button.check_favorite_state())

        # Очищаем предыдущий PhotoSwiper
        if self.photo_swiper:
            self.main_layout.remove_widget(self.photo_swiper)
            self.photo_swiper = None

        # Создаем новый PhotoSwiper и загружаем данные
        self.photo_swiper = PhotoSwiper()
        self.main_layout.add_widget(self.photo_swiper)
        self.load_apartment_data(value)
        self.photo_swiper.load_photos(value)

    def go_back(self, *args):
        """Возврат на экран избранного"""
        self.manager.current = 'favourites'

    def load_apartment_data(self, apartment_id):
        """Загрузка данных квартиры"""
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
        """Show error message"""
        self.info_card.clear_widgets()
        self.info_card.add_widget(MDLabel(
            text="Ошибка загрузки данных",
            halign='center',
            theme_text_color="Error"
        ))

class FavouritesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]
        self.current_user_id = self._get_current_user_id()
        self.build_ui()

    def _get_current_user_id(self):
        """Получает ID текущего пользователя из session.txt"""
        try:
            with open("session.txt", "r") as f:
                return int(f.read().strip())
        except:
            return None

    def build_ui(self):
        main_layout = MDFloatLayout()

        # Top App Bar
        self.top_app_bar = MDTopAppBar(
            title="Избранное",
            pos_hint={'top': 1},
            elevation=2,
            md_bg_color=(0.2, 0.6, 1, 1),
            size_hint=(1, None),
            height=dp(20),
            disabled = True,
            opacity=0
        )
        main_layout.add_widget(self.top_app_bar)

        # ScrollView с карточками
        self.scroll_view = MDScrollView(
            pos_hint={'top': 0.95, 'bottom': 0.1},
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
        main_layout.add_widget(self.scroll_view)

        self.add_widget(main_layout)

    def on_enter(self):
        """Загружает избранные квартиры при входе на экран"""
        if self.current_user_id:
            self.load_favorite_apartments()
        else:
            # Если пользователь не авторизован, очищаем grid
            self.card_grid.clear_widgets()
            self.card_grid.height = 0

    def load_favorite_apartments(self):
        """Загружает избранные квартиры пользователя"""
        self.card_grid.clear_widgets()
        self.card_grid.height = 0

        try:
            conn = sqlite3.connect(get_db_path())
            c = conn.cursor()

            query = """
                SELECT a.id, a.address, c.name, cat.name, a.price, a.description, 
                       ap.Photo_1, a.area, a.room_count_id
                FROM apartments a 
                JOIN cities c ON a.city_id = c.id 
                JOIN categories cat ON a.category_id = cat.id
                LEFT JOIN apartment_photos ap ON a.id = ap.apartment_id
                JOIN favorites f ON a.id = f.apartment_id
                WHERE f.user_id = ?
            """
            c.execute(query, (self.current_user_id,))
            favorite_apartments = c.fetchall()
            conn.close()

            for apt in favorite_apartments:
                self.card_grid.add_widget(self.create_apartment_card(apt))
                self.card_grid.height += dp(220)

        except Exception as e:
            logging.error(f"Ошибка загрузки избранных квартир: {e}")

    def create_apartment_card(self, apartment_data):
        """Создает карточку квартиры"""
        card = MDCard(
            size_hint=(None, None),
            size=(dp(250), dp(310)),
            padding=dp(5),
            elevation=0,
            md_bg_color=[0.95, 0.95, 0.95, 1],
            radius=[15, ]
        )
        card.apartment_id = apartment_data[0]

        # Основной контейнер с FloatLayout для правильного позиционирования
        main_layout = MDFloatLayout(
            size_hint_y=None,
            height=dp(300)
        )

        # Контейнер фотографии
        image_container = MDCard(
            size_hint=(1, None),
            height=dp(220),
            pos_hint={'top': 1, 'center_x': 0.5},
            padding=dp(-1),
            radius=[33.5, ],
            elevation=2,
            md_bg_color=[0.95, 0.95, 0.95, 1]
        )

        # Загрузка изображения (оптимизированный вариант)
        if apartment_data[6]:  # Если есть фото в БД
            try:
                # Создаем временный файл для изображения
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                    tmp_filename = tmp.name

                # Сохраняем изображение во временный файл
                with open(tmp_filename, 'wb') as f:
                    f.write(apartment_data[6])

                # Используем AsyncImage с путем к файлу
                img = AsyncImage(
                    source=tmp_filename,
                    size_hint=(1, 1),
                    keep_ratio=False,
                    allow_stretch=True,
                    pos_hint={'center_x': 0.5}
                )

                # Удаляем временный файл после загрузки изображения
                Clock.schedule_once(lambda dt: os.unlink(tmp_filename) if os.path.exists(tmp_filename) else None, 5)

                image_container.add_widget(img)
            except Exception as e:
                logging.error(f"Ошибка загрузки изображения: {e}")
                image_container.add_widget(MDLabel(
                    text="Ошибка фото",
                    halign='center',
                    theme_text_color="Error"
                ))
        else:
            # Заглушка если фото нет
            image_container.add_widget(MDLabel(
                text="Фото отсутствует",
                halign='center',
                theme_text_color="Secondary"
            ))

        def on_favorite_toggle():
            """Обработчик изменения состояния избранного"""
            self.update_favorites_grid(apartment_data[0])

        # Создаем кнопку избранного с принудительным установлением состояния
        favorite_btn = FavoriteButton(
            pos_hint={'right': 0.98, 'top': 0.98},
            apartment_id=apartment_data[0]
        )

        # Принудительно устанавливаем состояние "в избранном"
        favorite_btn.is_favorite = True
        favorite_btn.icon = "heart"  # Красное заполненное сердце
        favorite_btn.text_color = (1, 0, 0, 1)  # Красный цвет

        # Подписываемся на изменения состояния
        favorite_btn.favorites_manager.subscribe(apartment_data[0], on_favorite_toggle)

        # Текстовый блок
        text_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(3),
            size_hint_y=None,
            height=dp(93),
            pos_hint={'top': 0.3, 'center_x': 0.5}
        )

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

        category_area = MDLabel(
            text=f"{apartment_data[3] if apartment_data[3] else 'Категория не указана'} • {apartment_data[7] if apartment_data[7] else '?'} м²",
            size_hint_y=None,
            height=dp(25),
            theme_text_color="Primary",
            font_size="11sp",
            halign='left'
        )

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

        text_layout.add_widget(description)
        text_layout.add_widget(category_area)
        text_layout.add_widget(price)

        # Добавляем все виджеты в основной контейнер
        main_layout.add_widget(image_container)
        main_layout.add_widget(favorite_btn)
        main_layout.add_widget(text_layout)

        card.add_widget(main_layout)
        card.bind(on_release=lambda x: self.show_apartment_details(apartment_data[0]))
        return card

    def show_apartment_details(self, apartment_id):
        """Показывает детали квартиры"""
        if not hasattr(self, 'description_screen'):
            self.description_screen = FavoriteApartmentDescriptionScreen(name='favorite_apartment_description')
            self.manager.add_widget(self.description_screen)

        self.description_screen.apartment_id = apartment_id
        self.manager.current = 'favorite_apartment_description'

    def update_favorites_grid(self, apartment_id=None):
        """Обновляет grid карточек, удаляя карточку с apartment_id, если она есть"""
        if apartment_id is not None:
            # Удаляем конкретную карточку
            for card in self.card_grid.children[:]:
                if hasattr(card, 'apartment_id') and card.apartment_id == apartment_id:
                    self.card_grid.remove_widget(card)
                    self.card_grid.height -= dp(220)
        else:
            # Полностью перезагружаем список
            self.load_favorite_apartments()