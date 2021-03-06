# modified and developed by @mrconfused
from asyncio import sleep
from base64 import b64decode
from io import BytesIO
from math import floor
from os import remove
from random import choice
from re import findall
from string import ascii_lowercase, ascii_uppercase
from urllib.request import Request, urlopen

import emoji as emojiun
from bs4 import BeautifulSoup
from cloudscraper import create_scraper
from PIL.Image import new
from PIL.Image import open as Imopen
from telethon.events import NewMessage
from telethon.tl.functions.messages import GetStickerSetRequest, ImportChatInviteRequest
from telethon.tl.types import (
    DocumentAttributeFilename,
    DocumentAttributeSticker,
    InputStickerSetID,
    InputStickerSetShortName,
    MessageMediaPhoto,
)

from . import (
    DOGEKANG,
    _dogetools,
    crop_and_divide,
    doge,
    edl,
    eor,
    fsmessage,
    gvar,
    media_type,
    tr,
)

plugin_category = "misc"

combot_stickers_url = "https://combot.org/telegram/stickers?q="
EMOJI_SEN = [
    "Можно отправить несколько смайлов в одном сообщении, однако мы рекомендуем использовать не больше одного или двух на каждый стикер.",
    "You can list several emoji in one message, but I recommend using no more than two per sticker",
    "Du kannst auch mehrere Emoji eingeben, ich empfehle dir aber nicht mehr als zwei pro Sticker zu benutzen.",
    "Você pode listar vários emojis em uma mensagem, mas recomendo não usar mais do que dois por cada sticker.",
    "Puoi elencare diverse emoji in un singolo messaggio, ma ti consiglio di non usarne più di due per sticker.",
    "emoji",
]


def verify_cond(dogarray, text):
    return any(i in text for i in dogarray)


def pack_name(userid, pack, is_anim):
    if is_anim:
        return f"DogeUserBot_{userid}_{pack}_anim"
    return f"DogeUserBot_{userid}_{pack}"


def char_is_emoji(character):
    return character in emojiun.UNICODE_EMOJI["en"]


def pack_nick(username, pack, is_anim):
    if gvar("CUSTOM_STICKER_PACKNAME"):
        return (
            f"{gvar('CUSTOM_STICKER_PACKNAME')} A. {pack}"
            if is_anim
            else f"{gvar('CUSTOM_STICKER_PACKNAME')} {pack}"
        )
    elif is_anim:
        return f"@DogeUserBot @{username} A. {pack}"
    else:
        return f"@DogeUserBot @{username} {pack}"


async def resize_photo(photo):
    """Resize the given photo to 512x512"""
    image = Imopen(photo)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = floor(size1new)
        size2new = floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        maxsize = (512, 512)
        image.thumbnail(maxsize)
    return image


async def newpacksticker(
    dogevent,
    conv,
    cmd,
    args,
    pack,
    packnick,
    stfile,
    emoji,
    packname,
    is_anim,
    otherpack=False,
    pkang=False,
):
    await conv.send_message(cmd)
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.send_message(packnick)
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    if is_anim:
        await conv.send_file("AnimatedSticker.tgs")
        remove("AnimatedSticker.tgs")
    else:
        stfile.seek(0)
        await conv.send_file(stfile, force_document=True)
    rsp = await conv.get_response()
    if not verify_cond(EMOJI_SEN, rsp.text):
        await dogevent.edit(
            f"Failed to add sticker, use @Stickers bot to add the sticker manually.\n**Error:**{rsp}"
        )
        return
    await conv.send_message(emoji)
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.get_response()
    await conv.send_message("/publish")
    if is_anim:
        await conv.get_response()
        await conv.send_message(f"<{packnick}>")
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.send_message("/skip")
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.get_response()
    await conv.send_message(packname)
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    if not pkang:
        return otherpack, packname, emoji
    return pack, packname


