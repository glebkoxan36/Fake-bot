
import os
import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    Filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена бота из переменных окружения
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Пример данных о заказах
ORDERS_DATA = [
    "18/07/2025 - 0.12 MED VHQ - 🌤️ 115㎝",
    "16/07/2025 - 0.25 ALPA - PVP 💬️ 95㎝",
    "23/06/2025 - 0.30 ALPA - 💬️ 105㎝",
    "20/06/2025 - 0.30 ALPA 💬️ 105㎝",
    "10/06/2025 - 0.12 - MED VHQ 🌤️ 115㎝",
    "08/06/2025 - 0.20 - MED VHQ 🌤️ 170㎝",
    "03/06/2025 - 0.07 - MED VHQ 🌤️ 77㎝",
    "01/06/2025 - 0.30 ALPA 💬️ 105㎝",
    "28/05/2025 - 0.30 ALPA 💬️ 105㎝"
]

ORDER_DETAILS_DATA = {
    "order_number": "№307519",
    "city": "TBILISI",
    "district": "DIDI DIGOMI",
    "product": "0.12 MED VHQ - 🌤️",
    "size": "115m",
    "type": "TAINIK",
    "time": "5:04 AM"
}

# =============================================================================
# Функции для работы бота
# =============================================================================

def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start - главное меню"""
    keyboard = [
        [KeyboardButton("Баланс (0.0 cm)")],
        [KeyboardButton("Покупки (0)")],
        [KeyboardButton("Выбор города (1)")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "Welcome to the Bot: AVERSI*BESTT*SHOPP\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

def handle_main_menu(update: Update, context: CallbackContext) -> None:
    """Обработка главного меню"""
    text = update.message.text
    if "Покупки" in text:
        show_orders(update, context)
    elif "Баланс" in text:
        update.message.reply_text("Ваш баланс: 0.0 cm")
    elif "Выбор города" in text:
        update.message.reply_text("Текущий город: TBILISI")
    else:
        update.message.reply_text("Используйте кнопки меню")

def show_orders(update: Update, context: CallbackContext) -> None:
    """Показать историю заказов"""
    keyboard = []
    for i, order in enumerate(ORDERS_DATA):
        keyboard.append([InlineKeyboardButton(order, callback_data=f"order_{i}")])
    
    keyboard.append([
        InlineKeyboardButton("🟩 Hasaq", callback_data="confirm"),
        InlineKeyboardButton("Menu", callback_data="menu"),
        InlineKeyboardButton("Message", callback_data="message")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        update.message.reply_text("Ваши заказы:", reply_markup=reply_markup)
    else:
        update.callback_query.edit_message_text("Ваши заказы:", reply_markup=reply_markup)

def show_order_details(update: Update, context: CallbackContext) -> None:
    """Показать детали заказа"""
    query = update.callback_query
    query.answer()
    
    order_text = (
        f"Ваш заказ {ORDER_DETAILS_DATA['order_number']}\n"
        f"- Город: {ORDER_DETAILS_DATA['city']}\n"
        f"- Район: {ORDER_DETAILS_DATA['district']}\n\n"
        f"**Товар:** {ORDER_DETAILS_DATA['product']}\n"
        f"{ORDER_DETAILS_DATA['size']}\n\n"
        f"**Тип Товара:** {ORDER_DETAILS_DATA['type']}\n"
        f"{ORDER_DETAILS_DATA['time']}"
    )
    
    keyboard = [
        [InlineKeyboardButton("Диспут", callback_data="dispute")],
        [InlineKeyboardButton("Отзыв", callback_data="review")],
        [InlineKeyboardButton("Назад", callback_data="back_orders")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(order_text, reply_markup=reply_markup)

def handle_callbacks(update: Update, context: CallbackContext) -> None:
    """Обработка callback-запросов"""
    query = update.callback_query
    data = query.data
    
    if data.startswith("order_"):
        show_order_details(update, context)
    elif data == "back_orders":
        show_orders(update, context)
    elif data == "menu":
        start(update, context)
    elif data == "dispute":
        query.answer("Функция 'Диспут' в разработке")
    elif data == "review":
        query.answer("Функция 'Отзыв' в разработке")
    elif data == "confirm":
        query.answer("Подтверждено!")
    elif data == "message":
        query.answer("Сообщение отправлено")

# =============================================================================
# Веб-сервер для поддержания активности (для Render.com)
# =============================================================================

def run_flask_server():
    """Запуск Flask сервера для поддержания активности"""
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "Telegram Bot is running!"

    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# =============================================================================
# Основная функция
# =============================================================================

def main() -> None:
    """Запуск бота"""
    # Запускаем Flask сервер в отдельном потоке
    flask_thread = threading.Thread(target=run_flask_server, daemon=True)
    flask_thread.start()
    
    # Создаем экземпляр Updater и передаем токен бота
    updater = Updater(TOKEN, use_context=True)
    
    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_main_menu))
    dp.add_handler(CallbackQueryHandler(handle_callbacks))
    
    # Запускаем бота
    logger.info("Бот запущен. Ожидание сообщений...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
