import settings

from bot import TelegramClient
from worker import Worker
from models import SettingModel

# -----------------------------------------------

if __name__ == "__main__":
    # Update database settings
    s = SettingModel.select()
    for data in s:
        if data.param == 'API_REQUEST_DELAY':
            data.param_value = str(settings.API_REQUEST_DELAY)
            data.save()
        elif data.param == 'CENTER_REQUEST_DELAY_DAY':
            data.param_value = str(settings.CENTER_REQUEST_DELAY_DAY)
            data.save()
        elif data.param == 'CENTER_REQUEST_DELAY_NIGHT':
            data.param_value = str(settings.CENTER_REQUEST_DELAY_NIGHT)
            data.save()
        elif data.param == 'WATCH_LIMIT':
            data.param_value = str(settings.WATCH_LIMIT)
            data.save()
        elif data.param == 'DAY_HOUR':
            data.param_value = str(settings.DAY_HOUR)
            data.save()
        elif data.param == 'NIGHT_HOUR':
            data.param_value = str(settings.NIGHT_HOUR)
            data.save()
        elif data.param == 'CENTER_FETCH_CACHE_EXPIRE':
            data.param_value = str(settings.CENTER_FETCH_CACHE_EXPIRE)
            data.save()

    # Initialize telegram bot
    print("Create Telegram client ...")
    bot = TelegramClient()

    # Start worker
    print("Create and start worker ...")
    job = Worker(bot)
    job.start()

    # Start telegram bot
    print("Start Telegram client ...")
    bot.run()

    # Stop worker
    print("Telegram client stopped, stop worker ...")
    job.stop = True
    job.join()

    print("bye.")

# End of file app.py