from collections import defaultdict
from datetime import datetime
from re import compile
from typing import Optional, Union

from telethon import Button
from telethon.errors import UserIsBlockedError
from telethon.events import CallbackQuery, MessageDeleted, StopPropagation
from telethon.utils import get_display_name

from ..Config import Config
from ..core import check_owner, pool
from ..core.logger import logging
from ..core.session import tgbot
from ..helpers import reply_id
from ..helpers.utils import _format
from ..sql_helper.bot_blacklists import check_is_black_list
from ..sql_helper.bot_pms_sql import (
    add_user_to_db,
    get_user_id,
    get_user_logging,
    get_user_reply,
)
from ..sql_helper.bot_starters import add_starter_to_db, get_starter_details
from ..sql_helper.globals import dgvar, gvar
from . import BOTLOG, BOTLOG_CHATID, doge
from .botmanagers import ban_user_from_bot

plugin_category = "bot"
LOGS = logging.getLogger(__name__)
botusername = Config.BOT_USERNAME


class FloodConfig:
    BANNED_USERS = set()
    USERS = defaultdict(list)
    MESSAGES = 3
    SECONDS = 6
    ALERT = defaultdict(dict)
    AUTOBAN = 10


async def check_bot_started_users(user, event):
    if user.id == Config.OWNER_ID:
        return
    check = get_starter_details(user.id)
    if check is None:
        start_date = str(datetime.now().strftime("%B %d, %Y"))
        notification = f"đ¤ {_format.mentionuser(user.first_name , user.id)} has started me.\
                \n**đ ID: **`{user.id}`\
                \n**âšī¸ Name: **{get_display_name(user)}"
    else:
        start_date = check.date
        notification = f"đ¤ {_format.mentionuser(user.first_name , user.id)} has restarted me.\
                \n**đ ID: **`{user.id}`\
                \n**âšī¸ Name: **{get_display_name(user)}"
    try:
        add_starter_to_db(user.id, get_display_name(user), start_date, user.username)
    except Exception as e:
        LOGS.error(str(e))
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, notification)


@doge.shiba_cmd(
    pattern=f"^/start({botusername})?([\s]+)?$",
    incoming=True,
    func=lambda e: e.is_private,
)
async def bot_start(event):
    chat = await event.get_chat()
    user = await doge.get_me()
    if check_is_black_list(chat.id):
        return
    reply_to = await reply_id(event)
    mention = f"[{chat.first_name}](tg://user?id={chat.id})"
    my_mention = f"[{user.first_name}](tg://user?id={user.id})"
    first = chat.first_name
    last = chat.last_name
    fullname = f"{first} {last}" if last else first
    username = f"@{chat.username}" if chat.username else mention
    userid = chat.id
    my_first = user.first_name
    my_last = user.last_name
    my_fullname = f"{my_first} {my_last}" if my_last else my_first
    my_username = f"@{user.username}" if user.username else my_mention
    if chat.id != Config.OWNER_ID:
        customstrmsg = gvar("STARTTEXT") or None
        if customstrmsg is not None:
            start_msg = customstrmsg.format(
                mention=mention,
                first=first,
                last=last,
                fullname=fullname,
                username=username,
                userid=userid,
                my_first=my_first,
                my_last=my_last,
                my_fullname=my_fullname,
                my_username=my_username,
                my_mention=my_mention,
            )
        else:
            start_msg = f"**đļ Wolf! Wolf!**\
                        \nđž Hi {mention}!\
                        \n\n**đļ I am {my_mention}'s loyal dog.**\
                        \nđ­ You can contact to my master from here."
        buttons = [
            (Button.url("đŖ CĘá´É´É´á´Ę", "https://t.me/DogeUserBot"),),
            (
                Button.url("đŦ Sá´á´á´oĘá´", "https://t.me/DogeSup"),
                Button.url("đ§Š PĘá´ÉĸÉĒÉ´", "https://t.me/DogePlugin"),
            ),
        ]
    else:
        start_msg = f"**đļ Wolf! Wolf!\
                    \n\nđž Hey {my_mention}!\
                    \n\nđŦ How can i help you?**"
        buttons = [
            (Button.inline(f"đâđĻē Há´Ęá´", data="mainmenu"),),
        ]
    try:
        await event.client.send_message(
            chat.id,
            start_msg,
            link_preview=False,
            buttons=buttons,
            reply_to=reply_to,
        )
    except Exception as e:
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"**đ¨ ERROR:**\nâšī¸ There was a error while user starting your bot.\
                \nâĄī¸ `{e}`",
            )
    else:
        await check_bot_started_users(chat, event)


