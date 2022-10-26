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


FIXME: Preferencia de lectura y escritura

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


## Mastering MongodB

https://learning.oreilly.com/library/view/mastering-mongodb-6-x/9781803243863/B18155_02.xhtml#_idParaDest-53

Connecting using Python
A strong contender to Ruby and Rails is Python and Django. Similar to Mongoid, there is MongoEngine and an official MongoDB low-level driver, PyMongo.

Installing PyMongo can be done using pip or easy_install, as shown in the following code:

python -m pip install pymongo

python -m easy_install pymongo

Then, in our class, we can connect to a database, as shown in the following example:

>>> from pymongo import MongoClient

>>> client = MongoClient()

Connecting to a replica set requires a set of seed servers for the client to find out what the primary, secondary, or arbiter nodes in the set are, as indicated in the following example:

client = pymongo.MongoClient('mongodb://user:passwd@node1:p1,node2:p2/?replicaSet=rsname')

Using the connection string URL, we can pass a username and password and the replicaSet name all in a single string. Some of the most interesting options for the connection string URL are presented in the next section.

Connecting to a shard requires the server host and IP for the MongoDB router, which is the MongoDB process.

PyMODM ODM
Similar to Ruby’s Mongoid, PyMODM is an ODM for Python that follows Django’s built-in ORM closely. Installing pymodm can be done via pip, as shown in the following code:

pip install pymodm

Then, we need to edit settings.py and replace the ENGINE database with a dummy database, as shown in the following code:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy'
    }
}
Then we add our connection string anywhere in settings.py, as shown in the following code:

from pymodm import connect
connect("mongodb://localhost:27017/myDatabase", alias="MyApplication")
Here, we have to use a connection string that has the following structure:

mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
Options have to be pairs of name=value with an & between each pair. Some interesting pairs are shown in the following table:

Table 2.3 – PyMODM configuration options
Table 2.3 – PyMODM configuration options

Model classes need to inherit from MongoModel. The following code shows what a sample class will look like:

from pymodm import MongoModel, fields
class User(MongoModel):
    email = fields.EmailField(primary_key=True)
    first_name = fields.CharField()
    last_name = fields.CharField()
This has a User class with first_name, last_name, and email fields, where email is the primary field.

Inheritance with PyMODM models
Handling one-to-one and one-to-many relationships in MongoDB can be done using references or embedding. The following example shows both ways, which are references for the model user and embedding for the comment model:

from pymodm import EmbeddedMongoModel, MongoModel, fields
 
class Comment(EmbeddedMongoModel):
    author = fields.ReferenceField(User)
    content = fields.CharField()
 
class Post(MongoModel):
    title = fields.CharField()
    author = fields.ReferenceField(User)
    revised_on = fields.DateTimeField()
    content = fields.CharField()
    comments = fields.EmbeddedDocumentListField(Comment)
Similar to Mongoid for Ruby, we can define relationships as being embedded or referenced depending on our design decision.


## CRUD

https://learning.oreilly.com/library/view/mastering-mongodb-6-x/9781803243863/B18155_05.xhtml#_idParaDest-92

CRUD using the Python driver
PyMongo is the officially supported driver for Python by MongoDB. In this section, we will use PyMongo to create, read, update, and delete documents in MongoDB.

Creating and deleting data
The Python driver provides methods for CRUD just like Ruby and PHP. Following on from Chapter 2, Schema Design and Data Modeling, and the books variable that points to our books collection, we will write the following code block:

from pymongo import MongoClient
from pprint import pprint
>>> book = {
 'isbn': '301',
 'name': 'Python and MongoDB',
 'price': 60
}
>>> insert_result = books.insert_one(book)
>>> pprint(insert_result)
<pymongo.results.InsertOneResult object at 0x104bf3370>
>>> result = list(books.find())
>>> pprint(result)
[{u'_id': ObjectId('592149c4aabac953a3a1e31e'),
 u'isbn': u'101',
 u'name': u'Mastering MongoDB',
 u'price': 30.0,
 u'published': datetime.datetime(2017, 6, 25, 0, 0)},
{u'_id': ObjectId('59214bc1aabac954263b24e0'),
 u'isbn': u'102',
 u'name': u'MongoDB in 7 years',
 u'price': 50.0,
 u'published': datetime.datetime(2017, 6, 26, 0, 0)},
{u'_id': ObjectId('593c24443c8ca55b969c4c54'),
 u'isbn': u'201',
 u'meta': {u'authors': u'alex giamas'},
 u'name': u'Mastering MongoDB, 3rd Edition'},
{u'_id': ObjectId('594061a9aabac94b7c858d3d'),
 u'isbn': u'301',
 u'name': u'Python and MongoDB',
 u'price': 60}]
