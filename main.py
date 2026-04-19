import json
import os
from datetime import datetime, date
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.switch import Switch
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.storage.jsonstore import JsonStore
import urllib.request
import urllib.parse
import threading

Window.size = (400, 700)

# ─────────────────────────────────────────────
#  ДАННЫЕ: Диета №15 на 30 дней
# ─────────────────────────────────────────────
DIET_PLAN = [
    # День 1
    {
        "breakfast": "Овсяная каша на воде с яблоком и корицей\nЧай без сахара",
        "lunch":     "Куриный суп с овощами\nХлеб цельнозерновой",
        "snack":     "Кефир 1% — 200 мл\nГруша",
        "dinner":    "Запечённая куриная грудка с брокколи\nГречка отварная",
    },
    # День 2
    {
        "breakfast": "Творог 5% с мёдом и орехами\nТравяной чай",
        "lunch":     "Суп-пюре из тыквы\nОтварная индейка 150 г",
        "snack":     "Яблоко запечённое\nМиндаль 20 г",
        "dinner":    "Рыба на пару (хек/минтай)\nОтварной рис бурый",
    },
    # День 3
    {
        "breakfast": "Яйца всмятку 2 шт\nОгурец, помидор\nЦельнозерновой тост",
        "lunch":     "Борщ без зажарки\nКусочек куриной грудки",
        "snack":     "Смузи: банан + кефир",
        "dinner":    "Тушёные овощи с индейкой\nПшено отварное",
    },
    # День 4
    {
        "breakfast": "Манная каша на молоке 1.5%\nЯгоды замороженные",
        "lunch":     "Щи из свежей капусты\nОтварная говядина нежирная 120 г",
        "snack":     "Кефир\nЦельнозерновой хлебец",
        "dinner":    "Запечённый минтай с лимоном\nОтварная гречка",
    },
    # День 5
    {
        "breakfast": "Гречневая каша молочная\nЧай с лимоном",
        "lunch":     "Уха из горбуши\nОвощной салат с оливковым маслом",
        "snack":     "Творог 0% с ягодами",
        "dinner":    "Паровые котлеты из куриного фарша\nОтварная цветная капуста",
    },
    # День 6
    {
        "breakfast": "Омлет 2 яйца + молоко\nОгурец\nЧай",
        "lunch":     "Рисовый суп с курицей\nЦельнозерновой хлеб",
        "snack":     "Банан\nГрецкий орех 15 г",
        "dinner":    "Запечённое куриное филе с перцем\nОтварной картофель 150 г",
    },
    # День 7
    {
        "breakfast": "Пшённая каша с тыквой\nКомпот без сахара",
        "lunch":     "Овощной суп-минестроне\nОтварная телятина 120 г",
        "snack":     "Йогурт натуральный\nКивиягода",
        "dinner":    "Треска запечённая в фольге\nОтварной зелёный горошек",
    },
    # День 8
    {
        "breakfast": "Мюсли без сахара + молоко\nЗелёный чай",
        "lunch":     "Гороховый суп без копчёностей\nКуриная котлета паровая",
        "snack":     "Кефир 200 мл\nХлебец с отрубями",
        "dinner":    "Тушёная капуста с куриным филе\nОтварная гречка",
    },
    # День 9
    {
        "breakfast": "Творожная запеканка без сахара\nЧай",
        "lunch":     "Куриный бульон с вермишелью\nОвощной салат",
        "snack":     "Яблоко\nМиндаль 20 г",
        "dinner":    "Запечённый лосось\nОтварной рис",
    },
    # День 10
    {
        "breakfast": "Геркулесовая каша с изюмом\nТравяной чай",
        "lunch":     "Суп из чечевицы\nОтварная индейка",
        "snack":     "Смузи: шпинат + яблоко + кефир",
        "dinner":    "Паровые рыбные котлеты\nОтварная брокколи",
    },
    # День 11
    {
        "breakfast": "Яичница на оливковом масле\nПомидор\nЦельнозерновой тост",
        "lunch":     "Суп с фрикадельками (куриный фарш)\nОтварной картофель",
        "snack":     "Творог с мёдом",
        "dinner":    "Тушёная говядина с овощами\nОтварная гречка",
    },
    # День 12
    {
        "breakfast": "Рисовая каша на молоке\nЧай с молоком",
        "lunch":     "Окрошка (кефирная)\nОтварная куриная грудка",
        "snack":     "Грейпфрут\nКешью 15 г",
        "dinner":    "Запечённая треска с овощами\nОтварной рис бурый",
    },
    # День 13
    {
        "breakfast": "Овсянка с бананом и мёдом\nКофе с молоком",
        "lunch":     "Суп-лапша куриная\nОвощной салат",
        "snack":     "Кефир\nХлебец",
        "dinner":    "Куриное филе тушёное с грибами\nОтварное пшено",
    },
    # День 14
    {
        "breakfast": "Гречка отварная + яйцо\nЧай",
        "lunch":     "Рассольник без зажарки\nОтварная говядина",
        "snack":     "Йогурт натуральный\nГруша",
        "dinner":    "Паровой хек с лимоном\nОтварная цветная капуста",
    },
    # День 15
    {
        "breakfast": "Творог 5% + банан + корица\nТравяной чай",
        "lunch":     "Суп из кабачков\nКуриная котлета паровая",
        "snack":     "Яблоко\nФундук 20 г",
        "dinner":    "Запечённая индейка с перцем\nОтварной картофель",
    },
    # День 16
    {
        "breakfast": "Пшённая каша с молоком\nКомпот",
        "lunch":     "Борщ (постный)\nОтварная куриная грудка",
        "snack":     "Смузи: клубника + кефир",
        "dinner":    "Запечённый минтай\nОтварная гречка",
    },
    # День 17
    {
        "breakfast": "Омлет с овощами (болгарский перец, помидор)\nЧай",
        "lunch":     "Уха из трески\nЦельнозерновой хлеб",
        "snack":     "Кефир\nХлебец с отрубями",
        "dinner":    "Тушёные кабачки с индейкой\nОтварной рис",
    },
    # День 18
    {
        "breakfast": "Геркулес с черникой\nЗелёный чай",
        "lunch":     "Суп гречневый с курицей\nОвощной салат",
        "snack":     "Банан\nМиндаль 15 г",
        "dinner":    "Паровые котлеты говяжьи\nОтварная брокколи",
    },
    # День 19
    {
        "breakfast": "Яйца всмятку 2 шт\nОгурец\nЦельнозерновой тост",
        "lunch":     "Суп-пюре из горошка\nОтварная индейка",
        "snack":     "Творог 0% с кивиягодой",
        "dinner":    "Запечённый лосось с зеленью\nОтварной картофель",
    },
    # День 20
    {
        "breakfast": "Манная каша на молоке\nЧай с лимоном",
        "lunch":     "Щи с грибами\nОтварная куриная грудка",
        "snack":     "Кефир\nГруша",
        "dinner":    "Тушёная рыба с морковью\nОтварное пшено",
    },
    # День 21
    {
        "breakfast": "Гречка молочная\nТравяной чай",
        "lunch":     "Рисовый суп с курицей\nЦельнозерновой хлеб",
        "snack":     "Смузи: шпинат + банан + кефир",
        "dinner":    "Куриное филе запечённое\nОтварная гречка",
    },
    # День 22
    {
        "breakfast": "Творожная запеканка\nЧай",
        "lunch":     "Суп с чечевицей\nПаровая котлета",
        "snack":     "Яблоко запечённое\nОрехи 20 г",
        "dinner":    "Треска на пару с лимоном\nОтварной рис бурый",
    },
    # День 23
    {
        "breakfast": "Овсяная каша с яблоком\nКофе с молоком",
        "lunch":     "Борщ с телятиной\nЦельнозерновой хлеб",
        "snack":     "Йогурт натуральный\nКивиягода",
        "dinner":    "Запечённая индейка с брокколи\nОтварной картофель",
    },
    # День 24
    {
        "breakfast": "Мюсли + молоко\nЗелёный чай",
        "lunch":     "Куриный суп с рисом\nОвощной салат",
        "snack":     "Кефир\nХлебец",
        "dinner":    "Паровой минтай\nОтварная цветная капуста",
    },
    # День 25
    {
        "breakfast": "Яичница с помидором\nЦельнозерновой тост\nЧай",
        "lunch":     "Суп с фрикадельками\nОтварной картофель",
        "snack":     "Смузи: малина + творог",
        "dinner":    "Тушёная говядина с тушёными овощами\nОтварная гречка",
    },
    # День 26
    {
        "breakfast": "Пшённая каша с тыквой и мёдом\nТравяной чай",
        "lunch":     "Гороховый суп\nОтварная курица",
        "snack":     "Банан\nМиндаль 20 г",
        "dinner":    "Запечённый хек с морковью\nОтварной рис",
    },
    # День 27
    {
        "breakfast": "Геркулес с изюмом и орехами\nЧай с молоком",
        "lunch":     "Суп-лапша с индейкой\nОвощной салат",
        "snack":     "Творог с мёдом\nГруша",
        "dinner":    "Куриное филе тушёное с кабачком\nОтварная гречка",
    },
    # День 28
    {
        "breakfast": "Омлет 2 яйца + зелень\nОгурец\nЧай",
        "lunch":     "Рассольник\nОтварная телятина",
        "snack":     "Кефир\nЦельнозерновой хлебец",
        "dinner":    "Лосось запечённый\nОтварная брокколи",
    },
    # День 29
    {
        "breakfast": "Гречка с яйцом вкрутую\nЧай с лимоном",
        "lunch":     "Суп из кабачков с рисом\nПаровая котлета",
        "snack":     "Смузи: яблоко + кефир + корица",
        "dinner":    "Запечённая индейка\nОтварное пшено",
    },
    # День 30
    {
        "breakfast": "Творог 5% с ягодами\nМёд\nТравяной чай",
        "lunch":     "Борщ с говядиной\nЦельнозерновой хлеб",
        "snack":     "Йогурт натуральный\nКивиягода",
        "dinner":    "Рыба на пару\nОтварная гречка\nОвощной салат",
    },
]

