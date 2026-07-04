import telegram
from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler
from datetime import datetime
from flask import Flask
import threading
import asyncio

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is running!"

def run_web():
    app_web.run(host='0.0.0.0', port=8080)

TOKEN = '8792917417:AAE_FYd4fm42IIP-t2cpny_ta95HQbrANK8'
OWNER_ID = 6984662113

distributing = False
participants = []
admin_stats = {}
admin_names = {}
distributors = [OWNER_ID]

async def is_authorized(update: Update, context):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    return user_id == OWNER_ID or user_id in distributors
