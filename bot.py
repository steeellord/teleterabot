import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"


def extract_video(link):
    ydl_opts = {
        "quiet": True,
        "format": "best"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        return info["url"]


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if "terabox.com" in text or "1024tera.com" in text:

        await update.message.reply_text("Processing your link...")

        try:
            video_url = extract_video(text)

            await update.message.reply_video(
                video=video_url,
                supports_streaming=True
            )

        except Exception as e:
            await update.message.reply_text("Failed to process the link.")

    else:
        await update.message.reply_text("Send a TeraBox link.")


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("Bot running...")

app.run_polling()
