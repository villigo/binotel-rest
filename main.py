from binotel import CallStats
import telegram
from yaml import load

with open('config.yaml', 'r') as f:
    config = load(f)

token = config['token']
KEY = config['KEY']
SECRET = config['SECRET']

bot = telegram.Bot(token)

calls = CallStats(KEY, SECRET)
in_call, in_new_call = calls.incoming_calls()
out_call = calls.outgoing_calls()


text = f'''
Входящих звонков за вчера:
Всего - {in_call}
Новых - {in_new_call}

Исходящие звонки за вчера:
Всего - {out_call}
*****************************
'''

for last_update in bot.getUpdates():
    chat_id = last_update.message.chat.id
    bot.sendMessage(chat_id=chat_id, text=text)
