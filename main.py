import json
import os
import threading
import urllib.request
import urllib.parse
from datetime import datetime, date

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.storage.jsonstore import JsonStore
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp

# Только на десктопе задаём размер
import platform
if platform.system() in ('Windows', 'Darwin', 'Linux'):
    Window.size = (400, 700)

# ──────────────────────────────────────────────────
#  ДАННЫЕ: Диета №15 на 30 дней
# ──────────────────────────────────────────────────
DIET_PLAN = [
    {"breakfast":"Овсяная каша с яблоком","lunch":"Куриный суп с овощами","snack":"Кефир + груша","dinner":"Куриная грудка + брокколи"},
    {"breakfast":"Творог с медом и орехами","lunch":"Суп-пюре из тыквы + индейка","snack":"Запеченное яблоко","dinner":"Рыба на пару + бурый рис"},
    {"breakfast":"Яйца всмятку + тост","lunch":"Борщ без зажарки + курица","snack":"Смузи банан+кефир","dinner":"Тушеные овощи + индейка"},
    {"breakfast":"Манная каша + ягоды","lunch":"Щи из капусты + говядина","snack":"Кефир + хлебец","dinner":"Запеченный минтай + гречка"},
    {"breakfast":"Гречневая каша молочная","lunch":"Уха из горбуши","snack":"Творог с ягодами","dinner":"Паровые котлеты + цветная капуста"},
    {"breakfast":"Омлет 2 яйца + огурец","lunch":"Рисовый суп с курицей","snack":"Банан + орехи","dinner":"Куриное филе + картофель"},
    {"breakfast":"Пшённая каша с тыквой","lunch":"Суп-минестроне + телятина","snack":"Натуральный йогурт","dinner":"Треска запеченная + горошек"},
    {"breakfast":"Мюсли без сахара + молоко","lunch":"Гороховый суп + котлета","snack":"Кефир + хлебец","dinner":"Тушеная капуста + куриное филе"},
    {"breakfast":"Творожная запеканка","lunch":"Куриный бульон + вермишель","snack":"Яблоко + миндаль","dinner":"Запеченный лосось + рис"},
    {"breakfast":"Геркулес с изюмом","lunch":"Суп из чечевицы + индейка","snack":"Смузи шпинат+яблоко","dinner":"Паровые рыбные котлеты + брокколи"},
    {"breakfast":"Яичница + помидор + тост","lunch":"Суп с фрикадельками","snack":"Творог с медом","dinner":"Тушеная говядина + гречка"},
    {"breakfast":"Рисовая каша молочная","lunch":"Окрошка на кефире","snack":"Грейпфрут + кешью","dinner":"Запеченная треска + бурый рис"},
    {"breakfast":"Овсянка с бананом","lunch":"Суп-лапша куриная","snack":"Кефир + хлебец","dinner":"Куриное филе с грибами + пшено"},
    {"breakfast":"Гречка + яйцо","lunch":"Рассольник + говядина","snack":"Натуральный йогурт + груша","dinner":"Паровой хек + цветная капуста"},
    {"breakfast":"Творог + банан + корица","lunch":"Суп из кабачков + котлета","snack":"Яблоко + фундук","dinner":"Запеченная индейка + картофель"},
    {"breakfast":"Пшённая каша молочная","lunch":"Борщ постный + курица","snack":"Смузи клубника+кефир","dinner":"Запеченный минтай + гречка"},
    {"breakfast":"Омлет с овощами","lunch":"Уха из трески","snack":"Кефир + хлебец","dinner":"Тушеные кабачки + индейка + рис"},
    {"breakfast":"Геркулес с черникой","lunch":"Суп гречневый с курицей","snack":"Банан + миндаль","dinner":"Паровые котлеты говяжьи + брокколи"},
    {"breakfast":"Яйца всмятку + тост","lunch":"Суп-пюре из горошка","snack":"Творог с киви","dinner":"Запеченный лосось + картофель"},
    {"breakfast":"Манная каша молочная","lunch":"Щи с грибами + курица","snack":"Кефир + груша","dinner":"Тушеная рыба с морковью + пшено"},
    {"breakfast":"Гречка молочная","lunch":"Рисовый суп с курицей","snack":"Смузи шпинат+банан","dinner":"Куриное филе запеченное + гречка"},
    {"breakfast":"Творожная запеканка","lunch":"Суп с чечевицей + котлета","snack":"Запеченное яблоко + орехи","dinner":"Треска на пару + бурый рис"},
    {"breakfast":"Овсянка с яблоком","lunch":"Борщ с телятиной","snack":"Натуральный йогурт + киви","dinner":"Запеченная индейка + брокколи"},
    {"breakfast":"Мюсли + молоко","lunch":"Куриный суп с рисом","snack":"Кефир + хлебец","dinner":"Паровой минтай + цветная капуста"},
    {"breakfast":"Яичница + помидор + тост","lunch":"Суп с фрикадельками","snack":"Смузи малина+творог","dinner":"Тушеная говядина с овощами + гречка"},
    {"breakfast":"Пшённая каша с тыквой","lunch":"Гороховый суп + курица","snack":"Банан + миндаль","dinner":"Запеченный хек с морковью + рис"},
    {"breakfast":"Геркулес с изюмом","lunch":"Суп-лапша с индейкой","snack":"Творог с медом + груша","dinner":"Куриное филе с кабачком + гречка"},
    {"breakfast":"Омлет + зелень + огурец","lunch":"Рассольник + телятина","snack":"Кефир + хлебец","dinner":"Лосось запеченный + брокколи"},
    {"breakfast":"Гречка + яйцо вкрутую","lunch":"Суп из кабачков с рисом + котлета","snack":"Смузи яблоко+кефир","dinner":"Запеченная индейка + пшено"},
    {"breakfast":"Творог с ягодами","lunch":"Борщ с говядиной","snack":"Натуральный йогурт + киви","dinner":"Рыба на пару + гречка + салат"},
]

