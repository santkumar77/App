Episode 2⏤⁠⁠⁠⁠ 🍁:
import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8633160903:AAGjtHtDmI2QWjA4kYKM6OE3Xxh0eJCUqdA"

bot = telebot.TeleBot(TOKEN)

# 🔴 Owner ID (अपना Telegram ID डालो)
OWNER_ID = 8507640815

# 🔴 Force Join Channels
CHANNELS = [-1003721534860, -1002276966453]

user_data = {}
users = set()

# 🔎 Check user joined channels
def is_joined(user_id):
    try:
        for channel in CHANNELS:
            status = bot.get_chat_member(channel, user_id).status
            if status in ["left", "kicked"]:
                return False
        return True
    except:
        return False


@bot.message_handler(commands=['start'])
def send_welcome(message):

    users.add(message.chat.id)

    if not is_joined(message.from_user.id):

        markup = InlineKeyboardMarkup()

        markup.add(
            InlineKeyboardButton(
                "📢 Join Channel 1",
                url="https://t.me/+YfaD7kqaGfY1YjY1"
            )
        )

        markup.add(
            InlineKeyboardButton(
                "📢 Join Channel 2",
                url="https://t.me/+5gttInB7TgY3MTk1"
            )
        )

        markup.add(
            InlineKeyboardButton(
                "✅ Check Join",
                callback_data="check_join"
            )
        )

        bot.send_message(
            message.chat.id,
            "⚠️ Please join our channels to use this bot.",
            reply_markup=markup
        )
        return

    bot.send_message(message.chat.id,"👋 Welcome! Please enter the name of the app you're looking for:")


@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):

    if is_joined(call.from_user.id):
        bot.answer_callback_query(call.id,"✅ You joined successfully")
        bot.send_message(call.message.chat.id,"👋 Now send the app name you want.")
    else:
        bot.answer_callback_query(call.id,"❌ You didn't join the channels")


# 📢 BROADCAST COMMAND
@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.from_user.id != OWNER_ID:
        bot.reply_to(message,"❌ You are not allowed to use this command.")
        return

    msg = message.text.replace("/broadcast","").strip()

    if not msg:
        bot.reply_to(message,"⚠️ Usage: /broadcast your message")
        return

    sent = 0

    for user in users:
        try:
            bot.send_message(user,msg)
            sent += 1
        except:
            pass

    bot.reply_to(message,f"✅ Broadcast sent to {sent} users")


@bot.message_handler(func=lambda message: not message.text.startswith("/"))
def find_apk(message):

    users.add(message.chat.id)

    if not is_joined(message.from_user.id):
        bot.send_message(message.chat.id,"⚠️ Please join the channels first using /start")
        return

    app_name = message.text
    api_url = f"https://nametoapk.ytansh038.workers.dev/?name={app_name}"
    
    try:
        response = requests.get(api_url).json()

        if response and len(response) > 0:

            markup = InlineKeyboardMarkup()

            for index, item in enumerate(response):
                markup.add(
                    InlineKeyboardButton(
                        item.get('name','Unknown'),
                        callback_data=f"select_{index}"
                    )
                )

            bot.send_message(
                message.chat.id,
                f"🎯 Found {len(response)} apps. Tap to get download link:",
                reply_markup=markup
            )

            user_data[message.chat.id] = response

        else:
            bot.reply_to(message,"❌ Sorry, no apps found.")

    except:
        bot.reply_to(message,"⚠️ API Error! Please try again later.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_'))
def handle_selection(call):

    index = int(call.data.split('_')[1])

    chat_id = call.message.chat.id

    selected_app = user_data.get(chat_id,[])[index]

    name = selected_app.get('name','N/A')
version = selected_app.get('version','Unknown')

    size_bytes = selected_app.get('filesize',0)

    size = f"{round(size_bytes/1024/1024,2)} MB"

    photo = selected_app.get('image')

    link = selected_app.get('path')

    caption = (
        f"📩 {name}\n"
        f"Version: {version}\n"
        f"Size: {size}\n"
    )

    markup = InlineKeyboardMarkup()

    if link:
        markup.add(
            InlineKeyboardButton(
                "⬇️ Download APK",
                url=link
            )
        )
    else:
        markup.add(
            InlineKeyboardButton(
                "❌ Link Not Found",
                callback_data="none"
            )
        )

    try:
        bot.send_photo(chat_id,photo,caption=caption,reply_markup=markup,parse_mode="Markdown")
    except:
        bot.send_message(chat_id,caption,reply_markup=markup,parse_mode="Markdown")


bot.infinity_polling()