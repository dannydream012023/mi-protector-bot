# -*- coding: utf-8 -*-

import os
import logging
import time
import asyncio # ¡NUEVO! Para un manejo más eficiente de las tareas
from keep_alive import keep_alive
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import NetworkError # ¡NUEVO! Para capturar errores de red específicos

# --- Configuración del Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Carga de Secretos ---
try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    GRUPO_PRINCIPAL_ID = os.environ['GRUPO_PRINCIPAL']
    # ... (el resto de tus secretos)
    RESPALDO_1_ID = os.environ['RESPALDO_1']
    RESPALDO_2_ID = os.environ['RESPALDO_2']
    RESPALDO_3_ID = os.environ['RESPALDO_3']
except KeyError as e:
    logger.critical(f"FATAL: La variable secreta '{e}' no está configurada. El bot no puede iniciar.")
    exit()

GRUPOS_DE_RESPALDO_IDS = [GRUPO_PRINCIPAL_ID, RESPALDO_1_ID, RESPALDO_2_ID, RESPALDO_3_ID]

# --- Comandos y Funciones del Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Estoy listo para anonimizar tus archivos.")

async def anonimizar_y_respaldar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = update.effective_user
    
    # ... (El código de esta función es igual al anterior, no necesita cambios)
    file_id, file_type, caption = None, None, message.caption    
    try:
        if message.photo:
            file_id, file_type = message.photo[-1].file_id, 'photo'
            await context.bot.send_photo(chat_id=user.id, photo=file_id, caption=caption)
        elif message.video:
            file_id, file_type = message.video.file_id, 'video'
            await context.bot.send_video(chat_id=user.id, video=file_id, caption=caption)
        elif message.audio:
            file_id, file_type = message.audio.file_id, 'audio'
            await context.bot.send_audio(chat_id=user.id, audio=file_id, caption=caption)
        elif message.document:
            file_id, file_type = message.document.file_id, 'document'
            await context.bot.send_document(chat_id=user.id, document=file_id, caption=caption)
        elif message.voice:
            file_id, file_type = message.voice.file_id, 'voice'
            await context.bot.send_voice(chat_id=user.id, voice=file_id, caption=caption)
    except Exception as e:
        logger.error(f"Error al devolver archivo a {user.id}: {e}")
        return

    if file_id:
        info_usuario = f"📦 Archivo de {user.full_name} (ID: `{user.id}`)"
        for grupo_id in GRUPOS_DE_RESPALDO_IDS:
            try:
                if file_type == 'photo': await context.bot.send_photo(chat_id=grupo_id, photo=file_id, caption=caption)
                # ... (resto de los elif para otros tipos de archivo)
                elif file_type == 'video': await context.bot.send_video(chat_id=grupo_id, video=file_id, caption=caption)
                elif file_type == 'audio': await context.bot.send_audio(chat_id=grupo_id, audio=file_id, caption=caption)
                elif file_type == 'document': await context.bot.send_document(chat_id=grupo_id, document=file_id, caption=caption)
                elif file_type == 'voice': await context.bot.send_voice(chat_id=grupo_id, voice=file_id, caption=caption)
                await context.bot.send_message(chat_id=grupo_id, text=info_usuario, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Error al enviar copia a {grupo_id}: {e}")


# --- ¡NUEVO! Bucle Principal con Manejo de Errores Avanzado ---
async def bot_main_loop():
    """Configura y ejecuta el bot en un bucle robusto."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    media_filter = (filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.Document.ALL | filters.VOICE)
    application.add_handler(MessageHandler(media_filter, anonimizar_y_respaldar))

    logger.info("Iniciando bot, conectando con Telegram...")
    
    # El bot se ejecuta y maneja la reconexión internamente
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("¡Bot en línea y escuchando!")

    # Mantenemos el script corriendo para que el servidor web siga funcionando
    while True:
        await asyncio.sleep(3600) # Dormimos por una hora, luego revisamos de nuevo

if __name__ == '__main__':
    keep_alive() # Inicia el servidor web
    
    # Inicia el bucle principal del bot
    try:
        asyncio.run(bot_main_loop())
    except Exception as e:
        logger.critical(f"El bucle principal del bot ha fallado de forma inesperada: {e}")
        # En caso de un fallo catastrófico, esto nos dará una última pista.