# ──────────────────────────────────────────────────
#  ДАННЫЕ: ЛФК на 30 дней
# ──────────────────────────────────────────────────
LFK_PLAN = [
    {"title":"Дыхательная гимнастика","exercises":["Диафрагмальное дыхание — 10 мин","Медленные вдохи через нос — 15 раз","Выдох трубочкой — 15 раз","Подъём рук на вдохе лёжа — 10 раз"]},
    {"title":"Суставная разминка","exercises":["Вращение кистями — 10 раз","Вращение локтями — 10 раз","Вращение плечами — 10 раз","Наклоны головы — 8 раз"]},
    {"title":"Упражнения лёжа","exercises":["Сжимание пальцев — 15 раз","Подъём ноги лёжа — 10 раз","Велосипед лёжа — 30 сек","Мост (ягодицы вверх) — 10 раз"]},
    {"title":"Упражнения сидя","exercises":["Подъём на носки сидя — 15 раз","Разгибание колена — 10 раз","Наклоны туловища — 8 раз","Повороты корпуса — 8 раз"]},
    {"title":"Лёгкая растяжка","exercises":["Растяжка плеч — 2 мин","Наклон к ногам сидя — 10 раз","Растяжка икр — 1 мин","Кошка-корова — 10 раз"]},
    {"title":"Дыхание и релаксация","exercises":["Брюшное дыхание — 5 мин","Мышечная релаксация — 10 мин","Медитация лёжа — 5 мин"]},
    {"title":"Ходьба и равновесие","exercises":["Медленная ходьба — 10 мин","Стойка на одной ноге — 30 сек","Ходьба пятками — 2 мин","Ходьба на носках — 2 мин"]},
    {"title":"Упражнения для рук","exercises":["Сжимание мячика — 15 раз","Подъём рук вперёд — 10 раз","Разведение рук — 10 раз","Растяжка пальцев — 2 мин"]},
    {"title":"Укрепление спины","exercises":["Лодочка лёжа — 10 раз","Кошка-корова — 10 раз","Боковые наклоны — 10 раз","Повороты шеи — 8 раз"]},
    {"title":"Упражнения для ног","exercises":["Подъём ног лёжа — 10 раз","Сгибание колен стоя — 15 раз","Отведение ноги — 10 раз","Тяга пятки к ягодице — 10 раз"]},
    {"title":"Координация","exercises":["Ходьба по линии — 2 мин","Перешагивание — 5 мин","Марш на месте — 3 мин","Восьмёрки ногой — 10 раз"]},
    {"title":"Укрепление пресса","exercises":["Подъём головы лёжа — 10 раз","Втягивание живота — 10 раз","Подъём согнутых ног — 10 раз","Боковые скручивания — 8 раз"]},
    {"title":"Дыхание и суставы","exercises":["Полное дыхание — 5 мин","Вращение голеностопом — 10 раз","Вращение тазом — 10 раз","Потягивание — 2 мин"]},
    {"title":"Активный день","exercises":["Ходьба на улице — 20 мин","Приседания с опорой — 10 раз","Подъём на носки — 15 раз","Растяжка — 5 мин"]},
    {"title":"День восстановления","exercises":["Массаж кистей — 5 мин","Тёплая ванна для ног — 10 мин","Глубокое дыхание — 5 мин","Растяжка перед сном — 5 мин"]},
    {"title":"Равновесие","exercises":["Стойка у стены на носках — 1 мин","Перекаты с пятки на носок — 15 раз","Покачивание стоя — 2 мин","Ходьба с поворотами — 5 мин"]},
    {"title":"Комплекс для плеч","exercises":["Пожимание плечами — 15 раз","Вращение плечами — 10 раз","Разведение лопаток — 10 раз","Наклоны головы — 8 раз"]},
    {"title":"Лёжа и дыхание","exercises":["Мост — 10 раз","Велосипед — 30 сек","Дыхательные упражнения — 5 мин","Расслабление тела — 5 мин"]},
    {"title":"Мягкая нагрузка","exercises":["Ходьба — 15 мин","Подъём на носки — 15 раз","Марш с подъёмом колен — 2 мин","Растяжка икр — 2 мин"]},
    {"title":"Укрепление кора","exercises":["Планка на локтях — 20 сек","Боковая планка — 15 сек","Рука+нога противоположные — 10 раз","Скручивания мягкие — 10 раз"]},
    {"title":"День растяжки","exercises":["Растяжка тела лёжа — 5 мин","Растяжка бёдер — 2 мин","Растяжка плеч — 2 мин","Поза ребёнка — 3 мин"]},
    {"title":"Активация","exercises":["Мягкие прыжки — 30 сек","Приседания — 10 раз","Выпады вперёд — 8 раз","Ходьба на месте — 5 мин"]},
    {"title":"Суставы и дыхание","exercises":["Вращение суставов — 10 мин","Полное дыхание — 5 мин","Потягивание — 2 мин"]},
    {"title":"С эспандером","exercises":["Сгибание руки — 10 раз","Разгибание — 10 раз","Подъём ноги — 10 раз","Растяжка — 2 мин"]},
    {"title":"Осанка и дыхание","exercises":["Дыхание у стены — 5 мин","Прогиб назад — 10 раз","Стойка с ровной спиной — 3 мин","Растяжка груди — 2 мин"]},
    {"title":"Лёгкое кардио","exercises":["Ходьба — 25 мин","Подъём по ступеням — 5 мин","Растяжка после ходьбы — 5 мин"]},
    {"title":"Полное расслабление","exercises":["Глубокое дыхание — 10 мин","Шавасана — 10 мин","Самомассаж — 10 мин"]},
    {"title":"Укрепление ног","exercises":["Приседания у стены — 10 раз","Шаги в сторону — 15 раз","Подъём на носки — 20 раз","Растяжка бёдер — 2 мин"]},
    {"title":"Руки и плечи","exercises":["Отжимания от стены — 10 раз","Разведение рук — 10 раз","Подъём рук вперёд — 10 раз","Растяжка плеч — 3 мин"]},
    {"title":"Итоговая тренировка","exercises":["Дыхательная разминка — 3 мин","Суставная гимнастика — 5 мин","Ходьба — 15 мин","Упражнения на кор — 5 мин","Растяжка тела — 5 мин","Релаксация — 5 мин"]},
]

