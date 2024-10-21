import telebot
import requests
import sys
import importlib
import tomodachi_db
import tomodachi_outline
import builders
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import types
import logging

logging.basicConfig(level=logging.INFO)

cfg_name = sys.argv[1] + "_cfg"
cfg = importlib.import_module(cfg_name)

bot = telebot.TeleBot(cfg.bot_token)
provider_token = cfg.payments_token
prices = [types.LabeledPrice(
    label='VPN - ' + cfg.vpn_location + ', 1 month, 30GB', amount=16900)]

key_markup = types.InlineKeyboardMarkup()
opt1 = types.InlineKeyboardButton(
    text="Free key (0rub/week/3GB)", callback_data='free_key')
opt2 = types.InlineKeyboardButton(
    text="Paid key (169rub/month/30GB)", callback_data='paid_key')
key_markup.add(opt1)
key_markup.add(opt2)


@bot.message_handler(commands=["start"])
def start(message):
    try:
        tomodachi_db.insert_user(message.from_user)
        menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        opt1 = types.KeyboardButton("🔑 Get key")
        opt3 = types.KeyboardButton("⬇️ Download Outline")
        opt4 = types.KeyboardButton("📖 My keys")
        menu_markup.add(opt1, opt3, opt4)
        bot.send_message(
            message.chat.id,
            "Welcome! To obtain a new VPN configuration, please tap on 🔑 Get key. "
            "To use the key, download Outline on your device and import the key",
            reply_markup=menu_markup
        )
    except Exception as e:
        logging.error(f"Error executing command /start: {e}")
        bot.send_message(
            message.chat.id, "There was an unexpected error. Please try again later.")


@bot.message_handler(func=lambda message: message.text == "🔑 Get key")
def keys(message):
    bot.send_message(
        message.chat.id, "Please, choose your key type", reply_markup=key_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'get_key_type')
def get_key_type(call):
    uid = call.message.chat.id
    bot.send_message(
        uid, "Please, choose your key type", reply_markup=key_markup)


@bot.message_handler(func=lambda message: message.text == "📖 My keys")
def my_keys(message):
    user_keys = tomodachi_db.get_user_keys(message.chat.id)
    if len(user_keys) == 0:
        bot.send_message(
            message.chat.id, "You do not have active keys. Please get one!")
    else:
        reply = "Your keys: \n\n"
        for key in user_keys:
            reply += builders.build_key_description(
                key, cfg.vpn_location) + '\n\n'
        bot.send_message(
            message.chat.id, reply)


@bot.message_handler(func=lambda message: message.text == "⬇️ Download Outline")
def download_outline(message):
    bot.send_message(
        message.chat.id, "Outline is available on following platforms:\n" + builders.build_download_string(), parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == 'free_key')
def free_key(call):
    uid = call.message.chat.id

    management_api = tomodachi_db.get_single_server(cfg.vpn_location)

    if tomodachi_db.is_trial(uid) or uid == 123628079:
        access_url, key_server_id = tomodachi_outline.create_key(
            management_api, uid, cfg.free_bytes_limit, True)

        bot.send_message(
            uid, f"Next message contains a free Outline key which will work for 1 week and has {round(cfg.free_bytes_limit/1000000000)} GB")
        bot.send_message(
            uid, f"{access_url}#TomodachiVPN{cfg.vpn_location}", reply_markup=key_markup)

        bot.send_message(
            cfg.owner_id, f"User got a free key\n{builders.build_user_string(call)}")

        tomodachi_db.insert_key(
            f"free{uid}", key_server_id, f"{access_url}#TomodachiVPN{cfg.vpn_location}", management_api, uid, cfg.free_bytes_limit, 1)

        tomodachi_db.close_trial(uid)

    elif not tomodachi_db.is_trial(uid):
        bot.send_message(
            uid, "Unfortunately, you have already used a free key. Please consider purchasing paid key", reply_markup=key_markup)
        bot.send_message(
            cfg.owner_id, f"User have tried to get free key, but he is already out of trial\n{builders.build_user_string(call)}")


@bot.callback_query_handler(func=lambda call: call.data == 'paid_key')
def paid_key(call):
    message = call.message

    bot.send_message(message.chat.id,
                     "Sending your invoice", parse_mode='Markdown')
    bot.send_invoice(
        message.chat.id,  # chat_id
        'Paid key Tomodachi VPN',  # title
        '1 month, 30GB, ' + cfg.vpn_location + ' server',  # description
        'invoice',  # invoice_payload
        provider_token,  # provider_token
        'rub',  # currency
        prices,
        need_email=True,
        send_email_to_provider=True,
        provider_data=builders.build_provider_data())


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="There was an error processing your payment. "
                                                "Please try again later")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id,
                     'Congratulations! Next message contains your paid Outline key which will work for 1 month and has 30GB',
                     parse_mode='Markdown')

    uid = message.chat.id
    management_api = tomodachi_db.get_single_server(cfg.vpn_location)

    access_url, key_server_id = tomodachi_outline.create_key(
        management_api, uid, cfg.paid_bytes_limit, False)
    tomodachi_db.insert_key(
        f"paid{uid}", key_server_id, f"{access_url}#TomodachiVPN{cfg.vpn_location}", management_api, uid, cfg.paid_bytes_limit, 0)

    bot.send_message(
        uid, f"{access_url}#TomodachiVPN{cfg.vpn_location}", reply_markup=key_markup)
    bot.send_message(
        cfg.owner_id, f"User got a paid key\n{builders.build_user_string(message)}")


def find_expired_keys():
    expiring_keys = tomodachi_db.find_expired_keys()
    for key in expiring_keys:
        bot.send_message(
            key[3], f"Your key {key[4]} expired, and we had to delete it")
        management_api = tomodachi_db.get_single_server(cfg.vpn_location)
        tomodachi_outline.delete_key(management_api, key[2])


async def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(id='find_expired_keys', func=find_expired_keys,
                      trigger='interval', seconds=10)
    scheduler.start()
    await bot.infinity_polling()

if __name__ == "__main__":
    asyncio.run(main())
