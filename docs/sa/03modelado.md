---
title: Modelado NoSQL
description: asdf
---

things you need to keep in the back of your mind before you model:

The document model lets, and encourages, you to keep information that is used together inside one single document.
Atomicity, consistency, isolation, and durability (ACID) can be implemented by leveraging the document model, which is preferred, or by using MongoDB transactions.
Making early decisions and compromises about very large datasets will help make the data more manageable. For example, deleting or archiving documents after a given period of time may reduce the resources needed for the project.
Using a distributed system, like MongoDB, means that data can be written and read on servers all over the world. Carefully planning the location of the servers will improve performance and resilience of the applications.

1. Definir la carga (*workload*):

    * Comprender para qué operaciones estamos modelando
    * Cuantificar y calificar las operaciones de lectura y escritura
    * Listar las operaciones más importantes

    Diferentes cargas pueden provocar diferentes soluciones de modelado.

2. Modelar las relaciones
    * de forma similar a los modelos relacionales, las relaciones 1:1, 1:M y N:M.
    * Las relaciones 1:1 normalmente se modelan con un documento embebido
    * las relaciones 1:M y N:M mediante un array de documentos o referencias a documentos de otra colección.
    * El hecho de decidir si utilizar un documento embebido o crear un enlace entre diferentes documentos es la decisión más crítica a la hora de modelar.

3. Reconocer y Aplicar patrones de diseño
    * Ofrecen transformaciones sobre el esquema, que se centran en el rendimiento, mantenimiento o simplificación de los requisitos.

MongoDB es una base de datos documental, no relacional, donde el esquema no se debe basar en el uso de claves ajenas/joins, ya que no existen.

A la hora de diseñar un esquema, si nos encontramos que el esquema esta en 3FN o si cuando hacemos consultas (recordad que no hay joins) estamos teniendo que realizar varias consultas de manera programativa (primero acceder a una tabla, con ese _id ir a otra tabla, etc…​.) es que no estamos siguiendo el enfoque adecuado.

MongoDB no soporta transacciones, ya que su enfoque distribuido dificultaría y penalizaría el rendimiento. En cambio, sí que asegura que las operaciones sean atómicas. Los posibles enfoques para solucionar la falta de transacciones son:

1. Restructurar el código para que toda la información esté contenida en un único documento.
2. Implementar un sistema de bloqueo por software (semáforo, etc…​).
3. Tolerar un grado de inconsistencia en el sistema.

Dependiendo del tipo de relación entre dos documentos, normalizaremos los datos para minimizar la redundancia pero manteniendo en la medida de lo posible que mediante operaciones atómicas se mantenga la integridad de los datos. Para ello, bien crearemos referencias entre dos documentos o embeberemos un documento dentro de otro.

## Relacionando documentos

Las aplicaciones que emplean MongoDB utilizan dos técnicas para relacionar documentos:

* Referencias *Manuales*
* Uso de *DBRef*

### Referencias manuales

De manera similar a una base de datos relacional, se almacena el campo `_id` de un documento en otro documento a modo de clave ajena. De este modo, la aplicación realiza una segunda consulta para obtener los datos relacionados. Estas referencias son sencillas y suficientes para la mayoría de casos de uso.

<figure style="align: center;">
    <img src="images/03data-model-normalized.png" width="500px">
    <figcaption>Referencias manuales</figcaption>
</figure>

Por ejemplo, si nos basamos en el gráfico anterior, podemos conseguir referenciar manualmente estos objetos del siguiente modo:

``` js
var idUsuario = ObjectId();

db.usuario.insert({
  _id: idUsuario,
  nombre: "123xyz"
});

db.contacto.insert({
  usuario_id: idUsuario,
  telefono:  "123 456 7890",
  email: "xyz@ejemplo.com"
});
```

