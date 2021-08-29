from asyncio import sleep
from asyncio.exceptions import CancelledError
from datetime import timedelta
from glob import glob
from os import environ, execle, remove
from pathlib import Path
from random import randint
from sys import executable as sysexecutable
from sys import exit

from pylists import *
from requests import get
from telethon import Button
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.channels import InviteToChannelRequest, JoinChannelRequest
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.functions.help import GetConfigRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.types import User

from .. import BOTLOG, BOTLOG_CHATID, PLUGIN_CHANNEL, PM_LOGGER_GROUP_ID, tr
from ..Config import Config
from ..core.logger import logging
from ..core.session import doge
from ..helpers.utils import install_pip
from ..sql_helper.global_collection import (
    del_keyword_collectionlist,
    get_item_collectionlist,
)
from ..sql_helper.globals import dgvar, gvar, sgvar
from .pluginmanager import load_module
from .tools import create_channel, create_supergroup

LOGS = logging.getLogger("DogeUserBot")


async def setup_bot():
    """
    To setup bot for userbot
    """
    try:
        await doge.connect()
        config = await doge(GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == doge.session.server_address:
                if doge.session.dc_id != option.id:
                    LOGS.warning(
                        f"Fixed DC ID in session from {doge.session.dc_id}"
                        f" to {option.id}"
                    )
                doge.session.set_dc(option.id, option.ip_address, option.port)
                doge.session.save()
                break
        await autous()
    except Exception as e:
        LOGS.error(f"STRING_SESSION - {e}")
        exit()

    if gvar("DOGELANG") is None:
        sgvar("DOGELANG", str(Config.DOGELANG))

    m_e = await doge.get_me()
    m_y_i_d = m_e.id
    if str(m_y_i_d) in G_YS:
        await doge.send_message(
            "me",
            f"\
**🦮 SORRY DUDE!\
\n💔 I won't work with you.\
\n🐶 My admins have banned you from using @DogeUserBot!\
\n\
\n💡 To find out why,\
\n🤡 Check out @DogeGays\
\n\
\n🌪 To appeal,\
\n💬 You can write to my @DogeSup group.**",
            file="https://telegra.ph/file/b7e740bbda31d43d510ab.jpg",
        )
        LOGS.error(
            "🐶 My admins have banned you from using @DogeUserBot!\n\
            🐾 Check your saved messages in Telegram."
        )
        await doge.disconnect()
        exit(1)


async def setup_assistantbot():
    """
    To setup assistant bot
    """
    if Config.BOT_TOKEN:
        sgvar("BOT_TOKEN", str(Config.BOT_TOKEN))
        return
    if gvar("BOT_TOKEN"):
        return
    LOGS.info("🦴 I'm creating your Telegram assistant bot with @BotFather!")
    my = await doge.get_me()
    botname = "🐶 " + my.first_name + "'s Assɪsᴛᴀɴᴛ Boᴛ"
    if my.username:
        botusername = my.username + "_Bot"
    else:
        botusername = "Doge_" + (str(my.id))[5:] + "_Bot"
    bf = "BotFather"
    try:
        await doge.send_message(bf, "/cancel")
    except YouBlockedUserError:
        await doge(UnblockRequest(bf))
        await doge.send_message(bf, "/cancel")
    await sleep(0.5)
    await doge.send_message(bf, "/newbot")
    await sleep(1)
    is_ok = (await doge.get_messages(bf, limit=1))[0].text
    if is_ok.startswith("That I cannot do."):
        LOGS.error(
            "🚨 Create a bot with @BotFather\n\
            and set it's token to BOT_TOKEN variable and restart me."
        )
        exit(1)

    await doge.send_message(bf, botname)
    await sleep(1)
    is_ok = (await doge.get_messages(bf, limit=1))[0].text
    if not is_ok.startswith("Good."):
        await doge.send_message(bf, "🐶 Mʏ Doɢᴇ Assɪsᴛᴀɴᴛ Boᴛ")
        await sleep(1)
        is_ok = (await doge.get_messages(bf, limit=1))[0].text
        if not is_ok.startswith("Good."):
            LOGS.info(
                "🚨 Create a bot with @BotFather\n\
                and set it's token to BOT_TOKEN variable and restart me."
            )
            exit(1)

    await doge.send_message(bf, botusername)
    await sleep(1)
    is_ok = (await doge.get_messages(bf, limit=1))[0].text
    await doge.send_read_acknowledge(bf)
    if is_ok.startswith("Sorry,"):
        ran = randint(1, 100)
        botusername = "Doge_" + (str(my.id))[6:] + str(ran) + "_Bot"
        await doge.send_message(bf, botusername)
        await sleep(1)
        now_ok = (await doge.get_messages(bf, limit=1))[0].text
        if now_ok.startswith("Done!"):
            bottoken = now_ok.split("`")[1]
            sgvar("BOT_TOKEN", bottoken)
            await doge.send_message(bf, "/setinline")
            await sleep(1)
            await doge.send_message(bf, f"@{botusername}")
            await sleep(1)
            await doge.send_message(bf, "🐶 Search...")
            LOGS.info(
                f"🦴 DONE! @{botusername} I'm created your Telegram assistant bot successfully!"
            )
        else:
            LOGS.info(
                "🚨 Please delete some of your Telegram bots at @Botfather or set variable BOT_TOKEN with token of a bot."
            )
            exit(1)

    elif is_ok.startswith("Done!"):
        bottoken = is_ok.split("`")[1]
        sgvar("BOT_TOKEN", bottoken)
        await doge.send_message(bf, "/setinline")
        await sleep(1)
        await doge.send_message(bf, f"@{botusername}")
        await sleep(1)
        await doge.send_message(bf, "🐶 Search...")
        LOGS.info(
            f"🦴 DONE! @{botusername} I'm created your Telegram assistant bot successfully!"
        )
    else:
        LOGS.info(
            "🚨 Please delete some of your Telegram bots at @Botfather or set variable BOT_TOKEN with token of a bot."
        )
        exit(1)


async def setup_me_bot():
    """
    To setup some necessary data
    """
    doge.me = await doge.get_me()
    doge.uid = doge.me.id

    if not doge.me.bot and Config.OWNER_ID == 0:
        Config.OWNER_ID = doge.uid

    if gvar("ALIVE_NAME") is None:
        if Config.ALIVE_NAME:
            sgvar("ALIVE_NAME", str(Config.ALIVE_NAME))
        else:
            my_first_name = doge.me.first_name
            sgvar("ALIVE_NAME", my_first_name)

    await doge.tgbot.start(bot_token=gvar("BOT_TOKEN"))
    doge.tgbot.me = await doge.tgbot.get_me()
    bot_details = doge.tgbot.me
    Config.BOT_USERNAME = f"@{bot_details.username}"


async def ipchange():
    """
    Just to check if ip change or not
    """
    newip = (get("https://httpbin.org/ip").json())["origin"]
    if gvar("ipaddress") is None:
        sgvar("ipaddress", newip)
        return None
    oldip = gvar("ipaddress")
    if oldip != newip:
        dgvar("ipaddress")
        LOGS.info("IP change detected")
        try:
            await doge.disconnect()
        except (ConnectionError, CancelledError):
            pass
        return "ip change"


async def load_plugins(folder):
    """
    To load plugins from the mentioned folder
    """
    path = f"userbot/{folder}/*.py"
    files = sorted(glob(path))
    for name in files:
        with open(name) as f:
            path1 = Path(f.name)
            shortname = path1.stem
            try:
                if shortname.replace(".py", "") not in Config.NO_LOAD:
                    flag = True
                    check = 0
                    while flag:
                        try:
                            load_module(
                                shortname.replace(".py", ""),
                                plugin_path=f"userbot/{folder}",
                            )
                            break
                        except ModuleNotFoundError as e:
                            install_pip(e.name)
                            check += 1
                            if check > 5:
                                break
                else:
                    remove(Path(f"userbot/{folder}/{shortname}.py"))
            except Exception as e:
                remove(Path(f"userbot/{folder}/{shortname}.py"))
                LOGS.error(f"Unable to load {shortname} because of error {e}")


async def verifyLoggerGroup():
    """
    Will verify the both loggers group
    """
    flag = False
    if BOTLOG:
        try:
            entity = await doge.get_entity(BOTLOG_CHATID)
            if not isinstance(entity, User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        "Permissions missing to send messages for the specified PRIVATE_GROUP_BOT_API_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "Permissions missing to addusers for the specified PRIVATE_GROUP_BOT_API_ID."
                    )
        except ValueError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID can't be found. Make sure it's correct."
            )
        except TypeError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID is unsupported. Make sure it's correct."
            )
        except Exception as e:
            LOGS.error(
                "An Exception occured upon trying to verify the PRIVATE_GROUP_BOT_API_ID.\n"
                + str(e)
            )
    else:
        descript = "🚧 DON'T LEAVE THIS GROUP!\n⛔ If you delete group,\nall your previous snips, etc. will be lost.\nㅤ\n🧡 @DogeUserBot"
        gphoto = await doge.upload_file(file="userbot/helpers/resources/DogeBotLog.jpg")
        _, groupid = await create_supergroup(
            "🐾 Doɢᴇ Boᴛ Loɢ", doge, Config.BOT_USERNAME, descript, gphoto
        )
        descmsg = "**🚧 DON'T LEAVE OR\n🚧 DON'T DELETE OR\n🚧 DON'T CHANGE THIS GROUP!**\n\n⛔ If you change or delete group,\nall your previous snips, welcome, etc. will be lost.\n\n**🧡 @DogeUserBot**"
        msg = await doge.send_message(groupid, descmsg)
        await msg.pin()
        sgvar("PRIVATE_GROUP_BOT_API_ID", groupid)
        print(
            "Private Group for PRIVATE_GROUP_BOT_API_ID is created successfully and added to vars."
        )
        flag = True
    if Config.PMLOGGER:
        if PM_LOGGER_GROUP_ID != -100 or gvar("PM_LOGGER_GROUP_ID"):
            return
        descript = "🚧 DON'T DELETE THIS GROUP!\n⛔ If you delete group,\nPM Logger won't work.\nㅤ\n🧡 @DogeUserBot"
        gphoto = await doge.upload_file(file="userbot/helpers/resources/DogePmLog.jpg")
        _, groupid = await create_supergroup(
            "🐾 Doɢᴇ Pᴍ Loɢ", doge, Config.BOT_USERNAME, descript, gphoto
        )
        descmsg = "**🚧 DON'T LEAVE OR\n🚧 DON'T DELETE OR\n🚧 DON'T CHANGE THIS GROUP!**\n\n⛔ If you change or delete group,\nPM Logger will not work.\n\n**🦴 IF YOU WANT TO DELETE THIS GROUP,\nMUST FIRST WRITE:**\n`.set var PMLOGGER False`\n\n**🧡 @DogeUserBot**"
        msg = await doge.send_message(groupid, descmsg)
        await msg.pin()
        sgvar("PM_LOGGER_GROUP_ID", groupid)
        print(
            "Private Group for PM_LOGGER_GROUP_ID is created succesfully and added to vars."
        )
        flag = True

    if PM_LOGGER_GROUP_ID != -100:
        try:
            entity = await doge.get_entity(PM_LOGGER_GROUP_ID)
            if not isinstance(entity, User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        "Permissions missing to send messages for the specified PM_LOGGER_GROUP_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "Permissions missing to addusers for the specified PM_LOGGER_GROUP_ID."
                    )
        except ValueError:
            LOGS.error("PM_LOGGER_GROUP_ID can't be found. Make sure it's correct.")
        except TypeError:
            LOGS.error("PM_LOGGER_GROUP_ID is unsupported. Make sure it's correct.")
        except Exception as e:
            LOGS.error(
                "An Exception occured upon trying to verify the PM_LOGGER_GROUP_ID.\n"
                + str(e)
            )

    if Config.PLUGINS:
        if PLUGIN_CHANNEL or gvar("PLUGIN_CHANNEL"):
            return
        descript = "🚧 DON'T DELETE THIS CHANNEL!\n⛔ If you delete channel,\nall installed extra plugins will be lost.\nㅤ\n🧡 @DogeUserBot"
        cphoto = await doge.upload_file(
            file="userbot/helpers/resources/DogeExtraPlugin.jpg"
        )
        _, channelid = await create_channel(
            "🐾 Doɢᴇ Exᴛʀᴀ Pʟᴜɢɪɴs", doge, descript, cphoto
        )
        descmsg = "**🚧 DON'T LEAVE OR\n🚧 DON'T DELETE OR\n🚧 DON'T CHANGE THIS CHANNEL!**\n\n⛔ If you change or delete channel,\nall your installed externally plugins will be lost.\n\n**🦴 IF YOU WANT TO DELETE THIS CHANNEL,\nMUST FIRST WRITE:**\n`.set var PLUGINS False`\n\n**🧡 @DogeUserBot**"
        msg = await doge.send_message(channelid, descmsg)
        await msg.pin()
        sgvar("PLUGIN_CHANNEL", channelid)
        print(
            "Private Channel for PLUGIN_CHANNEL is created successfully and added to vars."
        )
        flag = True

    if flag:
        executable = sysexecutable.replace(" ", "\\ ")
        args = [executable, "-m", "userbot"]
        execle(executable, *args, environ)
        exit(0)