@doge.shiba_cmd(incoming=True, func=lambda e: e.is_private)
async def bot_pms(event):  # sourcery no-metrics
    chat = await event.get_chat()
    if check_is_black_list(chat.id):
        return
    if chat.id != Config.OWNER_ID:
        msg = await event.forward_to(Config.OWNER_ID)
        try:
            add_user_to_db(msg.id, get_display_name(chat), chat.id, event.id, 0, 0)
        except Exception as e:
            LOGS.error(str(e))
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"**đ¨ ERROR:**\nâšī¸ While storing messages details in database\
                    \nâĄī¸ `{str(e)}`",
                )
    else:
        if event.text.startswith("/"):
            return
        reply_to = await reply_id(event)
        if reply_to is None:
            return
        users = get_user_id(reply_to)
        if users is None:
            return
        for usr in users:
            user_id = int(usr.chat_id)
            reply_msg = usr.reply_id
            user_name = usr.first_name
            break
        if user_id is not None:
            try:
                if event.media:
                    msg = await event.client.send_file(
                        user_id, event.media, caption=event.text, reply_to=reply_msg
                    )
                else:
                    msg = await event.client.send_message(
                        user_id, event.text, reply_to=reply_msg, link_preview=False
                    )
            except UserIsBlockedError:
                return await event.reply(f"**â This bot was blocked by the user.**")
            except Exception as e:
                return await event.reply(f"**đ¨ ERROR:**\nâĄī¸ `{e}`")
            try:
                add_user_to_db(
                    reply_to, user_name, user_id, reply_msg, event.id, msg.id
                )
            except Exception as e:
                LOGS.error(str(e))
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        f"**đ¨ ERROR:**\nâšī¸ While storing messages details in database\
                        \nâĄī¸ `{e}`",
                    )


@doge.shiba_cmd(edited=True)
async def bot_pms_edit(event):  # sourcery no-metrics
    chat = await event.get_chat()
    if check_is_black_list(chat.id):
        return
    if chat.id != Config.OWNER_ID:
        users = get_user_reply(event.id)
        if users is None:
            return
        reply_msg = None
        for user in users:
            if user.chat_id == str(chat.id):
                reply_msg = user.message_id
                break
        if reply_msg:
            await event.client.send_message(
                Config.OWNER_ID,
                f"**âŦī¸ This message was edited by the user** {_format.mentionuser(get_display_name(chat) , chat.id)} **as:**\n",
                reply_to=reply_msg,
            )
            msg = await event.forward_to(Config.OWNER_ID)
            try:
                add_user_to_db(msg.id, get_display_name(chat), chat.id, event.id, 0, 0)
            except Exception as e:
                LOGS.error(str(e))
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        f"**đ¨ ERROR:**\nâšī¸ While storing messages details in database\
                        \nâĄī¸ `{e}`",
                    )
    else:
        reply_to = await reply_id(event)
        if reply_to is not None:
            users = get_user_id(reply_to)
            result_id = 0
            if users is None:
                return
            for usr in users:
                if event.id == usr.logger_id:
                    user_id = int(usr.chat_id)
                    reply_msg = usr.reply_id
                    result_id = usr.result_id
                    break
            if result_id != 0:
                try:
                    await event.client.edit_message(
                        user_id, result_id, event.text, file=event.media
                    )
                except Exception as e:
                    LOGS.error(str(e))