# ──────────────────────────────────────────────────
#  ХРАНИЛИЩЕ
# ──────────────────────────────────────────────────
store = JsonStore('healthmate_data.json')

def get_setting(key, default=None):
    try:
        if store.exists('settings'):
            return store.get('settings').get(key, default)
    except Exception:
        pass
    return default

def set_setting(key, value):
    try:
        d = dict(store.get('settings')) if store.exists('settings') else {}
        d[key] = value
        store.put('settings', **d)
    except Exception:
        pass

def get_day_index():
    return (date.today().timetuple().tm_yday - 1) % 30

# ──────────────────────────────────────────────────
#  POPUP HELPER
# ──────────────────────────────────────────────────
def show_popup(title, text, btn_text='OK'):
    content = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))
    content.add_widget(Label(
        text=text, halign='center', valign='middle',
        color=get_color_from_hex('#FFFFFF'),
        font_size=dp(14), text_size=(dp(260), None)
    ))
    btn = Button(
        text=btn_text, size_hint_y=None, height=dp(44),
        background_normal='', background_color=get_color_from_hex('#6BCB77'),
        color=get_color_from_hex('#FFFFFF'), font_size=dp(15)
    )
    content.add_widget(btn)
    popup = Popup(
        title=title, content=content,
        size_hint=(0.85, None), height=dp(200),
        background_color=get_color_from_hex('#1E2E3E'),
        title_color=get_color_from_hex('#FFD93D'),
        separator_color=get_color_from_hex('#6BCB77')
    )
    btn.bind(on_release=popup.dismiss)
    popup.open()
    return popup

