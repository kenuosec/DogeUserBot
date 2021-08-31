from googletrans import LANGUAGES
from telethon.events import NewMessage
from validators.url import url as validatorsurl

from . import (
    BOTLOG,
    BOTLOG_CHATID,
    dgvar,
    doge,
    edl,
    eor,
    fsmessage,
    gvar,
    lan,
    logging,
    sgvar,
    tgbot,
)

plugin_category = "bot"
LOGS = logging.getLogger(__name__)

vlist = [
    "AFK",
    "AFKBIO",
    "AFKRBIO",
    "ALIVE",
    "ALIVE_NAME",
    "ALIVE_PIC",
    "ALIVE_TEXT",
    "CUSTOM_STICKER_PACKNAME",
    "DOGELANG",
    "HELP_EMOJI",
    "HELP_TEXT",
    "IALIVE_PIC",
    "MAX_FLOOD_IN_PMS",
    "NO_OF_ROWS_IN_HELP",
    "NO_OF_COLUMNS_IN_HELP",
    "PM_PIC",
    "PM_TEXT",
    "PM_BLOCK",
    "STARTTEXT",
]
alist = [
    "ANTISPAMBOT_BAN",
    "CURRENCY_API",
    "DEEPAI_API",
    "G_DRIVE_CLIENT_ID",
    "G_DRIVE_CLIENT_SECRET",
    "G_DRIVE_DATA",
    "G_DRIVE_FOLDER_ID",
    "G_DRIVE_INDEX_LINK",
    "GENIUS_API",
    "GITHUB_ACCESS_TOKEN",
    "GIT_REPO_NAME",
    "IBM_WATSON_CRED_URL",
    "IBM_WATSON_CRED_PASSWORD",
    "IPDATA_API",
    "LASTFM_API",
    "LASTFM_USERNAME",
    "LASTFM_PASSWORD_PLAIN",
    "LASTFM_SECRET",
    "OCRSPACE_API",
    "RANDOMSTUFF_API",
    "REMOVEBG_API",
    "SPAMWATCH_API",
    "SPOTIFY_DC",
    "SPOTIFY_KEY",
    "SS_API",
    "TG_2STEP_VERIFICATION_CODE",
    "WATCH_COUNTRY",
    "WEATHER_API",
    "WEATHER_CITY",
]
oldvars = {
    "PM_TEXT": "pmpermit_txt",
    "PM_BLOCK": "pmblock",
}


