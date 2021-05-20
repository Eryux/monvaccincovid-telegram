import json

from peewee import *
from datetime import datetime, timedelta
from db import BaseModel, LongTextField
from doctolib import DoctolibRequest, DoctolibUtils

class CenterModel(BaseModel):

    name = TextField() # Doctolib name

    slots = IntegerField(default=0) # Number slot available

    doctolib_id = IntegerField()

    doctolib_name = TextField() # Doctolib query name

    doctolib_practice = IntegerField()

    doctolib_url = TextField()

    doctolib_data = LongTextField(default="{ }")

    last_fetch = DateTimeField(default=datetime.now())

    cache_expire = DateTimeField(default=datetime.now())

    update_hash = CharField(max_length=64, default="")

    city = CharField(max_length=254, default="")

    zip_code = FixedCharField(max_length=5, default="")

    address = TextField(default="")

    latitude = DoubleField(default=0)

    longitude = DoubleField(default=0)

    place_name = TextField()


    def fetch_center_data(self):
        api = DoctolibRequest()
        try:
            data = api.get_booking(self.doctolib_url)
            self.doctolib_data = json.dumps(data)
        except Exception as e:
            print(e)

    
    def fetch_availability(self, refs = [], limit = 2):
        data = {}

        today = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d")
        
        try:
            fetch_data = json.loads(self.doctolib_data)
            motives = DoctolibUtils.motives_from_center(fetch_data, refs)

            agendas = []
            for motive in motives:
                agendas.extend(DoctolibUtils.agendas_from_center(fetch_data, motive['id'], self.doctolib_practice, True))
                
            api = DoctolibRequest()

            # Fetch slots with agendas that doesn't correspond to motive may cause bugs, investigation needed
            data = api.get_availabilities(today, [str(x['id']) for x in motives], [str(x['id']) for x in agendas], [str(self.doctolib_practice)], limit)
        except Exception as e:
            print(str(e))
        
        return data

    class Meta:
        table_name = "vc_center"

# End of file center_model.py