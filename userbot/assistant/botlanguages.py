# Credits: Ultroid - UserBot
from re import compile

from telethon import Button
from telethon.events import CallbackQuery

from ..core import check_owner
from ..core.logger import logging
from ..sql_helper.globals import sgvar
from . import doge, get_back_button, lngs

plugin_category = "bot"
LOGS = logging.getLogger(__name__)


@doge.tgbot.on(CallbackQuery(data=compile(r"lang_menu")))
@check_owner
async def setlang(event):
    languages = lngs()
    dogelangs = [
        Button.inline(
            f"{languages[dogelang]['natively']}",
            data=f"set_{dogelang}",
        )
        for dogelang in languages
    ]
    buttons = list(zip(dogelangs[::2], dogelangs[1::2]))
    if len(dogelangs) % 2 == 1:
        buttons.append((dogelangs[-1],))
    buttons.append([Button.inline("🐾 Mᴇɴᴜ", data="mainmenu")])
    await event.edit(
        "**🐶 [Doɢᴇ UsᴇʀBoᴛ](https://t.me/DogeUserBot)\
        \n🐾 Hᴇʟᴘᴇʀ\
        \n\
        \n🌍 Doɢᴇ's Lᴀɴɢᴜᴀɢᴇs:**",
        buttons=buttons,
        link_preview=False,
    )


@doge.tgbot.on(CallbackQuery(data=compile(b"set_(.*)")))
@check_owner
async def setthelang(event):
    lang = event.data_match.group(1).decode("UTF-8")
    languages = lngs()
    sgvar("DOGELANG", lang)
    await event.edit(
        f"**🌍 From now on, I will speak in {languages[lang]['natively']}.**",
        buttons=get_back_button("lang_menu"),
    )