@doge.bot_cmd(
    pattern="(set|get|del)dog(?: |$)([\s\S]*)",
    command=("dog", plugin_category),
    info={
        "header": "Set vars in database or check or delete",
        "description": "Set, fetch or delete values or vars directly in database without restart or heroku vars.\n\nYou can set multiple pics by giving space after links in alive, ialive, pm permit.",
        "flags": {
            "set": "To set new var in database or modify the old var",
            "get": "To show the already existing var value.",
            "del": "To delete the existing value",
        },
        "var name": "**[List of Database Vars]**# TODO",
        "usage": [
            "{tr}setdog <var name> <var value>",
            "{tr}getdog <var name>",
            "{tr}deldog <var name>",
        ],
        "examples": [
            "{tr}setdog ALIVE_PIC <pic link>",
            "{tr}setdog ALIVE_PIC <pic link 1> <pic link 2>",
            "{tr}getdog ALIVE_PIC",
            "{tr}deldog ALIVE_PIC",
        ],
    },
)
async def dvdvdv(event):  # sourcery no-metrics
    "To manage vars in database"
    cmd = event.pattern_match.group(1).lower()
    vname = event.pattern_match.group(2)
    vnlist = "".join(f"{i}. `{each}`\n" for i, each in enumerate(vlist, start=1))
    apilist = "".join(f"{i}. `{each}`\n" for i, each in enumerate(alist, start=1))
    if not vname:
        return await eor(
            event,
            f"**🪀 Give correct VAR name from the list:\n\n**{vnlist}\n\n\n**⚙️ Give correct API name from the list:\n\n**{apilist}",
        )

    vinfo = None
    if " " in vname:
        vname, vinfo = vname.split(" ", 1)
    reply = await event.get_reply_message()
    if not vinfo and reply:
        vinfo = reply.text
    if vname in vlist:
        if vname in oldvars:
            vname = oldvars[vname]
        if cmd == "set":
            if not vinfo and (vname == "ALIVE" or vname == "AFK"):
                return await edl(
                    event,
                    "**💠 Check @DogeTemp for alive templates.**",
                    45,
                )

            if len(vinfo) > 70 and (vname == "AFKBIO" or vname == "AFKRBIO"):
                return await edl(
                    event,
                    "**🚧 Max bio length is 70 characters.**",
                )

            if not vinfo:
                return await edl(
                    event, f"Give some values which you want to save for **{vname}**"
                )

            check = vinfo.split(" ")
            for i in check:
                if "PIC" in vname and not validatorsurl(i):
                    return await edl(event, "**Give me a correct link...**")

            sgvar(vname, vinfo)
            if BOTLOG_CHATID:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"#SET_DATAVAR\
                    \n**{vname}** is updated newly in database as below",
                )
                await event.client.send_message(BOTLOG_CHATID, vinfo, silent=True)
            await edl(
                event, f"🪀 Value of **{vname}** is changed to: `{vinfo}`", time=20
            )
        if cmd == "get":
            var_data = gvar(vname)
            await edl(event, f"🪀 Value of **{vname}** is  `{var_data}`", time=20)
        elif cmd == "del":
            dgvar(vname)
            if BOTLOG_CHATID:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"#DEL_DATAVAR\
                    \n**{vname}** is deleted from database",
                )
            await edl(
                event,
                f"🪀 Value of **{vname}** is now deleted & set to default.",
                time=20,
            )
    elif vname in apilist:
        apiname = vname
        apinfo = vinfo
        if cmd == "set":
            if not apinfo:
                return await edl(
                    event, f"Give some values which you want to save for **{apiname}**"
                )

            sgvar(apiname, apinfo)
            if BOTLOG_CHATID:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"#SET_APIDATA\
                    \n**{apiname}** is updated newly in database as below",
                )
                await event.client.send_message(BOTLOG_CHATID, apinfo, silent=True)
            await edl(
                event,
                f"⚙️ Value of **{apiname}** is changed.",
            )
        if cmd == "get":
            api_data = gvar(apiname)
            await edl(event, "**I sent API data to BOTLOG.**")
            await event.client.send_message(
                BOTLOG_CHATID,
                f"⚙️ Value of **{apiname}** is  `{api_data}`",
            )
        elif cmd == "del":
            dgvar(apiname)
            if BOTLOG_CHATID:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"#DEL_APIDATA\
                    \n**{apiname}** is deleted from database",
                )
            await edl(
                event,
                f"⚙️ Value of **{apiname}** is now deleted & set to default.",
                time=20,
            )
    else:
        await eor(
            event,
            f"**🪀 Give correct VAR name from the list:\n\n**{vnlist}\n\n\n**⚙️ Give correct API name from the list:\n\n**{apilist}",
        )


