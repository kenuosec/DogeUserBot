# Credits: Ultroid - UserBot
from asyncio import sleep

from telegraph import upload_file
from telethon import Button
from telethon.events import NewMessage
from telethon.tl.functions.account import UpdateProfileRequest

from ..sql_helper.afk_sql import *
from ..sql_helper.pmpermit_sql import is_approved
from . import (
    BOTLOG_CHATID,
    DOGEAFK,
    Config,
    _format,
    doge,
    edl,
    eor,
    gvar,
    logging,
    media_type,
    tgbot,
)

plugin_category = "misc"
LOGS = logging.getLogger(__name__)

old_afk_msg = []


@doge.bot_cmd(
    pattern="afk(?:\s|$)([\s\S]*)",
    command=("afk", plugin_category),
    info={
        "header": "Enables afk for your account",
        "description": "When you are in afk if any one tags you then your bot will reply as he is offline.\
        AFK mean away from keyboard.",
        "options": "If you want AFK reason with media, then reply media.",
        "usage": [
            "{tr}afk <reason>",
        ],
        "examples": "{tr}afk Let Me Sleep",
        "note": "Switches off AFK when you type back anything, anywhere. You can use #afk in message to continue in afk without breaking it",
    },
)
async def set_afk(event):
    if event.client._bot:
        await edl(event, "Master, I'm a Bot, I can't be AFK..")
    elif is_afk():
        return

    text, media, minfo = None, None, None
    if event.pattern_match.group(1):
        text = event.text.split(maxsplit=1)[1]
    reply = await event.get_reply_message()
    if reply:
        if reply.text and not text:
            text = reply.text
        if reply.media:
            minfo = media_type(reply.media)
            if minfo.startswith(("Photo", "Gif")):
                file = await event.client.download_media(reply.media)
                iurl = upload_file(file)
                media = f"https://telegra.ph{iurl[0]}"
            elif "Sticker" in minfo:
                media = reply.file.id
            else:
                return await edl(event, "`Unsupported media`")

    await eor(event, "`Done`")
    add_afk(text, minfo, media)
    if gvar("AFKBIO"):
        await event.client(UpdateProfileRequest(about=f"{gvar('AFKBIO')}"))
    msg1, msg2 = None, None
    if text and media:
        if "Sticker" in minfo:
            msg1 = await event.client.send_file(event.chat_id, file=media)
            msg2 = await event.client.send_message(
                event.chat_id, "**I'm going AFK.**\n\n**Reason:** `{}`".format(text)
            )
        else:
            msg1 = await event.client.send_message(
                event.chat_id,
                "**I'm going AFK.**\n\n**Reason:** `{}`".format(text),
                file=media,
            )
    elif media:
        if "Sticker" in minfo:
            msg1 = await event.client.send_file(event.chat_id, file=media)
            msg2 = await event.client.send_message(event.chat_id, "**I'm going AFK.**")
        else:
            msg1 = await event.client.send_message(
                event.chat_id, "**I'm going AFK.**", file=media
            )
    elif text:
        msg1 = await event.client.send_message(
            event.chat_id, "**I'm going AFK.**\n\n**Reason:** `{}`".format(text)
        )
    else:
        msg1 = await event.client.send_message(event.chat_id, "**I'm going AFK.**")
    old_afk_msg.append(msg1)
    if msg2:
        old_afk_msg.append(msg2)
        return await tgbot.send_message(BOTLOG_CHATID, msg2.text)

    await tgbot.send_message(BOTLOG_CHATID, msg1.text)


@doge.on(NewMessage(outgoing=True))
async def remove_afk(event):
    if (
        event.is_private
        and gvar("pmpermit") == "true"
        and not is_approved(event.chat_id)
        and "afk"
        or "#afk" in event.text
    ):
        return

    if is_afk():
        _, _, _, afktime = is_afk()
        del_afk()
        if gvar("AFKRBIO"):
            await event.client(UpdateProfileRequest(about=f"{gvar('AFKRBIO')}"))
        afkevent = await event.reply(
            "**No Longer Afk**\n\nWas away for ~ `{}`".format(afktime)
        )
        await tgbot.send_message(
            BOTLOG_CHATID,
            "#AFK\nSet AFK mode to False.\nWas AFK since ~ `{}`".format(afktime),
        )
        for x in old_afk_msg:
            try:
                await x.delete()
            except BaseException:
                pass
        await sleep(3)
        await afkevent.delete()