# ─────────────────────────────────────────────
#  ДАННЫЕ: ЛФК на 30 дней (для пострадавших, реабилитация)
# ─────────────────────────────────────────────
LFK_PLAN = [
    {"title": "Дыхательная гимнастика", "exercises": [
        "Диафрагмальное дыхание — 10 мин",
        "Медленные вдохи через нос — 15 раз",
        "Выдох через губы трубочкой — 15 раз",
        "Лёжа: подъём рук на вдохе — 10 раз",
    ]},
    {"title": "Суставная разминка", "exercises": [
        "Вращение кистями — 10 раз в каждую сторону",
        "Вращение локтями — 10 раз",
        "Вращение плечами — 10 раз",
        "Наклоны головы вперёд-назад — 8 раз",
    ]},
    {"title": "Упражнения лёжа", "exercises": [
        "Сжимание-разжимание пальцев рук — 15 раз",
        "Подъём прямой ноги лёжа — 10 раз каждая",
        "Велосипед лёжа — 30 сек",
        "Мост (ягодицы вверх) — 10 раз",
    ]},
    {"title": "Упражнения сидя", "exercises": [
        "Подъём на носки сидя — 15 раз",
        "Разгибание ноги в колене — 10 раз каждая",
        "Наклоны туловища в стороны — 8 раз",
        "Повороты корпуса — 8 раз",
    ]},
    {"title": "Лёгкая растяжка", "exercises": [
        "Растяжка плечевого пояса — 2 мин",
        "Наклон к ногам сидя — 10 раз",
        "Растяжка икр у стены — 1 мин каждая",
        "Кошка-корова (спина) — 10 раз",
    ]},
    {"title": "Дыхание + релаксация", "exercises": [
        "Глубокое брюшное дыхание — 5 мин",
        "Прогрессивная мышечная релаксация — 10 мин",
        "Медитация лёжа — 5 мин",
    ]},
    {"title": "Ходьба и равновесие", "exercises": [
        "Медленная ходьба дома — 10 мин",
        "Стойка на одной ноге — 30 сек каждая",
        "Ходьба пятками — 2 мин",
        "Ходьба на носках — 2 мин",
    ]},
    {"title": "Упражнения для рук", "exercises": [
        "Сжимание мячика — 15 раз",
        "Подъём рук вперёд с гантелью 0.5 кг — 10 раз",
        "Разведение рук в стороны — 10 раз",
        "Растяжка пальцев — 2 мин",
    ]},
    {"title": "Укрепление спины", "exercises": [
        "Лодочка лёжа на животе — 10 раз",
        "Кошка-корова — 10 раз",
        "Боковые наклоны стоя — 10 раз",
        "Медленные повороты шеи — 8 раз",
    ]},
    {"title": "Упражнения для ног", "exercises": [
        "Подъём ног лёжа — 10 раз каждая",
        "Сгибание-разгибание колен стоя — 15 раз",
        "Отведение ноги в сторону — 10 раз",
        "Тяга пятки к ягодице стоя — 10 раз",
    ]},
    {"title": "Координация", "exercises": [
        "Ходьба по линии — 2 мин",
        "Перешагивание предметов — 5 мин",
        "Марш на месте — 3 мин",
        "Рисование ногой восьмёрок — 10 раз",
    ]},
    {"title": "Укрепление пресса (мягкое)", "exercises": [
        "Подъём головы лёжа — 10 раз",
        "Втягивание живота — 10 раз по 5 сек",
        "Подъём ног согнутых — 10 раз",
        "Боковые скручивания — 8 раз",
    ]},
    {"title": "Дыхательная + суставная", "exercises": [
        "Полное дыхание (3 фазы) — 5 мин",
        "Вращение голеностопом — 10 раз",
        "Вращение тазом стоя — 10 раз",
        "Потягивание всего тела — 2 мин",
    ]},
    {"title": "Активный день", "exercises": [
        "Ходьба на свежем воздухе — 20 мин",
        "Приседания с опорой — 10 раз",
        "Подъём на носки стоя — 15 раз",
        "Растяжка всего тела — 5 мин",
    ]},
    {"title": "Восстановление", "exercises": [
        "Массаж кистей — 5 мин",
        "Тёплая ванна для ног — 10 мин",
        "Глубокое дыхание — 5 мин",
        "Лёгкая растяжка перед сном — 5 мин",
    ]},
    {"title": "Упражнения для равновесия", "exercises": [
        "Стойка у стены на носках — 1 мин",
        "Перекаты с пятки на носок — 15 раз",
        "Лёгкое покачивание стоя — 2 мин",
        "Ходьба с изменением направления — 5 мин",
    ]},
    {"title": "Комплекс для плеч", "exercises": [
        "Пожимание плечами — 15 раз",
        "Вращение плечами — 10 раз",
        "Разведение лопаток — 10 раз",
        "Наклоны головы с растяжкой — 8 раз",
    ]},
    {"title": "Лёжа + дыхание", "exercises": [
        "Подъём таза (мост) — 10 раз",
        "Велосипед — 30 сек",
        "Дыхательные упражнения — 5 мин",
        "Расслабление тела поочерёдно — 5 мин",
    ]},
    {"title": "Мягкая нагрузка", "exercises": [
        "Ходьба по комнате — 15 мин",
        "Подъём на носки — 15 раз",
        "Марш с высоким подъёмом колен — 2 мин",
        "Растяжка икр — 2 мин",
    ]},
    {"title": "Укрепление кора", "exercises": [
        "Планка на локтях — 20 сек",
        "Боковая планка — 15 сек каждая",
        "Подъём противоположных руки/ноги — 10 раз",
        "Скручивания мягкие — 10 раз",
    ]},
    {"title": "День растяжки", "exercises": [
        "Растяжка всего тела лёжа — 5 мин",
        "Растяжка бёдер — 2 мин каждое",
        "Растяжка плеч — 2 мин",
        "Йога: поза ребёнка — 3 мин",
    ]},
    {"title": "Активация", "exercises": [
        "Прыжки на месте мягкие — 30 сек",
        "Приседания — 10 раз",
        "Выпады вперёд — 8 раз каждая нога",
        "Ходьба на месте — 5 мин",
    ]},
    {"title": "Суставная + дыхание", "exercises": [
        "Вращение всех суставов поочерёдно — 10 мин",
        "Полное дыхание — 5 мин",
        "Потягивание — 2 мин",
    ]},
    {"title": "Упражнения с сопротивлением", "exercises": [
        "Эспандер: сгибание руки — 10 раз",
        "Эспандер: разгибание — 10 раз",
        "Подъём ноги с эспандером — 10 раз",
        "Растяжка с эспандером — 2 мин",
    ]},
    {"title": "Дыхательная + осанка", "exercises": [
        "Дыхание у стены (спина ровная) — 5 мин",
        "Прогиб назад у стены — 10 раз",
        "Стойка у стены с правильной осанкой — 3 мин",
        "Растяжка грудного отдела — 2 мин",
    ]},
    {"title": "Лёгкий кардио день", "exercises": [
        "Ходьба — 25 мин",
        "Подъём-спуск по ступеням — 5 мин",
        "Растяжка после ходьбы — 5 мин",
    ]},
    {"title": "Полное расслабление", "exercises": [
        "Глубокое дыхание — 10 мин",
        "Йога: шавасана — 10 мин",
        "Мягкий самомассаж — 10 мин",
    ]},
    {"title": "Укрепление ног", "exercises": [
        "Приседания у стены — 10 раз",
        "Шаги в сторону — 15 раз",
        "Подъём на носки — 20 раз",
        "Растяжка бёдер стоя — 2 мин каждое",
    ]},
    {"title": "Комплекс для рук и плеч", "exercises": [
        "Отжимания от стены — 10 раз",
        "Разведение рук с гантелями — 10 раз",
        "Подъём рук вперёд — 10 раз",
        "Растяжка плечевого пояса — 3 мин",
    ]},
    {"title": "Итоговая тренировка месяца", "exercises": [
        "Дыхательная разминка — 3 мин",
        "Суставная гимнастика — 5 мин",
        "Ходьба — 15 мин",
        "Упражнения на кор — 5 мин",
        "Растяжка всего тела — 5 мин",
        "Релаксация — 5 мин",
    ]},
]