@doge.bot_cmd(
    pattern="(custom|de[gğ]i[sş]tir) (pmpermit|pmblock|startmsg|afk)$",
    command=("custom", plugin_category),
    info={
        "header": "To customize your DogeUserBot.",
        "options": {
            "pmpermit": "To customize pmpermit text. ",
            "pmblock": "To customize pmpermit block message.",
            "startmsg": "To customize startmsg of bot when some one started it.",
        },
        "custom": {
            "{mention}": "mention user",
            "{first}": "first name of user",
            "{last}": "last name of user",
            "{fullname}": "fullname of user",
            "{username}": "username of user",
            "{userid}": "userid of user",
            "{my_first}": "your first name",
            "{my_last}": "your last name ",
            "{my_fullname}": "your fullname",
            "{my_username}": "your username",
            "{my_mention}": "your mention",
            "{totalwarns}": "totalwarns",
            "{warns}": "warns",
            "{remwarns}": "remaining warns",
            "{afktime}": "see afk time for afk command",
        },
        "usage": "{tr}custom <option> reply",
        "NOTE": "You can set,fetch or delete these by `{tr}setdog` , `{tr}getdog` & `{tr}deldog` as well.",
    },
)
async def custom_dogeuserbot(event):
    "To customize your DogeUserBot."
    reply = await event.get_reply_message()
    text = None
    if reply:
        text = reply.text
    if text is None:
        return await edl(event, "__Reply to custom text or url__")
    input_str = event.pattern_match.group(1)
    if input_str == "pmpermit":
        sgvar("pmpermit_txt", text)
    if input_str == "pmblock":
        sgvar("pmblock", text)
    if input_str == "startmsg":
        sgvar("STARTTEXT", text)
    if input_str == "afk":
        sgvar("AFK", text)
    await eor(event, f"__Your custom {input_str} has been updated__")
    if BOTLOG_CHATID:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#SET_DATAVAR\
                    \n**{input_str}** is updated newly in database as below",
        )
        await event.client.send_message(BOTLOG_CHATID, text, silent=True)