async def add_bot_to_logger_group(chat_id):
    """
    To add bot to logger groups
    """
    bot_details = await doge.tgbot.get_me()
    try:
        await doge(
            AddChatUserRequest(
                chat_id=chat_id,
                user_id=bot_details.username,
                fwd_limit=1000000,
            )
        )
    except BaseException:
        try:
            await doge(
                InviteToChannelRequest(
                    channel=chat_id,
                    users=[bot_details.username],
                )
            )
        except Exception as e:
            LOGS.error(str(e))


async def customize_assistantbot():
    """
    To customize assistant bot
    """
    try:
        bot = await doge.get_entity(doge.tgbot.me.username)
        bf = "BotFather"
        if bot.photo is None:
            LOGS.info("🥏 I'm customizing your Telegram assistant bot with @BotFather!")
            botusername = f"@{doge.tgbot.me.username}"
            if (doge.me.username) is None:
                master = doge.me.first_name
            else:
                master = f"@{doge.me.username}"
            await doge.send_message(bf, "/cancel")
            await sleep(0.5)
            await doge.send_message(bf, "/start")
            await sleep(1)
            await doge.send_message(bf, "/setuserpic")
            await sleep(1)
            await doge.send_message(bf, botusername)
            await sleep(1)
            await doge.send_file(bf, "userbot/helpers/resources/DogeAssistant.jpg")
            await sleep(2)
            await doge.send_message(bf, "/setabouttext")
            await sleep(1)
            await doge.send_message(bf, botusername)
            await sleep(1)
            await doge.send_message(
                bf,
                f"🧡 I'ᴍ Assɪsᴛᴀɴᴛ Boᴛ oꜰ {master}\n\n🐶 Mᴀᴅᴇ wɪᴛʜ ❤️ ʙʏ @DogeUserBot 🐾",
            )
            await sleep(2)
            await doge.send_message(bf, "/setdescription")
            await sleep(1)
            await doge.send_message(bf, botusername)
            await sleep(1)
            await doge.send_message(
                bf,
                f"🐕‍🦺 Doɢᴇ UsᴇʀBoᴛ Assɪsᴛᴀɴᴛ Boᴛ\n🧡 Mᴀsᴛᴇʀ: {master}\n\n🐶 Mᴀᴅᴇ wɪᴛʜ ❤️ ʙʏ @DogeUserBot 🐾",
            )
            LOGS.info(
                f"🥏 DONE! @{botusername} I'm customized your Telegram assistant bot successfully!"
            )
    except Exception as e:
        LOGS.info(str(e))


