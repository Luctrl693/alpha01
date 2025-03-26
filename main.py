import logging
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from googletrans import Translator
import random

# Imposta il logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Ottieni le variabili d'ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TRIVIA_API_URL = "https://opentdb.com/api.php?amount=1&type=multiple"

# Funzione per chiamare l'API delle notizie
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    if response.get("articles"):
        top_article = response["articles"][0]
        title = top_article["title"]
        description = top_article["description"]
        url = top_article["url"]
        return f"Notizia: {title}\n{description}\nLeggi di più: {url}"
    return "Non sono riuscito a trovare notizie."

# Funzione per chiamare l'API di traduzione
def translate_text(text, target_language):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

# Funzione per ottenere una domanda trivia
def get_trivia():
    response = requests.get(TRIVIA_API_URL).json()
    if response.get("results"):
        question_data = response["results"][0]
        question = question_data["question"]
        correct_answer = question_data["correct_answer"]
        incorrect_answers = question_data["incorrect_answers"]
        options = [correct_answer] + incorrect_answers
        random.shuffle(options)
        return f"{question}\nA) {options[0]}\nB) {options[1]}\nC) {options[2]}\nD) {options[3]}"
    return "Non sono riuscito a trovare una domanda trivia."

# Funzione di avvio
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Notizie", callback_data='notizie')],
        [InlineKeyboardButton("Traduci", callback_data='traduci')],
        [InlineKeyboardButton("Trivia", callback_data='trivia')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Ciao! Sono il tuo assistente virtuale. Scegli cosa vuoi fare:", reply_markup=reply_markup)

# Funzione per gestire la risposta dei bottoni
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'notizie':
        news = get_news()
        await query.edit_message_text(text=f"Notizie:\n{news}")
    elif query.data == 'traduci':
        await query.edit_message_text(text="Scrivi il testo che desideri tradurre.")
        context.user_data['state'] = 'traduci'
    elif query.data == 'trivia':
        trivia = get_trivia()
        await query.edit_message_text(text=f"Trivia:\n{trivia}")

# Funzione per gestire i messaggi
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    state = context.user_data.get('state')

    if state == 'traduci':
        translated = translate_text(user_message, "en")
        await update.message.reply_text(f"Tradotto: {translated}")
        context.user_data['state'] = None
    else:
        await update.message.reply_text("Per favore, scegli un'azione tramite il menu.")

# Configura l'Application in modalità Polling
def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))
    
    logger.info("Bot avviato in modalità Polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