async def add_to_pack(
    dogevent,
    conv,
    args,
    packname,
    pack,
    userid,
    username,
    is_anim,
    stfile,
    emoji,
    cmd,
    pkang=False,
):
    await conv.send_message("/addsticker")
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.send_message(packname)
    x = await conv.get_response()
    while ("50" in x.text) or ("120" in x.text):
        try:
            val = int(pack)
            pack = val + 1
        except ValueError:
            pack = 1
        packname = pack_name(userid, pack, is_anim)
        packnick = pack_nick(username, pack, is_anim)
        await dogevent.edit(f"`Switching to Pack {pack} due to insufficient space`")
        await conv.send_message(packname)
        x = await conv.get_response()
        if x.text == "Invalid pack selected.":
            return await newpacksticker(
                dogevent,
                conv,
                cmd,
                args,
                pack,
                packnick,
                stfile,
                emoji,
                packname,
                is_anim,
                otherpack=True,
                pkang=pkang,
            )
    if is_anim:
        await conv.send_file("AnimatedSticker.tgs")
        remove("AnimatedSticker.tgs")
    else:
        stfile.seek(0)
        await conv.send_file(stfile, force_document=True)
    rsp = await conv.get_response()
    if not verify_cond(EMOJI_SEN, rsp.text):
        await dogevent.edit(
            f"Failed to add sticker, use @Stickers bot to add the sticker manually.\n**Error:**{rsp}"
        )
        return
    await conv.send_message(emoji)
    await args.client.send_read_acknowledge(conv.chat_id)
    await conv.get_response()
    await conv.send_message("/done")
    await conv.get_response()
    await args.client.send_read_acknowledge(conv.chat_id)
    if not pkang:
        return packname, emoji
    return pack, packname


@doge.bot_cmd(
    pattern="(kang|d[ıi]zla)(?:\s|$)([\s\S]*)",
    command=("kang", plugin_category),
    info={
        "header": "To kang a sticker.",
        "description": "Kang's the sticker/image to the specified pack and uses the emoji('s) you picked",
        "usage": ["{tr}kang <emoji('s)> <number>", "{tr}dızla <emoji('s)> <number>"],
    },
)
async def kang(args):  # sourcery no-metrics
    "To kang a sticker."
    photo = None
    emojibypass = False
    is_anim = False
    emoji = None
    message = await args.get_reply_message()
    user = await args.client.get_me()
    if not user.username:
        try:
            user.first_name.encode("utf-8").decode("ascii")
            username = user.first_name
        except UnicodeDecodeError:
            username = f"doge_{user.id}"
    else:
        username = user.username
    userid = user.id
    if message and message.media:
        if isinstance(message.media, MessageMediaPhoto):
            dogevent = await eor(args, DOGEKANG)
            photo = BytesIO()
            photo = await args.client.download_media(message.photo, photo)
        elif "image" in message.media.document.mime_type.split("/"):
            dogevent = await eor(args, DOGEKANG)
            photo = BytesIO()
            await args.client.download_file(message.media.document, photo)
            if (
                DocumentAttributeFilename(file_name="sticker.webp")
                in message.media.document.attributes
            ):
                emoji = message.media.document.attributes[1].alt
                emojibypass = True
        elif "tgsticker" in message.media.document.mime_type:
            dogevent = await eor(args, DOGEKANG)
            await args.client.download_file(
                message.media.document, "AnimatedSticker.tgs"
            )

            attributes = message.media.document.attributes
            for attribute in attributes:
                if isinstance(attribute, DocumentAttributeSticker):
                    emoji = attribute.alt
            emojibypass = True
            is_anim = True
            photo = 1
        else:
            await edl(args, "`Unsupported File!`")
            return
    else:
        await edl(args, "`I can't kang that...`")
        return
    if photo:
        splat = ("".join(args.text.split(maxsplit=1)[1:])).split()
        emoji = (
            emoji if emojibypass else choice(["🐾", "😂", "🧡", "🐕", "✨", "🤔", "😳", "😉"])
        )
        pack = 1
        if len(splat) == 2:
            if char_is_emoji(splat[0][0]):
                if char_is_emoji(splat[1][0]):
                    return await dogevent.edit(f"check `{tr}doge stickers`")
                pack = splat[1]  # User sent both
                emoji = splat[0]
            elif char_is_emoji(splat[1][0]):
                pack = splat[0]  # User sent both
                emoji = splat[1]
            else:
                return await dogevent.edit(f"check `{tr}doge stickers`")
        elif len(splat) == 1:
            if char_is_emoji(splat[0][0]):
                emoji = splat[0]
            else:
                pack = splat[0]
        packnick = pack_nick(username, pack, is_anim)
        packname = pack_name(userid, pack, is_anim)
        cmd = "/newpack"
        stfile = BytesIO()
        if is_anim:
            cmd = "/newanimated"
        else:
            image = await resize_photo(photo)
            stfile.name = "sticker.png"
            image.save(stfile, "PNG")
        response = urlopen(Request(f"http://t.me/addstickers/{packname}"))
        htmlstr = response.read().decode("utf8").split("\n")
        if (
            "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>."
            not in htmlstr
        ):
            async with args.client.conversation("Stickers") as conv:
                packname, emoji = await add_to_pack(
                    dogevent,
                    conv,
                    args,
                    packname,
                    pack,
                    userid,
                    username,
                    is_anim,
                    stfile,
                    emoji,
                    cmd,
                )
            await edl(
                dogevent,
                f"`Sticker kanged successfully!\
                    \nYour Pack is` [here](t.me/addstickers/{packname}) `and emoji for the kanged sticker is {emoji}`",
                30,
                parse_mode="md",
            )
        else:
            await dogevent.edit("`Brewing a new Pack...`")
            async with args.client.conversation("Stickers") as conv:
                otherpack, packname, emoji = await newpacksticker(
                    dogevent,
                    conv,
                    cmd,
                    args,
                    pack,
                    packnick,
                    stfile,
                    emoji,
                    packname,
                    is_anim,
                )
            if otherpack:
                await edl(
                    dogevent,
                    f"`Sticker kanged to a Different Pack !\
                    \nAnd Newly created pack is` [here](t.me/addstickers/{packname}) `and emoji for the kanged sticker is {emoji}`",
                    30,
                    parse_mode="md",
                )
            else:
                await edl(
                    dogevent,
                    f"`Sticker kanged successfully!\
                    \nYour Pack is` [here](t.me/addstickers/{packname}) `and emoji for the kanged sticker is {emoji}`",
                    30,
                    parse_mode="md",
                )


