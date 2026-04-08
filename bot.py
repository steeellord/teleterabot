import re
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
API_KEY = "YOUR_XAPIVERSE_API_KEY"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

SUPPORTED_DOMAINS = [
    "terabox.com",
    "1024tera.com",
    "4funbox.com",
    "mirrobox.com",
    "terasharelink.com"
]

def normalize_link(url):
    for d in SUPPORTED_DOMAINS:
        if d in url:
            return url.replace(d, "terabox.com")
    return None

def get_video_data(link):
    url = "https://xapiverse.com/api/terabox"

    headers = {
        "Content-Type": "application/json",
        "xAPIverse-Key": API_KEY
    }

    payload = {
        "url": link
    }

    r = requests.post(url, json=payload, headers=headers)
    return r.json()

@dp.message_handler()
async def handle_link(message: types.Message):

    url = normalize_link(message.text)

    if not url:
        return

    user_msg = message.message_id

    processing = await message.reply_animation(
        animation="https://media.giphy.com/media/y1ZBcOGOOtlpC/giphy.gif",
        caption="Fetching video..."
    )

    data = get_video_data(url)

    if not data.get("success"):
        await processing.edit_caption("Failed to fetch video")
        return

    videos = data["data"]["qualities"]

    keyboard = InlineKeyboardMarkup()

    for q in videos:
        keyboard.add(
            InlineKeyboardButton(
                text=q["quality"],
                callback_data=q["url"]
            )
        )

    await processing.edit_caption(
        "Select video quality:",
        reply_markup=keyboard
    )

    dp.current_state(chat=message.chat.id, user=message.from_user.id).set_data({
        "user_msg": user_msg,
        "processing_msg": processing.message_id
    })


@dp.callback_query_handler()
async def send_video(callback: types.CallbackQuery):

    video_url = callback.data

    chat = callback.message.chat.id

    video = await bot.send_video(chat, video_url)

    try:
        await bot.delete_message(chat, callback.message.message_id)
        await bot.delete_message(chat, callback.message.reply_to_message.message_id)
    except:
        pass

    await callback.answer()


if __name__ == "__main__":
    executor.start_polling(dp)