# ──────────────────────────────────────────────────
#  ЭКРАНЫ
# ──────────────────────────────────────────────────
class MainScreen(Screen):
    date_text = StringProperty('')
    def on_enter(self):
        self.update_date()
    def update_date(self):
        now = datetime.now()
        months = ['января','февраля','марта','апреля','мая','июня',
                  'июля','августа','сентября','октября','ноября','декабря']
        self.date_text = f"{now.day} {months[now.month-1]} {now.year}"


class LoginScreen(Screen):
    def show_unavailable(self):
        show_popup('Информация', 'Регистрация и вход\nбудут доступны в следующем обновлении')
    def guest_login(self):
        set_setting('is_guest', True)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'app_screen'


class AppScreen(Screen):
    date_text = StringProperty('')
    def on_enter(self):
        self.update_date()
    def update_date(self):
        now = datetime.now()
        months = ['января','февраля','марта','апреля','мая','июня',
                  'июля','августа','сентября','октября','ноября','декабря']
        self.date_text = f"{now.day} {months[now.month-1]} {now.year}"

    def open_diet_today(self):
        idx = get_day_index()
        day = DIET_PLAN[idx]
        content = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(14),
                        size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        rows = [
            ("Завтрак",  day["breakfast"]),
            ("Обед",     day["lunch"]),
            ("Полдник",  day["snack"]),
            ("Ужин",     day["dinner"]),
        ]
        for lbl, val in rows:
            item = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(74),
                             padding=[dp(12), dp(8)], spacing=dp(4))
            with item.canvas.before:
                Color(rgba=get_color_from_hex('#1B4D3E'))
                item._bg = RoundedRectangle(size=item.size, pos=item.pos, radius=[dp(10)])
            item.bind(size=lambda w,v: setattr(w._bg,'size',v))
            item.bind(pos=lambda w,v: setattr(w._bg,'pos',v))
            item.add_widget(Label(text=lbl, font_size=dp(12), bold=True,
                                  color=get_color_from_hex('#6BCB77'),
                                  halign='left', text_size=(dp(280), None),
                                  size_hint_y=None, height=dp(20)))
            item.add_widget(Label(text=val, font_size=dp(13),
                                  color=get_color_from_hex('#FFFFFF'),
                                  halign='left', text_size=(dp(280), None),
                                  size_hint_y=None, height=dp(38)))
            box.add_widget(item)
        content.add_widget(box)
        close_btn = Button(text='Закрыть', size_hint_y=None, height=dp(44),
                           background_normal='',
                           background_color=get_color_from_hex('#6BCB77'))
        wrap = BoxLayout(orientation='vertical')
        wrap.add_widget(content)
        wrap.add_widget(close_btn)
        popup = Popup(title=f'Диета — день {idx+1}', content=wrap,
                      size_hint=(0.93, 0.82),
                      background_color=get_color_from_hex('#1A2535'),
                      title_color=get_color_from_hex('#FFD93D'),
                      separator_color=get_color_from_hex('#6BCB77'))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def open_lfk_today(self):
        idx = get_day_index()
        day = LFK_PLAN[idx]
        content = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(14),
                        size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        box.add_widget(Label(text=day['title'], font_size=dp(15), bold=True,
                             color=get_color_from_hex('#FFD93D'),
                             halign='left', text_size=(dp(280), None),
                             size_hint_y=None, height=dp(30)))
        for ex in day['exercises']:
            lbl = Label(text=f"  - {ex}", font_size=dp(13),
                        color=get_color_from_hex('#FFFFFF'),
                        halign='left', text_size=(dp(280), None),
                        size_hint_y=None, height=dp(32))
            box.add_widget(lbl)
        content.add_widget(box)
        close_btn = Button(text='Закрыть', size_hint_y=None, height=dp(44),
                           background_normal='',
                           background_color=get_color_from_hex('#6BCB77'))
        wrap = BoxLayout(orientation='vertical')
        wrap.add_widget(content)
        wrap.add_widget(close_btn)
        popup = Popup(title=f'ЛФК — день {idx+1}', content=wrap,
                      size_hint=(0.93, 0.75),
                      background_color=get_color_from_hex('#1A2535'),
                      title_color=get_color_from_hex('#FFD93D'),
                      separator_color=get_color_from_hex('#6BCB77'))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()


