import json

from peewee import *
from datetime import datetime
from db import BaseModel
from models import CenterModel

class ChannelModel(BaseModel):

    channel = CharField(max_length=254)

    center = ForeignKeyField(CenterModel, backref='channels', on_delete='CASCADE')

    last_update = DateTimeField(default=datetime.now())

    class Meta:
        table_name = "vc_channel"
        primary_key = CompositeKey('channel', 'center')

# End of file channel_model.py