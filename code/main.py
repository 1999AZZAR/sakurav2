import os
from dotenv import load_dotenv
from telegram import Update, Bot, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from gemini_res import GeminiChat
from stability_res import ImageGenerator
import time

# Load environment variables from .env file
load_dotenv()

# Initialize the Telegram bot
bot = Bot(token=os.getenv("TELEGRAM_KEY"))
updater = Updater(bot=bot, use_context=True)

# Global initialization
chat_app = GeminiChat()
image_generator = ImageGenerator()

# Function to handle '/start' command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to the Chat Bot Interface!')

# Function to handle text messages
def handle_message(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text.lower()
    if user_input.startswith('imagine'):
        prompt = user_input[len('imagine'):].strip()
        prompt_text = prompt if prompt else 'Your prompt here'
        update.message.chat.send_action(ChatAction.TYPING)
        image_path = image_generator.generate_image(prompt_text)
        if image_path:
            update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
            update.message.reply_photo(open(image_path, 'rb'))
            # Delete the image file after sending
            os.remove(image_path)
        else:
            update.message.reply_text('Error generating image')
    else:
        update.message.chat.send_action(ChatAction.TYPING)
        response = chat_app.generate_chat(user_input)
        update.message.reply_text(response, parse_mode="MARKDOWN")

# Function to handle '/reset' command
def reset_conversation(update: Update, context: CallbackContext) -> None:
    global chat_app
    chat_app = GeminiChat()
    update.message.reply_text('Conversation reset successfully.')

def main() -> None:
    # Create an Updater with a larger connection pool
    updater = Updater(bot=bot, use_context=True, workers=20)  # Adjust the number according to your needs

    # Register handlers
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CommandHandler("reset", reset_conversation))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
