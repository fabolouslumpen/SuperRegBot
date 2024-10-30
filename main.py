import cfg
import telebot
from telebot import types

main_bot = telebot.TeleBot(cfg.main_bot_token)
admin_bot = telebot.TeleBot(cfg.admin_bot_token)
admin = cfg.admin_chat_token

user_data = {}

@main_bot.message_handler(commands=['start', 'register'])
def start_registration(message):
    user_id = message.chat.id
    user_data[user_id] = {}
    main_bot.send_message(user_id, "Вітаємо! Будь ласка, введіть своє ПІБ:")
    main_bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_id = message.chat.id
    user_data[user_id]['name'] = message.text
    main_bot.send_message(user_id, "Дякуємо! Тепер введіть свій номер телефону:")
    main_bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    user_id = message.chat.id
    user_data[user_id]['phone'] = message.text
    
    markup = types.InlineKeyboardMarkup()
    regions = ["Черкаси", "Худяки", "Дубіївка"]
    for region in regions:
        button = types.InlineKeyboardButton(region, callback_data=f"region_{region}")
        markup.add(button)
    
    main_bot.send_message(user_id, "Оберіть свій регіон:", reply_markup=markup)


@main_bot.callback_query_handler(func=lambda call: call.data.startswith("region_"))
def handle_region_selection(call):
    user_id = call.message.chat.id
    region = call.data.split("_")[1]
    user_data[user_id]['region'] = region
    
    main_bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)
    
    main_bot.send_message(user_id, "Дякуємо за реєстрацію! Заявка надіслана.")
    application_message = (
        f"Нова заявка:\n"
        f"ПІБ: {user_data[user_id]['name']}\n"
        f"Телефон: {user_data[user_id]['phone']}\n"
        f"Регіон: {user_data[user_id]['region']}\n"
        f"[Профіль користувача](tg://user?id={user_id})"
    )
    
    admin_bot.send_message(admin, application_message, parse_mode="Markdown")

main_bot.polling(none_stop=True)