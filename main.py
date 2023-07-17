import os
import telebot
from scraper import CompanyDetailsScraper


BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

scraper = CompanyDetailsScraper()


# replies for /start and /hello
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    text = "Howdy, how are you doing?\nI'm *NEPSE-ALERTER*!\nMy god is *Sir Mansij Maharjan*"
    bot.reply_to(message, text, parse_mode="Markdown")


# main functionalities
def scraper_handler(message):
    query_symbol = message.text.upper()
    symbol_details = scraper.scrape_company_details(query_symbol)

    symbol_message = f"Results for: " + "\n".join(symbol_details)
    bot.send_message(message.chat.id, symbol_message, parse_mode="Markdown")


@bot.message_handler(commands=['search', 'get', 'show', 'display'])
def get_company_details(message):
    text = "Send Company Symbol to get details of:\nExample: *GVL*, *NABIL*, *NIFRA*, *CITY*"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, scraper_handler)


bot.infinity_polling()