# ─────────────────────────────────────────────
#  НАПОМИНАНИЯ (фиксированные)
# ─────────────────────────────────────────────
REMINDERS = [
    {"time": "08:00", "label": "Завтрак", "icon": "🍳"},
    {"time": "12:00", "label": "Обед",    "icon": "🥗"},
    {"time": "16:00", "label": "Полдник", "icon": "🍎"},
    {"time": "18:00", "label": "Ужин",    "icon": "🍽️"},
    {"time": "22:00", "label": "Сон",     "icon": "🌙"},
]

# ─────────────────────────────────────────────
#  ХРАНИЛИЩЕ НАСТРОЕК
# ─────────────────────────────────────────────
store = JsonStore('healthmate_data.json')

def get_setting(key, default=None):
    try:
        if store.exists('settings'):
            d = store.get('settings')
            return d.get(key, default)
    except Exception:
        pass
    return default

def set_setting(key, value):
    try:
        d = {}
        if store.exists('settings'):
            d = dict(store.get('settings'))
        d[key] = value
        store.put('settings', **d)
    except Exception:
        pass

# ─────────────────────────────────────────────
#  ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДНЯ
# ─────────────────────────────────────────────
def get_day_index():
    """Возвращает индекс дня в цикле 0-29 на основе дня года."""
    return (date.today().timetuple().tm_yday - 1) % 30