In the previous example, we used insert_one() to insert a single document, which we can define using the Python dictionary notation; we can then query it for all the documents in the collection.

The resulting object for insert_one and insert_many has two fields of interest:

Acknowledged: A Boolean that is true if the insert has succeeded and false if it hasn’t, or if the write concern is 0 (a fire and forget write).
inserted_id for insert_one: The ObjectId property of the written document and the inserted_id properties for insert_many. This is the array of ObjectIds of the written documents.
We used the pprint library to pretty-print the find() results. The built-in way to iterate through the result set is by using the following code:

for document in results:
   print(document)
Deleting documents works in a similar way to creating them. We can use delete_one to delete the first instance or delete_many to delete all instances of the matched query:

>>> result = books.delete_many({ "isbn": "101" })
>>> print(result.deleted_count)
1
The deleted_count instance tells us how many documents were deleted; in our case, it is 1, even though we used the delete_many method.

To delete all documents from a collection, we can pass in the empty document, {}.

To drop a collection, we can use drop():

>>> books.delete_many({})
>>> books.drop()
Finding documents
To find documents based on top-level attributes, we can simply use a dictionary:

>>> books.find({"name": "Mastering MongoDB"})
[{u'_id': ObjectId('592149c4aabac953a3a1e31e'),
 u'isbn': u'101',
 u'name': u'Mastering MongoDB',
 u'price': 30.0,
 u'published': datetime.datetime(2017, 6, 25, 0, 0)}]
To find documents in an embedded document, we can use dot notation. In the following example, we are using meta.authors to access the authors embedded document inside the meta document:

>>> result = list(books.find({"meta.authors": {"$regex": "aLEx", "$options": "i"}}))
>>> pprint(result)
[{u'_id': ObjectId('593c24443c8ca55b969c4c54'),
 u'isbn': u'201',
 u'meta': {u'authors': u'alex giamas'},
 u'name': u'Mastering MongoDB, 3rd Edition'}]
In this example, we used a regular expression to match aLEx, which is case insensitive, in every document where the string is mentioned in the meta.authors embedded document. PyMongo uses this notation for regular expression queries, called the $regex notation in MongoDB documentation. The second parameter is the options parameter for $regex, which we will explain in detail in the Using regular expressions section later in this chapter.

Comparison operators are also supported, and a full list of these is given in the Comparison operators section, later in this chapter:

>>> result = list(books.find({ "price": {  "$gt":40 } }))
>>> pprint(result)
[{u'_id': ObjectId('594061a9aabac94b7c858d3d'),
 u'isbn': u'301',
 u'name': u'Python and MongoDB',
 u'price': 60}]
Let’s add multiple dictionaries to our query results in a logical AND query:

>>> result = list(books.find({"name": "Mastering MongoDB", "isbn": "101"}))
>>> pprint(result)
[{u'_id': ObjectId('592149c4aabac953a3a1e31e'),
 u'isbn': u'101',
 u'name': u'Mastering MongoDB',
 u'price': 30.0,
 u'published': datetime.datetime(2017, 6, 25, 0, 0)}]
For books that have both isbn=101 and name=Mastering MongoDB, to use logical operators such as $or and $and, we must use the following syntax:

>>> result = list(books.find({"$or": [{"isbn": "101"}, {"isbn": "102"}]}))
>>> pprint(result)
[{u'_id': ObjectId('592149c4aabac953a3a1e31e'),
 u'isbn': u'101',
 u'name': u'Mastering MongoDB',
 u'price': 30.0,
 u'published': datetime.datetime(2017, 6, 25, 0, 0)},
{u'_id': ObjectId('59214bc1aabac954263b24e0'),
 u'isbn': u'102',
 u'name': u'MongoDB in 7 years',
 u'price': 50.0,
 u'published': datetime.datetime(2017, 6, 26, 0, 0)}]
For books that have an isbn value of 101 or 102, if we want to combine the AND and OR operators, we must use the $and operator, as follows:

>>> result = list(books.find({"$or": [{"$and": [{"name": "Mastering MongoDB", "isbn": "101"}]}, {"$and": [{"name": "MongoDB in 7 years", "isbn": "102"}]}]}))
>>> pprint(result)
[{u'_id': ObjectId('592149c4aabac953a3a1e31e'),
 u'isbn': u'101',
 u'name': u'Mastering MongoDB',
 u'price': 30.0,
 u'published': datetime.datetime(2017, 6, 25, 0, 0)},
{u'_id': ObjectId('59214bc1aabac954263b24e0'),
 u'isbn': u'102',
 u'name': u'MongoDB in 7 years',
 u'price': 50.0,
 u'published': datetime.datetime(2017, 6, 26, 0, 0)}]