class CalendarScreen(Screen):
    def on_enter(self):
        grid = self.ids.calendar_grid
        grid.clear_widgets()
        today_idx = get_day_index()
        for i in range(30):
            diet = DIET_PLAN[i]
            lfk  = LFK_PLAN[i]
            is_today = (i == today_idx)
            row = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(54), spacing=dp(6), padding=[dp(10), dp(4)])
            bg = get_color_from_hex('#1B4D3E') if is_today else get_color_from_hex('#1E2E3E')
            with row.canvas.before:
                Color(rgba=bg)
                row._bg = RoundedRectangle(size=row.size, pos=row.pos, radius=[dp(8)])
            row.bind(size=lambda w,v: setattr(w._bg,'size',v))
            row.bind(pos=lambda w,v: setattr(w._bg,'pos',v))
            prefix = ">> " if is_today else ""
            row.add_widget(Label(
                text=f"{prefix}День {i+1}",
                font_size=dp(12), bold=is_today,
                color=get_color_from_hex('#FFD93D' if is_today else '#FFFFFF'),
                size_hint_x=0.22, halign='left', text_size=(dp(80), None)))
            row.add_widget(Label(
                text=diet['breakfast'][:26],
                font_size=dp(11), color=get_color_from_hex('#A8C5DA'),
                size_hint_x=0.45, halign='left', text_size=(dp(160), None)))
            row.add_widget(Label(
                text=lfk['title'][:18],
                font_size=dp(11), color=get_color_from_hex('#D8A8F0'),
                size_hint_x=0.33, halign='right', text_size=(dp(110), None)))
            grid.add_widget(row)


class ReminderScreen(Screen):
    pass


class CommunityScreen(Screen):
    def send_message(self, text_input):
        text = text_input.text.strip()
        if not text:
            return
        box = self.ids.chat_box
        msg_row = BoxLayout(orientation='vertical', size_hint_y=None,
                            height=dp(60), padding=[dp(10), dp(6)], spacing=dp(2))
        with msg_row.canvas.before:
            Color(rgba=get_color_from_hex('#1E3A5F'))
            msg_row._bg = RoundedRectangle(size=msg_row.size, pos=msg_row.pos,
                                           radius=[dp(10), dp(10), dp(2), dp(10)])
        msg_row.bind(size=lambda w,v: setattr(w._bg,'size',v))
        msg_row.bind(pos=lambda w,v: setattr(w._bg,'pos',v))
        msg_row.add_widget(Label(text='Вы', font_size=dp(11),
                                 color=get_color_from_hex('#6BCB77'),
                                 halign='left', text_size=(dp(300), None),
                                 size_hint_y=None, height=dp(18)))
        msg_row.add_widget(Label(text=text, font_size=dp(13),
                                 color=get_color_from_hex('#FFFFFF'),
                                 halign='left', text_size=(dp(300), None),
                                 size_hint_y=None, height=dp(26)))
        box.add_widget(msg_row)
        text_input.text = ''
        Clock.schedule_once(lambda dt: setattr(self.ids.chat_scroll, 'scroll_y', 0), 0.1)