# ─────────────────────────────────────────────
#  ЭКРАНЫ
# ─────────────────────────────────────────────
class NavButton(ButtonBehavior, Image):
    pass

class MainScreen(Screen):
    date_text = StringProperty('')

    def on_enter(self):
        self.update_date()
        Clock.schedule_interval(lambda dt: self.update_date(), 60)

    def update_date(self):
        now = datetime.now()
        months = ['января','февраля','марта','апреля','мая','июня',
                  'июля','августа','сентября','октября','ноября','декабря']
        self.date_text = f"{now.day} {months[now.month-1]} {now.year}"

    def on_leave(self):
        Clock.unschedule(self.update_date)


class LoginScreen(Screen):
    def show_unavailable(self):
        self._show_popup('ℹ️', 'Регистрация и вход\nбудут доступны в следующем обновлении')

    def guest_login(self):
        set_setting('is_guest', True)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'app_screen'

    def _show_popup(self, title, text):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=text, halign='center', color=(0.2,0.2,0.2,1)))
        btn = Button(text='OK', size_hint_y=None, height=40,
                     background_color=get_color_from_hex('#6BCB77'))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.35))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()


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
        content = ScrollView()
        box = BoxLayout(orientation='vertical', spacing=8, padding=12,
                        size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        items = [
            ("🍳 Завтрак", day["breakfast"]),
            ("🥗 Обед",    day["lunch"]),
            ("🍎 Полдник", day["snack"]),
            ("🍽️ Ужин",   day["dinner"]),
        ]
        for title, text in items:
            box.add_widget(Label(
                text=f"[b]{title}[/b]\n{text}",
                markup=True, halign='left', valign='top',
                color=(0.15,0.15,0.15,1),
                size_hint_y=None, height=90,
                text_size=(320, None)
            ))
        content.add_widget(box)
        popup = Popup(
            title=f'Диета — день {idx+1}',
            content=content,
            size_hint=(0.92, 0.75)
        )
        popup.open()

    def open_lfk_today(self):
        idx = get_day_index()
        day = LFK_PLAN[idx]
        content = ScrollView()
        box = BoxLayout(orientation='vertical', spacing=8, padding=12,
                        size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        box.add_widget(Label(
            text=f"[b]💪 {day['title']}[/b]",
            markup=True, halign='left', color=(0.15,0.15,0.15,1),
            size_hint_y=None, height=40
        ))
        for ex in day['exercises']:
            box.add_widget(Label(
                text=f"• {ex}",
                halign='left', valign='top',
                color=(0.2,0.2,0.2,1),
                size_hint_y=None, height=36,
                text_size=(320, None)
            ))
        content.add_widget(box)
        popup = Popup(
            title=f'ЛФК — день {idx+1}',
            content=content,
            size_hint=(0.92, 0.6)
        )
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
            bg = get_color_from_hex('#1B4D3E') if is_today else get_color_from_hex('#1E2E3E')
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(52),
                spacing=8,
                padding=[12, 4]
            )
            with row.canvas.before:
                from kivy.graphics import Color as KColor, RoundedRectangle as KRR
                r, g, b, a = bg
                KColor(rgba=(r, g, b, a))
                row._rect = KRR(size=row.size, pos=row.pos, radius=[10])
            row.bind(size=lambda w, v: setattr(w._rect, 'size', v))
            row.bind(pos=lambda w, v: setattr(w._rect, 'pos', v))
            day_label = Label(
                text=f"{'→ ' if is_today else ''}День {i+1}",
                font_size='13sp',
                bold=is_today,
                color=get_color_from_hex('#FFD93D' if is_today else '#FFFFFF'),
                size_hint_x=0.22,
                halign='left',
                text_size=(None, None)
            )
            diet_label = Label(
                text=diet['breakfast'].split('\n')[0][:28],
                font_size='11sp',
                color=get_color_from_hex('#A8C5DA'),
                size_hint_x=0.45,
                halign='left',
                text_size=(None, None)
            )
            lfk_label = Label(
                text=lfk['title'][:20],
                font_size='11sp',
                color=get_color_from_hex('#D8A8F0'),
                size_hint_x=0.33,
                halign='right',
                text_size=(None, None)
            )
            row.add_widget(day_label)
            row.add_widget(diet_label)
            row.add_widget(lfk_label)
            grid.add_widget(row)


class ReminderScreen(Screen):
    pass


class CommunityScreen(Screen):
    messages = ListProperty([])

    def on_enter(self):
        if not self.messages:
            self.messages = [
                ("Тренер Алина", "Привет! Добро пожаловать в чат 💚"),
                ("Михаил",       "Уже 2 недели занимаюсь по программе — чувствую себя лучше!"),
                ("Тренер Алина", "Отлично, Михаил! Продолжай в том же духе 🎯"),
                ("Светлана",     "Сегодня сделала всё ЛФК расписание. Горжусь собой 🙌"),
                ("Дмитрий",      "Кто ещё занимается дыхательной гимнастикой утром?"),
            ]

    def send_message(self, text_input):
        text = text_input.text.strip()
        if text:
            self.messages.append(("Вы", text))
            text_input.text = ''
            self.ids.chat_scroll.scroll_y = 0


class WeatherScreen(Screen):
    city_name   = StringProperty('Алматы')
    weather_data = ListProperty([])
    loading      = BooleanProperty(False)
    error_text   = StringProperty('')

    WEATHER_CODES = {
        0:'☀️ Ясно', 1:'🌤️ Преим. ясно', 2:'⛅ Переменная облачность',
        3:'☁️ Пасмурно', 45:'🌫️ Туман', 48:'🌫️ Иней',
        51:'🌦️ Лёгкая морось', 61:'🌧️ Дождь', 63:'🌧️ Умер. дождь',
        65:'🌧️ Сильный дождь', 71:'❄️ Снег', 80:'🌦️ Ливень',
        95:'⛈️ Гроза',
    }

    def fetch_weather(self, city):
        self.city_name  = city.strip() or 'Алматы'
        self.loading    = True
        self.error_text = ''
        self.weather_data = []
        threading.Thread(target=self._fetch_thread, daemon=True).start()

    def _fetch_thread(self):
        try:
            geo_url = (
                f"https://geocoding-api.open-meteo.com/v1/search"
                f"?name={urllib.parse.quote(self.city_name)}&count=1&language=ru&format=json"
            )
            with urllib.request.urlopen(geo_url, timeout=10) as r:
                geo = json.loads(r.read())
            results = geo.get('results', [])
            if not results:
                Clock.schedule_once(lambda dt: self._set_error('Город не найден'))
                return
            lat  = results[0]['latitude']
            lon  = results[0]['longitude']
            name = results[0].get('name', self.city_name)
            wx_url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum"
                f"&timezone=auto&forecast_days=2"
            )
            with urllib.request.urlopen(wx_url, timeout=10) as r:
                wx = json.loads(r.read())
            daily  = wx['daily']
            dates  = daily['time']
            codes  = daily['weathercode']
            t_max  = daily['temperature_2m_max']
            t_min  = daily['temperature_2m_min']
            precip = daily['precipitation_sum']
            data = []
            day_names = ['Сегодня', 'Завтра']
            for i in range(2):
                desc = self.WEATHER_CODES.get(codes[i], '🌡️ Данные получены')
                data.append({
                    'day':    day_names[i],
                    'date':   dates[i],
                    'desc':   desc,
                    'tmax':   f"{t_max[i]:.0f}°C",
                    'tmin':   f"{t_min[i]:.0f}°C",
                    'precip': f"{precip[i]:.1f} мм",
                    'city':   name,
                })
            Clock.schedule_once(lambda dt: self._set_data(data))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._set_error(f'Ошибка: {str(e)[:60]}'))

    def _set_data(self, data):
        self.weather_data = data
        self.loading = False
        self._build_weather_cards(data)

    def _build_weather_cards(self, data):
        try:
            cards_box = self.ids.weather_cards
            cards_box.clear_widgets()
            for d in data:
                card = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(160),
                    padding=[16, 14],
                    spacing=6
                )
                bg_color = get_color_from_hex('#1E3A5F') if d['day'] == 'Сегодня' else get_color_from_hex('#1B4D3E')
                with card.canvas.before:
                    from kivy.graphics import Color as KC, RoundedRectangle as KR
                    r, g, b, a = bg_color
                    KC(rgba=(r, g, b, a))
                    card._rect = KR(size=card.size, pos=card.pos, radius=[16])
                card.bind(size=lambda w,v: setattr(w._rect,'size',v))
                card.bind(pos=lambda w,v: setattr(w._rect,'pos',v))

                header = Label(
                    text=f"[b]{d['day']}[/b]  {d['date']}  📍 {d['city']}",
                    markup=True,
                    font_size='14sp',
                    color=get_color_from_hex('#FFD93D'),
                    halign='left',
                    text_size=(350, None),
                    size_hint_y=None,
                    height=dp(28)
                )
                desc = Label(
                    text=d['desc'],
                    font_size='24sp',
                    halign='left',
                    text_size=(350, None),
                    size_hint_y=None,
                    height=dp(40)
                )
                temps = Label(
                    text=f"🌡️  Макс: {d['tmax']}   Мин: {d['tmin']}",
                    font_size='14sp',
                    color=get_color_from_hex('#FFFFFF'),
                    halign='left',
                    text_size=(350, None),
                    size_hint_y=None,
                    height=dp(26)
                )
                precip = Label(
                    text=f"💧 Осадки: {d['precip']}",
                    font_size='13sp',
                    color=get_color_from_hex('#A8C5DA'),
                    halign='left',
                    text_size=(350, None),
                    size_hint_y=None,
                    height=dp(24)
                )
                card.add_widget(header)
                card.add_widget(desc)
                card.add_widget(temps)
                card.add_widget(precip)
                cards_box.add_widget(card)
        except Exception:
            pass

    def _set_error(self, msg):
        self.error_text = msg
        self.loading = False