For a result of OR between two queries, consider the following:

The first query is asking for documents that have isbn=101 AND name=Mastering MongoDB
The second query is asking for documents that have isbn=102 AND name=MongoDB in 7 years
The result is the union of these two datasets
Updating documents
In the following code block, you can see an example of updating a single document using the update_one helper method.

This operation matches one document in the search phase and modifies one document based on the operation to be applied to the matched documents:

>>> result = books.update_one({"isbn": "101"}, {"$set": {"price": 100}})
>>> print(result.matched_count)
1
>>> print(result.modified_count)
1
In a similar way to inserting documents, when updating documents, we can use update_one or update_many:

The first argument here is the filter document for matching the documents that will be updated
The second argument is the operation to be applied to the matched documents
The third (optional) argument is to use upsert=false (the default) or true, which is used to create a new document if it’s not found
Another interesting argument is bypass_document_validation=false (the default) or true, which is optional. This will ignore validations (if there are any) for the documents in the collection.

The resulting object will have matched_count for the number of documents that matched the filter query, and modified_count for the number of documents that were affected by the update part of the query.

In our example, we are setting price=100 for the first book with isbn=101 through the $set update operator. A list of all update operators can be found in the Update operators section later in this chapter.

NOTE

If we don’t use an update operator as the second argument, the contents of the matched document will be entirely replaced by the new document.

CRUD using PyMODM
PyMODM is a core ODM that provides simple and extensible functionality. It is developed and maintained by MongoDB’s engineers who get fast updates and support for the latest stable version of MongoDB available.

In Chapter 2, Schema Design and Data Modeling, we explored how to define different models and connect to MongoDB. CRUD, when using PyMODM, as with every ODM, is simpler than when using low-level drivers.

Creating documents
A new user object, as defined in Chapter 2, Schema Design and Data Modeling, can be created with a single line:

>>> user = User('alexgiamas@packt.com', 'Alex', 'Giamas').save()
In this example, we used positional arguments in the same order that they were defined in the user model to assign values to the user model attributes.

We can also use keyword arguments or a mix of both, as follows:

>>> user = User(email='alexgiamas@packt.com', 'Alex', last_name='Giamas').save()
Bulk saving can be done by passing in an array of users to bulk_create():

>>> users = [ user1, user2,...,userN]
>>>  User.bulk_create(users)
Updating documents
We can modify a document by directly accessing the attributes and calling save() again:

>>> user.first_name = 'Alexandros'
>>> user.save()
If we want to update one or more documents, we must use raw() to filter out the documents that will be affected and chain update() to set the new values:

>>> User.objects.raw({'first_name': {'$exists': True}})
              .update({'$set': {'updated_at': datetime.datetime.now()}})
In the preceding example, we search for all User documents that have a first name and set a new field, updated_at, to the current timestamp. The result of the raw() method is QuerySet, a class used in PyMODM to handle queries and work with documents in bulk.

Deleting documents
Deleting an API is similar to updating it – by using QuerySet to find the affected documents and then chaining on a .delete() method to delete them:

>>> User.objects.raw({'first_name': {'$exists': True}}).delete()
Querying documents
Querying is done using QuerySet, as described previously.

Some of the convenience methods that are available include the following:

all()
count()
first()
exclude(*fields): To exclude some fields from the result
only(*fields): To include only some fields in the result (this can be chained for a union of fields)
limit(limit)
order_by(ordering)
reverse(): If we want to reverse the order_by() order
skip(number)
values(): To return Python dict instances instead of model instances
By using raw(), we can use the same queries that we described in the previous PyMongo section for querying and still exploit the flexibility and convenience methods provided by the ODM layer.

## Change Streams

https://learning.oreilly.com/library/view/mastering-mongodb-6-x/9781803243863/B18155_05.xhtml#_idParaDest-98

Change streams
The change streams functionality was introduced in version 3.6 and updated in versions 4.0 and 5.1, making it a safe and efficient way to listen for database changes.

Introduction
The fundamental problem that change streams solve is the need for applications to react immediately to changes in the underlying data. Modern web applications need to be reactive to data changes and refresh the page view without reloading the entire page. This is one of the problems that frontend frameworks (such as Angular, React, and Vue.js) are solving. When a user performs an action, the frontend framework will submit the request to the server asynchronously and refresh the relevant fragment of the page based on the response from the server.