class WeatherScreen(Screen):
    loading    = BooleanProperty(False)
    error_text = StringProperty('')

    WEATHER_CODES = {
        0:'Ясно', 1:'Преим. ясно', 2:'Переменная облачность',
        3:'Пасмурно', 45:'Туман', 48:'Иней',
        51:'Легкая морось', 61:'Дождь', 63:'Умеренный дождь',
        65:'Сильный дождь', 71:'Снег', 80:'Ливень', 95:'Гроза',
    }

    def fetch_weather(self, city):
        self.loading = True
        self.error_text = ''
        self.ids.weather_cards.clear_widgets()
        threading.Thread(target=self._fetch_thread, args=(city.strip() or 'Алматы',), daemon=True).start()

    def _fetch_thread(self, city_name):
        try:
            geo_url = (f"https://geocoding-api.open-meteo.com/v1/search"
                       f"?name={urllib.parse.quote(city_name)}&count=1&language=ru&format=json")
            with urllib.request.urlopen(geo_url, timeout=10) as r:
                geo = json.loads(r.read())
            results = geo.get('results', [])
            if not results:
                Clock.schedule_once(lambda dt: setattr(self, 'error_text', 'Город не найден'))
                Clock.schedule_once(lambda dt: setattr(self, 'loading', False))
                return
            lat  = results[0]['latitude']
            lon  = results[0]['longitude']
            name = results[0].get('name', city_name)
            wx_url = (f"https://api.open-meteo.com/v1/forecast"
                      f"?latitude={lat}&longitude={lon}"
                      f"&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum"
                      f"&timezone=auto&forecast_days=2")
            with urllib.request.urlopen(wx_url, timeout=10) as r:
                wx = json.loads(r.read())
            daily = wx['daily']
            data = []
            for i in range(2):
                data.append({
                    'day':    'Сегодня' if i == 0 else 'Завтра',
                    'date':   daily['time'][i],
                    'desc':   self.WEATHER_CODES.get(daily['weathercode'][i], 'Данные получены'),
                    'tmax':   f"{daily['temperature_2m_max'][i]:.0f}",
                    'tmin':   f"{daily['temperature_2m_min'][i]:.0f}",
                    'precip': f"{daily['precipitation_sum'][i]:.1f}",
                    'city':   name,
                })
            Clock.schedule_once(lambda dt: self._build_cards(data))
        except Exception as e:
            msg = f'Ошибка соединения\n{str(e)[:50]}'
            Clock.schedule_once(lambda dt: setattr(self, 'error_text', msg))
            Clock.schedule_once(lambda dt: setattr(self, 'loading', False))

    def _build_cards(self, data):
        self.loading = False
        box = self.ids.weather_cards
        box.clear_widgets()
        colors = ['#1E3A5F', '#1B4D3E']
        for i, d in enumerate(data):
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150),
                             padding=[dp(16), dp(12)], spacing=dp(6))
            with card.canvas.before:
                Color(rgba=get_color_from_hex(colors[i]))
                card._bg = RoundedRectangle(size=card.size, pos=card.pos, radius=[dp(14)])
            card.bind(size=lambda w,v: setattr(w._bg,'size',v))
            card.bind(pos=lambda w,v: setattr(w._bg,'pos',v))
            card.add_widget(Label(
                text=f"{d['day']}  {d['date']}  | {d['city']}",
                font_size=dp(13), bold=True, color=get_color_from_hex('#FFD93D'),
                halign='left', text_size=(dp(340), None), size_hint_y=None, height=dp(24)))
            card.add_widget(Label(
                text=d['desc'], font_size=dp(18), bold=True,
                color=get_color_from_hex('#FFFFFF'),
                halign='left', text_size=(dp(340), None), size_hint_y=None, height=dp(34)))
            card.add_widget(Label(
                text=f"Макс: {d['tmax']}C  |  Мин: {d['tmin']}C",
                font_size=dp(14), color=get_color_from_hex('#FFFFFF'),
                halign='left', text_size=(dp(340), None), size_hint_y=None, height=dp(24)))
            card.add_widget(Label(
                text=f"Осадки: {d['precip']} мм",
                font_size=dp(12), color=get_color_from_hex('#A8C5DA'),
                halign='left', text_size=(dp(340), None), size_hint_y=None, height=dp(22)))
            box.add_widget(card)