async def startupmessage():
    """
    Start up message in Telegram logger group
    """
    try:
        if BOTLOG:
            Config.DOGELOGO = await doge.tgbot.send_file(
                BOTLOG_CHATID,
                "https://telegra.ph/file/dd72e42027e6e7de9c0c9.jpg",
                caption="**🧡 Doɢᴇ UsᴇʀBoᴛ Rᴇᴀᴅʏ To Usᴇ 🧡**",
                buttons=[
                    (
                        Button.inline(
                            f"🐕‍🦺 Hᴇʟᴘ",
                            data="mainmenu",
                        ),
                    ),
                    (
                        Button.inline(
                            f"🌍 Cʜoosᴇ ᴀ Lᴀɴɢᴜᴀɢᴇ",
                            data="lang_menu",
                        ),
                    ),
                    (
                        Button.url("💬 Sᴜᴘᴘoʀᴛ", "https://t.me/DogeSup"),
                        Button.url("🧩 Pʟᴜɢɪɴ", "https://t.me/DogePlugin"),
                    ),
                ],
            )
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        msg_details = list(get_item_collectionlist("restart_update"))
        if msg_details:
            msg_details = msg_details[0]
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        if msg_details:
            await doge.check_testcases()
            message = await doge.get_messages(msg_details[0], ids=msg_details[1])
            text = message.text + "\n\n**🐶 Doge is back and alive.**"
            await doge.edit_message(msg_details[0], msg_details[1], text)
            if gvar("restartupdate") is not None:
                await doge.send_message(
                    msg_details[0],
                    f"{tr}ping",
                    reply_to=msg_details[1],
                    schedule=timedelta(seconds=10),
                )
            del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
        return None


async def autous():
    try:
        await doge(JoinChannelRequest("@DogeUserBot"))
        if gvar("AUTOUS") is False:
            return
        else:
            try:
                await doge(JoinChannelRequest("@DogeSup"))
            except:
                pass
            try:
                await doge(JoinChannelRequest("@DogePlugin"))
            except:
                pass
    except:
        pass