@doge.bot_cmd(
    pattern="(pkang|pd[iı]zla)(?:\s|$)([\s\S]*)",
    command=("pkang", plugin_category),
    info={
        "header": "To kang entire sticker sticker.",
        "description": "Kang's the entire sticker pack of replied sticker to the specified pack",
        "usage": ["{tr}pkang <number>", "{tr}pdızla <number>"],
    },
)
async def pack_kang(event):  # sourcery no-metrics
    "To kang entire sticker sticker."
    user = await event.client.get_me()
    if user.username:
        username = user.username
    else:
        try:
            user.first_name.encode("utf-8").decode("ascii")
            username = user.first_name
        except UnicodeDecodeError:
            username = f"doge_{user.id}"
    photo = None
    userid = user.id
    is_anim = False
    emoji = None
    reply = await event.get_reply_message()
    dog = b64decode("QUFBQUFGRV9vWjVYVE5fUnVaaEtOdw==")
    if not reply or media_type(reply) is None or media_type(reply) != "Sticker":
        return await edl(
            event, "`reply to any sticker to send all stickers in that pack`"
        )
    try:
        stickerset_attr = reply.document.attributes[1]
        dogevent = await eor(
            event, "`Fetching details of the sticker pack, please wait..`"
        )
    except BaseException:
        return await edl(event, "`This is not a sticker. Reply to a sticker.`", 5)
    try:
        get_stickerset = await event.client(
            GetStickerSetRequest(
                InputStickerSetID(
                    id=stickerset_attr.stickerset.id,
                    access_hash=stickerset_attr.stickerset.access_hash,
                )
            )
        )
    except Exception:
        return await edl(
            dogevent,
            "`I guess this sticker is not part of any pack. So, i can't kang this sticker pack try kang for this sticker`",
        )
    kangst = 1
    reqd_sticker_set = await event.client(
        GetStickerSetRequest(
            stickerset=InputStickerSetShortName(
                short_name=f"{get_stickerset.set.short_name}"
            )
        )
    )
    noofst = get_stickerset.set.count
    blablapacks = []
    blablapacknames = []
    pack = None
    for message in reqd_sticker_set.documents:
        if "image" in message.mime_type.split("/"):
            await eor(
                dogevent,
                f"`This sticker pack is kanging now . Status of kang process: {kangst}/{noofst}`",
            )
            photo = BytesIO()
            await event.client.download_file(message, photo)
            if (
                DocumentAttributeFilename(file_name="sticker.webp")
                in message.attributes
            ):
                emoji = message.attributes[1].alt
        elif "tgsticker" in message.mime_type:
            await eor(
                dogevent,
                f"`This sticker pack is kanging now . Status of kang process: {kangst}/{noofst}`",
            )
            await event.client.download_file(message, "AnimatedSticker.tgs")
            attributes = message.attributes
            for attribute in attributes:
                if isinstance(attribute, DocumentAttributeSticker):
                    emoji = attribute.alt
            is_anim = True
            photo = 1
        else:
            await edl(dogevent, "`Unsupported File!`")
            return
        if photo:
            splat = ("".join(event.text.split(maxsplit=1)[1:])).split()
            emoji = emoji or choice(["🐾", "😂", "🧡", "🐕", "✨", "🤔", "😳", "😉"])
            if pack is None:
                pack = 1
                if len(splat) == 1:
                    pack = splat[0]
                elif len(splat) > 1:
                    return await edl(
                        dogevent,
                        "`Sorry the given name can't be used for pack or there is no pack with that name`",
                    )
            try:
                dog = ImportChatInviteRequest(dog)
                await event.client(dog)
            except BaseException:
                pass
            packnick = pack_nick(username, pack, is_anim)
            packname = pack_name(userid, pack, is_anim)
            cmd = "/newpack"
            stfile = BytesIO()
            if is_anim:
                cmd = "/newanimated"
            else:
                image = await resize_photo(photo)
                stfile.name = "sticker.png"
                image.save(stfile, "PNG")
            response = urlopen(Request(f"http://t.me/addstickers/{packname}"))
            htmlstr = response.read().decode("utf8").split("\n")
            if (
                "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>."
                in htmlstr
            ):
                async with event.client.conversation("Stickers") as conv:
                    pack, dogpackname = await newpacksticker(
                        dogevent,
                        conv,
                        cmd,
                        event,
                        pack,
                        packnick,
                        stfile,
                        emoji,
                        packname,
                        is_anim,
                        pkang=True,
                    )
            else:
                async with event.client.conversation("Stickers") as conv:
                    pack, dogpackname = await add_to_pack(
                        dogevent,
                        conv,
                        event,
                        packname,
                        pack,
                        userid,
                        username,
                        is_anim,
                        stfile,
                        emoji,
                        cmd,
                        pkang=True,
                    )
            if dogpackname not in blablapacks:
                blablapacks.append(dogpackname)
                blablapacknames.append(pack)
        kangst += 1
        await sleep(2)
    result = "`This sticker pack is kanged into the following your sticker pack(s):`\n"
    for i in enumerate(blablapacks):
        result += (
            f"  •  [pack {blablapacknames[i[0]]}](t.me/addstickers/{blablapacks[i[0]]})"
        )
    await dogevent.edit(result)


