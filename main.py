import os
import telebot
import asyncio
from scraper import CompanyDetailsScraper


BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

scraper = CompanyDetailsScraper()


# replies for /start and /hello
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    text = "Howdy 👋, how are you doing?\nI'm *NEPSE-ALERTER*!\nMy god is *Sir Mansij Maharjan*"
    bot.reply_to(message, text, parse_mode="Markdown")


# main functionalities
def scraper_handler(message):
    query_symbol = message.text.upper()
    symbol_details = scraper.scrape_company_details(query_symbol)

    # symbol_message = f"Results for: " + "\n".join(symbol_details)
    if symbol_details['result']:
        symbol_message = f"""
        🔍 `Search Result for`: *{symbol_details['company_full_name']}*\n
        *Sector*: `{symbol_details['sector']}`
        *Shares Outstanding*: `{symbol_details['shares_outstanding']}`
        *Market Price*: `{symbol_details['market_price']}`
        *% Change*: `{symbol_details['%_change']}`
        *Last Traded On*: `{symbol_details['last_traded_on']}`
        *52 Weeks High - Low*: `{symbol_details['52_weeks_high_-_low']}`
        *180 Day Average*: `{symbol_details['180_day_average']}`
        *120 Day Average*: `{symbol_details['120_day_average']}`
        *1 Year Yield*: `{symbol_details['1_year_yield']}`
        *EPS*: `{symbol_details['eps']}`
        *P/E Ratio*: `{symbol_details['p/e_ratio']}`
        *Book Value*: `{symbol_details['book_value']}`
        *PBV*: `{symbol_details['pbv']}`
        """
    else:
        symbol_message = "❌ *Invalid Symbol!*\nPlease send a valid Company Symbol"

    bot.send_message(message.chat.id, symbol_message, parse_mode="Markdown")


@bot.message_handler(commands=['search', 'get', 'show'])
def get_company_details(message):
    text = "Send Company Symbol to get details of:\nExample: *GVL*, *NABIL*, *NIFRA*, *CITY*"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, scraper_handler)


print("Started...")
asyncio.run(bot.polling())