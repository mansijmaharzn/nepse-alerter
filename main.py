import os
import telebot
import asyncio
import json
import threading
import math
from scraper import CompanyDetailsScraper


BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

scraper = CompanyDetailsScraper()


# replies for /start and /hello
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    text = "Howdy 👋, how are you doing?\nI'm *NEPSE-ALERTER*!\nHit that *hamburger* menu for my commands! 😜"
    bot.reply_to(message, text, parse_mode="Markdown")


# main functionalities
def get_user_data():
    with open('watchlist.json', 'r') as f:
        users = json.load(f)

    return users


def open_account(user):
    users = get_user_data()

    if str(user.id) in users:
        return False

    else:
        users[str(user.id)] = {}
        users[str(user.id)]['username'] = user.username
        users[str(user.id)]['userWatchList'] = []

    with open('watchlist.json', 'w') as f:
        json.dump(users, f, indent=4)

    return True


def add_symbol_to_watchlist(message):
    add_symbol = message.text.upper()
    symbol_details = scraper.scrape_company_details(add_symbol)

    if symbol_details['result']:
        # message.from_user.first_name
        # message.from_user.last_name
        # message.from_user.username
        user = message.from_user

        if open_account(user):
            text = "Welcome 👋! Your account has been created successfully."
            bot.send_message(message.chat.id, text)

        users = get_user_data()

        text = f"At what price should I notify 🔔 about this company?\n*Current Market Price*: `{symbol_details['market_price']}`\nExample: `500`, `500.67`\n*Only numbers*"
        notify_price = bot.send_message(message.chat.id, text, parse_mode="Markdown")
        
        # Now we need to wait for the user's response to get the notify_price
        @bot.message_handler(func=lambda m: m.from_user.id == message.from_user.id)
        def handle_notify_price(message):
            try:
                # Convert the user's response to a float
                notify_price_value = float(message.text)

                object_to_add = {
                    "company_name": symbol_details['company_full_name'],
                    "company_symbol": add_symbol,
                    "notify_price": notify_price_value,
                    "notified": False
                }

                users[str(user.id)]['userWatchList'].append(object_to_add)

                with open('watchlist.json', 'w') as f:
                    json.dump(users, f, indent=4)

                text = f"Successfully added *{symbol_details['company_full_name']}* to your *Watch List*! ✅\nYou'll be notified when its price reaches around *Rs. {notify_price_value}*."
                bot.send_message(message.chat.id, text, parse_mode="Markdown")

            except ValueError:
                bot.send_message(message.chat.id, "❌ Invalid price format! Please enter a valid number. Try Again.")


        bot.register_next_step_handler(notify_price, handle_notify_price)

    else:
        text = "❌ *Invalid Symbol!*\nPlease try again sending a *Valid Company Symbol*!"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")


def delete_symbol_from_watchlist(message):
    delete_symbol = message.text.upper()
    symbol_details = scraper.scrape_company_details(delete_symbol)

    if symbol_details['result']:
        user = message.from_user

        if open_account(user):
            text = "Welcome 👋! Your account has been created successfully."
            bot.send_message(message.chat.id, text)

        users = get_user_data()

        user_watchlist = users[str(user.id)]['userWatchList']

        found = False
        for watchlist in user_watchlist:
            if watchlist['company_symbol'] == delete_symbol:
                found = True
                user_watchlist.remove(watchlist)

        with open('watchlist.json', 'w') as f:
            json.dump(users, f, indent=4)

        if found:
            text = f"Successfully removed *{symbol_details['company_full_name']}* from your *Watch List*! 🗑"
        else:
            text = f"❌ *Invalid Symbol!*\nDidn't find anything with {delete_symbol} in your *Watch List*! Please try again sending a *Valid Company Symbol*!"

    else:
        text = "❌ *Invalid Symbol!*\nPlease try again sending a *Valid Company Symbol*!"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


def send_company_details(message):
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


# command handlers
@bot.message_handler(commands=['search', 'get'])
def get_company_details(message):
    text = "Send Company Symbol to *Get Details* of:\nExample: *GVL*, *NABIL*, *NIFRA*, *CITY*"
    query_symbol = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(query_symbol, send_company_details)


@bot.message_handler(commands=['add'])
def add_company_to_watchlist(message):
    text = "Send Company Symbol to add in your *Watch List*:\nExample: *GVL*, *NABIL*, *NIFRA*, *CITY*"
    add_symbol = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(add_symbol, add_symbol_to_watchlist)


@bot.message_handler(commands=['delete'])
def add_company_to_watchlist(message):
    text = "Send Company Symbol to delete from your *Watch List*:\nExample: *GVL*, *NABIL*, *NIFRA*, *CITY*"
    delete_symbol = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(delete_symbol, delete_symbol_from_watchlist)


@bot.message_handler(commands=['list', 'watchlist'])
def get_watchlist(message):
    user = message.from_user

    if open_account(user):
        text = "Welcome 👋! Your account has been created successfully."
        bot.send_message(message.chat.id, text)

    users = get_user_data()

    user_watchlist = users[str(user.id)]['userWatchList']

    list_data = "*Your Watch List* 👀\n"

    for item in user_watchlist:
        symbol_details = scraper.scrape_company_details(item['company_symbol'])
        list_data += f"\n*{item['company_name']}*: `{item['notify_price']}`\n*Current Price*: {symbol_details['market_price']}\n"

    bot.send_message(message.chat.id, list_data, parse_mode="Markdown")


# Function to be executed at specific intervals
def watchlist_checker():
    users = get_user_data()

    for user in users:
        user_watchlist = users[user]['userWatchList']
        index = 0
        for company in user_watchlist:
            if not company["notified"]:
                symbol_details = scraper.scrape_company_details(company['company_symbol'])

                if math.isclose(float(symbol_details['market_price']), company['notify_price'], abs_tol=5):
                    users[user]['userWatchList'].pop(index)

                    with open('watchlist.json', 'w') as f:
                        json.dump(users, f, indent=4)

                    text = f"*{symbol_details['company_full_name']}* has reached close to your\n*Target Price*: `{company['notify_price']}`\n*Current Market Price*: `{symbol_details['market_price']}`"
                    bot.send_message(user, text, parse_mode="Markdown")
            
            index += 1


    # Adjust the interval_seconds to your desired time (in seconds)
    interval_seconds = 300 # in seconds

    # Schedule the next run of the function
    timer = threading.Timer(interval_seconds, watchlist_checker)
    timer.daemon = True
    timer.start()


def start_bot():
    asyncio.run(bot.polling())


if __name__ == '__main__':
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Schedule the first run of the function
    watchlist_checker()
    
    # Keep the main thread alive
    while True:
        pass