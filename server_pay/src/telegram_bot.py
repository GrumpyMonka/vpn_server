import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from db import init_db, is_admin, check_trial, add_admin, remove_admin
from xui import get_vpn_config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_main_menu():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Подписка"), KeyboardButton("Поддержка")]],
        resize_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"[{user_id}] Команда /start выполнена")
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! Добро пожаловать в VPN-бот. Выбери опцию:",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    logger.info(f"[{user_id}] Получено сообщение: {text}")

    if text == "Подписка":
        trial_end = check_trial(user_id)
        keyboard = []
        if not trial_end:
            # Проверяем, был ли пробный период использован
            from db import check_trial_used
            if not check_trial_used(user_id):
                keyboard.append([KeyboardButton("Пробная подписка")])
            await update.message.reply_text("У вас нет активной подписки.")
        else:
            await update.message.reply_text(f"У вас активна пробная подписка до {trial_end}")
        keyboard.append([KeyboardButton("Тарифы"), KeyboardButton("Главное меню")])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

    elif text == "Поддержка":
        logger.info(f"[{user_id}] Запрошена поддержка")
        await update.message.reply_text("Напишите ваше сообщение для поддержки:")
        context.user_data['awaiting_support'] = True

    elif text == "Пробная подписка":
        from db import activate_trial, check_trial_used
        if not check_trial_used(user_id):
            trial_end = activate_trial(user_id)
            logger.info(f"[{user_id}] Пробный период активирован до {trial_end}")
            await update.message.reply_text(f"Пробный период активирован до {trial_end}. "
                                            "Для доступа к VPN используйте /get_vpn")
            await get_vpn(update, context)
        else:
            logger.info(f"[{user_id}] Пробный период уже использован")
            await update.message.reply_text("Вы уже использовали пробный период.")
        await update.message.reply_text("Выберите действие:", reply_markup=get_main_menu())

    elif text == "Тарифы":
        logger.info(f"[{user_id}] Запрошены тарифы")
        await update.message.reply_text("Оплата пока недоступна. Свяжитесь с поддержкой.")
        await update.message.reply_text("Выберите действие:", reply_markup=get_main_menu())

    elif text == "Главное меню":
        logger.info(f"[{user_id}] Возврат в главное меню")
        await update.message.reply_text("Выберите опцию:", reply_markup=get_main_menu())

    elif context.user_data.get('awaiting_support'):
        logger.info(f"[{user_id}] Сообщение для поддержки принято")
        # Заглушка для обработки сообщения поддержки
        await update.message.reply_text("Ваше сообщение принято. Мы свяжемся с вами скоро.")
        context.user_data['awaiting_support'] = False
        await update.message.reply_text("Выберите опцию:", reply_markup=get_main_menu())

async def get_vpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    trial_end = check_trial(user_id)
    if trial_end:
        config = get_vpn_config(user_id)
        logger.info(f"[{user_id}] Запрошен VPN-конфиг")
        await update.message.reply_text(f"Ваш VPN-конфиг: {config}")
    else:
        logger.info(f"[{user_id}] Запрос VPN-конфига отклонён: пробный период не активен")
        await update.message.reply_text("Пробный период истёк или не активирован. Используйте /trial или /buy")
    await update.message.reply_text("Выберите опцию:", reply_markup=get_main_menu())

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"[{user_id}] Запрошена покупка")
    await update.message.reply_text("Оплата пока недоступна. Свяжитесь с поддержкой.")
    await update.message.reply_text("Выберите опцию:", reply_markup=get_main_menu())

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_admin(user_id):
        logger.info(f"[{user_id}] Запрошена админ-панель")
        await update.message.reply_text("Админ-панель: /add_admin <telegram_id>, /remove_admin <telegram_id>")
    else:
        logger.info(f"[{user_id}] Доступ к админ-панели отклонён")
        await update.message.reply_text("Доступ запрещён")
    await update.message.reply_text("Выберите опцию:", reply_markup=get_main_menu())

async def add_admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_admin(user_id):
        try:
            target_id = int(context.args[0])
            add_admin(target_id)
            logger.info(f"[{user_id}] Добавлен админ: {target_id}")
            await update.message.reply_text(f"Пользователь {target_id} теперь админ")
        except (IndexError, ValueError):
            logger.info(f"[{user_id}] Ошибка добавления админа: неверный telegram_id")
            await update.message.reply_text("Укажите telegram_id: /add_admin <telegram_id>")
    else:
        logger.info(f"[{user_id}] Попытка добавления админа отклонена")
        await update.message.reply_text("Доступ запрещён")
    await update.message.reply_text("Выберите опцию:", reply_markup=get_main_menu())

async def remove_admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_admin(user_id):
        try:
            target_id = int(context.args[0])
            remove_admin(target_id)
            logger.info(f"[{user_id}] Удалён админ: {target_id}")
            await update.message.reply_text(f"Пользователь {target_id} больше не админ")
        except (IndexError, ValueError):
            logger.info(f"[{user_id}] Ошибка удаления админа: неверный telegram_id")
            await update.message.reply_text("Укажите telegram_id: /remove_admin <telegram_id>")
    else:
        logger.info(f"[{user_id}] Попытка удаления админа отклонена")
        await update.message.reply_text("Доступ запрещён")
    await update.message.reply_text("Выберите опцию:", reply_markup=get_main_menu())

def run_bot(token):
    logger.info("[bot] Запуск бота")
    init_db()
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('get_vpn', get_vpn))
    application.add_handler(CommandHandler('buy', buy))
    application.add_handler(CommandHandler('admin', admin))
    application.add_handler(CommandHandler('add_admin', add_admin_cmd))
    application.add_handler(CommandHandler('remove_admin', remove_admin_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()