import os
import telebot
from datetime import datetime, timedelta
from collections import defaultdict

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

CANAL_ID = "@PoesíaErótica"
GRUPO_ID = -1000000000000  # Reemplazar por el ID real del grupo (como entero)

uso_diario = defaultdict(lambda: {"count": 0, "last_used": datetime.now().date()})

def puede_usar(user_id):
    hoy = datetime.now().date()
    if uso_diario[user_id]["last_used"] != hoy:
        uso_diario[user_id] = {"count": 0, "last_used": hoy}
    return uso_diario[user_id]["count"] < 5

def incrementar_uso(user_id):
    uso_diario[user_id]["count"] += 1

@bot.message_handler(commands=["start"])
def welcome_user(message):
    bienvenida = (
        "👋 *Bienvenido/a al bot anónimo.*\n\n"
        "💬 Podés enviar mensajes, fotos y videos de hasta 60 segundos de forma anónima.\n"
        "⚠️ Tenés *5 usos por día*. Superado ese límite, deberás esperar 24hs.\n"
        "❌ No se permiten enlaces.\n\n"
        "📝 Usá el bot con respeto. Todo es *completamente anónimo*."
    )
    bot.reply_to(message, bienvenida, parse_mode="Markdown")

@bot.message_handler(content_types=["text", "photo", "video"])
def anon_mensaje(message):
    user_id = message.from_user.id

    if not puede_usar(user_id):
        bot.reply_to(message, "📨 Ya alcanzaste el límite de 5 mensajes anónimos por hoy. Esperá 24hs.")
        return

    if message.content_type == "text":
        if "http://" in message.text or "https://" in message.text or "t.me/" in message.text:
            bot.reply_to(message, "🚫 No se permiten enlaces en los mensajes.")
            return
        if len(message.text) > 1000:
            bot.reply_to(message, "⚠️ El mensaje es muy largo. Limitado a 1000 caracteres.")
            return
        bot.send_message(CANAL_ID, f"✉️ *Mensaje Anónimo:*\n{message.text}", parse_mode="Markdown")

    elif message.content_type == "photo":
        bot.send_photo(CANAL_ID, message.photo[-1].file_id, caption="📷 *Foto Anónima*", parse_mode="Markdown")

    elif message.content_type == "video":
        if message.video.duration > 60:
            bot.reply_to(message, "⚠️ El video no puede durar más de 60 segundos.")
            return
        bot.send_video(CANAL_ID, message.video.file_id, caption="🎥 *Video Anónimo*", parse_mode="Markdown")

    incrementar_uso(user_id)
    bot.reply_to(message, "✅ Tu mensaje fue enviado anónimamente.")

print("🤖 Bot en funcionamiento...")
bot.polling(none_stop=True)
