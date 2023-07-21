from peewee import *
from  conf import conf
from playhouse.sqliteq import SqliteQueueDatabase


db = SqliteQueueDatabase(conf['db'][conf['env']]['db_name'],
    use_gevent=False,  # Use the standard library "threading" module.
    autostart=True,  # The worker thread now must be started manually.
    queue_max_size=64,  # Max. # of pending writes that can accumulate.
    results_timeout=5.0)

import datetime
from peewee import *


class BaseModel(Model):
    class Meta:
        database = db

class Monitor(BaseModel):
    id = BigAutoField(primary_key = True)
    data_run = DateTimeField(default=datetime.datetime.now)
    titolo=TextField(null=True)
    flow = TextField(null=True)
    data_aggiornamento=DateTimeField(formats='%d/%m/%Y %H:%M', null=True, index=True)
    start_periodo=DateTimeField()
    end_periodo=DateTimeField()
    download  =  BooleanField(default=False)
    note = TextField(null=True)   ### tempo?

class Download(BaseModel):
    titolo=TextField(null=True)
    flow = TextField(null=True)
    data_aggiornamento=DateTimeField(formats='%d/%m/%Y %H:%M', null=True, index=True)
    anno=DateTimeField()
    volume = TextField(null=True)
    note = TextField(null=True)   

def initialize_db():
    db.connect()
    db.create_tables([Monitor,Download], safe = True)
    db.close()

initialize_db()