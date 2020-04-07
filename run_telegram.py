from cool_defi_bot import telegram_bot


bot = telegram_bot.get_bot()
bot.start_polling()
print("Bot started")