class SettingsScreen(Screen):
    dark_mode           = BooleanProperty(False)
    notif_screen        = BooleanProperty(True)
    notif_enabled       = BooleanProperty(True)
    pin_enabled         = BooleanProperty(False)
    is_guest            = BooleanProperty(True)

    def on_enter(self):
        self.dark_mode    = get_setting('dark_mode',    False)
        self.notif_screen = get_setting('notif_screen', True)
        self.notif_enabled= get_setting('notif_enabled',True)
        self.pin_enabled  = get_setting('pin_enabled',  False)
        self.is_guest     = get_setting('is_guest',     True)

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
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        inp = TextInput(hint_text='Введите 4-значный PIN',
                        input_filter='int', multiline=False,
                        password=True, max_chars=4)
        content.add_widget(inp)
        btn_row = BoxLayout(spacing=8, size_hint_y=None, height=44)
        popup = Popup(title='🔒 Установить PIN', content=content, size_hint=(0.8,0.4))
        ok = Button(text='Сохранить',
                    background_color=get_color_from_hex('#6BCB77'))
        cancel = Button(text='Отмена',
                        background_color=get_color_from_hex('#cccccc'))
        def save(*a):
            if len(inp.text) == 4:
                set_setting('pin_code', inp.text)
                set_setting('pin_enabled', True)
                self.pin_enabled = True
                popup.dismiss()
            else:
                inp.hint_text = 'Нужно 4 цифры!'
        ok.bind(on_release=save)
        cancel.bind(on_release=popup.dismiss)
        btn_row.add_widget(cancel)
        btn_row.add_widget(ok)
        content.add_widget(btn_row)
        popup.open()

    def invite_friends(self):
        self._popup('ℹ️ Приглашение', 'Приложения нет в открытом доступе')

    def delete_profile(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=12)
        content.add_widget(Label(
            text='Вы уверены, что хотите\nудалить профиль?',
            halign='center', color=(0.2,0.2,0.2,1)
        ))
        row = BoxLayout(spacing=8, size_hint_y=None, height=44)
        popup = Popup(title='⚠️ Удаление', content=content, size_hint=(0.8,0.38))
        yes = Button(text='Да, удалить',
                     background_color=get_color_from_hex('#E74C3C'))
        no  = Button(text='Отмена',
                     background_color=get_color_from_hex('#95a5a6'))
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

    def _popup(self, title, text):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=text, halign='center', color=(0.2,0.2,0.2,1)))
        btn = Button(text='OK', size_hint_y=None, height=40,
                     background_color=get_color_from_hex('#6BCB77'))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.35))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'app_screen'


# ─────────────────────────────────────────────
#  ПРИЛОЖЕНИЕ
# ─────────────────────────────────────────────
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
