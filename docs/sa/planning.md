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

Si tenemos un documento que provoca tener que realizar joins para recuperar unos pocos atributos, usaremos el patron:
    Atributo
    Referencia extendida
    Cubo
    Atípico


## Framework de agregación (1h)

Sobre la colección de productos trabajada en clase, trabajando con el framework de agreagación, si queremos obtener la cantidad de productos que tenemos de cada tipo, realizaremos:

    una fase para $group y otra para $count
    en la fase de $group hacemos $count
    en la fase de $group hacemos $sum
    una fase para $gorup y otra para $sum


 db.productos.aggregate([
  { $group: {
      _id: "$fabricante",
      total: { $sum:1 }
    }
  }])
  
var pipeline = [
        { $match: {
            genres: {$in: ["Romance"]}, // Romance movies only.
            released: {$lte: new ISODate("2001-01-01T00:00: 00Z") }}},
        { $sort: {"imdb.rating": -1}}, // Sort by IMDB rating.
        { $limit: 3 }, // Limit to 3 results.
        { $project: { title: 1, genres: 1, released: 1, "imdb.rating": 1}}
    ];

var pipeline = [
     {$group: {
         _id: "$rated",
         "numTitles": { $sum: 1},
     }}
    ];

var pipeline = [
    { $match: {
    released: {$lte: new ISODate("2001-01-01T00:00:00Z") }}},
    { $group: {
        _id: {"$arrayElemAt": ["$genres", 0]},
        "popularity": { $avg: "$imdb.rating"},
        "top_movie": { $max: "$imdb.rating"},
        "longest_runtime": { $max: "$runtime"}
    }},
    { $sort: { popularity: -1}},
    { $project: {
        _id: 1,
        popularity: 1,
        top_movie: 1,
        adjusted_runtime: { $add: [ "$longest_runtime", 12 ] } } }
    ];

var pipeline = [

{ $match: {
    released: {$lte: new ISODate("2001-01-01T00:00:00Z") },
        runtime: {$lte: 218},
        "imdb.rating": {$gte: 7.0}
    }
    },
    { $sort: {"imdb.rating": -1}},
    { $group: {
        _id: {"$arrayElemAt": ["$genres", 0]},
        "titulo_recomendado": {$first: "$title"},
        "nota_recomendado": {$first: "$imdb.rating"},
        "tiempo_recomendado": {$first: "$runtime"},
        "popularidad": { $avg: "$imdb.rating"},
        "mejor_nota": { $max: "$imdb.rating"},
        "tiempo_maslargo": { $max: "$runtime"}
    }},
    { $sort: { popularity: -1}},
    { $project: {
        _id: 1,
            popularidad: 1,
            mejor_nota: 1,
            titulo_recomendado: 1,
            nota_recomendado: 1,
            tiempo_recomendado: 1,
            tiempo_ajustado_maslargo: { $add: [ "$tiempo_maslargo", 12 ] } } }
];

db.movies.aggregate(pipeline);

var pipeline = [
             { $group: {
                 _id: "$movie_id",
                 "sumComments": { $sum: 1}
             }},
             { $sort: { "sumComments": -1}},
             { $limit: 5},
             { $lookup: {
                 from: "movies",
                 localField: "_id",
                 foreignField: "_id",
                 as: "movie"
             }},
             { $unwind: "$movie" },
             { $project: {
                 "movie.title": 1,
                 "movie.imdb.rating": 1,
                 "sumComments": 1,
             }},
             { $out: "most_commented_movies" }
    ];
db.comments.aggregate(pipeline);

var pipeline = [
    { $match: {
        "awards.wins": { $gte: 1},
        genres: {$in: ["Documentary"]},
    }},
    { $sort: {"awards.wins": -1}}, // Sort by award wins.
    { $limit: 3},
    { $project: { title: 1, genres: 1, awards: 1}},
];

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
