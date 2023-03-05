from faker import Faker
import json, time
from random import randint
from datetime import date

fake=Faker('es_ES')
today = str(date.today())
i=0

while True:
       filename = 'datosClientes' + today + '_' + str(i) + '.json'
       output=open(filename,'w')

       datos={}
       datos['records']=[]
       cant_personas = randint(100,500)

       for x in range(cant_personas):
              data={"nombre":fake.name(),
              "edad":fake.random_int(min=18, max=80, step=1),
              "calle":fake.street_address(),
              "ciudad":fake.city(),
              "provincia":fake.state(),
              "cp":fake.postcode(),
              "longitud":float(fake.longitude()),
              "latitud":float(fake.latitude())}
              
              datos['records'].append(data)
                     
       json.dump(datos, output, indent = 6)

       i = i + 1
       
       time.sleep(5) # 5 segundos