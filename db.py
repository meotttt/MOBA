import logging
import asyncio
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from typing import Dict, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, InputMediaPhoto
import re
import time
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, PreCheckoutQueryHandler, ContextTypes, filters
import uuid  # Добавляем для генерации уникальных ID для каждой полученной карты
import os


# Получаем путь к папке, где лежит текущий файл python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Путь к папке с картинками (если папка images лежит в той же папке, что и скрипт)
IMAGE_PATH = os.path.join(BASE_DIR, "images")

# Ключ: (chat_id, message_id), Значение: user_id владельца
NOTEBOOK_MENU_OWNERSHIP: Dict[Tuple[int, int], int] = {}
PHOTO_BASE_PATH = "."
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ДОБАВЛЕНО: Список ID пользователей с пожизненным премиумом ---
LIFETIME_PREMIUM_USER_IDS = {2123680656}

# Конфигурация
TOKEN = "8375881488:AAGPQeq7GrPPFNwiCnDpDbfcbQ0QfibB2S8"  # ЗАМЕНИТЕ НА ВАШ ТОКЕН!
ADMIN_ID = 123456789  # Ваш ID
DEFAULT_PROFILE_IMAGE = r"C:\Users\anana\PycharmProjects\PythonProject2\images\d41aeb3c-2496-47f7-8a8c-11bcddcbc0c4.png"
# Имитация базы данных (в реальном проекте используйте SQLite/PostgreSQL)
users = {}

# 1. Базовые статы по редкости
RARITY_STATS = {
    "regular card":     {"min_bo": 100, "max_bo": 300, "points": 400, "min_diamonds": 1, "max_diamonds": 2},
    "rare card":        {"min_bo": 301, "max_bo": 600, "points": 500, "min_diamonds": 2, "max_diamonds": 3},
    "exclusive card":   {"min_bo": 601, "max_bo": 900, "points": 800, "min_diamonds": 3, "max_diamonds": 4},
    "epic card":        {"min_bo": 901, "max_bo": 1200, "points": 1000, "min_diamonds": 4, "max_diamonds": 5},
    "collectible card": {"min_bo": 901, "max_bo": 1200, "points": 1500, "min_diamonds": 4,"max_diamonds": 5},
    "LIMITED":          {"min_bo": 901, "max_bo": 1200, "points": 2500, "min_diamonds": 4, "max_diamonds": 5}}
RARITY_CHANCES = {
    "regular card": 25,
    "rare card": 20,
    "exclusive card": 19,
    "epic card": 12,
    "collectible card": 18,
    "LIMITED": 5}
PREMIUM_RARITY_CHANCES = {
    "regular card": 12,
    "rare card": 12,
    "exclusive card": 25,
    "epic card": 20,
    "collectible card": 25,
    "LIMITED": 10}
