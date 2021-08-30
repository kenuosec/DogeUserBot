from telethon.events import NewMessage

from . import doge, edl, eor, fsmessage, parse_pre, reply_id

plugin_category = "tool"


@doge.bot_cmd(
    pattern="scan(i)?$",
    command=("scan", plugin_category),
    info={
        "header": "To scan the replied file for virus.",
        "flag": {"i": "to get output as image."},
        "usage": ["{tr}scan", "{tr}scani"],
    },
)
async def _(event):
    input_str = event.pattern_match.group(1)
    if not event.reply_to_msg_id:
        return await edl(event, "```Reply to any user message.```")
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        return await edl(event, "```Reply to a media message```")
    chat = "@VS_Robot"
    dogevent = await eor(event, "`Sliding my tip, of fingers over it`")
    async with event.client.conversation(chat) as conv:
        response1 = conv.wait_event(NewMessage(incoming=True, from_users=chat))
        await fsmessage(event, reply_message, forward=True, chat=chat)
        response1 = await response1
        if response1.text:
            await event.client.send_read_acknowledge(conv.chat_id)
            return await dogevent.edit(response1.text, parse_mode=parse_pre)
        response2 = conv.wait_event(NewMessage(incoming=True, from_users=chat))
        response2 = await response2
        await event.client.send_read_acknowledge(conv.chat_id)
        response3 = conv.wait_event(NewMessage(incoming=True, from_users=chat))
        response4 = conv.wait_event(NewMessage(incoming=True, from_users=chat))
        await event.client.send_read_acknowledge(conv.chat_id)
        if not input_str:
            return await eor(dogevent, response4.text)
        await dogevent.delete()
        await event.client.send_file(
            event.chat_id, response3.media, reply_to=(await reply_id(event))
        )
        await conv.mark_read()
        await conv.cancel_all()


@doge.bot_cmd(
    pattern="vscan$",
    command=("vscan", plugin_category),
    info={
        "header": "To scan with @DrWebBot the replied file for virus.",
        "usage": "{tr}vscan",
    },
)
async def scan(event):
    if not event.reply_to_msg_id:
        return await edl(event, "```Reply to any user message.```")
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        return await edl(event, "```Reply to a media message```")
    chat = "@DrWebBot"
    dogevent = await eor(event, "`Sliding my tip, of fingers over it`")
    async with event.client.conversation(chat) as conv:
        response = conv.wait_event(NewMessage(incoming=True, from_users=chat))
        await fsmessage(event, reply_message, forward=True, chat=chat)
        response = await response
        if response.text.startswith("Forward"):
            await edl(
                dogevent,
                "`Can you kindly disable your forward privacy settings for good?`",
            )
        elif response.text.startswith("Select"):
            await event.client.send_message(chat, "English")
            response = conv.wait_event(NewMessage(incoming=True, from_users=chat))
            await event.client.forward_messages(chat, reply_message)
            response = conv.wait_event(NewMessage(incoming=True, from_users=chat))
            response = await response
            await dogevent.edit(
                f"**Virus scan ended.\nResults:** {response.message.message}"
            )
        elif response.text.startswith("Still"):
            await dogevent.edit("File is scanning...")
            response = conv.wait_event(NewMessage(incoming=True, from_users=chat))
            response = await response
            if response.text.startswith("No threats"):
                await event.edit("Virus scan ended. This file is clean. Go on!")
            else:
                await event.edit(
                    f"**The virus scan is ended. Whopsie! This case is dangerous. Don't download!**\nInfo: {response.message.message}"
                )
        await conv.mark_read()
        await conv.cancel_all()
