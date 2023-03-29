from faker import Faker
import time
from random import randint
from datetime import date, datetime, timedelta
from kafka import KafkaProducer
from json import dumps

fake = Faker('es_ES')
today = str(date.today())
i=0

producer = KafkaProducer(
    value_serializer=lambda m: dumps(m, default=str).encode('utf-8'),
    bootstrap_servers=['iabd-virtualbox:9092'])

while True:

    datos={}
    datos['records']=[]
    cant_bizums = randint(1,5)

    for x in range(cant_bizums):
        # datos de un bizum
        seg_random = randint(1,59)

        data = {
            "timestamp": datetime.now() + timedelta(seconds=seg_random),
            "nombre":fake.name(),
            "cantidad":fake.random_int(min=15, max=600, step=1),
            "concepto":fake.sentence(nb_words=3)
        }

        producer.send("iabd-bizum", value=data)


    producer.flush()
    i = i + 1
    time.sleep(10) # 10 segundos   
