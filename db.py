import settings

from peewee import Model, MySQLDatabase, TextField
from playhouse.shortcuts import ReconnectMixin

# -----------------------------------------------

class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass

_db = ReconnectMySQLDatabase(
    settings.DATABASE['db'], 
    host = settings.DATABASE['host'], 
    port = settings.DATABASE['port'], 
    user = settings.DATABASE['user'],
    password = settings.DATABASE['password'],
    charset='utf8'
)

try:
    _db.connect()
except Exception as e:
    print(e)

# -----------------------------------------------

class BaseModel(Model):
    class Meta:
        database = _db

class LongTextField(TextField):
    field_type = 'LONGTEXT'

# End of file db.py