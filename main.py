import asyncio

import bot

if __name__ == '__main__':
    print('INFO:    BOT STARTED')
    asyncio.run(bot.start_polling())
    asyncio.run(bot.check_users())