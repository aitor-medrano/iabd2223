# pip install python-aemet
# https://github.com/pablo-moreno/python-aemet
# https://opendata.aemet.es/centrodedescargas/inicio

from aemet import Aemet, Municipio
aemet_client = Aemet(api_key='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhLm1lZHJhbm9AZWR1Lmd2YS5lcyIsImp0aSI6IjE1ODNlY2NjLWM4ODMtNDBmZC1iZDMyLTdjYjllZmI4M2FhNyIsImlzcyI6IkFFTUVUIiwiaWF0IjoxNjc1Nzk1ODY4LCJ1c2VySWQiOiIxNTgzZWNjYy1jODgzLTQwZmQtYmQzMi03Y2I5ZWZiODNhYTciLCJyb2xlIjoiIn0.hja2rX0UPrw8szze18Lq_gZNjQhM6CX3ozZho8LVGjY')

m = Municipio.buscar('Elche')
for municipios in m:
    print(municipios)

print("------")
p = aemet_client.get_prediccion('03065')
print(p.__dict__)

for predicciones in p.prediccion:
    print(predicciones.__dict__)

# observaciones = aemet_client.get_observacion_convencional('8416Y')  # Valencia station
# assert type(observaciones) is list

# for observacion in observaciones:
#     print(observacion.__dict__)


https://www.el-tiempo.net/api

https://github.com/schibsted/jslt/blob/master/tutorial.md
https://www.el-tiempo.net/api/json/v2/provincias/03/municipios/03065