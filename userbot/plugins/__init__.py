from os import makedirs
from os import path as osp

from heroku3 import from_key
from requests import get
from spamwatch import Client as spamwclient
from validators.url import url as validatorsurl

from .. import *
from ..Config import Config
from ..core.logger import logging
from ..core.managers import edl, eor
from ..core.session import doge, tgbot
from ..helpers import *
from ..helpers.utils import _dogetools, _dogeutils, _format, install_pip, reply_id
from ..languages import lan
from ..languages.constants import *

LOGS = logging.getLogger(__name__)
bot = doge


# OWNER:
ALIVE_NAME = gvarstatus("ALIVE_NAME")
AUTONAME = Config.AUTONAME

BIO_PREFIX = Config.BIO_PREFIX
DEFAULT_BIO = Config.DEFAULT_BIO

USERID = doge.uid if Config.OWNER_ID == 0 else Config.OWNER_ID
mention = f"[{gvarstatus('ALIVE_NAME')}](tg://user?id={USERID})"
hmention = f"<a href = tg://user?id={USERID}>{gvarstatus('ALIVE_NAME')}</a>"


# API VARS:
ANTISPAMBOT_BAN = gvarstatus("ANTISPAMBOT_BAN")

CURRENCY_API = gvarstatus("CURRENCY_API")

DEEPAI_API = gvarstatus("DEEPAI_API")

G_DRIVE_CLIENT_ID = gvarstatus("G_DRIVE_CLIENT_ID")
G_DRIVE_CLIENT_SECRET = gvarstatus("G_DRIVE_CLIENT_SECRET")
G_DRIVE_DATA = gvarstatus("G_DRIVE_DATA")
G_DRIVE_FOLDER_ID = gvarstatus("G_DRIVE_FOLDER_ID")
G_DRIVE_INDEX_LINK = gvarstatus("G_DRIVE_INDEX_LINK")

GENIUS_API = gvarstatus("GENIUS_API")

GITHUB_ACCESS_TOKEN = gvarstatus("GITHUB_ACCESS_TOKEN")
GIT_REPO_NAME = gvarstatus("GIT_REPO_NAME")

IBM_WATSON_CRED_URL = gvarstatus("IBM_WATSON_CRED_URL")
IBM_WATSON_CRED_PASSWORD = gvarstatus("IBM_WATSON_CRED_PASSWORD")

IPDATA_API = gvarstatus("IPDATA_API")

LASTFM_API = gvarstatus("LASTFM_API")
LASTFM_SECRET = gvarstatus("LASTFM_SECRET")
LASTFM_USERNAME = gvarstatus("LASTFM_USERNAME")
LASTFM_PASSWORD_PLAIN = gvarstatus("LASTFM_PASSWORD_PLAIN")

OCRSPACE_API = gvarstatus('OCRSPACE_API')

RANDOMSTUFF_API = gvarstatus("RANDOMSTUFF_API")

REMOVEBG_API = gvarstatus("REMOVEBG_API")

if gvarstatus("SPAMWATCH_API"):
    token = gvarstatus("SPAMWATCH_API")
    SPAMWATCH = spamwclient(token)
else:
    SPAMWATCH = None

SPOTIFY_DC = gvarstatus("SPOTIFY_DC")
SPOTIFY_KEY = gvarstatus("SPOTIFY_KEY")

SS_API = gvarstatus("SS_API")

TG_2STEP_VERIFICATION_CODE = gvarstatus("TG_2STEP_VERIFICATION_CODE")

WATCH_COUNTRY = gvarstatus("WATCH_COUNTRY")

WEATHER_API = gvarstatus("WEATHER_API") or '6fded1e1c5ef3f394283e3013a597879'
WEATHER_CITY = gvarstatus("WEATHER_CITY") or "Istanbul"


# PM:
PM_START = []
PMMESSAGE_CACHE = {}
PMMENU = "pmpermit_menu" not in Config.NO_LOAD


# HEROKU:
Heroku = from_key(Config.HEROKU_API_KEY)
heroku_api = "https://api.heroku.com"
HEROKU_APP_NAME = Config.HEROKU_APP_NAME
HEROKU_API_KEY = Config.HEROKU_API_KEY


# DIRECTORIES:
TMP_DOWNLOAD_DIRECTORY = Config.TMP_DOWNLOAD_DIRECTORY

if not osp.isdir(TMP_DOWNLOAD_DIRECTORY):
    makedirs(TMP_DOWNLOAD_DIRECTORY)

thumb_image_path = osp.join(TMP_DOWNLOAD_DIRECTORY, "thumb_image.jpg")

if Config.THUMB_IMAGE is not None:
    check = validatorsurl(Config.THUMB_IMAGE)
    if check:
        try:
            with open(thumb_image_path, "wb") as f:
                f.write(get(Config.THUMB_IMAGE).content)
        except Exception as e:
            LOGS.info(str(e))
