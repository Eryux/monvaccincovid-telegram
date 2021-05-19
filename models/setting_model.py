from peewee import *
from db import BaseModel

class SettingModel(BaseModel):

    param = CharField()

    param_value = TextField(default="")

    class Meta:
        table_name = "vc_setting"

# End of file setting_model.py