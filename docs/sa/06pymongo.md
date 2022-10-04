---
title: PyMongo
description: Acceso a MongoDB desde Python mediante la librería PyMongo
---

# PyMongo

Para acceder a MongoDB desde Python nos vamos a centrar en la librería [PyMongo](https://pypi.org/project/pymongo/).

Para instalar la librería mediante `pip` usaremos el comando (recuerda hacerlo dentro de un entorno virtual):

``` bash
pip install pymongo
```

Se recomienda consultar la [documentación](https://pymongo.readthedocs.io/en/stable/) o el [API](https://pymongo.readthedocs.io/en/stable/api/index.html) para cualquier duda o aclaración.

!!! info "Versión"
    En el momento de escribir los apuntes, estamos utilizando la versión 4.2.0 de PyMongo.

## MFlix

<https://s3.amazonaws.com/edu-downloads.10gen.com/M220P/2022/July/static/handouts/m220/mflix-python.zip>

### Estructura del proyecto

verything you will implement is located in the mflix/db.py file, which contains all database interfacing methods. The API will make calls to db.py to interact with MongoDB.

The unit tests in tests will test these database access methods directly, without going through the API. The UI will run these methods in integration tests, and therefore requires the full application to be running.

The API layer is fully implemented, as is the UI. If you need to run on a port other than 5000, you can edit the index.html file in the build directory to modify the value of window.host.

Please do not modify the API layer in any way, movies.py and user.py under the mflix/api directory. Doing so will most likely result in the frontend application failing to validate some of the labs.

### Preparando el entorno

Descargamos y descomprimimos el archivo
Dentro de la carpeta, vamos a crear un entorno virtual con venv:

``` bash
virtualenv mflix_venv
```

A continuación, lo activamos:

``` bash
source mflix_venv/bin/activate
```

E instalamos los requisitos:

``` bash
pip install -r requirements.txt
```

Running the Application

In the mflix-python directory you can find a file called dotini.

Open this file and enter your Atlas SRV connection string as directed in the comment. This is the information the driver will use to connect. Make sure not to wrap your Atlas SRV connection between quotes:

COPY
MFLIX_DB_URI = mongodb+srv://...
Rename this file to .ini with the following command:

COPY
mv dotini_unix .ini  # on Unix
ren dotini_win .ini # on Windows
Note: Once you rename this file to .ini, it will no longer be visible in Finder or File Explorer. However, it will be visible from Command Prompt or Terminal, so if you need to edit it again, you can open it from there:

COPY
vi .ini       # on Unix
notepad .ini  # on Windows

### Arrancando y Probando

Para arrancar la aplicación ejecutaremos el script `run.py`:

``` bash
python run.py
```

Al ejecutar el script, arrancará la aplicación y podremos acceder a ella a través de <http://127.0.0.1:5000/>.

PANTALLAZO

Si queremos ejecutar los test:

Running the Unit Tests

To run the unit tests for this course, you will use pytest and needs to be run from mflix-python directory. Each course lab contains a module of unit tests that you can call individually with a command like the following:

COPY
pytest -m LAB_UNIT_TEST_NAME
Each ticket will contain the command to run that ticket's specific unit tests. For example to run the Connection Ticket test your shell command will be:

COPY
pytest -m connection

Un ejemplo básico podría ser similar a:

``` python
client = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')
filter = {
    'age': {
        '$lt': 30
    }
}
test_db = client.test
people_coll = test_db.people
result = people_coll.find(
  filter = filter
)
````

## MongoClient

A partir de la URI de conexión a MongoDB, hemos de instanciar la clase [`MongoClient`](https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient):

```  python
uri = "mongodb+srv://usuario:contrasenya@host"
cliente = MongoCliente(uri)
```

Podemos obtener información de la conexión mediante la propiedad `state`:

``` python
print(cliente.state)
```

Por ejemplo, en nuestro caso, nos hemos conectado a MongoAtlas y de la salida del estado podemos ver los diferentes *hosts* que forman parte del conjunto de réplicas:

``` js
Database(MongoClient(host=['ac-hrdpnx0-shard-00-02.4hm7u8y.mongodb.net:27017', 'ac-hrdpnx0-shard-00-01.4hm7u8y.mongodb.net:27017', 'ac-hrdpnx0-shard-00-00.4hm7u8y.mongodb.net:27017'], document_class=dict, tz_aware=False, connect=True, authsource='admin', replicaset='atlas-pxc2m9-shard-0', ssl=True, connecttimeoutms=200, retrywrites=True), 'stats')
```

!!! info "Parámetros adicionales"
    A la hora de crear el cliente, también podemos indicarle opciones de configuración:

    ``` 
    cliente200Retry = MongoClient(uri, connectTimeoutMS=200, retryWrites=True)
    ```

También podemos obtener un listado de las bases de datos mediante [`list_database_names()`](https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient.list_database_names):

``` python
print(cliente.list_database_names())
# ['sample_airbnb', 'sample_analytics', 'sample_geospatial', 'sample_guides', 'sample_mflix', 'sample_restaurants', 'sample_supplies', 'sample_training', 'sample_weatherdata', 'admin', 'local']
```

Para conectarnos a una base de datos en concreto, únicamente accederemos a ella como una propiedad del cliente:

``` python
bd = cliente.sample_mflix
bd = cliente["sample_mflix'] # tb podemos acceder como si fuera un diccionario
```

!!! tip inline end "Bases de datos y colecciones Lazy"
    Es conveniente tener en cuenta que tantos las colecciones como las bases de datos se crean y carga de forma perezosa, esto es, hasta que no realizamos una operación sobre ellas, no se accede realmente a ellas. Así pues, para crear realmente una colección, hemos de insertar un documento en ella.

Una vez tenemos la base de datos, el siguiente paso es obtener una colección:

``` python
coleccion = bd.movies
coleccion = bd["movies'] 
```

Si queremos obtener el nombre de todas las colecciones usaremos el método `list_collection_names()`:

``` python
print(bd.list_collection_names())
# ['sessions', 'theaters', 'movies', 'comments', 'users']
```

## Primeras consultas

Finalmente, sobre una colección ya podemos realizar consultas y otras operaciones:

``` python
movies = bd.movies
movies.count_documents({})
# 23530
movies.find_one()
```

Por ejemplo, podemos filtrar las películas de Salma Hayek:

``` python
movies.find( { "cast": "Salma Hayek" } )
```

``` python
# return the count of movies with "Salma Hayek" in the "cast"
movies.find( { "cast": "Salma Hayek" } ).count()
```

Para mostrar los documentos BSON, vamos a utilizar la función `dumps` que transforma el documento a JSON:

``` python
# find all movies with Salma Hayek
# then pretty print
cursor = movies.find( { "cast": "Salma Hayek" } )
from bson.json_util import dumps
print(dumps(cursor, indent=2))
```

``` python
# find all movies with Salma Hayek, but only project the "_id" and "title" fields
cursor = movies.find( { "cast": "Salma Hayek" }, { "title": 1 } )
print(dumps(cursor, indent=2))
```

``` python
# find all movies with Salma Hayek, but only project the "title" field
cursor = movies.find( { "cast": "Salma Hayek" }, { "title": 1, "_id": 0 } )
print(dumps(cursor, indent=2))
```

## Trabajando con cursores

A continuación vamos a realizar algunas operaciones sobre los [cursores](https://pymongo.readthedocs.io/en/stable/api/pymongo/cursor.html) con PyMongo y a comparar a cómo podemos realizar la misma operación mediante el motor de agregaciones.

### Limitando

Sobre el cursor podemos restringir la cantidad de resultados devueltos mediante el método `.limit()` equivalente a la agregación `$limit`:

=== "PyMongo"

    ``` python hl_lines="4"
    limited_cursor = movies.find(
        { "directors": "Sam Raimi" },
        { "_id": 0, "title": 1, "cast": 1 }
    ).limit(2)

    print(dumps(limited_cursor, indent=2))
    ```

=== "Agregación"

    ``` python hl_lines="4"
    pipeline = [
        { "$match": { "directors": "Sam Raimi" } },
        { "$project": { "_id": 0, "title": 1, "cast": 1 } },
        { "$limit": 2 }
    ]

    limited_aggregation = movies.aggregate( pipeline )

    print(dumps(limited_aggregation, indent=2))
    ```

=== "Salida"

    ``` json
    [
        {
            "cast": [
                "Bruce Campbell",
                "Ellen Sandweiss",
                "Richard DeManincor",
                "Betsy Baker"
            ],
            "title": "The Evil Dead"
        },
        {
            "title": "Evil Dead II",
            "cast": [
                "Bruce Campbell",
                "Sarah Berry",
                "Dan Hicks",
                "Kassie Wesley DePaiva"
            ]
        }
    ]
    ```

### Ordenando

Para ordenar usaremos el método `.sort()` que además de los campos de ordenación, indicaremos si el criterio será ascendente o descendente, de forma similar a como lo hacemos con la operación de agregación `$sort`:

=== "PyMongo"

    ``` python hl_lines="6"
    from pymongo import DESCENDING, ASCENDING

    sorted_cursor = movies.find(
        { "directors": "Sam Raimi" },
        { "_id": 0, "year": 1, "title": 1, "cast": 1 }
    ).sort("year", ASCENDING)

    print(dumps(sorted_cursor, indent=2))
    ```

=== "Agregación"

    ``` python hl_lines="4"
    pipeline = [
        { "$match": { "directors": "Sam Raimi" } },
        { "$project": { "_id": 0, "year": 1, "title": 1, "cast": 1 } },
        { "$sort": { "year": ASCENDING } }
    ]

    sorted_aggregation = movies.aggregate( pipeline )

    print(dumps(sorted_aggregation, indent=2))
    ```

=== "Salida"

    ``` json
    [
    {
        "cast": [
            "Bruce Campbell",
            "Ellen Sandweiss",
            "Richard DeManincor",
            "Betsy Baker"
        ],
        "title": "The Evil Dead",
        "year": 1981
    },
    {
        "year": 1987,
        "title": "Evil Dead II",
        "cast": [
            "Bruce Campbell",
            "Sarah Berry",
            "Dan Hicks",
            "Kassie Wesley DePaiva"
        ]
    },
    {
        "year": 1990,
        ...
    }
    ]
    ```

En el caso de tener una clave compuesta de ordenación, le pasaremos como parámetro una lista de tuplas clave/criterio:

=== "PyMongo"

    ``` python hl_lines="4"
    sorted_cursor = movies.find(
        { "cast": "Tom Hanks" },
        { "_id": 0, "year": 1, "title": 1, "cast": 1 }
    ).sort([("year", ASCENDING), ("title", ASCENDING)])

    print(dumps(sorted_cursor, indent=2))
    ```

=== "Agregación"

    ``` python hl_lines="4"
    pipeline = [
        { "$match": { "cast": "Tom Hanks" } },
        { "$project": { "_id": 0, "year": 1, "title": 1, "cast": 1 } },
        { "$sort": { "year": ASCENDING, "title": ASCENDING } }
    ]

    sorted_aggregation = movies.aggregate( pipeline )

    print(dumps(sorted_aggregation, indent=2))
    ```

=== "Salida"

    ``` json
    [
    {
        "cast": [
            "Tom Hanks",
            "Daryl Hannah",
            "Eugene Levy",
            "John Candy"
        ],
        "title": "Splash",
        "year": 1984
    },
    {
        "cast": [
            "Tom Hanks",
            "Jackie Gleason",
            "Eva Marie Saint",
            "Hector Elizondo"
        ],
        "title": "Nothing in Common",
        "year": 1986
    },
    {
        "cast": [
            "Tom Hanks",
            "Elizabeth Perkins",
            "Robert Loggia",
            "John Heard"
        ],
        "title": "Big",
        "year": 1988
    },
    {
        "cast": [
            "Sally Field",
            "Tom Hanks",
            "John Goodman",
            "Mark Rydell"
        ],
        "title": "Punchline",
        "year": 1988
    },
    ...
    ]
    ```

### Saltando

Cuando paginamos los resultados, para saltar los documentos, haremos uso del método `.skip()`, el cual es similar a la operación `$skip`.

Por ejemplo, la siguiente consulta devuelve 13 documentos, de manera que al saltarnos 12, sólo nos devolverá uno:

=== "PyMongo"

    ``` python hl_lines="4"
    skipped_sorted_cursor = movies.find(
        { "directors": "Sam Raimi" },
        { "_id": 0, "title": 1, "year": 1, "cast": 1 } 
    ).sort("year", ASCENDING).skip(12)
    ```

=== "Agregación"

    ``` python hl_lines="5"
    pipeline = [
        { "$match": { "directors": "Sam Raimi" } },
        { "$project": { "_id": 0, "year": 1, "title": 1, "cast": 1 } },
        { "$sort": { "year": ASCENDING } },
        { "$skip": 12 }
    ]

    sorted_skipped_aggregation = movies.aggregate( pipeline )

    print(dumps(sorted_skipped_aggregation, indent=2))
    ```

=== "Salida"

    ``` json
    [
        {
            "cast": [
                "James Franco",
                "Mila Kunis",
                "Rachel Weisz",
                "Michelle Williams"
            ],
            "title": "Oz the Great and Powerful",
            "year": 2013
        }
    ]
    ```

## Agregaciones básicas

``` python
match_stage = { "$match": { "directors": "Sam Raimi" } }
project_stage = { "$project": { "_id": 0, "title": 1, "cast": 1 } }

pipeline = [
    match_stage,
    project_stage
]

sam_raimi_aggregation = movies.aggregate( pipeline )

print(dumps(sam_raimi_aggregation, indent=2))
```

``` python
unwind_stage = { "$unwind": "$directors" }

group_stage = {
    "$group": {
        "_id": {
            "director": "$directors"
        },
        "average_rating": { "$avg": "$imdb.rating" }
    }
}

sort_stage = {
    "$sort": { "average_rating": -1 }
}

# create pipeline from four different stages
pipeline = [
    unwind_stage,
    group_stage,
    sort_stage
]

# aggregate using pipeline
director_ratings = movies.aggregate(pipeline)

# iterate through the resulting cursor
list(director_ratings)
```

* First Write
    insert_one
    update_one -> upsert
        Si ya existía , al obtener raw_result, la propiedad nModified = 0 y updatedExisting sería True

* Write Concern

``` python
db.users.with_options(write_concern=WriteConcern(w="majority")).insert_one({
    "name": name,
    "email": email,
    "password": hashedpw
})
```

* Update operations

    update_one
    update_many

    Las operaciones de modificación devuelven un UpdateResult que contiene las propiedades `aknowledge`, `matched_count`, `modified_count` y `upserted_id`.
    `modified_count` y `matched_count` serán 0 en caso de un upsert.

* Join entre movies y comments
$lookup -> from, let, pipeline, as // from, localField, foreignField, as

``` python
pipeline = [
    {
        "$match": {
            "_id": ObjectId(id)
        }
    },
    {
        "$lookup": {
            "from": 'comments',
            "let": {'id': '$_id'},
            "pipeline": [
                {'$match':
                    {'$expr': {'$eq': ['$movie_id', '$$id']}}
                    }, {"$sort":
                        {"date": -1}}
            ],
            "as": 'comments'
        }
    }
]

movie = db.movies.aggregate(pipeline).next()
```

Al hacer join, los comentarios tienen que unirse a las películas con campos de tipo ObjectId:

``` python
comment_doc = {"name": user.name, "email": user.email,
                "movie_id": ObjectId(movie_id), "text": comment, "date": date}
db.comments.insert_one(comment_doc)

db.comments.update_one(
    {"_id": ObjectId(comment_id), "email": user_email},
    {"$set": {"text": text, "date": date}}
)
```

Al crear un pool de conexiones, especificar tamaño del pool y timeout:

``` python
db = getattr(g, "_database", None)
    DB_URI = current_app.config["DB_URI"]
    DB_NAME = current_app.config["DB_NAME"]
    if db is None:
        db = g._database = MongoClient(
            DB_URI,
            maxPoolSize=50,
            wtimeout=2500
        )[DB_NAME]
    return db
```

Siempre especificar un `wtimemout` con se realiza una escritura con un una mayoría de escrituras, por si fallase algún nodo, no se quedase colgado esperando.

db.users.with_options(write_concern=WriteConcern(w="majority"), wtimeout=5000).insert_one({
    "name": name,
    "email": email,
    "password": hashedpw
})

Siempre configurar y capturar los errores de tipo `serverSelectionTimeout`.

DuplicateKeyError puede saltar en _id y en otros campos si creamos un índice *unique*.

Principio de "menos privilegios".

## Referencias

<https://www.askpython.com/python-modules/python-mongodb>

* [Tutorial oficial de PyMongo](https://pymongo.readthedocs.io/en/stable/tutorial.html)

## Actividades
