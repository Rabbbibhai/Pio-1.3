
import os
import time
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai

# Bot identity
BOT_NAME = "Pio"
CREATOR_NAME = "Rabbi"

# OpenRouter API key
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

# In-memory user message tracker for spam detection
user_message_times = {}

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! I'm Pio, your therapy chatbot. Let's talk.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text

    # Check spam
    now = time.time()
    history = user_message_times.get(user_id, [])
    history = [t for t in history if now - t < 30]  # last 30 seconds
    history.append(now)
    user_message_times[user_id] = history

    if len(history) > 5:
        await update.message.reply_text("Slow mode is on. You’ve sent too many messages. Please wait a while.")
        return

    if "who made you" in user_text.lower() or "creator" in user_text.lower():
        await update.message.reply_text(f"I was made by {CREATOR_NAME}.")
        return

    # Send user input to OpenRouter AI
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}],
        )
        reply = response["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"Error: {e}"

    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token("7641804956:AAE1Dp5rJlXhwwit6LgvJm60W0b1TTHv3-Y").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
