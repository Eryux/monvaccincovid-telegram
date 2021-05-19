import json

from doctolib import DoctolibUtils
from models import CenterModel

centers = CenterModel.select()

for center in centers:
    print("Update {} ...".format(center.name), end='')

    try:
        data = json.loads(center.doctolib_data)
        center_place = DoctolibUtils.place_from_center(data, 'practice-' + str(center.doctolib_practice))
        center.city = center_place['city']
        center.zip_code = center_place['zipcode']
        center.address = center_place['address']
        center.latitude = center_place['latitude']
        center.longitude = center_place['longitude']
        center.place_name = center_place['formal_name']
        center.save()
        print("Updated")
    except:
        print("Failed")