@doge.bot_cmd(
    pattern="gridpack(?:\s|$)([\s\S]*)",
    command=("gridpack", plugin_category),
    info={
        "header": "To split the replied image and make sticker pack.",
        "flags": {
            ".e": "to use custom emoji by default ▫️️ is emoji.",
        },
        "usage": [
            "{tr}gridpack <packname>",
            "{tr}gridpack .e👌 <packname>",
        ],
        "examples": [
            "{tr}gridpack .e👌 DogeUserBot",
        ],
    },
)
async def pic2packcmd(event):
    "To split the replied image and make sticker pack."
    reply = await event.get_reply_message()
    mediatype = media_type(reply)
    if not reply or not mediatype or mediatype not in ["Photo", "Sticker"]:
        return await edl(event, "__Reply to photo or sticker to make pack.__")
    if mediatype == "Sticker" and reply.document.mime_type == "application/x-tgsticker":
        return await edl(
            event,
            "__Reply to photo or sticker to make pack. Animated sticker is not supported__",
        )
    args = event.pattern_match.group(1)
    if not args:
        return await edl(event, "__What's your packname? Pass along with cmd.__")
    dogevent = await eor(event, "__🔪Cropping and adjusting the image...__")
    try:
        emoji = (findall(r".e[\U00010000-\U0010ffff]+", args))[0]
        args = args.replace(emoji, "")
        emoji = emoji.replace(".e", "")
    except Exception:
        emoji = "▫️️"
    chat = "@Stickers"
    name = "DogeUserBot_" + "".join(
        choice(list(ascii_lowercase + ascii_uppercase)) for _ in range(16)
    )
    image = await _dogetools.media_to_pic(dogevent, reply, noedits=True)
    if image[1] is None:
        return await edl(
            image[0], "__Unable to extract image from the replied message.__"
        )
    image = Imopen(image[1])
    w, h = image.size
    www = max(w, h)
    img = new("RGBA", (www, www), (0, 0, 0, 0))
    img.paste(image, ((www - w) // 2, 0))
    newimg = img.resize((100, 100))
    new_img = BytesIO()
    new_img.name = name + ".png"
    images = await crop_and_divide(img)
    newimg.save(new_img)
    new_img.seek(0)
    dogevent = await event.edit("__Making the pack.__")
    async with event.client.conversation(chat) as conv:
        i = 0
        await fsmessage(event=event, text="/cancel", chat=chat)
        await conv.wait_event(NewMessage(incoming=True, from_users=chat))
        await event.client.send_message(chat, "/newpack")
        await conv.wait_event(NewMessage(incoming=True, from_users=chat))
        await event.client.send_message(chat, args)
        await conv.wait_event(NewMessage(incoming=True, from_users=chat))
        for im in images:
            img = BytesIO(im)
            img.name = name + ".png"
            img.seek(0)
            await event.client.send_file(chat, img, force_document=True)
            await conv.wait_event(NewMessage(incoming=True, from_users=chat))
            await event.client.send_message(chat, emoji)
            await conv.wait_event(NewMessage(incoming=True, from_users=chat))
            await event.client.send_read_acknowledge(conv.chat_id)
            await sleep(1)
            i += 1
            await dogevent.edit(f"__Making the pack.\nProgress: {i}/{len(images)}__")
        await event.client.send_message(chat, "/publish")
        await conv.wait_event(NewMessage(incoming=True, from_users=chat))
        await event.client.send_file(chat, new_img, force_document=True)
        await conv.wait_event(NewMessage(incoming=True, from_users=chat))
        await event.client.send_message(chat, name)
        ending = await conv.wait_event(NewMessage(incoming=True, from_users=chat))
        await event.client.send_read_acknowledge(conv.chat_id)
        for packname in ending.raw_text.split():
            stick_pack_name = packname
            if stick_pack_name.startswith("https://t.me/"):
                break
        await dogevent.edit(
            f"__Successfully created the pack for the replied media: __[{args}]({stick_pack_name})"
        )
        await conv.mark_read()
        await conv.cancel_all()


@doge.bot_cmd(
    pattern="stkrinfo$",
    command=("stkrinfo", plugin_category),
    info={
        "header": "To get information about a sticker pick.",
        "description": "Gets info about the sticker packk",
        "usage": "{tr}stkrinfo",
    },
)
async def get_pack_info(event):
    "To get information about a sticker pick."
    if not event.is_reply:
        return await edl(event, "`I can't fetch info from nothing, can I ?!`", 5)
    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        return await edl(event, "`Reply to a sticker to get the pack details`", 5)
    try:
        stickerset_attr = rep_msg.document.attributes[1]
        dogevent = await eor(
            event, "`Fetching details of the sticker pack, please wait..`"
        )
    except BaseException:
        return await edl(event, "`This is not a sticker. Reply to a sticker.`", 5)
    if not isinstance(stickerset_attr, DocumentAttributeSticker):
        return await dogevent.edit("`This is not a sticker. Reply to a sticker.`")
    get_stickerset = await event.client(
        GetStickerSetRequest(
            InputStickerSetID(
                id=stickerset_attr.stickerset.id,
                access_hash=stickerset_attr.stickerset.access_hash,
            )
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    OUTPUT = (
        f"**Sticker Title:** `{get_stickerset.set.title}\n`"
        f"**Sticker Short Name:** `{get_stickerset.set.short_name}`\n"
        f"**Official:** `{get_stickerset.set.official}`\n"
        f"**Archived:** `{get_stickerset.set.archived}`\n"
        f"**Stickers In Pack:** `{get_stickerset.set.count}`\n"
        f"**Emojis In Pack:**\n{' '.join(pack_emojis)}"
    )
    await dogevent.edit(OUTPUT)


@doge.bot_cmd(
    pattern="stickers ?([\s\S]*)",
    command=("stickers", plugin_category),
    info={
        "header": "To get list of sticker packs with given name.",
        "description": "shows you the list of non-animated sticker packs with that name.",
        "usage": "{tr}stickers <query>",
    },
)
async def cb_sticker(event):
    "To get list of sticker packs with given name."
    split = event.pattern_match.group(1)
    if not split:
        return await edl(event, "`Provide some name to search for pack.`", 5)
    dogevent = await eor(event, "`Searching sticker packs....`")
    scraper = create_scraper()
    text = scraper.get(combot_stickers_url + split).text
    soup = BeautifulSoup(text, "lxml")
    results = soup.find_all("div", {"class": "sticker-pack__header"})
    if not results:
        return await edl(dogevent, "`No results found:(.`", 5)
    reply = f"**Sticker packs found for {split} are:**"
    for pack in results:
        if pack.button:
            packtitle = (pack.find("div", "sticker-pack__title")).get_text()
            packlink = (pack.a).get("href")
            packid = (pack.button).get("data-popup")
            reply += f"\n **• ID: **`{packid}`\n [{packtitle}]({packlink})"
    await dogevent.edit(reply)
