import news_api
import datetime, json, os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, Updater, CommandHandler, RegexHandler, MessageHandler, CallbackQueryHandler

TOKEN = os.environ['BOT_TOKEN']

updater = Updater(token=TOKEN, use_context=True)

# Actions
def handle_start(update, context):
	start_info = '''
	<b>👋 Hi There!\nI'm a news bot! 🤖</b>
\n\nI can send you latest news article links from TheHindu newspaper!
	'''
	context.bot.send_message(chat_id=update.effective_chat.id, text=start_info, parse_mode='HTML')
	handle_help(update, context)

def handle_help(update, context):
	help_info = '''
	<b>😊 Try following commands:</b>
	👉 <b>/start</b> : to start chatting with me anytime

	👉 <b>/news</b> : to get today's news
	👉 <b>/news</b> YYYY/MM/DD : to get news for a particular date (YYYY/MM/DD)

	👉 <b>/help</b> : to know all commands
	'''
	context.bot.send_message(chat_id=update.effective_chat.id, text=help_info, parse_mode='HTML')

def handle_news(update, context):
	pub_type = 'print' # or 'web'
	pub_date = datetime.datetime.now().strftime('%Y/%m/%d')

	args = context.args
	if len(args) == 1:
		try:
			pub_date = datetime.datetime.strptime(context.args[0], '%Y/%m/%d').strftime('%Y/%m/%d')
		except Exception as e:
			raise e;
		else:
			pass
		finally:
			pass

	context.bot.send_message(chat_id=update.effective_chat.id, text=f"🙂 Please wait!\nI'm finding news sections from the <b>{pub_type}</b> edition for <b>{pub_date}</b>", parse_mode='HTML')
	
	reader = news_api.TheHinduReader(pub_date)
	res = reader.get_articles()
	news_data = json.loads(res)

	sec_options = []
	for section in news_data:
		art_count = len(section['articles'])
		art_unit = 'article' if art_count == 1 else 'articles'
		sec_info = f"{section['title'].title()}\t({art_count} {art_unit})"
		data = json.dumps({'section':section['title'], 'date': pub_date})
		sec_options.append([InlineKeyboardButton(sec_info, callback_data=data)])

	msg = InlineKeyboardMarkup(sec_options)
	update.message.reply_text('Sections from TheHindu Newspaper\n', reply_markup=msg)

def handle_btn_press(update, context):
	sel_sec = json.loads(update.callback_query.data)
	context.bot.send_message(chat_id=update.effective_chat.id, text=f"🙂 Please wait!\nI'm collecting articles from <b>{sel_sec['section'].title()}</b> section.", parse_mode='HTML')

	'''
	TODO: DO NOT FETCH AGAIN, STORE DATA
	'''
	reader = news_api.TheHinduReader(sel_sec['date'])
	news_data = json.loads(reader.get_articles())

	articles = []
	for sec in news_data:
		if sec['title'] == sel_sec['section']:
			articles = sec['articles']
			break

	msg = f"Articles in **{sel_sec['section'].title()}** section :"
	max_msg_len = 4096
	for article in articles:
		title = article['title']
		url = article['url']
		#tmp = f"\n👉 <a href='{url}'>{title}</a>"
		tmp = f"\n👉 [{title}]({url})"
		if (len(msg)+len(tmp)) <= max_msg_len:
			msg += tmp
		else:
			context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode='Markdown')
			msg = ""
	if len(msg) > 0:
			context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode='Markdown')

def handle_unknown(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id, text="😢 Sorry, I didn't understand that.\nI'll ask my developer to make me smart! 😎")
	handle_help(update, context)

def handle_bye(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id, text="👋 Ok Bye!\nHope to see you again!")

def handle_rude(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id, text="🙄 Hey Hey Hey!\nDon't use these bad words please!🙏")

# Command Handling
updater.dispatcher.add_handler(CommandHandler('start', handle_start))
updater.dispatcher.add_handler(CommandHandler('help', handle_help))
updater.dispatcher.add_handler(CommandHandler('news', handle_news))
updater.dispatcher.add_handler(CallbackQueryHandler(handle_btn_press))

#msgs [TODO use more advanced means]
updater.dispatcher.add_handler(RegexHandler(r'(?i).*\s?(fuck|cunt|bastard|shit|hoe|whore|dick)\s?.*', handle_rude))
updater.dispatcher.add_handler(RegexHandler(r'(?i).*\s?(hi|hello|namaste)\s?.*', handle_start))
updater.dispatcher.add_handler(RegexHandler(r'(?i).*\s?(bye|ciao|alvida|see you)\s?.*', handle_bye))

#unknown commands
updater.dispatcher.add_handler(RegexHandler(r'/.*', handle_unknown))
updater.dispatcher.add_handler(RegexHandler(r'.*', handle_unknown))

# Execute

print('Bot is running...')
updater.start_polling()
updater.idle()
#updater.stop()
