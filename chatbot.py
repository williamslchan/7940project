from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import configparser
import logging
import redis
import mysql.connector
import datetime


global sql_config
global redis1

def main():
    # Load your token and create an Updater for your Bot
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=(config['REDIS']['REDISPORT']))
    
    global sql_config
    sql_config = {
        'user': config['GOOGLE_CLOUD_SQL']['USER'],
        'password': config['GOOGLE_CLOUD_SQL']['PASSWORD'],
        'host': config['GOOGLE_CLOUD_SQL']['HOST'],
        'database': config['GOOGLE_CLOUD_SQL']['DATABASE']
    }
    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    
    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("calories", calories))
    dispatcher.add_handler(CommandHandler("track", track))



    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Usage: /calories <food> <amount (g)>, \n eg /calories bread 50, /calories egg 75 \n Usage: /track <weight (kg)>, \n eg /track 55.8')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try: 
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg +  ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')


def hello(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hello is issued."""
    try: 
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
       
        update.message.reply_text('Good day, ' + msg + '!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')

def calories(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /calories is issued."""
    try:
        foodName = str(context.args[0]) 
        grams = context.args[1] 
        cnxn = mysql.connector.connect(**sql_config)
        cursor = cnxn.cursor()
        select_stmt = "SELECT * FROM calories WHERE food LIKE %(foodName)s LIMIT 1"
        cursor.execute(select_stmt, {'foodName': foodName})
        out = cursor.fetchall()
        result_calories = out[0][1] * int(grams) / 100
        update.message.reply_text('Calories for '+ grams + '(g) ' + foodName + ' is about ' + str(result_calories) + ' kcal.' )
    except (IndexError, ValueError):
        update.message.reply_text('Sorry we do not have this food item in database \n Usage: /calories <food> <amount in grams>')

def track(update: Update, context: CallbackContext) -> None:
    try:
        now = datetime.datetime.now().strftime('%x')
        user = update.message.from_user
        weight = context.args[0]
        cnxn = mysql.connector.connect(**sql_config)
        cursor = cnxn.cursor()
        insert_stmt = "INSERT INTO Weights (userId, weight, dateTime) VALUES (%(userId)s, %(weight)s, %(dateTime)s)"
        cursor.execute(insert_stmt, {'userId': user['id'], 'weight': weight, 'dateTime': now})
        cnxn.commit()
        select_stmt = "SELECT dateTime, weight FROM Weights WHERE userId = %(userId)s"
        cursor.execute(select_stmt, {'userId': user['id']})
        out = cursor.fetchall()
        update.message.reply_text('Hi '+ str(user['username']+ ', here is your body weight records:'))
        for row in out:
            update.message.reply_text('Date: ' + row[0] + ' Weight: ' + str(row[1])+'kg')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /track <body weight(kg)>')


if __name__ == '__main__':
    main()