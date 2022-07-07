from strings import get_string
from YukkiMusic.misc import SUDOERS
from YukkiMusic.utils.database.memorydatabase import is_nonadmin_chat
import random
from config import BANNED_USERS, adminlist
from pyrogram import filters
from pyrogram.types import Message
from YukkiMusic import app
from YukkiMusic.utils.database.assistantdatabase import assistantdict
from YukkiMusic.core.mongo import mongodb

db = mongodb.assistants

async def set_assistant(chat_id,num=0):
    from YukkiMusic.core.userbot import assistants

    if num == 0:
        ran_assistant = random.choice(assistants)
    else:
        ran_assistant = num

    assistantdict[chat_id] = ran_assistant
    await db.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran_assistant}},
        upsert=True,
    )    
    return ran_assistant

async def get_assistant(chat_id: int) -> str:
    from YukkiMusic.core.userbot import assistants

    assistant = assistantdict.get(chat_id)
    if not assistant:
        dbassistant = await db.find_one({"chat_id": chat_id})
        if not dbassistant:
            userbot = await set_assistant(chat_id)
            return userbot
        else:
            got_assis = dbassistant["assistant"]
            if got_assis in assistants:
                assistantdict[chat_id] = got_assis
                userbot = got_assis
                return userbot
            else:
                userbot = await set_assistant(chat_id)
                return userbot
    else:
        if assistant in assistants:
            userbot = assistant
            return userbot
        else:
            userbot = await set_assistant(chat_id)
            return userbot

def AdminRightsCheck(mystic):
    async def wrapper(client, message):
        _ = get_string("en")
        is_non_admin = await is_nonadmin_chat(message.chat.id)
        if not is_non_admin:
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id)
                if not admins:
                    return await message.reply_text(_["admin_18"])
                else:
                    if message.from_user.id not in admins:
                        return await message.reply_text(_["admin_19"])
        return await mystic(client, message)
    return wrapper

@app.on_message(
    filters.command("checkassistant")
    & filters.group
    & ~filters.edited
    & ~BANNED_USERS
)
@AdminRightsCheck
async def checkassistant(_,message: Message):
    ass = str(await get_assistant(message.chat.id))

    return await message.reply_text(f"⭐️ **Current Assistant : {ass}**")

@app.on_message(
    filters.command("setassistant")
    & filters.group
    & ~filters.edited
    & ~BANNED_USERS
)
@AdminRightsCheck
async def setassistant(_,message: Message):
    from YukkiMusic.core.userbot import assistants
    asst = ""
    for i in assistants:
        asst += str(i) + ", "

    num = message.command[1]
    try:
        num = int(num)
        if num not in assistants:
            return await message.reply_text(f"⭐️ **Available Assistants : {asst}**")
    except:
        return await message.reply_text(f"⭐️ **Available Assistants : {asst}**")

    ass = int(await get_assistant(message.chat.id))
    if num == ass:
        return await message.reply_text(f"⭐️ **Already Assistant {ass} Is Assigned Here**")

    await set_assistant(message.chat.id,num)
    return await message.reply_text(f"⭐️ **Changed Assistant To : {ass}**")