FIXME: Para relacionar los dos documentos, haremos uso de la operación [`$lookup`](https://www.mongodb.com/docs/manual/reference/operator/aggregation/lookup/) para hacer el *join*, o haremos una segunda consulta para la segunda colección.

FIXME: poner código

### DBRef

Son referencias de un documento a otro mediante el valor del campo `_id`, el nombre de la colección y, opcionalmente, el nombre de la base de datos. Estos objetos siguen una convención para representar un documento mediante la notación `{ "$ref" : <nombreColeccion>, "$id" : <valorCampo_id>, "$db" : <nombreBaseDatos> }`.

Al incluir estos nombres, las *DBRef* permite referenciar documentos localizados en diferentes colecciones.

Así pues, si reescribimos el código anterior mediante *DBRef* tendríamos que el contacto queda de la siguiente manera:

``` js
db.contacto.insert({
  usuario_id: new DBRef("usuario", idUsuario),
  telefono:  "123-456-7890",
  email: "xyz@example.com"
});
```

De manera similar a las referencias manuales, mediante consultas adicionales se obtendrán los documentos referenciados.

Muchos drivers (incluido el de Python, mediante la clase [DBRef](https://pymongo.readthedocs.io/en/stable/api/bson/dbref.html)) contienen métodos auxiliares que realizan las consultas con referencias DBRef automáticamennte.

Desde la propia documentación de *MongoDB* recomiendan el uso de referencias manuales y el uso de `$lookup`, a no ser que dispongamos documentos de una colección que referencian a documentos que se encuentran en varias colecciones diferentes.

## Datos embebidos

En cambio, si dentro de un documento almacenamos los datos mediante sub-documentos, ya sea dentro de un atributo o un array, podremos obtener todos los datos mediante un único acceso, sin necesidad de claves ajenas ni comprobaciones de integridad referencial.

<figure style="align: center;">
    <img src="images/03data-model-denormalized.png" width="500px">
    <figcaption>Datos embebidos</figcaption>
</figure>

Generalmente, emplearemos datos embebidos cuando tengamos:

* relaciones "contiene" entre entidades, entre relaciones de documentos "uno a uno" o "uno a pocos".
* relaciones "uno a muchos" entre entidades. En estas relaciones los documentos hijo (o "muchos") siempre aparecen dentro del contexto del padre o del documento "uno".

Los datos embebidos ofrecen mejor rendimiento al permitir obtener los datos mediante una única operación, así como modificar datos relacionados en una sola operación atómica de escritura.

Un aspecto a tener en cuenta es que un documento BSON puede contener un máximo de 16MB. Si quisiéramos que un atributo contenga más información, tendríamos que utilizar el API de GridFS.

## Relaciones

Vamos a estudiar en detalle cada uno de los tipos de relaciones, para intentar clarificar cuando es conveniente utilizar referencias o datos embebidos.

### 1:1

Cuando existe una relación 1:1, como pueda ser entre Persona y Curriculum, o Persona y Direccion hay que embeber un documento dentro del otro, como parte de un atributo.

Ejemplo relación 1:1 - Persona/Dirección

``` js
{
  nombre: "Aitor",
  edad: 38,
  direccion: {
    calle: "Mayor",
    ciudad: "Elx"
  }
}
```

La principal ventaja de este planteamiento es que mediante una única consulta podemos obtener tanto los detalles del usuario como su dirección.

Un par de aspectos que nos pueden llevar a no embeberlos son:

la frecuencia de acceso. Si a uno de ellos se accede raramente, puede que convenga tenerlos separados para liberar memoria.

el tamaño de los elementos. Si hay uno que es mucho más grande que el otro, o uno lo modificamos muchas más veces que el otro, para que cada vez que hagamos un cambio en un documento no tengamos que modificar el otro será mejor separarlos en documentos separados.

Pero siempre teniendo en cuenta la atomicidad de los datos, ya que si necesitamos modificar los dos documentos al mismo tiempo, tendremos que embeber uno dentro del otro.

### 1:N

Vamos a distinguir dos tipos:

* **1 a muchos**, como puede ser entre Editorial y Libro. Para este tipo de relación es mejor usar referencias entre los documentos colocando la referencia en el lado del muchos:

Ejemplo relación 1:N - Editorial

``` js
{
  _id: 1,
  nombre: "O'Reilly",
  pais: "EE.UU."
}
```

Ejemplo relación 1:N - Libro

``` js
{
  _id: 1234,
  titulo: "MongoDB: The Definitive Guide",
  autor: [ "Kristina Chodorow", "Mike Dirolf" ],
  numPaginas: 216,
  editorial_id: 1,
}
{
  _id: 1235,
  titulo: "50 Tips and Tricks for MongoDB Developer",
  autor: "Kristina Chodorow",
  numPaginas: 68,
  editorial_id: 1,
}
```

* **1 a pocos**, como por ejemplo, dentro de un blog, la relación entre Mensaje y Comentario. En este caso, la mejor solución es crear un array dentro de la entidad 1 ( en nuestro caso, Mensaje). De este modo, el Mensaje contiene un array de Comentario:

Ejemplo relación 1:N - Mensaje/Comentario

``` js
{
  titulo: "La broma asesina",
  url: "http://es.wikipedia.org/wiki/Batman:_The_Killing_Joke",
  texto: "La dualidad de Batman y Joker",
  comentarios: [
    {
      autor: "Bruce Wayne",
      fecha: ISODate("2015-04-01T09:31:32Z"),
      comentario: "A mi me encantó"
    },
    {
      autor: "Bruno Díaz",
      fecha: ISODate("2015-04-03T10:07:28Z"),
      comentario: "El mejor"
    }
  ]
}
```

Hay que tener siempre en mente la restricción de los 16 MB de BSON. Si vamos a embeber muchos documentos y estos son grandes, hay que vigilar no llegar a dicho tamaño.
En ocasiones las relaciones 1 a muchos se traducen en documentos embebidos cuando la información que nos interesa es la que contiene en un momento determinado. Por ejemplo, dentro de Pedido, el precio de los productos debe embeberse, ya que si en un futuro se modifica el precio de un producto determinado debido a una oferta, el pedido realizado no debe modificar su precio total.

Del mismo modo, al almacenar la dirección de una persona, también es conveniente embeberla. No queremos que la dirección de envío de un pedido se modique si un usuario modifica sus datos personales.

### N:M

Más que relaciones muchos a muchos, suelen ser relaciones pocos a pocos, como por ejemplo, Libro y Autor, o Profesor y Estudiante.

Supongamos que tenemos libros de la siguiente manera y autores con la siguiente estructura:

Ejemplo relación N:N - Libro

``` js
{
  _id: 1,
  titulo: "La historia interminable",
  anyo: 1979
}
```

Ejemplo relación N:M - Autor

``` js
{
  _id: 1,
  nombre: "Michael Ende",
  pais: "Alemania"
}
```

Podemos resolver estas relaciones de tres maneras:

1. Siguiendo un enfoque relacional, empleando un documento como la entidad que agrupa con referencias manuales a los dos documentos.

    Ejemplo relación N:M - Autor/Libro

    ```  js
    {
    autor_id: 1,
    libro_id: 1
    }
    ```

    Este enfoque se desaconseja porque necesita tres consultas para obtener toda la información.

2. Mediante 2 documentos, cada uno con un array que contenga los ids del otro documento (2 Way Embedding). Hay que tener cuidado porque podemos tener problemas de inconsistencia de datos si no actualizamos correctamente.

    Ejemplo relación N:N - Libro referencia a Autor

    ``` js
    {
    _id: 1,
    titulo: "La historia interminable",
    anyo: 1979,
    autores: [1]
    },{
    _id: 2,
    titulo: "Momo",
    anyo: 1973,
    autores: [1]
    }
    ```

    Ejemplo relación N:M - Autor referencia a Libro

    ``` js
    {
    _id: 1,
    nombre: "Michael Ende",
    pais: "Alemania",
    libros: [1,2]
    }
    ```

3. Embeber un documento dentro de otro (One Way Embedding). Por ejemplo:

    Ejemplo relación N:M - Autor embebido en Libro

    ``` js
    {
        _id: 1,
        titulo: "La historia interminable",
        anyo: 1979,
        autores: [{nombre:"Michael Ende", pais:"Alemania"}]
    },{
        _id: 2,
        titulo: "Momo",
        anyo: 1973,
        autores: [{nombre:"Michael Ende", pais:"Alemania"}]
    }
    ```

    En principio este enfoque no se recomienda porque el documento puede crecer mucho y provocar anomalías de modificaciones donde la información no es consistente. Si se opta por esta solución, hay que tener en cuenta que si un documento depende de otro para su creación (por ejemplo, si metemos los profesores dentro de los estudiantes, no vamos a poder dar de alta a profesores sin haber dado de alta previamente a un alumno).

A modo de resumen, en las relaciones N:M, hay que establecer el tamaño de N y M. Si N como máximo vale 3 y M 500000, entonces deberíamos seguir un enfoque de embeber la N dentro de la M (One Way Embedding).

En cambio, si N vale 3 y M vale 5, entonces podemos hacer que ambos embeban al otro documento (Two Way Embedding).

!!! tip "Rendimiento e Integridad"
    A modo de resumen, embeber documentos ofrece un mejor rendimiento que referenciar, ya que con una única operación (ya sea una lectura o una escritura) podemos acceder a varios documentos.

Más información en <http://docs.mongodb.org/manual/applications/data-models-relationships/>

## Jerárquicas

Si tenemos que modelar alguna entidad que tenga hijos y nos importa las relaciones padre-hijos (categoría-subcategoría), podemos tanto embeber un array con los hijos de un documento (children), como embeber un array con los padres de un documento (ancestors)

Más información en <http://docs.mongodb.org/manual/applications/data-models-tree-structures/>

## Patrones

<https://www.mongodb.com/blog/post/building-with-patterns-a-summary>

<https://www.mongodb.com/developer/products/mongodb/schema-design-anti-pattern-summary/>

<figure style="align: center;">
    <img src="images/03patterns.png">
    <figcaption>Patrones y Casos de Uso - mongodb.com</figcaption>
</figure>

### Duplicidad, caducidad e integridad

### Attribute Pattern

### Extended Reference Pattern

In this case, the Extended Reference Pattern will easily take care of the additional queries our application is making. To implement the pattern we can modify the inventory item documents by adding frequently-accessed order data directly to them. This will result in lowering the number of related queries on the orders collection, since the relevant data about the orders will now be part of the inventory item documents.

### Subset Pattern

### Computed Pattern

En vez de calcular un dato agregado en cada lectura, en una colección aparte se guardan los datos calculados, de manera que cuando llega un nuevo registro, se recalcula este valor y se modifica el documento oportuno.

Tiene sentido en aplicaciones donde hay muchas más lecturas que escrituras.

The Computed Pattern allows your application to calculate values at write time. In this case, the sum of the number of views would be calculated in a rolling fashion by book genre.

### Bucket Pattern

Agrupar los datos por fecha o categoría para reducir la cantidad de documentos o el tamaño de los mismos.

The Bucket pattern allows us to record data in hour interval documents, which can then be stored in yearly collections. This makes it easy to store, analyze, and purge the data within the given time requirements.

### Schema Versioning Pattern

Añade un atributo schema_version para indicar que versión del esquema cumplen los datos.
Permite evitar downtime al realizar la actualización del esquema

This pattern allows for the application to quickly identify which document structure it is dealing with, the old one or the new. This helps to minimize downtime for the application user, while allowing the database to smoothly transition to the new schema.

### Tree Pattern

Representación de datos jerárquicos.

Referencias de hijos, padre, array de *ancestors*, *materilized paths*.

### Polymorphic Pattern

The problem states that bodegas sell a variety of items from different categories, with different purposes and properties. In this case, the Polymorphic Pattern will be the best candidate to catalog this set of goods.

!!! note "Otros patrones"
  asdf

## Validación de esquemas

Aunque los esquemas son dinámicos y podemos añadir nuevos campos confome evoluciona nuestro modelo, podemos validar los esquemas para:

* asegurar la existencia de un campo
* asegurar que un campo está rellenado (no nulo)
* asegurar el tipo de datos de un campo
* restringir entre un conjunto de valores

Para ello se utiliza el operador [`$jsonSchema`](https://www.mongodb.com/docs/manual/reference/operator/query/jsonSchema/#json-schema). Por ejemplo:

``` json
{
  $jsonSchema: {
     required: [ "name", "major", "gpa", "address" ],
     properties: {
        name: {
           bsonType: "string",
           description: "must be a string and is required"
        },
        address: {
           bsonType: "object",
           required: [ "zipcode" ],
           properties: {
               "street": { bsonType: "string" },
               "zipcode": { bsonType: "string" }
           }
        }
     }
  }
}
```

De este modo, podemos validar un documento contra uno o más esquemas a la vez, lo que facilita la evolución de los esquemas a lo lago del tiempo.

<https://www.mongodb.com/docs/manual/core/schema-validation/specify-json-schema/#std-label-schema-validation-json>

<https://www.mongodb.com/docs/manual/core/schema-validation/use-json-schema-query-conditions/#std-label-use-json-schema-query-conditions>

FIXME: revisar la validación de los esquemas
<https://www.mongodb.com/docs/manual/core/schema-validation/>
<https://www.digitalocean.com/community/tutorials/how-to-use-schema-validation-in-mongodb>

## Referencias

Vídeo [A Complete Methodology of Data Modeling for MongoDB](https://www.youtube.com/watch?v=DUCvYbcgGsQ)

<https://andreshevia.com/2020/10/18/diseno-de-modelos-de-datos-nosql/>

<https://www.mongodb.com/developer/products/mongodb/mongodb-schema-design-best-practices/>

<https://medium.com/geekculture/mongodb-data-modeling-matters-first-step-to-optimization-data-modeling-series-1-158be911ecb8>

<https://www.mongodb.com/developer/products/mongodb/schema/tutorials/>
<https://www.mongodb.com/developer/products/mongodb/schema-design-anti-pattern-summary/>

<https://www.mongodb.com/blog/post/performance-best-practices-mongodb-data-modeling-and-memory-sizing>

## Actividades

1. (1p) Estimación de la carga de trabajo en un proceso de ingesta de datos. (Metodología curso MongoDB University)
2. (2p) Ejercicios de modelado de relaciones 1:1, 1:N, N:M que impliquen documentos embebidos y/o relaciones
3. (1p) Consultas agregadas sobre documentos con o sin referencias a otras colecciones.

<!--

RDBMS Parent-Child Tables vs. MongoDB Nested Sub-Document or Array

A table has a relationship to other tables, relations like one-to-one, one-to-many, or many-to-many by linking attributes from both tables.

MongoDB can express the relationships between collections similarly. However, MongoDB has an additional feature, the ability to take the fields of child table and embed it with the parent table as a single collection.

This grouping leads to a data model with far fewer collections than the number of tables in the corresponding relational model.

----

RDBMS Join vs. MongoDB Embedding, Linking, or $lookup

Joins are used in a relational database to get data from two or more tables.

With MongoDB, there is a $lookup operator to perform the same link between collections.

Additionally, some relationships are also expressed by embedding the child table in the parent table. For these relationship, there is no need to use the $lookup keyword, as the data is already pre-joined in the document. The document model makes things much natural and queries so much simpler.

-->