import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
from flask import Flask
import threading

TOKEN = '8792917417:AAE_FYd4fm42IIP-t2cpny_ta95HQbrANK8'
OWNER_ID = 6984662113

distributors = {OWNER_ID}
registered_users = {}
counter = 1
is_distributing = False

app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot is running!"

async def start_dist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID: return
    global is_distributing, counter
    is_distributing = True
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = await update.message.reply_text(f"تم بدء التوزيع\nالتاريخ والوقت: {now}")
    await context.bot.pin_chat_message(chat_id=update.message.chat_id, message_id=msg.message_id)

async def stop_dist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID: return
    global is_distributing
    is_distributing = False
    await update.message.reply_text("تم إيقاف التوزيع.")

async def register_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_distributing or not update.message.reply_to_message: return
    global counter
    user = update.message.from_user
    sony_id = update.message.text
    registered_users[user.id] = {"name": user.full_name, "sony_id": sony_id, "number": counter}
    await update.message.reply_text(f"تم تسجيل الأي دي ورقمك {counter}")
    counter += 1

async def notify_winner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID: return
    try:
        target_num = int(context.args[0])
        for uid, data in registered_users.items():
            if data['number'] == target_num:
                await context.bot.send_message(chat_id=update.message.chat_id, text=f"مبروك وصل دورك اقبل وجون")
                return
    except: pass

async def manage_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID or not update.message.reply_to_message: return
    target_id = update.message.reply_to_message.from_user.id
    text = update.message.text
    if "أمن" in text:
        distributors.add(target_id)
        await update.message.reply_text("تم إعطاء صلاحيات التوزيع.")
    elif "سحب" in text:
        distributors.discard(target_id)
        await update.message.reply_text("تم سحب الصلاحيات.")

async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in distributors: return
    text = "قائمة المسجلين:\n"
    for uid, data in registered_users.items():
        text += f"{data['number']} - {data['name']} (ID: {data['sony_id']})\n"
    await update.message.reply_text(text)

if __name__ == '__main__':
    threading.Thread(target=lambda: app_web.run(host='0.0.0.0', port=8080)).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("بدء", start_dist))
    app.add_handler(CommandHandler("إيقاف", stop_dist))
    app.add_handler(CommandHandler("قائمة", show_list))
    app.add_handler(CommandHandler("مشرف", notify_winner))
    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT & ~filters.COMMAND, register_id))
    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT & filters.Regex('(أمن|سحب)'), manage_role))
    app.run_polling()