@tgbot.on(MessageDeleted)
async def handler(event):
    for msg_id in event.deleted_ids:
        users_1 = get_user_reply(msg_id)
        users_2 = get_user_logging(msg_id)
        if users_2 is not None:
            result_id = 0
            for usr in users_2:
                if msg_id == usr.logger_id:
                    user_id = int(usr.chat_id)
                    result_id = usr.result_id
                    break
            if result_id != 0:
                try:
                    await event.client.delete_messages(user_id, result_id)
                except Exception as e:
                    LOGS.error(str(e))
        if users_1 is not None:
            reply_msg = None
            for user in users_1:
                if user.chat_id != Config.OWNER_ID:
                    reply_msg = user.message_id
                    break
            try:
                if reply_msg:
                    users = get_user_id(reply_msg)
                    for usr in users:
                        user_id = int(usr.chat_id)
                        user_name = usr.first_name
                        break
                    if check_is_black_list(user_id):
                        return
                    await event.client.send_message(
                        Config.OWNER_ID,
                        f"**âŦī¸ This message was deleted by the user** {_format.mentionuser(user_name , user_id)}.",
                        reply_to=reply_msg,
                    )
            except Exception as e:
                LOGS.error(str(e))


@doge.shiba_cmd(pattern="^/uinfo$", from_users=Config.OWNER_ID)
async def bot_start(event):
    reply_to = await reply_id(event)
    if not reply_to:
        return await event.reply("**âšī¸ Reply to a message to get message info.**")
    info_msg = await event.client.send_message(
        event.chat_id,
        "`đ Searching for this user in my database...`",
        reply_to=reply_to,
    )
    users = get_user_id(reply_to)
    if users is None:
        return await info_msg.edit(
            "**đ¨ ERROR:** \nđ `Sorry! I couldn't find this user in my database.`"
        )
    for usr in users:
        user_id = int(usr.chat_id)
        user_name = usr.first_name
        break
    if user_id is None:
        return await info_msg.edit(
            "**đ¨ ERROR:** \nđ `Sorry! I couldn't find this user in my database.`"
        )
    uinfo = f"**đ¤ This message was sent by** {_format.mentionuser(user_name , user_id)}\
            \n**âšī¸ First Name:** {user_name}\
            \n**đ User ID:** `{user_id}`"
    await info_msg.edit(uinfo)


async def send_flood_alert(user_) -> None:
    # sourcery no-metrics
    buttons = [
        (
            Button.inline("đĢ Bá´É´", data=f"bot_pm_ban_{user_.id}"),
            Button.inline(
                "â Boá´ AÉ´á´ÉĒFĘooá´ OŌŌ",
                data="toggle_bot-antiflood_off",
            ),
        )
    ]
    found = False
    if FloodConfig.ALERT and (user_.id in FloodConfig.ALERT.keys()):
        found = True
        try:
            FloodConfig.ALERT[user_.id]["count"] += 1
        except KeyError:
            found = False
            FloodConfig.ALERT[user_.id]["count"] = 1
        except Exception as e:
            if BOTLOG:
                await doge.tgbot.send_message(
                    BOTLOG_CHATID,
                    f"**đ¨ ERROR:**\nâšī¸ While updating flood count\
                    \nâĄī¸ `{e}`",
                )
        flood_count = FloodConfig.ALERT[user_.id]["count"]
    else:
        flood_count = FloodConfig.ALERT[user_.id]["count"] = 1

    flood_msg = (
        r"**â ī¸ī¸ #Flood_Warning**"
        "\n\n"
        f"**đ ID:** `{user_.id}`\n"
        f"**âšī¸ Name:** {get_display_name(user_)}\n"
        f"**đ¤ User:** {_format.mentionuser(get_display_name(user_), user_.id)}"
        f"\n\n**âŊ is spamming your {botusername}!** -> [ Flood rate ({flood_count}) ]\n"
        f"__đĄ Quick Action__: Ignored from bot for a while."
    )

    if found:
        if flood_count >= FloodConfig.AUTOBAN:
            if user_.id in Config.SUDO_USERS:
                sudo_spam = (
                    f"**đ¤ Sudo User** {_format.mentionuser(user_.first_name , user_.id)}\
                    \n**đ ID:** `{user_.id}`\n\n"
                    f"**âŊ is flooding your {botusername}!**\
                    \n\nâšī¸ Check `.doge delsudo` to remove the user from Sudo."
                )
                if BOTLOG:
                    await doge.tgbot.send_message(BOTLOG_CHATID, sudo_spam)
            else:
                await ban_user_from_bot(
                    user_,
                    f"**â Auto banned flooding from {botusername}** [exceeded flood rate of ({FloodConfig.AUTOBAN})]",
                )
                FloodConfig.USERS[user_.id].clear()
                FloodConfig.ALERT[user_.id].clear()
                FloodConfig.BANNED_USERS.remove(user_.id)
            return
        fa_id = FloodConfig.ALERT[user_.id].get("fa_id")
        if not fa_id:
            return
        try:
            msg_ = await doge.tgbot.get_messages(BOTLOG_CHATID, fa_id)
            if msg_.text != flood_msg:
                await msg_.edit(flood_msg, buttons=buttons)
        except Exception as fa_id_err:
            LOGS.debug(fa_id_err)
            return
    else:
        if BOTLOG:
            fa_msg = await doge.tgbot.send_message(
                BOTLOG_CHATID,
                flood_msg,
                buttons=buttons,
            )
        try:
            chat = await doge.tgbot.get_entity(BOTLOG_CHATID)
            await doge.tgbot.send_message(
                Config.OWNER_ID,
                f"**â ī¸ī¸ [{botusername} flood warning!](https://t.me/c/{chat.id}/{fa_msg.id})**",
            )
        except UserIsBlockedError:
            if BOTLOG:
                await doge.tgbot.send_message(
                    BOTLOG_CHATID, f"**đ¨ Please unblock {botusername}!**"
                )
    if FloodConfig.ALERT[user_.id].get("fa_id") is None and fa_msg:
        FloodConfig.ALERT[user_.id]["fa_id"] = fa_msg.id


