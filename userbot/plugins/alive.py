from datetime import datetime
from platform import python_version
from random import choice
from re import compile
from time import time

from telethon.errors.rpcerrorlist import (
    MediaEmptyError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
)
from telethon.events import CallbackQuery
from telethon.version import __version__

from . import (
    Config,
    StartTime,
    check_data_base_heal_th,
    doge,
    dogealive,
    eor,
    get_readable_time,
    gvar,
    mention,
    reply_id,
    tr,
    vdoge,
)

plugin_category = "bot"

temp = "{msg}\n\
\n\
┏━━━━━━✦❘༻༺❘✦━━━━━━┓\n\
┃ ᴅoɢᴇ oғ - {mention}\n\
┗━━━━━━✦❘༻༺❘✦━━━━━━┛\n\
\n\
┏━━━━━━✦❘༻༺❘✦━━━━━━┓\n\
┃ ᴅoɢᴇ ᴠᴇʀꜱɪoɴ - {dv}\n\
┃ ᴀʟɪᴠᴇ ꜱɪɴᴄᴇ - {uptime}\n\
┃ ꜱᴛᴀᴛᴜꜱ - {db}\n\
┃ ᴛᴇʟᴇᴛʜoɴ ᴠᴇʀꜱɪoɴ - {tv}\n\
┃ ᴘʏᴛʜoɴ ᴠᴇʀꜱɪoɴ - {pv}\n\
┗━━━━━━✦❘༻༺❘✦━━━━━━┛\n\
\n\
┏━━━━━━✦❘༻༺❘✦━━━━━━┓\n\
┃ ᴘɪɴɢ - {ping} ms\n\
┗━━━━━━✦❘༻༺❘✦━━━━━━┛\n\
        ↠━━━━━ღ◆ღ━━━━━↞"

itemp = "{msg}\n\
┏━━━━━━✦❘༻༺❘✦━━━━━━┓\n\
┃ ᴅoɢᴇ oғ - {mention}\n\
┗━━━━━━✦❘༻༺❘✦━━━━━━┛\n\
\n\
┏━━━━━━✦❘༻༺❘✦━━━━━━┓\n\
┃ ᴅoɢᴇ ᴠᴇʀꜱɪoɴ - {dv}\n\
┃ ᴀʟɪᴠᴇ ꜱɪɴᴄᴇ - {uptime}\n\
┃ ꜱᴛᴀᴛᴜꜱ - {db}\n\
┃ ᴛᴇʟᴇᴛʜoɴ ᴠᴇʀꜱɪoɴ - {tv}\n\
┃ ᴘʏᴛʜoɴ ᴠᴇʀꜱɪoɴ - {pv}\n\
┗━━━━━━✦❘༻༺❘✦━━━━━━┛"


@doge.bot_cmd(
    pattern="alive$",
    command=("alive", plugin_category),
    info={
        "header": "To check bot's alive status",
        "options": "To show media in this cmd you need to set ALIVE_PIC with media link, get this by replying the media by {tr}tgm",
        "usage": [
            "{tr}alive",
        ],
    },
)
async def thisalive(event):
    "A kind of showing bot details"
    start = datetime.now()
    await event.edit("ㅤ")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    reply_to_id = await reply_id(event)
    uptime = await get_readable_time((time() - StartTime))
    _, check_sgnirts = check_data_base_heal_th()
    ALIVE_TEXT = gvar("ALIVE_TEXT") or "🐶 Doɢᴇ UsᴇʀBoᴛ 🐾"
    DOG_IMG = gvar("ALIVE_PIC") or "https://telegra.ph/file/dd72e42027e6e7de9c0c9.jpg"
    doge_caption = gvar("ALIVE") or temp
    caption = doge_caption.format(
        msg=ALIVE_TEXT,
        mention=mention,
        dv=vdoge,
        uptime=uptime,
        db=check_sgnirts,
        tv=__version__,
        pv=python_version(),
        ping=ms,
    )
    if DOG_IMG:
        DOG = [x for x in DOG_IMG.split()]
        PIC = choice(DOG)
        try:
            await event.client.send_file(
                event.chat_id, PIC, caption=caption, reply_to=reply_to_id
            )
            await event.delete()
        except (WebpageMediaEmptyError, MediaEmptyError, WebpageCurlFailedError):
            return await eor(
                event,
                f"**Media Value Error!!**\n__Change the link by __`{tr}setdog`\n\n**__Can't get media from this link :-**__ `{PIC}`",
            )
    else:
        await eor(event, caption)


@doge.bot_cmd(
    pattern="ialive$",
    command=("ialive", plugin_category),
    info={
        "header": "To check bot's alive status via inline mode",
        "options": "To show media in this cmd you need to set ALIVE_PIC with media link, get this by replying the media by .tgm",
        "usage": [
            "{tr}ialive",
        ],
    },
)
async def thisialive(event):
    "A kind of showing bot details by your inline bot"
    start = datetime.now()
    await eor(event, "ㅤ")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    reply_to_id = await reply_id(event)
    uptime = await get_readable_time((time() - StartTime))
    _, check_sgnirts = check_data_base_heal_th()
    ALIVE_TEXT = "ㅤ"
    doge_caption = gvar("ALIVE") or itemp
    caption = doge_caption.format(
        msg=ALIVE_TEXT,
        mention=mention,
        uptime=uptime,
        tv=__version__,
        dv=vdoge,
        pv=python_version(),
        db=check_sgnirts,
        ping=ms,
    )
    results = await event.client.inline_query(Config.BOT_USERNAME, caption)
    await results[0].click(event.chat_id, reply_to=reply_to_id, hide_via=True)
    await event.delete()


@doge.tgbot.on(CallbackQuery(data=compile(b"infos")))
async def on_plug_in_callback_query_handler(event):
    statstext = await dogealive()
    await event.answer(statstext, cache_time=0, alert=True)