Thinking of a multiuser web application, there are cases where a database change may have occurred as a result of another user’s action. For example, in a project management Kanban board, user A may be viewing the Kanban board, while another user, B, may be changing the status of a ticket from “To do” to “In progress.”

User A’s view needs to be updated with the change that user B has performed in real time, without refreshing the page. There are already three approaches to this problem, as follows:

The most simple approach is to poll the database every X number of seconds and determine if there has been a change. Usually, this code will need to use some kind of status, timestamp, or version number to avoid fetching the same change multiple times. This is simple, yet inefficient, as it cannot scale with a great number of users. Having thousands of users polling the database at the same time will result in a high database-locking rate.
To overcome the problems imposed by the first approach, database-and application-level triggers have been implemented. A database trigger relies on the underlying database executing some code in response to a database change. However, the main downside is, again, similar to the first approach in that the more triggers that we add to a database, the slower our database will become. It is also coupled to the database, instead of being a part of the application code base.
Finally, we can use the database transaction or replication log to query for the latest changes and react to them. This is the most efficient and scalable approach of the three as it doesn’t put a strain on the database. The database writes to this log anyway; it is usually appended only and our background task serially reads entries as they come into the log. The downside of this method is that it is the most complicated one to implement and one that can lead to nasty bugs if it’s not implemented properly.
Change streams provide a way to solve this problem that is developer-friendly and easy to implement and maintain. Change streams are based on the oplog, which is MongoDB’s operations log and contains every operation happening server-wide across all databases on the server. This way, the developer does not have to deal with the server-wide oplog or tailable cursors, which are often not exposed or as easy to develop from the MongoDB language-specific drivers. Also, the developer does not have to decipher and understand any of the internal oplog data structures that are designed and built for MongoDB’s benefit, and not for an application developer.

Change streams also have other advantages around security:

Users can only create change streams on collections, databases, or deployments that they have read access to.
Change streams are also idempotent by design. Even in the case that the application cannot fetch the absolute latest change stream event notification ID, it can resume applying from an earlier known one and it will eventually reach the same state.
Finally, change streams are resumable. Every change stream response document includes a resume token. If the application gets out of sync with the database, it can send the latest resume token back to the database and continue processing from there. This token needs to be persisted in the application, as the MongoDB driver won’t keep application failures and restarts. It will only keep state and retry in case of transient network failures and MongoDB replica set elections.
Setup 
A change stream can be opened against a collection, a database, or an entire deployment (such as a replica set or sharded cluster). A change stream will not react to changes in any system collection or any collection in the admin, config, and local databases.

A change stream requires a WiredTiger storage engine and replica set protocol version 1 (pv1). pv1 is the only supported version starting from MongoDB 4.0. Change streams are compatible with deployments that use encryption-at-rest.

Using change streams
To use a change stream, we need to connect to our replica set. A replica set is a prerequisite to using change streams. As change streams internally use the oplog, it’s not possible to work without it. Change streams will also output documents that won’t be rolled back in a replica set setting, so they need to follow a majority read concern. Either way, it’s a good practice to develop and test locally using a replica set, as this is the recommended deployment for production. As an example, we are going to use a signals collection within our database named streams.

We will use the following sample Python code:

from pymongo import MongoClient
class MongoExamples:
   def __init__(self):
       self.client = MongoClient('localhost', 27017)
       db = self.client.streams
       self.signals = db.signals
   # a basic watch on signals collection
   def change_books(self):
       with self.client.watch() as stream:
           for change in stream:
               print(change)
def main():
   MongoExamples().change_books()
if __name__ == '__main__':
   main()
We can open one Terminal and run it using python change_streams.py.

Then, in another Terminal, we connect to our MongoDB replica set using the following code:

> mongo

> use streams

> db.signals.insert({value: 114.3, signal:1})

Going back to our first Terminal window, we can now observe that the output is similar to the following code block:

{'_id': {'_data': '825BB7A25E0000000129295A1004A34408FB07864F8F960BF14453DFB98546645F696400645BB7A25EE10ED33145BCF7A70004'}, 'operationType': 'insert', 'clusterTime': Timestamp(1538761310, 1), 'fullDocument': {'_id': ObjectId('5bb7a25ee10ed33145bcf7a7'), 'value': 114.3, 'signal': 1.0}, 'ns': {'db': 'streams', 'coll': 'signals'}, 'documentKey': {'_id': ObjectId('5bb7a25ee10ed33145bcf7a7')}}

Here, we have opened a cursor that’s watching the entire streams database for changes. Every data update in our database will be logged and outputted in the console.

For example, if we go back to the mongo shell, we can issue the following code:

