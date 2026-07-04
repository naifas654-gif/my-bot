import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from datetime import datetime
from flask import Flask
import threading

TOKEN = '8792917417:AAE_FYd4fm42IIP-t2cpny_ta95HQbrANK8'
OWNER_ID = 6984662113

distributors = {OWNER_ID}
registered_users = {}
distributor_stats = {} 
server_message_content = "محتوى السيرفر الافتراضي"
counter = 1
is_distributing = False

app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot is running!"

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_distributing, counter, server_message_content, distributor_stats
    text = update.message.text
    user = update.message.from_user
    chat_id = update.message.chat_id

    if user.id == OWNER_ID:
        if text.startswith("تعديل سيرفر "):
            server_message_content = text.replace("تعديل سيرفر ", "")
            await update.message.reply_text("تم تحديث رسالة السيرفر.")
            return
        elif "أمن" in text or "سحب" in text:
            target_user = None
            if update.message.reply_to_message:
                target_user = update.message.reply_to_message.from_user
            elif update.message.entities:
                for entity in update.message.entities:
                    if entity.type == 'mention':
                        username = text[entity.offset+1:entity.offset+entity.length]
                        target_member = await context.bot.get_chat_member(chat_id, username)
                        target_user = target_member.user
            if target_user:
                if "أمن" in text:
                    distributors.add(target_user.id)
                    await update.message.reply_text(f"تم إعطاء الصلاحيات لـ {target_user.first_name}")
                elif "سحب" in text:
                    distributors.discard(target_user.id)
                    await update.message.reply_text(f"تم سحب الصلاحيات من {target_user.first_name}")
                return

    if text == "سيرفر" and user.id in distributors:
        await update.message.reply_text(server_message_content)
        return

    if text == "توزيع" and update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
        if user.id in distributors:
            is_distributing = True
            distributor_stats = {d: 0 for d in distributors}
            counter = 1
            registered_users.clear()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = await update.message.reply_text(f"تم بدء التوزيع\nالتاريخ والوقت: {now}")
            await context.bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id)
        return

    if text == "وقف توزيع" and user.id in distributors:
        is_distributing = False
        stats_text = "إحصائيات التوزيع:\n"
        for d_id, count in distributor_stats.items():
            try:
                member = await context.bot.get_chat_member(chat_id=chat_id, user_id=d_id)
                name = member.user.username or member.user.first_name
                stats_text += f"الموزع: {name} | سجل: {count} أعضاء\n"
            except: continue
        await update.message.reply_text(f"تم إيقاف التوزيع.\n{stats_text}")
        return

    if text == "قائمة" and user.id in distributors:
        list_text = "قائمة المسجلين:\n"
        for uid, data in registered_users.items():
            name = data['username'] or data['name']
            list_text += f"{data['number']} - {name} (ID: {data['sony_id']})\n"
        await update.message.reply_text(list_text)
        return

    if is_distributing and update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
        registered_users[user.id] = {"name": user.full_name, "username": user.username, "sony_id": text, "number": counter}
        distributor_stats[user.id] = distributor_stats.get(user.id, 0) + 1
        await update.message.reply_text(f"تم تسجيل الأي دي ورقمك {counter}")
        counter += 1

if __name__ == '__main__':
    threading.Thread(target=lambda: app_web.run(host='0.0.0.0', port=8080)).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.run_polling()
