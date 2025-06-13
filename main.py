import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from keep_alive import keep_alive
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# 🌐 Keep the bot alive
keep_alive()

# 🔐 Use secure token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ❌ Banned keywords
BANNED_WORDS = ["terrorist", "9/11", "gun"]

# 📝 Logging
logging.basicConfig(level=logging.INFO)

# 💾 Save group ID if not already saved
def save_group(chat_id):
    with open("groups.txt", "a+") as f:
        f.seek(0)
        lines = f.read().splitlines()
        if str(chat_id) not in lines:
            f.write(f"{chat_id}\n")

# 🚨 Notify all admins when a message is deleted
async def notify_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    mentions = []
    for admin in admins:
        user = admin.user
        if not user.is_bot:
            mentions.append(f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})")
    if mentions:
        mention_text = ", ".join(mentions)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🚨 Banned word detected and message deleted. Alerting admins: {mention_text}",
            parse_mode="Markdown"
        )

# 🧹 Monitor and delete banned words
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type in ['group', 'supergroup']:
        save_group(update.effective_chat.id)
        text = update.message.text.lower()
        if any(word in text for word in BANNED_WORDS):
            try:
                await update.message.delete()
                await notify_admins(update, context)
            except Exception as e:
                print(f"Error deleting or notifying: {e}")

# 📢 Admin broadcast to all saved groups
async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /send Your message here")
        return
    msg = " ".join(context.args)
    with open("groups.txt", "r") as f:
        ids = f.read().splitlines()
    for gid in ids:
        try:
            await context.bot.send_message(chat_id=int(gid), text=msg)
        except Exception as e:
            print(f"Error sending to {gid}: {e}")
    await update.message.reply_text("✅ Message sent to all groups.")

# 👋 Welcome/start message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤\n🤖 REPORT PROTECTION BOT\n\n"
        "🔒 This bot protects your group from being mass reported and banned.\n"
        "🚨 Automatically deletes dangerous messages and alerts admins.\n"
        "⚠️ Please make sure the bot is an admin in your group!"
    )

# 🚀 Start bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("darupio", send))  # Use /send in private chat
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

if __name__ == "__main__":
    try:
        print("✅ Bot is running...")
        app.run_polling()
    except Exception as e:
        print(f"❌ Bot crashed with error: {e}")

