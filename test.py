from typing import Set
import settings

from models import CenterModel, ChannelModel, SettingModel

#_db.create_tables([CenterModel, ChannelModel, SettingModel])

for s in SettingModel.select():
    print(s.param)