class SettingsScreen(Screen):
    dark_mode      = BooleanProperty(False)
    notif_screen   = BooleanProperty(True)
    notif_enabled  = BooleanProperty(True)
    pin_enabled    = BooleanProperty(False)
    is_guest       = BooleanProperty(True)

    def on_enter(self):
        self.dark_mode     = get_setting('dark_mode',     False)
        self.notif_screen  = get_setting('notif_screen',  True)
        self.notif_enabled = get_setting('notif_enabled', True)
        self.pin_enabled   = get_setting('pin_enabled',   False)
        self.is_guest      = get_setting('is_guest',      True)

    def toggle_dark(self, value):
        self.dark_mode = value
        set_setting('dark_mode', value)

    def toggle_notif_screen(self, value):
        self.notif_screen = value
        set_setting('notif_screen', value)

    def toggle_notif(self, value):
        self.notif_enabled = value
        set_setting('notif_enabled', value)

    def set_pin(self):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(14))
        inp = TextInput(hint_text='Введите 4-значный PIN', input_filter='int',
                        multiline=False, password=True,
                        background_color=get_color_from_hex('#1E2E3E'),
                        foreground_color=get_color_from_hex('#FFFFFF'),
                        hint_text_color=get_color_from_hex('#A8C5DA'),
                        font_size=dp(16), size_hint_y=None, height=dp(44))
        content.add_widget(inp)
        row = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(44))
        popup = Popup(title='Установить PIN', content=content,
                      size_hint=(0.85, None), height=dp(180),
                      background_color=get_color_from_hex('#1A2535'),
                      title_color=get_color_from_hex('#FFD93D'))
        ok = Button(text='Сохранить', background_normal='',
                    background_color=get_color_from_hex('#6BCB77'))
        cancel = Button(text='Отмена', background_normal='',
                        background_color=get_color_from_hex('#555'))
        def save(*a):
            if len(inp.text) == 4:
                set_setting('pin_code', inp.text)
                set_setting('pin_enabled', True)
                self.pin_enabled = True
                popup.dismiss()
            else:
                inp.hint_text = 'Нужно ровно 4 цифры!'
        ok.bind(on_release=save)
        cancel.bind(on_release=popup.dismiss)
        row.add_widget(cancel)
        row.add_widget(ok)
        content.add_widget(row)
        popup.open()

    def invite_friends(self):
        show_popup('Приглашение', 'Приложения нет\nв открытом доступе')

    def delete_profile(self):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(14))
        content.add_widget(Label(text='Вы уверены, что хотите\nудалить профиль?',
                                 halign='center', color=get_color_from_hex('#FFFFFF'),
                                 font_size=dp(14)))
        row = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(44))
        popup = Popup(title='Удаление профиля', content=content,
                      size_hint=(0.85, None), height=dp(180),
                      background_color=get_color_from_hex('#1A2535'),
                      title_color=get_color_from_hex('#FFD93D'))
        yes = Button(text='Удалить', background_normal='',
                     background_color=get_color_from_hex('#E74C3C'))
        no  = Button(text='Отмена', background_normal='',
                     background_color=get_color_from_hex('#555'))
        def confirm(*a):
            try:
                store.delete('settings')
            except Exception:
                pass
            popup.dismiss()
            self.manager.current = 'main'
        yes.bind(on_release=confirm)
        no.bind(on_release=popup.dismiss)
        row.add_widget(no)
        row.add_widget(yes)
        content.add_widget(row)
        popup.open()

    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'app_screen'


# ──────────────────────────────────────────────────
#  APP
# ──────────────────────────────────────────────────
class HealthMateApp(App):
    def build(self):
        self.title = 'HealthMate'
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(AppScreen(name='app_screen'))
        sm.add_widget(CalendarScreen(name='calendar'))
        sm.add_widget(ReminderScreen(name='reminder'))
        sm.add_widget(CommunityScreen(name='community'))
        sm.add_widget(WeatherScreen(name='weather'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

if __name__ == '__main__':
    HealthMateApp().run()
