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

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_distributing, counter
    text = update.message.text
    user = update.message.from_user

    # أوامر صاحب البوت
    if user.id == OWNER_ID:
        if text == "بدء":
            is_distributing = True
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = await update.message.reply_text(f"تم بدء التوزيع\nالتاريخ والوقت: {now}")
            await context.bot.pin_chat_message(chat_id=update.message.chat_id, message_id=msg.message_id)
            return
        elif text == "إيقاف":
            is_distributing = False
            await update.message.reply_text("تم إيقاف التوزيع.")
            return
        elif text.startswith("مشرف"):
            try:
                target_num = int(text.split()[1])
                for uid, data in registered_users.items():
                    if data['number'] == target_num:
                        await context.bot.send_message(chat_id=update.message.chat_id, text=f"مبروك وصل دورك اقبل وجون")
                        return
            except: pass
            return

    # أوامر الموزعين
    if user.id in distributors:
        if text == "قائمة":
            list_text = "قائمة المسجلين:\n"
            for uid, data in registered_users.items():
                list_text += f"{data['number']} - {data['name']} (ID: {data['sony_id']})\n"
            await update.message.reply_text(list_text)
            return

    # تسجيل الأي دي
    if is_distributing and update.message.reply_to_message:
        sony_id = text
        registered_users[user.id] = {"name": user.full_name, "sony_id": sony_id, "number": counter}
        await update.message.reply_text(f"تم تسجيل الأي دي ورقمك {counter}")
        counter += 1
        return

    # إدارة الصلاحيات
    if user.id == OWNER_ID and update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        if "أمن" in text:
            distributors.add(target_id)
            await update.message.reply_text("تم إعطاء صلاحيات التوزيع.")
        elif "سحب" in text:
            distributors.discard(target_id)
            await update.message.reply_text("تم سحب الصلاحيات.")

if __name__ == '__main__':
    threading.Thread(target=lambda: app_web.run(host='0.0.0.0', port=8080)).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
