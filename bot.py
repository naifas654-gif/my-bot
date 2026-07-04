from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
from flask import Flask
from threading import Thread

app_web = Flask(__name__)
@app_web.route('/')
def home():
    return "Bot is running!"

def run_web():
    app_web.run(host='0.0.0.0', port=8080)

TOKEN = '8639550044:AAFV6yiRM6KEK3sv5QZHXXlVqReoPcuXoeI'
OWNER_ID = 6984662113

distributing = False
participants = []
admin_stats = {}
admin_names = {}
distributors = [OWNER_ID]

async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    member = await context.bot.get_chat_member(chat_id, user_id)
    is_admin = member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    return is_admin or (user_id in distributors)

async def is_reply_to_pinned(update: Update):
    if update.message.reply_to_message:
        chat = await update.get_chat()
        return chat.pinned_message and update.message.reply_to_message.message_id == chat.pinned_message.message_id
    return False

async def start_dist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context): return
    global distributing
    distributing = True
    await update.message.reply_text(f"✅ تم بدء جلسة توزيع العينات في تاريخ {datetime.now().strftime('%Y-%m-%d')}")

async def stop_dist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context): return
    global distributing, participants, admin_stats, admin_names
    distributing = False
    report = "📊 **تقرير توزيع العينات النهائي:**\n\n"
    if not admin_stats: report += "لم يتم توزيع أي عينات."
    else:
        for admin_id, count in admin_stats.items():
            report += f"{admin_names[admin_id]} : وزع {count} عينات\n"
    await update.message.reply_text(report, parse_mode="HTML")
    participants = []
    admin_stats = {}
    admin_names = {}
