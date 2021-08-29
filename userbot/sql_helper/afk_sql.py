# Credits: Ultroid - UserBot
from datetime import datetime

from .globals import addgvar, gvarstatus

try:
    gvarstatus("AFK_DB")
except BaseException:
    addgvar("AFK_DB", "[]")


def add_afk(msg, media_type, media):
    time = datetime.now().strftime("%b %d %Y %I:%M:%S%p")
    addgvar("AFK_DB", str([msg, media_type, media, time]))
    return


def is_afk():
    afk = gvarstatus("AFK_DB")
    if afk:
        start_time = datetime.strptime(afk[3], "%b %d %Y %I:%M:%S%p")
        afk_since = str(datetime.now().replace(microsecond=0) - start_time)
        return afk[0], afk[1], afk[2], afk_since
    return False


def del_afk():
    return addgvar("AFK_DB", "[]")
