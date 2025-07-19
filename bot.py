import os
import logging
import threading
import sys
import time
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

# Настройка подробного логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Получение токена бота из переменных окружения
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("Токен бота не найден! Убедитесь, что переменная TELEGRAM_BOT_TOKEN установлена.")
    sys.exit(1)

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
    try:
        user = update.effective_user
        logger.info(f"Получена команда /start от пользователя {user.id} ({user.username})")
        
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
        logger.info("Ответ на /start отправлен успешно")
        
    except Exception as e:
        logger.error(f"Ошибка в обработке /start: {str(e)}", exc_info=True)
        if update.message:
            update.message.reply_text("⚠️ Произошла ошибка при обработке команды. Попробуйте позже.")

def handle_main_menu(update: Update, context: CallbackContext) -> None:
    """Обработка главного меню"""
    try:
        text = update.message.text
        user = update.effective_user
        logger.info(f"Обработка команды '{text}' от {user.id}")
        
        if "Покупки" in text:
            logger.info("Пользователь запросил историю покупок")
            show_orders(update, context)
        elif "Баланс" in text:
            update.message.reply_text("Ваш баланс: 0.0 cm")
        elif "Выбор города" in text:
            update.message.reply_text("Текущий город: TBILISI")
        else:
            update.message.reply_text("Используйте кнопки меню")
            
    except Exception as e:
        logger.error(f"Ошибка в handle_main_menu: {str(e)}", exc_info=True)

def show_orders(update: Update, context: CallbackContext) -> None:
    """Показать историю заказов"""
    try:
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
            
        logger.info("История заказов отображена")
        
    except Exception as e:
        logger.error(f"Ошибка в show_orders: {str(e)}", exc_info=True)

def show_order_details(update: Update, context: CallbackContext) -> None:
    """Показать детали заказа"""
    try:
        query = update.callback_query
        query.answer()
        logger.info(f"Показаны детали заказа для callback: {query.data}")
        
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
        
    except Exception as e:
        logger.error(f"Ошибка в show_order_details: {str(e)}", exc_info=True)

def handle_callbacks(update: Update, context: CallbackContext) -> None:
    """Обработка callback-запросов"""
    try:
        query = update.callback_query
        data = query.data
        logger.info(f"Обработка callback: {data}")
        
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
        else:
            logger.warning(f"Неизвестный callback: {data}")
            query.answer(f"Неизвестная команда: {data}")
            
    except Exception as e:
        logger.error(f"Ошибка в handle_callbacks: {str(e)}", exc_info=True)

# =============================================================================
# Веб-сервер для поддержания активности (для Render.com)
# =============================================================================

def run_flask_server():
    """Запуск Flask сервера для поддержания активности"""
    try:
        from flask import Flask
        app = Flask(__name__)

        @app.route('/')
        def home():
            return "Telegram Bot is running!"

        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Запуск Flask сервера на порту {port}")
        app.run(host='0.0.0.0', port=port)
        
    except Exception as e:
        logger.error(f"Ошибка запуска Flask: {str(e)}", exc_info=True)

# =============================================================================
# Основная функция
# =============================================================================

def main() -> None:
    """Запуск бота"""
    try:
        logger.info("=" * 50)
        logger.info("Запуск бота AVERSIBESST_BOT")
        logger.info(f"Токен бота: {'установлен' if TOKEN else 'НЕ НАЙДЕН!'}")
        logger.info(f"Текущий рабочий каталог: {os.getcwd()}")
        logger.info(f"Содержимое рабочей директории: {os.listdir('.')}")
        logger.info("=" * 50)
        
        # Запускаем Flask сервер в отдельном потоке
        flask_thread = threading.Thread(target=run_flask_server, daemon=True)
        flask_thread.start()
        logger.info("Flask сервер запущен в фоновом режиме")
        
        # Даем время для запуска Flask
        time.sleep(2)
        
        # Создаем экземпляр Updater
        logger.info("Создание экземпляра Updater...")
        updater = Updater(TOKEN, use_context=True)
        logger.info("Updater успешно создан")
        
        # Получаем диспетчер для регистрации обработчиков
        dp = updater.dispatcher

        # Регистрируем обработчики команд
        dp.add_handler(CommandHandler("start", start))
        logger.info("Обработчик команды /start зарегистрирован")
        
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_main_menu))
        logger.info("Обработчик текстовых сообщений зарегистрирован")
        
        dp.add_handler(CallbackQueryHandler(handle_callbacks))
        logger.info("Обработчик callback-запросов зарегистрирован")
        
        # Запускаем бота
        logger.info("Запуск polling...")
        updater.start_polling()
        logger.info("Бот запущен и начал polling")
        
        # Запускаем idle для поддержания работы бота
        logger.info("Переход в режим idle")
        updater.idle()
        
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
