import threading
import settings
import time
import json
import dateutil.parser

from datetime import datetime, timedelta
from hashlib import sha256

from models import CenterModel, ChannelModel, SettingModel
from doctolib import DoctolibRequest, DoctolibUtils

# -----------------------------------------------

class Worker(threading.Thread):

    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.bot = bot
        self.stop = False

    @staticmethod
    def get_str_hash(str_value):
        m = sha256()
        m.update(str_value.encode('utf-8'))
        return m.hexdigest()

    def run(self):
        stat_alerts = SettingModel.get(SettingModel.param == 'NB_ALERT')
        stat_slots = SettingModel.get(SettingModel.param == 'NB_SLOTS')

        while self.stop is False:
            centers = []

            # Retrieve centers from database
            current_hour = datetime.now().hour
            if current_hour >= settings.DAY_HOUR and current_hour < settings.NIGHT_HOUR:
                centers = CenterModel.select().where(CenterModel.last_fetch < (datetime.now() - timedelta(seconds=settings.CENTER_REQUEST_DELAY_DAY))).order_by(CenterModel.last_fetch)
            else:
                centers = CenterModel.select().where(CenterModel.last_fetch < (datetime.now() - timedelta(seconds=settings.CENTER_REQUEST_DELAY_NIGHT))).order_by(CenterModel.last_fetch)

            for center in centers:
                now = datetime.now()

                # Retrieve channels for the centers
                channels = ChannelModel.select().where(ChannelModel.center == center, ChannelModel.last_update < (now - timedelta(minutes=3)))

                # Update center cache data
                if center.cache_expire < now:
                    print("Fetch data for {}".format(center.doctolib_name))
                    center.fetch_center_data()
                    center.cache_expire = now + timedelta(seconds=settings.CENTER_FETCH_CACHE_EXPIRE)

                # Retrieve slots
                print("Fetch availabilities for {} ... ".format(center.doctolib_name), end='')

                # If no channel needs to be updated for this center, we fake the update to avoid unnecessary requests
                if len(channels) != 0:
                    availabilities = center.fetch_availability(settings.DOCTOLIB_REFS, 2)

                    if 'total' in availabilities:
                        print("found {}".format(availabilities['total']))
                    else:
                        print("fail")

                    center.slots = int(availabilities['total']) if 'total' in availabilities else 0
                    center.last_fetch = now
                    center.save()

                    if 'total' in availabilities and availabilities['total'] > 0:
                        # Calculate response hash
                        availabilities_hash = Worker.get_str_hash(json.dumps(availabilities))

                        # Build message
                        message = "💉 {} créneau(x) de vaccination disponible(s) à {}.\n\n".format(availabilities['total'], center.name)

                        try:
                            slots = DoctolibUtils.slots_from_availabilities(availabilities)
                            for slot_day in slots:
                                if len(slots[slot_day]) == 0:
                                    continue
                                message += "Le {} : {}\n".format(dateutil.parser.parse(slot_day).strftime("%d/%m"), ', '.join([x.strftime("%H:%M") for x in slots[slot_day]]))
                        except:
                            pass
                        
                        message += "\nLien : " + DoctolibUtils.create_center_link(center.doctolib_url, center.doctolib_practice)

                        # Update stats
                        stat_slots.param_value = str(int(stat_slots.param_value) + availabilities['total'])
                        stat_slots.save()

                        stat_alerts.param_value = str(int(stat_alerts.param_value) + len(channels))
                        stat_alerts.save()

                        # Send message
                        for channel in channels:
                            if channel.update_hash != availabilities_hash:
                                channel.update_hash = availabilities_hash
                                channel.last_update = now
                                channel.save()
                                self.bot.send_alert_message(int(channel.channel), message, center.id)
                else:
                    print("faked")
                    center.slots = 0
                    center.last_fetch = now
                    center.save()
                    continue

                time.sleep(settings.API_REQUEST_DELAY / 1000)

            time.sleep(3)

# End of file worker.py