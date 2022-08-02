---
title: asdf
description: asdf
---

# Modelado NoSQL

MongoDB es una base de datos documental, no relacional, donde el esquema no se debe basar en el uso de claves ajenas/joins, ya que no existen.

A la hora de diseñar un esquema, si nos encontramos que el esquema esta en 3FN o si cuando hacemos consultas (recordad que no hay joins) estamos teniendo que realizar varias consultas de manera programativa (primero acceder a una tabla, con ese _id ir a otra tabla, etc…​.) es que no estamos siguiendo el enfoque adecuado.

MongoDB no soporta transacciones, ya que su enfoque distribuido dificultaría y penalizaría el rendimiento. En cambio, sí que asegura que las operaciones sean atómicas. Los posibles enfoques para solucionar la falta de transacciones son:

1. Restructurar el código para que toda la información esté contenida en un único documento.
2. Implementar un sistema de bloqueo por software (semáforo, etc…​).
3. Tolerar un grado de inconsistencia en el sistema.

Dependiendo del tipo de relación entre dos documentos, normalizaremos los datos para minimizar la redundancia pero manteniendo en la medida de lo posible que mediante operaciones atómicas se mantenga la integridad de los datos. Para ello, bien crearemos referencias entre dos documentos o embeberemos un documento dentro de otro.

## Referencias

Las aplicaciones que emplean MongoDB utilizan dos técnicas para relacionar documentos:

* Referencias *Manuales*
* Uso de *DBRef*

### Referencias manuales

De manera similar a una base de datos relacional, se almacena el campo _id de un documento en otro documento a modo de clave ajena. De este modo, la aplicación realiza una segunda consulta para obtener los datos relaciones. Estas referencias son sencillas y suficientes para la mayoría de casos de uso.

FIXME: imagen

Referencias manuales
Figure 1. Referencias manuales

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

### DBRef

Son referencias de un documento a otro mediante el valor del campo `_id`, el nombre de la colección y, opcionalmente, el nombre de la base de datos. Estos objetos siguen una convención para representar un documento mediante la notación `{ "$ref" : <nombreColeccion>, "$id" : <valorCampo_id>, "$db" : <nombreBaseDatos> }`.

Al incluir estos nombres, las *DBRef* permite referenciar documentos localizados en diferentes colecciones.

Así pues, si reescribimos el código anterior mediante *DBRef* tendríamos que el contacto queda de la siguiente manera:

Ejemplo de DBRef - Usuario/Contacto

``` js
db.contacto.insert({
  usuario_id: new DBRef("usuario", idUsuario),
  telefono:  "123-456-7890",
  email: "xyz@example.com"
});
```

De manera similar a las referencias manuales, mediante consultas adicionales se obtendrán los documentos referenciados.

Muchos drivers (incluido el de Java, mediante la clase DBRef) contienen métodos auxiliares que realizan las consultas con referencias DBRef automáticamennte.

Desde la propia documentación de MongoDB, recomiendan el uso de referencias manuales, a no ser de que dispongamos documentos de una colección que referencian a documentos que se encuentran en varias colecciones diferentes.

## Datos embebidos

En cambio, si dentro de un documento almacenamos los datos mediante sub-documentos, ya sea dentro de un atributo o un array, podremos obtener todos los datos mediante un único acceso.

FIXME: imagen

Datos Embebidos
Figure 2. Datos Embebidos

Generalmente, emplearemos datos embebidos cuando tengamos:

* relaciones "contiene" entre entidades, entre relaciones de documentos "uno a uno" o "uno a pocos".
* relaciones "uno a muchos" entre entidades. En estas relaciones los documentos hijo (o "muchos") siempre aparecen dentro del contexto del padre o del documento "uno".

Los datos embebidos ofrecen mejor rendimiento al permitir obtener los datos mediante una única operación, así como modificar datos relacionados en una sola operación atómica de escritura.

Un aspecto a tener en cuenta es que un documento BSON puede contener un máximo de 16MB. Si quisiéramos que un atributo contenga más información, tendríamos que utilizar el API de GridFS que veremos más adelante.

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

* **1 a muchos**, como puede ser entre Editorial y Libro. Para este tipo de relación es mejor usar referencias entre los documentos:

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

Más información en <http://docs.mongodb.org/manual/applications/data-models-relationships/>

## Jerárquicas

Si tenemos que modelar alguna entidad que tenga hijos y nos importa las relaciones padre-hijos (categoría-subcategoría), podemos tanto embeber un array con los hijos de un documento (children), como embeber un array con los padres de un documento (ancestors)

Más información en <http://docs.mongodb.org/manual/applications/data-models-tree-structures/>