@doge.bot_cmd(
    pattern="lang (ai|tocr|trt|tts|xg) ([\s\S]*)",
    command=("lang", plugin_category),
    info={
        "header": "Set language for many command.",
        "description": "For langugage codes check [this link](https://telegra.ph/LANGUAGE-CODES-07-01)",
        "options": {
            "ai": "Set language for chatbot(ai)",
            "tocr": "Set language for tocr command",
            "trt": "Set language for trt command",
            "tts": "Set language for tts command",
            "xg": "Set language for Xiaomi plugin",
        },
        "usage": "{tr}lang option <language codes>",
        "examples": [
            "{tr}lang ai tr",
            "{tr}lang tocr tur",
            "{tr}lang trt tr",
            "{tr}lang tts tr",
            "{tr}lang xg tr",
        ],
    },
)
async def lang_set(value):
    "To set language for trt comamnd."
    arg = value.pattern_match.group(2).lower()
    input_str = value.pattern_match.group(1)
    if arg not in LANGUAGES:
        return await eor(
            value,
            f"`🚨 Invalid Language code!`\n**🌐 Available language codes:**\n\n`{LANGUAGES}`",
        )
    LANG = LANGUAGES[arg]
    if input_str == "trt":
        sgvar("TRT_LANG", arg)
        await eor(value, f"**🌐 Language for Translator changed to {LANG.title()}.**")
    elif input_str == "tts":
        sgvar("TTS_LANG", arg)
        await eor(value, f"**🌐 Language for Text to Speech changed to {LANG.title()}.**")
    elif input_str == "tocr":
        sgvar("TOCR_LANG", arg)
        await eor(value, f"**🌐 Language for Translated OCR changed to {LANG.title()}.**")
    elif input_str == "ai":
        sgvar("AI_LANG", arg)
        await eor(value, f"**🌐 Language for AI ChatBot changed to {LANG.title}.**")
    elif input_str == "xg":
        dogevent = await eor(value, lan("processing"))
        chat = "@XiaomiGeeksBot"
        async with doge.conversation(chat) as conv:
            if arg == "ar":
                xl = "ar - Arabic (العربية)"
            elif arg == "be":
                xl = "be - Belarusian (Беларуская)"
            elif arg == "bg":
                xl = "bg - Bulgarian (български език)"
            elif arg == "cn":
                xl = "zh-CN - Chinese (中文)"
            elif arg == "cs":
                xl = "cs - Czech (česky)"
            elif arg == "de":
                xl = "de - German (Deutsch)"
            elif arg == "en":
                xl = "en - English (English)"
            elif arg == "es":
                xl = "es-ES - Spanish (español)"
            elif arg == "fr":
                xl = "fr - French (français)"
            elif arg == "id":
                xl = "id - Indonesian (Bahasa Indonesia)"
            elif arg == "it":
                xl = "it - Italian (Italiano)"
            elif arg == "mx":
                xl = "es-MX - Spanish (Mexico) (español)"
            elif arg == "nl":
                xl = "nl - Dutch (Nederlands)"
            elif arg == "pl":
                xl = "pl - Polish (polski)"
            elif arg == "pt":
                xl = "pt-BR - Portuguese (Brazil) (Português)"
            elif arg == "ru":
                xl = "ru - Russian (русский язык)"
            elif arg == "sq":
                xl = "sq - Albanian (Shqip)"
            elif arg == "tr":
                xl = "tr - Turkish (Türkçe)"
            try:
                await fsmessage(
                event=value,
                text=xl,
                chat=chat,
                )
            except UnboundLocalError:
                return await edl(
                value,
                "🌐 @XiaomiGeekBot Language List:\
                        \n\
                        \n🇸🇦 `ar` - Arabic (العربية)\
                        \n🇧🇾 `be` - Belarusian (Беларуская)\
                        \n🇧🇬 `bg` - Bulgarian (български език)\
                        \n🇨🇳 `cn` - Chinese (中文)\
                        \n🇨🇿 `cs` - Czech (česky)\
                        \n🇩🇪 `de` - German (Deutsch)\
                        \n🇬🇧 `en` - English (English)\
                        \n🇪🇸 `es` - Spanish (español)\
                        \n🇲🇽 `mx` - Spanish (Mexico) (español)\
                        \n🇫🇷 `fr` - French (français)\
                        \n🇮🇩 `id` - Indonesian (Bahasa Indonesia)\
                        \n🇮🇹 `it` - Italian (Italiano)\
                        \n🇳🇱 `nl` - Dutch (Nederlands)\
                        \n🇵🇱 `pl` - Polish (polski)\
                        \n🇵🇹 `pt` - Portuguese (Brazil) (Português)\
                        \n🇷🇺 `ru` - Russian (русский язык)\
                        \n🇦🇱 `sq` - Albanian (Shqip)\
                        \n🇹🇷 `tr` - Turkish (Türkçe)",
                time=60,
            )

            await conv.wait_event(NewMessage(incoming=True, from_users=chat))
            await dogevent.edit(
                f"**🌐 Language for @XiaomiGeeksBot changed to {LANG.title}.**"
            )
            await conv.mark_read()
            await conv.cancel_all()

    if BOTLOG:
        if input_str == "trt":
            await tgbot.send_message(
                BOTLOG_CHATID, f"#SET_LANGUAGE\n\n**🌐 Language for Translator changed to {LANG.title()}.**"
            )
        elif input_str == "tts":
            await tgbot.send_message(
                BOTLOG_CHATID, f"#SET_LANGUAGE\n\n**🌐 Language for Text to Speech changed to {LANG.title()}.**"
            )
        elif input_str == "tocr":
            await tgbot.send_message(
                BOTLOG_CHATID,
                f"#SET_LANGUAGE\n\n**🌐 Language for Translated OCR changed to {LANG.title()}.**",
            )
        elif input_str == "ai":
            await tgbot.send_message(
                BOTLOG_CHATID, f"#SET_LANGUAGE\n\n**🌐 Language for AI ChatBot is changed to {LANG.title()}.**"
            )
        elif input_str == "xg":
            await tgbot.send_message(
                BOTLOG_CHATID,
                f"#SET_LANGUAGE\n\n**🌐 Language for @XiaomiGeekBot is changed to {LANG.title()}.**",
            )