@doge.on(
    NewMessage(incoming=True, func=lambda e: bool(e.mentioned or e.is_private)),
)
async def on_afk(event):
    if (
        event.is_private
        and gvar("pmpermit") == "true"
        and not is_approved(event.chat_id)
        or not is_afk()
        or "afk"
        and "#afk" in event.text
    ):
        return

    text, minfo, media, afktime = is_afk()
    msg1, msg2 = None, None
    chat = await event.get_user()
    mention = f"[{chat.first_name}](tg://user?id={chat.id})"
    first = chat.first_name
    last = chat.last_name
    fullname = f"{first} {last}" if last else first
    username = f"@{chat.username}" if chat.username else mention
    me = await event.client.get_me()
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    my_first = me.first_name
    my_last = me.last_name
    my_fullname = f"{my_first} {my_last}" if my_last else my_first
    my_username = f"@{me.username}" if me.username else my_mention
    customafkmsg = gvar("AFK") or None
    if customafkmsg is not None:
        if text:
            dogeafk = (
                customafkmsg.format(
                    mention=mention,
                    first=first,
                    last=last,
                    fullname=fullname,
                    username=username,
                    my_first=my_first,
                    my_last=my_last,
                    my_fullname=my_fullname,
                    my_username=my_username,
                    my_mention=my_mention,
                    afktime=afktime,
                )
                + f"\n\n\
                **???? Reason:** `{text}`"
            )
        else:
            dogafk = customafkmsg.format(
                mention=mention,
                first=first,
                last=last,
                fullname=fullname,
                username=username,
                my_first=my_first,
                my_last=my_last,
                my_fullname=my_fullname,
                my_username=my_username,
                my_mention=my_mention,
                afktime=afktime,
            )
    else:
        if text:
            dogeafk = (
                DOGEAFK
                + f"\n\n\
                **???? Reason:** `{text}`"
            )
        else:
            dogafk = DOGEAFK
    if text and media:
        if "Sticker" in minfo:
            msg1 = await event.reply(file=media)
            msg2 = await event.reply(dogeafk)
        else:
            msg1 = await event.reply(dogeafk, file=media)
    elif media:
        if "Sticker" in minfo:
            msg1 = await event.reply(file=media)
            msg2 = await event.reply(dogafk)
        else:
            msg1 = await event.reply(dogafk, file=media)
    elif text:
        msg1 = await event.reply(dogeafk)
    else:
        msg1 = await event.reply(dogafk)
    for x in old_afk_msg:
        try:
            await x.delete()
        except BaseException:
            pass
    old_afk_msg.append(msg1)
    if msg2:
        old_afk_msg.append(msg2)
    hmm = await event.get_chat()
    if Config.PM_LOGGER_GROUP_ID == -100:
        return

    full = None
    try:
        full = await event.client.get_entity(event.message.from_id)
    except Exception as e:
        LOGS.info(str(e))
    messaget = media_type(event)
    resalt = f"#AFK\n<b>Group: </b><code>{hmm.title}</code>"
    if full is not None:
        resalt += (
            f"\n<b>From: </b> ???? {_format.htmlmentionuser(full.first_name , full.id)}"
        )
    if messaget is not None:
        resalt += f"\n<b>Message Type: </b><code>{messaget}</code>"
    else:
        resalt += f"\n<b>Message: </b>{event.message.message}"
    button = [(Button.url("???? Message", f"https://t.me/c/{hmm.id}/{event.message.id}"))]
    if not event.is_private:
        await tgbot.send_message(
            Config.PM_LOGGER_GROUP_ID,
            resalt,
            parse_mode="html",
            link_preview=False,
            buttons=button,
        )