# 2. Список всех карт.
CARDS = {
    # Каждая карта - это словарь. Для удобства, ID 1-10 для мальчиков, 11-20 для девочек
    1: {"path": os.path.join(PHOTO_BASE_PATH, "1.jpg"), "caption": "❤️‍🔥 LOVE IS…\nрай!\n\n🔖…1!"},
    2: {"path": os.path.join(PHOTO_BASE_PATH, "2.jpg"), "caption": "❤️‍🔥 LOVE IS…\nкогда вместе!\n\n🔖…2! "},
    3: {"path": os.path.join(PHOTO_BASE_PATH, "3.jpg"), "caption": "❤️‍🔥 LOVE IS…\nуметь переглядываться!\n\n🔖…3! "},
    4: {"path": os.path.join(PHOTO_BASE_PATH, "4.jpg"), "caption": "❤️‍🔥 LOVE IS…\nбыть на коне!\n\n🔖…4! "},
    5: {"path": os.path.join(PHOTO_BASE_PATH, "5.jpg"),
        "caption": "❤️‍🔥 LOVE IS…\nпочувствовать легкое головокружение!\n\n🔖…5! "},
    6: {"path": os.path.join(PHOTO_BASE_PATH, "6.jpg"), "caption": "❤️‍🔥 LOVE IS…\nобнимашки!\n\n🔖…6! "},
    7: {"path": os.path.join(PHOTO_BASE_PATH, "7.jpg"), "caption": "❤️‍🔥 LOVE IS…\nне только сахар!\n\n🔖…7! "},
    8: {"path": os.path.join(PHOTO_BASE_PATH, "8.jpg"),
        "caption": "❤️‍🔥 LOVE IS…\nпонимать друг друга без слов!\n\n🔖…8! "},
    9: {"path": os.path.join(PHOTO_BASE_PATH, "9.jpg"), "caption": "❤️‍🔥 LOVE IS…\nуметь успокоить!\n\n🔖…9! "},
    10: {"path": os.path.join(PHOTO_BASE_PATH, "10.jpg"), "caption": "❤️‍🔥 LOVE IS…\nсуметь удержаться!\n\n🔖…10! "},
    11: {"path": os.path.join(PHOTO_BASE_PATH, "11.jpg"), "caption": "❤️‍🔥 LOVE IS…\nне дать себя запутать!\n\n🔖…11! "},
    12: {"path": os.path.join(PHOTO_BASE_PATH, "12.jpg"),
         "caption": "❤️‍🔥 LOVE IS…\nсуметь сохранить секретик!\n\n🔖…12! "},
    13: {"path": os.path.join(PHOTO_BASE_PATH, "13.jpg"), "caption": "❤️‍🔥 LOVE IS…\nпод прикрытием\n\n🔖…13! "},
    14: {"path": os.path.join(PHOTO_BASE_PATH, "14.jpg"), "caption": "❤️‍🔥 LOVE IS…\nкогда нам по пути!\n\n🔖…14! "},
    15: {"path": os.path.join(PHOTO_BASE_PATH, "15.jpg"), "caption": "❤️‍🔥 LOVE IS…\nпрорыв.\n\n🔖…15! "},
    16: {"path": os.path.join(PHOTO_BASE_PATH, "16.jpg"), "caption": "❤️‍🔥 LOVE IS…\nзагадывать желание\n\n🔖…16!  "},
    17: {"path": os.path.join(PHOTO_BASE_PATH, "17.jpg"), "caption": "❤️‍🔥 LOVE IS…\nлето круглый год!\n\n🔖…17! "},
    18: {"path": os.path.join(PHOTO_BASE_PATH, "18.jpg"), "caption": "❤️‍🔥 LOVE IS…\nромантика!\n\n🔖…18! "},
    19: {"path": os.path.join(PHOTO_BASE_PATH, "19.jpg"), "caption": "❤️‍🔥 LOVE IS…\nкогда жарко!\n\n🔖…19! "},
    20: {"path": os.path.join(PHOTO_BASE_PATH, "20.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nраскрываться!\n\n🔖…20! "},
    21: {"path": os.path.join(PHOTO_BASE_PATH, "21.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nвыполнять обещания\n\n🔖…21! "},
    22: {"path": os.path.join(PHOTO_BASE_PATH, "22.jpg"), "caption": "❤️‍🔥 LOVE IS…\nцирк вдвоем!\n\n🔖…22! "},
    23: {"path": os.path.join(PHOTO_BASE_PATH, "23.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nслышать друг друга!\n\n🔖…23! "},
    24: {"path": os.path.join(PHOTO_BASE_PATH, "24.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nсладость\n\n🔖…24! "},
    25: {"path": os.path.join(PHOTO_BASE_PATH, "25.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nне упустить волну!\n\n🔖…25! "},
    26: {"path": os.path.join(PHOTO_BASE_PATH, "26.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nсказать о важном!\n\n🔖…26! "},
    27: {"path": os.path.join(PHOTO_BASE_PATH, "27.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nискриться!\n\n🔖…27! "},
    28: {"path": os.path.join(PHOTO_BASE_PATH, "28.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nтолько мы вдвоём\n\n🔖…28! "},
    29: {"path": os.path.join(PHOTO_BASE_PATH, "29.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nпервое прикосновение\n\n🔖…29! "},
    30: {"path": os.path.join(PHOTO_BASE_PATH, "30.jpg"),
         "caption": "️‍❤️‍🔥 LOVE IS…\nвзять дело в свои руки\n\n🔖…30! "},
    31: {"path": os.path.join(PHOTO_BASE_PATH, "31.jpg"),
         "caption": "️‍❤️‍🔥 LOVE IS…\nкогда не важно какая погода\n\n🔖…31! "},
    32: {"path": os.path.join(PHOTO_BASE_PATH, "32.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nуметь прощать!\n\n🔖…32! "},
    33: {"path": os.path.join(PHOTO_BASE_PATH, "33.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nотметиться!\n\n🔖…33! "},
    34: {"path": os.path.join(PHOTO_BASE_PATH, "34.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nпервый поцелуй\n\n🔖…34!"},
    35: {"path": os.path.join(PHOTO_BASE_PATH, "35.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nкогда без интернета! \n\n🔖…35!"},
    36: {"path": os.path.join(PHOTO_BASE_PATH, "36.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nлегкое головокружение\n\n🔖…36!"},
    37: {"path": os.path.join(PHOTO_BASE_PATH, "37.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nпозвонить просто так\n\n🔖…37!"},
    38: {"path": os.path.join(PHOTO_BASE_PATH, "38.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nвсё что нужно\n\n🔖…38!"},
    39: {"path": os.path.join(PHOTO_BASE_PATH, "39.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nто, что создаёшь ты\n\n🔖…39!"},
    40: {"path": os.path.join(PHOTO_BASE_PATH, "40.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nсвобода\n\n🔖…40!"},
    41: {"path": os.path.join(PHOTO_BASE_PATH, "41.jpg"),
         "caption": "️‍❤️‍🔥 LOVE IS…\nкогда пробежала искра!\n\n🔖…41!"},
    42: {"path": os.path.join(PHOTO_BASE_PATH, "42.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nизображать недотрогу \n\n🔖…42!"},
    43: {"path": os.path.join(PHOTO_BASE_PATH, "43.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nсварить ему борщ)\n\n🔖…43!"},
    44: {"path": os.path.join(PHOTO_BASE_PATH, "44.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nпотрясать мир \n\n🔖…44!"},
    45: {"path": os.path.join(PHOTO_BASE_PATH, "45.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nкогда он не ангел!\n\n🔖…45!"},
    46: {"path": os.path.join(PHOTO_BASE_PATH, "46.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nпритягивать разных!\n\n🔖…46!"},
    47: {"path": os.path.join(PHOTO_BASE_PATH, "47.jpg"),
         "caption": "️‍❤️‍🔥 LOVE IS…\nтепло внутри, когда холодно снаружи \n\n🔖…47!"},
    48: {"path": os.path.join(PHOTO_BASE_PATH, "48.jpg"),
         "caption": "️‍❤️‍🔥 LOVE IS…\nделать покупки друг друга\n\n🔖…48!"},
    49: {"path": os.path.join(PHOTO_BASE_PATH, "49.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nнемного колкости\n\n🔖…49!"},
    50: {"path": os.path.join(PHOTO_BASE_PATH, "50.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nкогда тянет магнитом \n\n🔖…50!"},
    51: {"path": os.path.join(PHOTO_BASE_PATH, "51.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nбыть на седьмом небе!\n\n🔖…51!"},
    52: {"path": os.path.join(PHOTO_BASE_PATH, "52.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nты и я\n\n🔖…52!"},
    53: {"path": os.path.join(PHOTO_BASE_PATH, "53.jpg"),
         "caption": "️‍❤️‍🔥 LOVE IS…\nкогда купил самое необходимое!\n\n🔖…53!"},
    54: {"path": os.path.join(PHOTO_BASE_PATH, "54.jpg"),
         "caption": "️‍❤️‍🔥 LOVE IS…\nкак первый день весны!\n\n🔖…54!"},
    55: {"path": os.path.join(PHOTO_BASE_PATH, "55.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nпоздравить первым!\n\n🔖…55!"},
    56: {"path": os.path.join(PHOTO_BASE_PATH, "56.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nоставить след!\n\n🔖…56!"},
    57: {"path": os.path.join(PHOTO_BASE_PATH, "57.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nмикс чувств!\n\n🔖…57!"},
    58: {"path": os.path.join(PHOTO_BASE_PATH, "58.jpg"), "caption": "❤️‍🔥 LOVE IS…\nслучайные порывы!\n\n🔖…58!"},
    59: {"path": os.path.join(PHOTO_BASE_PATH, "59.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nкогда мысли сходятся!\n\n🔖…59!"},
    60: {"path": os.path.join(PHOTO_BASE_PATH, "60.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nпосильная ноша!\n\n🔖…60!"},
    61: {"path": os.path.join(PHOTO_BASE_PATH, "61.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nвыбрать свое сердце!\n\n🔖…61!"},
    62: {"path": os.path.join(PHOTO_BASE_PATH, "62.jpg"),
         "caption": "️‍❤️‍🔥 LOVE IS…\nто, что требует заботы!\n\n🔖…62!"},
    63: {"path": os.path.join(PHOTO_BASE_PATH, "63.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nбессонные ночи!\n\n🔖…63!"},
    64: {"path": os.path.join(PHOTO_BASE_PATH, "64.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nбыть на вершине мира\n\n🔖…64!"},
    65: {"path": os.path.join(PHOTO_BASE_PATH, "65.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nисправлять ошибки!\n\n🔖…65!"},
    66: {"path": os.path.join(PHOTO_BASE_PATH, "66.jpg"),
         "caption": "️‍❤️‍🔥 LOVE IS…\nлюбоваться друг другом!\n\n🔖…66!"},
    67: {"path": os.path.join(PHOTO_BASE_PATH, "67.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nдарить главное!\n\n🔖…67!"},
    68: {"path": os.path.join(PHOTO_BASE_PATH, "68.jpg"),
         "caption": "️‍❤️‍🔥 LOVE IS…\nкогда совсем не холодно!\n\n🔖…68!"},
    69: {"path": os.path.join(PHOTO_BASE_PATH, "69.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nдобавить изюминку!\n\n🔖…69!"},
    70: {"path": os.path.join(PHOTO_BASE_PATH, "70.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nснится друг другу!\n\n🔖…70!"},
    71: {"path": os.path.join(PHOTO_BASE_PATH, "71.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nпикник на двоих!\n\n🔖…71!"},
    72: {"path": os.path.join(PHOTO_BASE_PATH, "72.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nдурачиться, как дети\n\n🔖…72!"},
    73: {"path": os.path.join(PHOTO_BASE_PATH, "73.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nдарить себя!\n\n🔖…73!"},
    74: {"path": os.path.join(PHOTO_BASE_PATH, "74.jpg"), "caption": "️‍❤️‍🔥 LOVE IS…\nгорячее сердце!\n\n🔖…74!"},}

# 3. Фиксированная редкость для каждой карты по ее ID.
FIXED_CARD_RARITIES = {
    1: "collectible card",
    2: "collectible card",
    3: "collectible card",
    4: "collectible card",
    5: "collectible card",
    6: "collectible card",
    7: "collectible card",
    8: "collectible card",
    9: "regular card",
    10: "collectible card",
    11: "collectible card",
    12: "collectible card",
    13: "collectible card",
    14: "collectible card",
    15: "collectible card",
    16: "collectible card",
    17: "collectible card",
    18: "collectible card",
    19: "collectible card",
    20: "collectible card",
    21: "collectible card",
    22: "collectible card",
    23: "collectible card",
    24: "collectible card",
    25: "collectible card",
    26: "collectible card",
    27: "collectible card",
    28: "collectible card",
    29: "collectible card",
    30: "collectible card",
    31: "collectible card",
    32: "collectible card",
    33: "collectible card",
    34: "regular card",
    35: "LIMITED",
    36: "LIMITED",
    37: "LIMITED",
    38: "LIMITED",
    39: "LIMITED",
    40: "LIMITED",
    41: "LIMITED",
    42: "LIMITED",
    43: "LIMITED",
    44: "collectible card",
    45: "collectible card",
    46: "collectible card",
    47: "regular card",
    48: "regular card",
    49: "regular card",
    50: "collectible card",
    51: "collectible card",
    52: "collectible card",
    53: "collectible card",
    54: "collectible card",
    55: "collectible card",
    56: "collectible card",
    57: "collectible card",
    58: "collectible card",
    59: "collectible card",
    60: "collectible card",
    61: "collectible card",
    62: "collectible card",
    63: "regular card",
    64: "regular card",
    65: "collectible card",
    66: "collectible card",
    67: "collectible card",
    68: "regular card",
    69: "regular card",
    70: "collectible card",
    71: "collectible card",
    72: "collectible card",
    73: "regular card",
    74: "regular card",
    75: "collectible card",
    76: "collectible card",
    77: "collectible card",
    78: "collectible card",
    79: "collectible card",
    80: "collectible card",
    81: "LIMITED",
    82: "LIMITED",
    83: "LIMITED",
    84: "collectible card",
    85: "collectible card",
    86: "collectible card",
    87: "collectible card",
    88: "collectible card",
    89: "collectible card",
    90: "collectible card",
    91: "collectible card",
    92: "regular card",
    93: "regular card",
    94: "regular card",
    95: "collectible card",
    96: "collectible card",
    97: "collectible card",
    98: "collectible card",
    99: "regular card",
    100: "collectible card",
    101: "collectible card",
    102: "collectible card",
    103: "collectible card",
    104: "collectible card",
    105: "collectible card",
    106: "collectible card",
    107: "collectible card",
    108: "collectible card",
    109: "regular card",
    110: "collectible card",
    111: "collectible card",
    112: "collectible card",
    113: "collectible card",
    114: "collectible card",
    115: "collectible card",
    116: "regular card",
    117: "regular card",
    118: "regular card",
    119: "regular card",
    120: "collectible card",
    121: "collectible card",
    122: "collectible card",
    123: "collectible card",
    124: "collectible card",
    125: "collectible card",
    126: "collectible card",
    127: "collectible card",
    128: "collectible card",
    129: "collectible card",
    130: "collectible card",
    131: "collectible card",
    132: "collectible card",
    133: "collectible card",
    134: "regular card",
    135: "regular card",
    136: "regular card",
    137: "regular card",
    138: "regular card",
    139: "regular card",
    140: "regular card",
    141: "regular card",
    142: "regular card",
    143: "regular card",
    144: "regular card",
    145: "regular card",
    146: "rare card",
    147: "rare card",
    148: "rare card",
    149: "rare card",
    150: "rare card",
    151: "rare card",
    152: "rare card",
    153: "rare card",
    154: "rare card",
    155: "rare card",
    156: "rare card",
    157: "rare card",
    158: "rare card",
    159: "rare card",
    160: "rare card",
    161: "rare card",
    162: "rare card",
    163: "rare card",
    164: "rare card",
    165: "rare card",
    166: "rare card",
    167: "rare card",
    168: "rare card",
    169: "rare card",
    170: "rare card",
    171: "rare card",
    172: "rare card",
    173: "rare card",
    174: "rare card",
    175: "rare card",
    176: "rare card",
    177: "rare card",
    178: "rare card",
    179: "exclusive card",
    180: "exclusive card",
    181: "exclusive card",
    182: "exclusive card",
    183: "exclusive card",
    184: "exclusive card",
    185: "exclusive card",
    186: "exclusive card",
    187: "exclusive card",
    188: "exclusive card",
    189: "exclusive card",
    190: "exclusive card",
    191: "exclusive card",
    192: "exclusive card",
    193: "exclusive card",
    194: "exclusive card",
    195: "exclusive card",
    196: "exclusive card",
    197: "exclusive card",
    198: "exclusive card",
    199: "exclusive card",
    200: "exclusive card",
    201: "exclusive card",
    202: "exclusive card",
    203: "exclusive card",
    204: "exclusive card",
    205: "exclusive card",
    206: "exclusive card",
    207: "exclusive card",
    208: "exclusive card",
    209: "exclusive card",
    210: "exclusive card",
    211: "exclusive card",
    212: "exclusive card",
    213: "exclusive card",
    214: "exclusive card",
    215: "exclusive card",
    216: "exclusive card",
    217: "exclusive card",
    218: "exclusive card",
    219: "exclusive card",
    220: "exclusive card",
    221: "exclusive card",
    222: "exclusive card",
    223: "exclusive card",
    224: "exclusive card",
    225: "exclusive card",
    226: "exclusive card",
    227: "exclusive card",
    228: "exclusive card",
    229: "exclusive card",
    230: "epic card",
    231: "epic card",
    232: "epic card",
    233: "epic card",
    234: "epic card",
    235: "epic card",
    236: "epic card",
    237: "epic card",
    238: "epic card",
    239: "epic card",
    240: "epic card",
    241: "epic card",
    242: "epic card",
    243: "epic card",
    244: "epic card",
    245: "epic card",
    246: "epic card",
    247: "epic card",
    248: "epic card",
    249: "epic card",
    250: "epic card",
    251: "epic card",
    252: "epic card",
    253: "epic card",
    254: "epic card",
    255: "epic card",
    256: "epic card",
    257: "epic card",
    258: "epic card",
    259: "epic card",
    260: "epic card",
    261: "collectible card",
    262: "collectible card",
    263: "collectible card",
    264: "rare card",
    265: "rare card",
    266: "rare card",
    267: "rare card",
    268: "rare card",
    269: "rare card",

}
# Данные о сезоне
season_data = {
    "start_date": datetime.now(),
    "season_number": 1
}
RANK_NAMES = ["Воин", "Эпик", "Легенда", "Мифический", "Мифическая Слава"]
WIN_PHRASES = [
    "🔥 <b>MVP!</b> Ты затащил эту катку!",
    "⚡️ф <b>Victory!</b> Твой скилл неоспорим!",
    "💥 <b>Double Kill!</b> Звезда летит в твою копилку!",
    "💥 <b>Легендарный камбек!</b> Ты вырвал победу!",
    "🔥 <b>Wiped Out!</b> Вся вражеская команда в таверне!",
    "⚡️ <b>Безупречно!</b> Ты контролируешь эту карту!",
    "⚡️ <b>Твой стрелок не подвел!</b> Звезда получена!"
]

LOSE_PHRASES = [
    "💀 <b>Defeat!</b> Твой лесник опять в засаде... своей базы",
    "🥀 <b>Минус звезда.</b> Союзники решили пофидить",
    "💀 <b>Трон упал!</b> Враги оказались сильнее в этот раз",
    "🧨 <b>Тебя загангали!</b> Звезда потеряна",
    "🐌 <b>Огромный пинг!</b> Купи наконец то wifi ",
    "🌑 <b>Поражение.</b> Эпики в твоей команде — это приговор",
    "💀 <b>Твой билд не сработал.</b> Попробуй в следующий раз"
]


def get_rank_info(stars):
    if stars <= 0:
        return "Без ранга", "0 звезд"

    # Список рангов: (Название, кол-во дивизионов, звезд в дивизионе)
    # Порядок дивизионов в игре обратный: III, II, I или V, IV, III, II, I
    rank_configs = [
        ("Воин", 3, 3),  # 1-9 звезды
        ("Элита", 3, 4),  # 10-21 звезды
        ("Мастер", 4, 4),  # 22-37 звезды
        ("Грандмастер", 5, 5),  # 38-62 звезды
        ("Эпик", 5, 5),  # 63-87 звезды
        ("Легенда", 5, 5)  # 88-112 звезды
    ]

    current_threshold = 0
    for name, divs, stars_per_div in rank_configs:
        rank_total_stars = divs * stars_per_div
        if stars <= current_threshold + rank_total_stars:
            # Мы внутри этого ранга
            stars_in_rank = stars - current_threshold
            # Определяем дивизион (например, из 5 дивизионов: 5, 4, 3, 2, 1)
            div_index = (stars_in_rank - 1) // stars_per_div
            div_number = divs - div_index
            # Звезды внутри дивизиона
            stars_left = ((stars_in_rank - 1) % stars_per_div) + 1
            return f"{name} {div_number}", f"{stars_left}⭐️"

        current_threshold += rank_total_stars

    # Если звезд больше 112 — это Мифический уровень
    mythic_stars = stars - 112
    if mythic_stars < 25:
        return "Мифический", f"{mythic_stars}⭐️"
    elif mythic_stars < 50:
        return "Мифическая Честь", f"{mythic_stars}⭐️"
    elif mythic_stars < 100:
        return "Мифическая Слава", f"{mythic_stars}⭐️"
    else:
        return "Мифический Бессмертный", f"{mythic_stars}⭐️"


# --- ОБНОВЛЕННЫЙ ОБРАБОТЧИК РЕГНУТЬ ---
async def regnut_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if update.message.text.lower().strip() != "регнуть":
        return

    user = get_user(update.effective_user.id)
    now = time.time()

    # Кулдаун 15 секунд
    if now - user.get("last_reg_time", 0) < 15:
        wait = int(15 - (now - user["last_reg_time"]))
        await update.message.reply_text(f"⏳ Поиск матча<blockquote>Катку можно регнуть через {wait} секунд</blockquote>")
        return

    user["last_reg_time"] = now

    # ШАНС ПОБЕДЫ (60% до Грандмастера, дальше 50%)
    # Грандмастер начинается с 38-й звезды
    win_chance = 60 if user["stars"] < 38 else 50

    win = random.randint(1, 100) <= win_chance
    coins = random.randint(15, 60)
    user["coins"] += coins
    user["reg_total"] += 1

    if win:
        user["stars"] += 1
        user["reg_success"] += 1
        if user["stars"] > user["max_stars"]: user["max_stars"] = user["stars"]
        msg = random.choice(WIN_PHRASES)
        change = "📈 <b>+1 звезда</b>"
    else:
        if user["stars"] > 0: user["stars"] -= 1
        msg = random.choice(LOSE_PHRASES)
        change = "📉 <b>-1 звезда</b>"

    rank_name, star_info = get_rank_info(user["stars"])
    wr = (user["reg_success"] / user["reg_total"]) * 100

    res = (
        f"{msg}\n\n"
        f"💰 <b>Награда:</b> <code>+{coins} монет</code>\n"
        f"{change}\n"
        f"🏆 <b>Ранг:</b> <code>{rank_name} ({star_info})</code>\n"
        f"📊 <b>Винрейт:</b> <code>{wr:.1f}%</code>"
    )
    await update.message.reply_text(res, parse_mode=ParseMode.HTML)

def generate_card_stats(rarity: str, card_data: dict) -> dict:
    stats_range = RARITY_STATS.get(rarity)

    if not stats_range:
        stats_range = RARITY_STATS["regular card"]

    # ЛОГИКА ПОИНТОВ:
    if rarity == "collectible card":
        # Берем points из словаря карты в CARDS. Если там нет - берем дефолт из RARITY_STATS
        card_points = card_data.get("points", stats_range["points"])
    else:
        # Для всех остальных берем строго по редкости
        card_points = stats_range["points"]

    return {
        "rarity": rarity,
        "bo": random.randint(stats_range["min_bo"], stats_range["max_bo"]),
        "points": card_points,
        "diamonds": random.randint(stats_range["min_diamonds"], stats_range["max_diamonds"])
    }

async def id_detection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    # Регулярное выражение: 9 цифр, пробел, скобка, 4 цифры, скобка
    pattern = r"^\d{9}\s\(\d{4}\)$"

    if re.match(pattern, text):
        context.user_data['temp_mlbb_id'] = text
        keyboard = [
            [InlineKeyboardButton("Добавить", callback_data="confirm_add_id"),
             InlineKeyboardButton("Пока не добавлять", callback_data="cancel_add_id")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "<b>👾 GAME ID</b>\n<blockquote>Хотите добавить свой айди в профиль?</blockquote>",
            reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )

async def confirm_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = get_user(user_id)

    # Берем сохраненный ранее ID
    new_game_id = context.user_data.get('temp_mlbb_id')

    if new_game_id:
        user['game_id'] = new_game_id  # Сохраняем в профиль
        await query.edit_message_text(f"<b>👾 GAME ID</b>\n<blockquote>Твой GAME ID обновлен! Проверь профиль</blockquote>", parse_mode=ParseMode.HTML)
        # Очищаем временную память
        context.user_data.pop('temp_mlbb_id', None)
    else:
        await query.edit_message_text("❌ Произошла ошибка. Попробуйте отправить ID еще раз.")

async def cancel_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop('temp_mlbb_id', None)  # Удаляем временные данные
    await query.edit_message_text("<b>👾 GAME ID</b>\n<blockquote>Твой  ID не был добавлен.</blockquote>", parse_mode=ParseMode.HTML )

def get_user(user_id, username=""):
    if user_id not in users:
        users[user_id] = {
            "id": user_id,
            "nickname": f"моблер",
            "points": 0,
            "game_id": None,
            "diamonds": 0,
            "coins": 0,
            "cards": [],
            "premium_until": None,
            "last_mobba_time": 0,
            "booster_active": False,
            "stars": 0,
            "last_reg_time": 0,# Звезды текущего сезона
            "stars_all_time": 0,     # Общие звезды (для топа всех времен)
            "max_stars": 0,          # Максимальный ранг (пик)
            "reg_total": 0,          # Всего нажатий "регнуть"
            "reg_success": 0         # Успешных (где +1 звезда)
        }

    if user_id in LIFETIME_PREMIUM_USER_IDS:
        # Устанавливаем дату, которая точно не истечет в обозримом будущем
        users[user_id]["premium_until"] = datetime.now() + timedelta(days=365 * 10) # 10 лет

    return users[user_id]

async def check_season_reset():
    """Сбрасывает звезды каждые 3 месяца (90 дней)"""
    global season_data
    if datetime.now() > season_data["start_date"] + timedelta(days=90):
        for uid in users:
            users[uid]["stars"] = 0  # Сброс текущих звезд
        season_data["start_date"] = datetime.now()
        season_data["season_number"] += 1
        logging.info(f"Сезон {season_data['season_number']} начался!")

# --- ОБНОВЛЕННЫЙ ОБРАБОТЧИК РЕГНУТЬ ---
async def regnut_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()
    if text != "регнуть":
        return

    user = get_user(update.effective_user.id)
    now = time.time()
    cooldown = 15

    # 1. Проверка Кулдауна (15 секунд)
    last_reg = user.get("last_reg_time", 0)
    if now - last_reg < cooldown:
        wait_time = int(cooldown - (now - last_reg))
        await update.message.reply_text(
            f"<b>⏳ Поиск матча...</b>\n<blockquote>Катку можно регнуть через {wait_time} сек</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return

    await check_season_reset()
    user["last_reg_time"] = now

    # 2. ОПРЕДЕЛЕНИЕ ШАНСА ПОБЕДЫ
    # По вашей логике: 1-25 звезд это Воин (от 5 до 1 ранга)
    if user["stars"] <= 25:
        win_chance = 60  # 60% на Воине
    else:
        win_chance = 50  # 50% на Эпике и выше

    # Ролл шанса
    roll = random.randint(1, 100)
    win = roll <= win_chance

    # 3. НАГРАДА И СТАТИСТИКА
    coins_reward = random.randint(15, 60)
    user["reg_total"] += 1
    user["coins"] += coins_reward

    if win:
        user["stars"] += 1
        user["stars_all_time"] += 1
        user["reg_success"] += 1
        if user["stars"] > user["max_stars"]:
            user["max_stars"] = user["stars"]
        status_msg = random.choice(WIN_PHRASES)
        change_text = "<b>⚡️ Победа ! </b>"
    else:
        if user["stars"] > 0:
            user["stars"] -= 1
        status_msg = random.choice(LOSE_PHRASES)
        change_text = "<b>🏴 Поражение ! </b>"

    # 4. ПОЛУЧЕНИЕ ДАННЫХ О РАНГЕ
    rank_name, star_count = get_rank_info(user["stars"])

    # Расчет винрейта для вывода
    wr = (user['reg_success'] / user['reg_total']) * 100

    response = (
        f"<b>{status_msg}</b>\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"💰 <b><i>+ {coins_reward}  БО!</i></b> \n"
        f"<blockquote><b>Текущий ранг • {rank_name} ({star_count})</b></blockquote>\n"

    )

    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)
    await update.message.reply_text("Привет! Используй /name чтобы сменить ник и напиши 'моба' чтобы получить карту.")

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    new_name = " ".join(context.args)
    if 5 <= len(new_name) <=16:
        user["nickname"] = new_name
        await update.message.reply_text(f"Ник изменен на: {new_name}")
    else:
        await update.message.reply_text("<b>👾 Придумай свой ник</b>\n<blockquote>Длина от 5 до 16 символов\nПример: /name помидорка</blockquote>", parse_mode=ParseMode.HTML)

async def mobba_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or update.message.text.lower() != "моба":
        return

    user = get_user(update.effective_user.id)
    now = time.time()
    is_premium = user["premium_until"] and user["premium_until"] > datetime.now()
    cooldown = 3 if is_premium else 10

    if now - user["last_mobba_time"] < cooldown:
        wait = int(cooldown - (now - user["last_mobba_time"]))

        # Различные сообщения в зависимости от премиум-статуса
        if is_premium:
            message_text = (
                f"<b>🃏 Вы уже получали карту</b>"
                f"<blockquote>Попробуйте через {wait} сек</blockquote>\n"
                f"<b>🚀 Premium сократил время на 25% !</b>\n"
            )
        else:
            message_text = (
                f"<b>🃏 Вы уже получали карту</b>"
                f"<blockquote>Попробуйте через {wait} сек</blockquote>\n")
        await update.message.reply_text(message_text, parse_mode=ParseMode.HTML)
        return

    user["last_mobba_time"] = now
 base_card_data = random.choice(CARDS)
  if not isinstance(base_card_data, dict) or "id" not in base_card_data:
    logging.error("Invalid card selected from CARDS: %r", base_card_data, exc_info=False)
    # Попробуем выбрать валидную карту из списка
    valid_cards = [c for c in CARDS if isinstance(c, dict) and "id" in c]
    if not valid_cards:
      await update.message.reply_text("Ошибка: нет доступных карт. Обратитесь к администратору.")
      return
    base_card_data = random.choice(valid_cards)

  # Берём id и аккуратно подбираем ключ для FIXED_CARD_RARITIES (int/str)
  card_id = base_card_data.get("id")
  try:
    card_id_int = int(card_id) if card_id is not None else None
  except Exception:
    card_id_int = None

  # Сначала пробуем по числовому ключу, затем по исходному значению, потом дефолт
  chosen_rarity = (
    FIXED_CARD_RARITIES.get(card_id_int)
    or FIXED_CARD_RARITIES.get(card_id)
    or "regular card"
  )

  card_stats = generate_card_stats(chosen_rarity, base_card_data)
  img_name = base_card_data.get("image_filename", "1.jpg")
  path_to_image = os.path.join(IMAGE_PATH, img_name)

  full_card_data = {
    "unique_id": str(uuid.uuid4()),
    "card_id": card_id,
    "name": base_card_data.get("name", "Unknown"),
    "collection": base_card_data.get("collection", ""),
    "image_path": path_to_image,
    card_stats
  }

    user["cards"].append(full_card_data)
    user["points"] += full_card_data["points"]
    user["diamonds"] += full_card_data["diamonds"]

    caption = (
        f"<b><i>🃏 {full_card_data['collection']} •  {full_card_data['name']}</i></b>\n"
        f"<blockquote><b><i>+ {full_card_data['points']} ОЧКОВ !</i></b></blockquote>\n\n"
        f"<b>✨ Редкость •</b> <i>{full_card_data['rarity']}</i>\n"
        f"<b>💰 БО •</b><i> {full_card_data['bo']}</i>\n"
        f"<b>💎 Алмазы •</b> <i>{full_card_data['diamonds']}</i>\n\n"
        f"<blockquote><b><i>Добавлено в ваши карты!</i></b></blockquote>"
    )

    try:
        with open(full_card_data["image_path"], 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=caption, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при загрузке фото: {e}")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    is_premium = user["premium_until"] and user["premium_until"] > datetime.now()
    prem_status = "🚀 Счастливый обладатель Premium" if is_premium else "Не обладает Premium"
    # Расчет рангов
    curr_rank, curr_stars = get_rank_info(user["stars"])
    max_rank, max_stars_info = get_rank_info(user["max_stars"])

    # Расчет процента побед (регнуть)
    winrate = 0
    if user["reg_total"] > 0:
        winrate = (user["reg_success"] / user["reg_total"]) * 100

    # Получаем фото профиля
    photos = await update.effective_user.get_profile_photos(limit=1)
    display_id = user.get('game_id') if user.get('game_id') else "Не добавлен"
    text = (
        f"Ценитель <b>MOBILE LEGENDS\n \n«{user['nickname']}»</b>\n"
        f"<blockquote><b>👾GAME ID •</b> <i>{display_id}</i></blockquote>\n\n"
        f"<b>🏆 Ранг •</b> <i>{curr_rank} ({curr_stars})</i>\n"
        f"<b>⚜️ Макс ранг •</b> <i>{max_rank}</i>\n"
        f"<b>🎗️ Win rate •</b> <i>{winrate:.1f}%</i>\n\n"
        f"<b>🃏 Карт •</b> <i>{len(user['cards'])}</i>\n"
        f"<b>✨ Очков •</b> <i>{user['points']}</i>\n"
        f"<b>💰 Монет • </b><i>{user['coins']}</i>\n"
        f"<b>💎 Алмазов • </b><i>{user['diamonds']}</i>\n\n"
        f"<blockquote>{prem_status}</blockquote>"
    )

    keyboard = [
        [InlineKeyboardButton("🃏 Мои карты", callback_data="my_cards"),
         InlineKeyboardButton("👝 Сумка", callback_data="bag")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if photos.photos:
        # Если фото есть, используем его file_id
        await update.message.reply_photo(
            photo=photos.photos[0][0].file_id,
            caption=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    else:
        # Если фото нет, открываем наше стандартное фото
        try:
            with open(DEFAULT_PROFILE_IMAGE, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
        except FileNotFoundError:
            # На случай, если вы забыли положить файл по пути DEFAULT_PROFILE_IMAGE
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def premium_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Генерируем ссылку заранее
    invoice_link = await context.bot.create_invoice_link(
        title="Премиум",
        description="30 дней подписки",
        payload="premium_30",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("Цена", 10)]
    )

    text = (
        "🚀 <b>Premium</b>\n\n"
        "<blockquote>• 🔥 Шанс на особые карты увеличен на 10%\n"  # Это относится к случайной редкости, но у нас сейчас фиксированная. Можно переформулировать.
        "• ⏳ Время получения следующей карты снижено на 25%\n"
        "• 💰 Выпадение монет увеличено на 20 %\n"
        "• 🚀 Значок в топе\n\n"
        "Срок действия • 30 дней</blockquote>"
    )
    # Кнопка сразу ведет на оплату
    keyboard = [[InlineKeyboardButton("🚀 Купить за 3 • ⭐️", url=invoice_link)]]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Монеты", callback_data="shop_coins"),
         InlineKeyboardButton("📦 Наборы", callback_data="shop_packs")],  # Добавлен второй уровень для "Наборы"
        [InlineKeyboardButton("👑 Премиум", callback_data="buy_prem"),
         InlineKeyboardButton("⚡️ Бустер", callback_data="shop_booster")]]
    await update.message.reply_text("🛒 **Магазин**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# --- ОБРАБОТКА ПЛАТЕЖЕЙ (STARS) ---
async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Параметры платежа (те же, что были)
    if query.data == "buy_prem":
        title = "Премиум подписка"
        description = "Доступ к премиум функциям на 30 дней"
        payload = "premium_30"
        price = 3
    elif query.data == "shop_coins":
        title = "100 Монет"
        description = "Игровая валюта"
        payload = "coins_100"
        price = 1
    else:
        return

    # 1. Генерируем прямую ссылку на оплату (Stars)
    invoice_link = await context.bot.create_invoice_link(
        title=title,
        description=description,
        payload=payload,
        provider_token="",  # Для Stars пусто
        currency="XTR",
        prices=[LabeledPrice("Цена", price)]
    )

    # 2. Создаем кнопку с этой ссылкой
    keyboard = [
        [InlineKeyboardButton(f"💳 Подтвердить оплату ({price} ⭐️)", url=invoice_link)],
        [InlineKeyboardButton("⬅️ Отмена", callback_query_handler="shop")]  # Или другой возврат
    ]

    # 3. Редактируем старое сообщение, вставляя кнопку оплаты
    await query.edit_message_text(
        text=f"{title}\n\n{description}\n\nНажмите на кнопку ниже для перехода к оплате:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def handle_bag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Текст сообщения
    msg_text = "<b>👝 Сумка</b>\n<blockquote>Ваша сумка пока пуста</blockquote>"

    # Кнопка возврата в профиль

    # Если в сообщении есть фото (профиль обычно с фото), его лучше удалить и отправить текст,
    # либо просто заменить подпись. Здесь мы заменяем текст/подпись:
    if query.message.photo:
        # Если хотим просто текст вместо фото:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg_text,

            parse_mode=ParseMode.HTML
        )
    else:
        await query.edit_message_text(
            text=msg_text,

            parse_mode=ParseMode.HTML
        )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    # Всегда отвечаем True для Stars
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    user = get_user(update.effective_user.id)
    payload = payment.invoice_payload

    if payload == "premium_30":
        user["premium_until"] = datetime.now() + timedelta(days=30)
        await update.message.reply_text("<blockquote>🚀 Премиум активирован на 30 дней!</blockquote>", parse_mode=ParseMode.HTML)
    elif payload == "coins_100":
        user["coins"] += 100
        await update.message.reply_text("💰 Вы купили 100 монет!")
    # Здесь можно добавить логику для других покупок
    # elif payload == "booster_cooldown":
    #     user["booster_active"] = True
    #     await update.message.reply_text("⚡️ Бустер активирован на следующее получение карты!")
    # elif payload.startswith("card_pack_"):
    #     # Логика выдачи карт из набора
    #     category = payload.split('_')[2]
    #     await update.message.reply_text(f"📦 Вы получили набор карт из категории '{category}'!")
    else:
        await update.message.reply_text("Спасибо за покупку, но не удалось определить, что вы купили.")

# --- ТОП ---
async def top_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Первое окно при команде /top"""
    keyboard = [
        [InlineKeyboardButton("🃏 Карточный бот", callback_data="top_category_cards")],
        [InlineKeyboardButton("🎮 Игровой бот", callback_data="top_category_game")]
    ]
    msg = "🏆 <b>Главное меню рейтинга</b>\n\nВыберите категорию, по которой хотите увидеть лучших игроков:"

    if update.callback_query:
        await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard),
                                                      parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

async def top_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "top_category_cards":
        keyboard = [
            [InlineKeyboardButton("✨ По очкам", callback_data="top_points"),
             InlineKeyboardButton("🃏 По картам", callback_data="top_cards")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="top_main")]
        ]
        await query.edit_message_text("🏆 <b>Рейтинг коллекционеров</b>", reply_markup=InlineKeyboardMarkup(keyboard),
                                      parse_mode=ParseMode.HTML)

    elif query.data == "top_category_game":
        keyboard = [
            [InlineKeyboardButton("🌟 Топ сезона", callback_data="top_stars_season"),
             InlineKeyboardButton("🌍 За все время", callback_data="top_stars_all")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="top_main")]
        ]
        await query.edit_message_text("🏆 <b>Рейтинг игроков (Ранг)</b>", reply_markup=InlineKeyboardMarkup(keyboard),
                                      parse_mode=ParseMode.HTML)

async def show_specific_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    title = ""
    sorted_users = []

    if data == "top_points":
        title = "Топ по очкам"
        sorted_users = sorted(users.values(), key=lambda x: x['points'], reverse=True)[:10]
        suffix = "очков"
    elif data == "top_cards":
        title = "Топ по картам"
        sorted_users = sorted(users.values(), key=lambda x: len(x['cards']), reverse=True)[:10]
        suffix = "карт"
    elif data == "top_stars_season":
        title = "Топ сезона (Звезды)"
        sorted_users = sorted(users.values(), key=lambda x: x['stars'], reverse=True)[:10]
        suffix = "⭐"
    elif data == "top_stars_all":
        title = "Топ всех времен (Звезды)"
        sorted_users = sorted(users.values(), key=lambda x: x['stars_all_time'], reverse=True)[:10]
        suffix = "⭐"

    text = f"🏆 <b>{title}</b>\n\n"
    if not sorted_users:
        text += "<i>Рейтинг пока пуст</i>"
    else:
        for i, u in enumerate(sorted_users, 1):
            is_prem = u["premium_until"] and u["premium_until"] > datetime.now()
            prem_icon = "🚀 " if is_prem else ""

            if data == "top_points":
                val = u['points']
            elif data == "top_cards":
                val = len(u['cards'])
            elif data == "top_stars_season":
                val = u['stars']
            else:
                val = u['stars_all_time']

            text += f"{i}. {prem_icon}{u['nickname']} — <b>{val}</b> {suffix}\n"

    back_button = "top_category_cards" if data in ["top_points", "top_cards"] else "top_category_game"
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data=back_button)]]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

#async def top_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #keyboard = [
        #[InlineKeyboardButton("Топ по картам", callback_data="top_cards")],
        #[InlineKeyboardButton("Топ по очкам", callback_data="top_points")]
    #]
    #await update.message.reply_text("🏆 Выберите категорию топа:", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "top_points":
        sorted_users = sorted(users.values(), key=lambda x: x['points'], reverse=True)[:10]
        title = "Топ по очкам"
    else:
        sorted_users = sorted(users.values(), key=lambda x: len(x['cards']), reverse=True)[:10]
        title = "Топ по картам"

    text = f"🏆 **{title}**\n\n"
    if not sorted_users:
        text += "Топ пока пуст."
    else:
        for i, u in enumerate(sorted_users, 1):
            is_prem = u["premium_until"] and u["premium_until"] > datetime.now()
            prem_icon = "🚀 " if is_prem else ""
            val = u['points'] if query.data == "top_points" else len(u['cards'])
            text += f"{i}. {u['nickname']} {prem_icon} — {val}\n"

    # ПРОВЕРКА: Если есть фото, правим подпись, если нет - текст
    if query.message.photo:
        await query.edit_message_caption(caption=text, parse_mode="Markdown")
    else:
        await query.edit_message_text(text, parse_mode="Markdown")

# --- ОБРАБОТЧИК КАРТ (Мои карты) ---
async def handle_my_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)

    if not user["cards"]:
        msg_text = ("<b>🃏 У тебя нет карт</b>\n"
                    "<blockquote>Получи карту командой «моба»</blockquote>")
        keyboard = None
    else:
        msg_text = (f"🃏 <b>Ваши карты</b>\n"
                    f"<blockquote>Всего {len(user['cards'])} / 260 карт</blockquote>")
        keyboard_layout = [
            [InlineKeyboardButton("❤️‍🔥 Коллекции", callback_data="show_collections")],
            [InlineKeyboardButton("🪬 LIMITED", callback_data="show_cards_rarity_LIMITED")],
            [InlineKeyboardButton("🃏 Все карты", callback_data="show_cards_all_none")]
        ]
        keyboard = InlineKeyboardMarkup(keyboard_layout)
    text = f"🃏 <b>Ваши карты</b>\n<blockquote>Всего {len(user['cards'])} карт</blockquote>"

    if query.message.photo:
        # Если есть фото, мы не можем редактировать текст. Удаляем фото и шлем текст.
        await query.message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        # Если фото нет (это уже текстовое сообщение), просто редактируем текст
        await query.edit_message_text(
            text=msg_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

async def handle_collections_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)

    # 1. Получаем названия коллекций ТОЛЬКО тех карт, которые есть у пользователя
    # Мы проходим по user["cards"] и собираем уникальные имена коллекций
    user_owned_collections = sorted(list(set(c['collection'] for c in user["cards"] if c.get('collection'))))

    if not user_owned_collections:
        text = "❤️‍🔥 <b>Ваши коллекции</b>\n\n<blockquote>У вас пока нет карт, принадлежащих какой-либо коллекции.</blockquote>"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("< Назад", callback_data="my_cards")]])
    else:
        keyboard = []
        for col_name in user_owned_collections:
            # Считаем сколько УНИКАЛЬНЫХ карт этой коллекции есть у игрока
            # (используем set, чтобы если у игрока 5 одинаковых карт, они считались как 1 в прогрессе коллекции)
            owned_ids_in_this_col = set(c['card_id'] for c in user["cards"] if c.get('collection') == col_name)
            count_in_col = len(owned_ids_in_this_col)

            # Считаем сколько всего карт в этой коллекции существует в глобальной базе CARDS
            total_in_col = sum(1 for c in CARDS if c.get('collection') == col_name)

            # Добавляем кнопку коллекции
            button_text = f"{col_name} ({count_in_col}/{total_in_col})"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_col_{col_name}_0")])

        keyboard.append([InlineKeyboardButton("< Назад", callback_data="my_cards")])
        text = "❤️‍🔥 <b>Ваши коллекции</b>\n<blockquote>Выберите коллекцию для просмотра</blockquote>"
        markup = InlineKeyboardMarkup(keyboard)

    # Отображение
    try:
        await query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    except Exception:
        await query.delete_message()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=text,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )

# 2. ПРОСМОТР КАРТОЧЕК КОЛЛЕКЦИИ (с перелистыванием)
async def view_collection_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)

    data = query.data.split("_")
    col_name, index = data[2], int(data[3])

    filtered = [c for c in user["cards"] if c["collection"] == col_name]
    card = filtered[index]

    caption = (f"<b><i>🃏 {col_name} •  {card['name']}</i></b>\n"
            f"<blockquote><b><i>Принесла вас {card['points']} очков !</i></b></blockquote>\n\n"
            f"<b>✨ Редкость •</b> <i>{card['rarity']}</i>\n"
            f"<b>💰 БО •</b><i> {card['bo']}</i>\n"
            f"<b>💎 Алмазы •</b> <i>{card['diamonds']}</i>\n\n"
            f"<blockquote><b><i>Карта добавлена в коллекцию!</i></b></blockquote>")

    nav = []
    if index > 0:
        nav.append(InlineKeyboardButton("<", callback_data=f"view_col_{col_name}_{index - 1}"))
    if index < len(filtered) - 1:
        nav.append(InlineKeyboardButton(">", callback_data=f"view_col_{col_name}_{index + 1}"))

    kb = [nav, [InlineKeyboardButton("К коллекциям", callback_data="show_collections")]]

    with open(card["image_path"], 'rb') as photo:
        if query.message.photo:
            await query.edit_message_media(InputMediaPhoto(photo, caption=caption, parse_mode=ParseMode.HTML),
                                           reply_markup=InlineKeyboardMarkup(kb))
        else:
            await query.message.delete()
            await context.bot.send_photo(query.message.chat_id, photo, caption=caption,
                                         reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

def get_card_view_markup(card, index, total, filter_type, filter_value):
    caption = (
        f"<b>⚜️ «{card['collection']}»</b>\n"
        f"<blockquote><i>Карта: {card['name']}</i></blockquote>\n\n"
        f"<b>✨ Редкость •</b> <i>{card['rarity']}</i>\n"
        f"<b>💰 БО •</b><i> {card['bo']}</i>\n"
        f"<b>💎 Алмазы •</b> <i>{card['diamonds']}</i>\n"
        f"<b>🔢 {index + 1} из {total}</b>"
    )

    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton("<", callback_data=f"move_{filter_type}_{filter_value}_{index - 1}"))
    if index < total - 1:
        nav_buttons.append(InlineKeyboardButton(">", callback_data=f"move_{filter_type}_{filter_value}_{index + 1}"))

    keyboard = [nav_buttons, [InlineKeyboardButton("< Назад", callback_data="my_cards")]]
    return caption, InlineKeyboardMarkup(keyboard)

async def show_filtered_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)

    # pattern: show_cards_{type}_{value}
    parts = query.data.split('_')
    if len(parts) < 4: return

    f_type, f_value = parts[2], parts[3]

    if f_type == "all":
        filtered = user["cards"]
    elif f_type == "rarity":
        filtered = [c for c in user["cards"] if c["rarity"] == f_value]
    else:
        filtered = []

    if not filtered:
        await query.answer("Карт не найдено", show_alert=True)
        return

    # Берем первую карту для показа
    card = filtered[0]
    caption, reply_markup = get_card_view_markup(card, 0, len(filtered), f_type, f_value)

    try:
        # Удаляем старое текстовое сообщение и отправляем фото
        await query.message.delete()
        with open(card["image_path"], 'rb') as photo:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logging.error(f"Error in show_filtered: {e}")
        await context.bot.send_message(query.message.chat_id, "Ошибка при загрузке фото.")

async def move_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)

    # pattern: move_{type}_{value}_{index}
    parts = query.data.split('_')
    f_type, f_value, index = parts[1], parts[2], int(parts[3])

    if f_type == "all":
        filtered = user["cards"]
    elif f_type == "rarity":
        filtered = [c for c in user["cards"] if c["rarity"] == f_value]
    else:
        filtered = []

    card = filtered[index]
    caption, reply_markup = get_card_view_markup(card, index, len(filtered), f_type, f_value)

    try:
        with open(card["image_path"], 'rb') as photo:
            await query.edit_message_media(
                media=InputMediaPhoto(media=photo, caption=caption, parse_mode=ParseMode.HTML),
                reply_markup=reply_markup
            )
    except Exception as e:
        logging.error(f"Error in move_card: {e}")

async def back_to_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Просто вызываем функцию профиля, но адаптированную под callback
    user = get_user(query.from_user.id)
    is_premium = user["premium_until"] and user["premium_until"] > datetime.now()
    prem_status = "✅ Есть" if is_premium else "❌ Нет"

    text = (
            f"👤 **Профиль: {user['nickname']}**\n"
            f"🆔 ID: `{user['id']}`\n"
            f"🎴 Карт: {len(user['cards'])}\n"
            f"📊 Очков: {user['points']}\n"
            f"💎 Алмазов: {user['diamonds']}\n"
            f"💰 Монет: {user['coins']}\n"
            f"👑 Премиум: {prem_status}"
    )
    keyboard = [[InlineKeyboardButton("🃏 Мои карты", callback_data="my_cards"),
                     InlineKeyboardButton("Сумка", callback_data="bag")]]

        # Так как профиль обычно с фото, а мы могли прийти из текстового меню:
    await query.message.delete()
    photos = await update.effective_user.get_profile_photos(limit=1)
    if photos.photos:
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=photos.photos[0][0].file_id,
                                         caption=text, reply_markup=InlineKeyboardMarkup(keyboard),
                                         parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text=text,
                                           reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    # --- ОБНОВЛЕННЫЙ MAIN ---

def main():
    application = Application.builder().token(TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("name", set_name))
    application.add_handler(CommandHandler("shop", shop))
    application.add_handler(CommandHandler("top", top_main_menu))
    #application.add_handler(CommandHandler("top", top_menu))
    application.add_handler(CommandHandler("premium", premium_info))
    application.add_handler(CommandHandler("account", profile))

    # Текстовые команды (Слова)
    application.add_handler(MessageHandler(filters.Regex(r"(?i)^аккаунт$"), profile))
    application.add_handler(MessageHandler(filters.Regex(r"(?i)^регнуть$"), regnut_handler))
    application.add_handler(MessageHandler(filters.Regex(r"(?i)^моба$"), mobba_handler))
    application.add_handler(MessageHandler(filters.Regex(r"^\d{9}\s\(\d{4}\)$"), id_detection_handler))
    # Профиль по слову "аккаунт"
    application.add_handler(MessageHandler(filters.Regex(r"(?i)^аккаунт$")
, profile))

    # Проверка ID (цифры)
    application.add_handler(MessageHandler(filters.Regex(r"^\d{9}\s\(\d{4}\)$"), id_detection_handler))

    # Получение карты по слову "моба"
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mobba_handler))

    # Платежи
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    application.add_handler(CallbackQueryHandler(top_main_menu, pattern="^top_main$"))
    application.add_handler(CallbackQueryHandler(top_category_callback, pattern="^top_category_"))
    application.add_handler(
        CallbackQueryHandler(show_specific_top, pattern="^top_(points|cards|stars_season|stars_all)$"))

    # Старые колбэки
    application.add_handler(CallbackQueryHandler(confirm_id_callback, pattern="^confirm_add_id$"))
    application.add_handler(CallbackQueryHandler(cancel_id_callback, pattern="^cancel_add_id$"))
    application.add_handler(CallbackQueryHandler(handle_my_cards, pattern="^my_cards$"))
    application.add_handler(CallbackQueryHandler(show_filtered_cards, pattern="^show_cards_"))
    application.add_handler(CallbackQueryHandler(move_card, pattern="^move_"))
    application.add_handler(CallbackQueryHandler(back_to_profile, pattern="^back_to_profile$"))
    application.add_handler(CallbackQueryHandler(handle_collections_menu, pattern="^show_collections$"))
    application.add_handler(CallbackQueryHandler(view_collection_cards, pattern="^view_col_"))
    application.add_handler(CallbackQueryHandler(handle_bag, pattern="^bag$"))
    application.add_handler(CallbackQueryHandler(start_payment, pattern="^(buy_prem|shop_coins)$"))
    # Callback-кнопки
    application.add_handler(CallbackQueryHandler(confirm_id_callback, pattern="^confirm_add_id$"))
    application.add_handler(CallbackQueryHandler(cancel_id_callback, pattern="^cancel_add_id$"))
    application.add_handler(CallbackQueryHandler(handle_my_cards, pattern="^my_cards$"))
    application.add_handler(CallbackQueryHandler(show_filtered_cards, pattern="^show_cards_"))
    application.add_handler(CallbackQueryHandler(move_card, pattern="^move_"))
    application.add_handler(CallbackQueryHandler(back_to_profile, pattern="^back_to_profile$"))
    application.add_handler(CallbackQueryHandler(handle_collections_menu, pattern="^show_collections$"))
    application.add_handler(CallbackQueryHandler(view_collection_cards, pattern="^view_col_"))
    application.add_handler(CallbackQueryHandler(handle_bag, pattern="^bag$"))
    application.add_handler(CallbackQueryHandler(show_top, pattern="^top_"))
    application.add_handler(CallbackQueryHandler(start_payment, pattern="^(buy_prem|shop_coins)$"))

    application.run_polling()


if __name__ == '__main__':

    main()