@doge.tgbot.on(CallbackQuery(data=compile(b"bot_pm_ban_([0-9]+)")))
@check_owner
async def bot_pm_ban_cb(c_q: CallbackQuery):
    user_id = int(c_q.pattern_match.group(1))
    try:
        user = await doge.get_entity(user_id)
    except Exception as e:
        await c_q.answer(f"**đ¨ ERROR:**\nâĄī¸ `{e}`")
    else:
        await c_q.answer(f"**âŗ Banning UserID ->** `{user_id}`**...**", alert=False)
        await ban_user_from_bot(user, "Spamming Bot")
        await c_q.edit(f"**â Successfully banned!\nđ User ID:** `{user_id}`")


def time_now() -> Union[float, int]:
    return datetime.timestamp(datetime.now())


@pool.run_in_thread
def is_flood(uid: int) -> Optional[bool]:
    """Checks if a user is flooding"""
    FloodConfig.USERS[uid].append(time_now())
    if (
        len(
            list(
                filter(
                    lambda x: time_now() - int(x) < FloodConfig.SECONDS,
                    FloodConfig.USERS[uid],
                )
            )
        )
        > FloodConfig.MESSAGES
    ):
        FloodConfig.USERS[uid] = list(
            filter(
                lambda x: time_now() - int(x) < FloodConfig.SECONDS,
                FloodConfig.USERS[uid],
            )
        )
        return True


@doge.tgbot.on(CallbackQuery(data=compile(b"toggle_bot-antiflood_off$")))
@check_owner
async def settings_toggle(c_q: CallbackQuery):
    if gvar("bot_antif") is None:
        return await c_q.answer(
            "**âšī¸ Bot AntiFlood was already disabled.**", alert=False
        )
    dgvar("bot_antif")
    await c_q.answer("**âšī¸ Bot AntiFlood disabled.**", alert=False)
    await c_q.edit("**âšī¸ BOT_ANTIFLOOD is now disabled!**")


@doge.shiba_cmd(incoming=True, func=lambda e: e.is_private)
@doge.shiba_cmd(edited=True, func=lambda e: e.is_private)
async def antif_on_msg(event):
    if gvar("bot_antif") is None:
        return
    chat = await event.get_chat()
    if chat.id == Config.OWNER_ID:
        return
    user_id = chat.id
    if check_is_black_list(user_id):
        raise StopPropagation
    if await is_flood(user_id):
        await send_flood_alert(chat)
        FloodConfig.BANNED_USERS.add(user_id)
        raise StopPropagation
    if user_id in FloodConfig.BANNED_USERS:
        FloodConfig.BANNED_USERS.remove(user_id)
