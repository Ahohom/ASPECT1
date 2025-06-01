from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDListItem, MDListItemHeadlineText
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField, MDTextFieldHelperText
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.boxlayout import BoxLayout
import sqlite3
from db_utils import get_db_path

class RealtorConstructorScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 1]  # Белый фон
        self.dialog = None