> db.a_random_collection.insert({test: 'bar'})

The Python code output should be similar to the following code:

{'_id': {'_data': '825BB7A3770000000229295A10044AB37F707D104634B646CC5810A40EF246645F696400645BB7A377E10ED33145BCF7A80004'}, 'operationType': 'insert', 'clusterTime': Timestamp(1538761591, 2), 'fullDocument': {'_id': ObjectId('5bb7a377e10ed33145bcf7a8'), 'test': 'bar'}, 'ns': {'db': 'streams', 'coll': 'a_random_collection'}, 'documentKey': {'_id': ObjectId('5bb7a377e10ed33145bcf7a8')}}

This means that we are getting notifications for every data update across all the collections in our database.

Now, we can change line 11 of our code to the following:

> with self.signals.watch() as stream:

This will result in only watching the signals collection, as should be the most common use case.

PyMongo’s watch command can take several parameters, as follows:

watch(pipeline=None, full_document='default', resume_after=None, max_await_time_ms=None, batch_size=None, collation=None, start_at_operation_time=None, session=None)

The most important parameters are as follows:

Pipeline: This is an optional parameter that we can use to define an aggregation pipeline to be executed on each document that matches watch(). Because the change stream itself uses the aggregation pipeline, we can attach events to it. The aggregation pipeline events we can use are as follows:
$match

$project

$addFields

$replaceRoot

$redact

$replaceWith

$set

$unset

Full_document: This is an optional parameter that we can use by setting it to 'updateLookup' to force the change stream to return a copy of the document as it has been modified in the fullDocument field, along with the document’s delta in the updateDescription field. The default None value will only return the document’s delta.
start_at_operation_time: This is an optional parameter that we can use to only watch for changes that occurred at, or after, the specified timestamp.
session: This is an optional parameter in case our driver supports passing a ClientSession object to watch for updates.
Change streams response documents have to be under 16 MB in size. This is a global limit in MongoDB for BSON documents and the change stream has to follow this rule.

Specification
The following document shows all of the possible fields that a change event response may or may not include, depending on the actual change that happened:

{  _id : { <BSON Object> },
  "operationType" : "<operation>",
  "fullDocument" : { <document> },
  "ns" : {
     "db" : "<database>",
     "coll" : "<collection"
  },
  "documentKey" : { "_id" : <ObjectId> },
  "updateDescription" : {
     "updatedFields" : { <document> },
     "removedFields" : [ "<field>", ... ]
  }
  "clusterTime" : <Timestamp>,
  "txnNumber" : <NumberLong>,
  "lsid" : {
     "id" : <UUID>,
     "uid" : <BinData>
  }
}
The most important fields are as follows:

Table 5.6 – Change streams – the most common events
Table 5.6 – Change streams – the most common events

Important notes
When using a sharded database, change streams need to be opened against a MongoDB server. When using replica sets, a change stream can only be opened against any data-bearing instance. Each change stream will open a new connection, as of 4.0.2. If we want to have lots of change streams in parallel, we need to increase the connection pool (as per the SERVER-32946 JIRA MongoDB ticket) to avoid severe performance degradation.

Production recommendations
Let’s look at some of the best recommendations by MongoDB and expert architects at the time of writing.

Replica sets
Starting from MongoDB 4.2, a change stream can still be available even if the Read Concern of the majority is not satisfied. The way to enable this behavior is by setting { majority : false }.

Invalidating events, such as dropping or renaming a collection, will close the change stream. We cannot resume a change stream after an invalidating event closes it.

As the change stream relies on the oplog size, we need to make sure that the oplog size is large enough to hold events until they are processed by the application.

We can open a change stream operation against any data-bearing member in a replica set.

Sharded clusters
On top of the considerations for replica sets, there are a few more to keep in mind for sharded clusters. They are as follows:

The change stream is executed against every shard in a cluster and will be as fast as the slowest shard
To avoid creating change stream events for orphaned documents, we need to use the new feature of ACID-compliant transactions if we have multi-document updates under sharding
We can only open a change stream operation against the mongos member in a sharded cluster.

While sharding an unsharded collection (that is, migrating from a replica set to sharding), the documentKey property of the change stream notification document will include _id until the change stream catches up to the first chunk migration.

## Referencias

<https://www.askpython.com/python-modules/python-mongodb>

* [Tutorial oficial de PyMongo](https://pymongo.readthedocs.io/en/stable/tutorial.html)

## Actividades

https://learning.oreilly.com/library/view/mastering-mongodb-6-x/9781803243863/B18155_06.xhtml#_idParaDest-111