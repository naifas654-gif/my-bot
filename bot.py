import telegram
from telegram import Update
from telegram.ext import Application
from flask import Flask
import threading

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is running!"

def run_web():
    app_web.run(host='0.0.0.0', port=8080)

TOKEN = '8792917417:AAE_FYd4fm42IIP-t2cpny_ta95HQbrANK8'
OWNER_ID = 6984662113

if __name__ == '__main__':
    threading.Thread(target=run_web).start()
    application = Application.builder().token(TOKEN).build()
    application.run_polling()
