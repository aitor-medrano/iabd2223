# Planning (10h)

## 01 NoSQL (1h)

<!--
<https://www.cs.us.es/cursos/bd/Contents.html#primero>
<https://www.cs.us.es/cursos/bd/temas/BD-Tema-7-print.pdf>
-->

Revisar: <https://aws.amazon.com/es/nosql/>
Revisar: <https://www.mongodb.com/es/nosql-explained>

## 02 MongoDB (1h + 1h)

Conceptos
Uso mediante Docker ... poner enlaces para instalar Mongo desde comandos
Restore/dump

Consultas sencillas (1h)
CRUD

En MongoDB, los documentos se almacenan en formato:

BSON
JSON
CSV
SQL

Para borrar todos los datos de una colección llamada pruebas usaremos:

db.pruebas.deleteMany({})
db.pruebas.deleteOne({})
db.pruebas.drop()
db.pruebas.removeCollection()
db.pruebas.unset()

Sobre la colección `trips` trabajada en el aula, para recuperar la duración de los viajes de las clientes nacidos en los años 1977 y 1981 ejecutaremos la consulta:

db.trips.find({ "birth year": {$in: [1977, 1981]} }, {tripduration:1})
db.trips.find({ "birth year": {$in: [1977, 1981]} , {usertype:"Customer"}})
db.trips.find({ "birth year": {$in: [1977, 1981]} , {usertype:"Customer"}}, {tripduration:0})
db.trips.find({ "birth year": {$in: [1977, 1981]} , {usertype:"Customer"}}, {tripduration:1})

## 03 Modelado (1h)

Modelado
    Relaciones
    Patrones


22 - Relaciones 1 a muchos
Para las relaciones uno a muchos:

Si hay pocos datos, lo mejor en colocar las referencias en un array.
Si hay pocos datos, lo mejor es colocar los documentos embebidos dentro de un array.
Si hay muchos datos, lo mejor en colocar las referencias en un array.
Si hay muchos datos, lo mejor es colocar los documentos embebidos dentro de un array.
Si hay muchos datos, la referencia se coloca en el muchos hacia el 1.
Si hay muchos datos, el documento embebido se coloca en el muchos hacia el 1.
Si hay muchísimos datos, la referencia se coloca en el muchos hacia el 1.
Si hay muchísimos datos, lo mejor en colocar las referencias en un array.


Respecto a la validación de los documentos respecto a un esquema:
Es obligatorio definir siempre un esquema.
Si hemos añadido una validación, los nuevos documentos no pueden contener nuevos campos
Sólo podemos comprobar la existencia y el tipo de los datos
Siempre indicaremos el esquema a validar cuando creamos las colecciones
Podemos definir expresiones de validación entre campos

Para validar un docume

## Framework de agregación (1h)

## 04 Formatos (1h)

csv
json
columnar
avro
parquet
orc

## 05 Escalabilidad y Rendimiento (2h)

MongoAtlas / Compass
Cluster
    ReplicaSet

Replicación
Sharding

Rendimiento
    Índices

## 06 PyMongo (2h)

## Sesiones

1. NoSQL + MongoDB I
2. MongoDB II. Framework de agregación
3. Formatos de datos. Modelado NoSQL
4. Escalabilidad y Rendimiento.
5. Mongo y Python

## Pendiente

Capped collections: colecciones limitadas
