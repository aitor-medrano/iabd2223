---
title: Analítica de datos con Spark Streaming
description: Analítica de datos con Spark Streaming. Uso de fuentes de datos y sinks. Ingesta en streaming desde/hacia Kafka con Spark Streaming.
---

# Spark Streaming I

Aunque ya estudiamos el concepto de *Streaming* en la sesión sobre [Ingesta de Datos](../hadoop/02etl.md), no viene mal recordar que cuando el procesamiento se realiza en *streaming*:

* Los datos se generan de manera continuada desde una o más fuentes de datos.
* Las fuentes de datos, por lo general, envían los datos de forma simultánea.
* Los datos se reciben en pequeños fragmentos (del orden de KB).

Vamos a considerar un *stream* como un flujo de datos continuo e ilimitado, sin un final definido que aporta datos a nuestros sistemas cada segundo.

El desarrollo de aplicaciones que trabajan con datos en *streaming* suponen un mayor reto que las aplicaciones *batch*, dada la impredecibilidad de los datos, tanto su ritmo de llegada como su orden.

Uno de los casos de uso más comunes del procesamiento en *streaming* es realizar algún cálculo agregado sobre los datos que llegan y resumirlos/sintetizarlos en un destino externo para que luego ya sea un aplicación web o un motor de analítica de datos los consuman.

Las principales herramientas para el tratamiento de datos en *streaming* son [Apache Samza](https://samza.apache.org/), [Apache Flink](https://flink.apache.org/), [Apache Kafka](https://kafka.apache.org/) (de manera conjunta con *Kafka Streams*) y por supuesto, [Apache Spark](https://spark.apache.org/).

## *Streaming* en *Spark*

*Spark Streaming* es una extensión del núcleo de *Spark* que permite el procesamiento de flujos de datos en vivo ofreciendo tolerancia a fallos, un alto rendimiento y altamente escalable.

Los datos se pueden ingestar desde diversas fuentes de datos, como *Kafka*, *sockets* TCP, etc.. y se pueden procesar mediante funciones de alto nivel, ya sea mediante el uso de RDD y algoritmos *MapReduce*, o utilizando *DataFrames* y la sintaxis SQL. Finalmente, los datos procesados se almacenan en sistemas de ficheros, bases de datos o cuadros de mandos.

<figure style="align: center;">
    <img src="images/03streaming-arch.png">
    <figcaption>Streaming con Spark</figcaption>
</figure>

De hecho, podemos utilizar tanto *Spark MLlib* y sus algoritmos de *machine learning* como el procesamiento de grafos en los flujos de datos.

Spark dispone dos soluciones para trabajar con datos en *streaming*:

* [*Spark DStream*](https://spark.apache.org/docs/latest/streaming-programming-guide.html): más antigua, conocida como la primera generación,  basada en RDDs
* [*Spark Structured Streaming*](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html) basada en el uso de *DataFrames* y diseñada para construir aplicaciones que puedan reaccionar a los datos en tiempo real.

Vamos a presentar ambas soluciones, pero en este sesión nos centraremos principalmente en *Spark Structured Streaming*.

### DStream

[*Spark DStream*](https://spark.apache.org/docs/latest/streaming-programming-guide.html) (*Discretized Stream*), como ya hemos comentado, es la primera versión y actualmente no se recomienda su uso.

Funciona mediante un modelo de *micro-batching* para dividir los flujos de entrada de datos en fragmentos que son procesados por el núcleo de Spark. Este planteamiento tenía mucho sentido cuando el principal modelo de programación de Spark eran los RDD, ya que cada fragmento recibido se representaba mediante un RDD.

Así pues, *Spark DStream* recibe los datos de entrada en flujos y los divide en *batches*, por ejemplo en bloques cada N segundos, los cuales procesa *Spark* mediante RDD para generar los flujos de resultados procesados:

<figure style="align: center;">
    <img src="images/03streaming-flow.png">
    <figcaption>DStream por dentro</figcaption>
</figure>

### Structured Streaming

[*Spark Structured Streaming*](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html) es la segunda generación de motor para el tratamiento de datos en *streaming*, y fue diseñado para ser más rápido, escalable y con mayor tolerancia a los errores que *DStream*, ya que utiliza el motor de *Spark SQL*.

Además, podemos expresar los procesos en streaming de la misma manera que realizaríamos un proceso *batch* con datos estáticos. El motor de *Spark SQL* se encarga de ejecutar los datos de forma continua e incremental, y actualizar el resultado final como datos streaming. Para ello, podemos utilizar el API de Java, Scala, Python o R para expresar las agregaciones, ventanas de eventos, joins de *stream* a *batch*, etc.... Finalmente, el sistema asegura la tolerancia de fallos mediante la entrega de cada mensaje una sola vez (***exactly-once***) a través de *checkpoints* y logs.

Los pasos esenciales a realizar al codificar una aplicación en *streaming* son:

1. Especificar uno o más fuentes de datos
2. Desarrollar la lógica para manipular los flujos de entrada de datos mediante transformaciones de *DataFrames*,
3. Definir el modo de salida
4. Definir el *trigger* que provoca la lectura
5. Indicar el destino de los datos (*data sink*) donde escribir los resultados.

<figure style="align: center;">
    <img src="images/03streaming-fases.jpg">
    <figcaption>Elementos para procesar datos en Streaming</figcaption>
</figure>

Debido a que tanto el modo de salida como el *trigger* tienen valores por defecto, es posible que no tengamos que indicarlos ni configurarlos, lo que reduce el desarrollo de procesos a un bucle infinito de leer, transformar y enviar al destino (*read + transform + sink*). Cada una de las iteraciones de ese bucle infinito se conoce como un ***micro-batch***, las cuales tienen unas latencias situadas alrededor de los 100 ms. Desde Spark 2.3 existe un nuevo modo de procesamiento de baja latencia conocido como [Procesamiento Continuo](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#continuous-processing), que puede obtener latencias de 1ms. Al tratarse todavía de un tecnología en fase de experimentación, queda fuera de la presente sesión.

## Caso 1: Hola Spark Streaming

Para ver nuestro primer caso de uso, vamos a realizar un proceso de contar palabras sobre un flujo continuo de datos que proviene de un socket.

Para ello, en un terminal, abrimos un *listener* de *Netcat* en el puerto 9999:

``` bash
nc -lk 9999
```

Tras arrancar *Netcat*, ya podemos crear nuestra aplicación *Spark* (vamos a indicar que cree 2 hilos, lo cual es el mínimo necesario para realizar *streaming*, uno para recibir y otro para procesar), en la cual tenemos diferenciadas:

* la fuente de datos: creación del flujo de lectura mediante [`readStream`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.readStream.html) que devuelve un [DataStreamReader](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.DataStreamReader.html) que utilizaremos para cargar un *DataFrame*.
* la lógica de procesamiento, ya sea mediante *DataFrames API* o *Spark SQL*.
* la persistencia de los datos mediante [writeStream](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.writeStream.html) que devuelve un [DataStreamWriter](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.DataStreamWriter.html) donde indicamos el modo de salida, el cual, al iniciarlo con `start` nos devuelve un [StreamingQuery](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.StreamingQuery.html)
* y finalmente el cierre del flujo de datos a partir de la consulta en *streaming* mediante [`awaitTermination`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.StreamingQuery.awaitTermination.html?highlight=awaittermination).

``` python hl_lines="5 10 25 28 31"
from pyspark.sql import SparkSession
spark = SparkSession \
        .builder \
        .appName("Streaming IABD WordCount") \
        .master("local[2]") \
        .getOrCreate()

# Creamos un flujo de escucha sobre netcat en localhost:9999
# En Spark Streaming, la lectura se realiza mediante readStream
lineasDF = spark.readStream \
        .format("socket") \
        .option("host", "localhost") \
        .option("port", "9999") \
        .load()

# Leemos las líneas y las pasamos a palabras.
# Sobre ellas, realizamos la agrupación count (transformación)
from pyspark.sql.functions import explode, split
palabrasDF = lineasDF.select(explode(split(lineasDF.value, ' ')).alias('palabra'))
cantidadDF = palabrasDF.groupBy("palabra").count()

# Mostramos las palabras por consola (sink)
# En Spark Streaming, la persistencia se realiza mediante writeStream
#  y en vez de realizar un save, ahora utilizamos start
wordCountQuery = cantidadDF.writeStream \
        .format("console") \
        .outputMode("complete") \
        .start()

# dejamos Spark a la escucha
wordCountQuery.awaitTermination()
```

Conforme escribamos en el terminal de *Netcat* irán apareciendo en la consola de *Spark* los resultados:

<figure style="align: center;">
    <img src="images/03streaming-wc.gif">
    <figcaption>Ejecución de Streaming WordCount</figcaption>
</figure>

Al ejecutar la consulta, *Spark* crea un proceso a la escucha de manera ininterrumpida de nuevos datos. Mientras no lleguen datos, Spark queda a la espera, de manera que cuando llegue algún dato al flujo de entrada, se creará un nuevo *micro-batch*, lo que lanzará un nuevo *job* de Spark.

Si queremos detenerlo, podemos hacerlo de forma explícita:

``` python
wordCountQuery.stop()
```

Una buena práctica al trabajar es configurar la *SparkSession* mediante la propiedad `spark.streaming.stopGracefullyOnShutdown` para que detenga el *streaming* al finalizar el proceso:

``` python hl_lines="3"
spark = SparkSession.builder \
        .appName("Streaming WordCount") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .getOrCreate()
```

Por defecto, Spark utiliza 200 particiones para barajar los datos. Como no tenemos muchos datos, para obtener un mejor rendimiento, podemos reducir su cantidad mediante la propiedad `spark.sql.shuffle.partitions`:

``` python hl_lines="4"
spark = SparkSession.builder \
        .appName("Streaming WordCount") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.sql.shuffle.partitions", 3) \
        .getOrCreate()
```

!!! tip "Nombre de la consulta"
    Una buena práctica es indicar el nombre de la consulta mediante el método [queryName](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.DataStreamWriter.queryName.html), el cual nos sirve luego para monitorizar la ejecución del flujo:

    ``` python hl_lines="2"
    wordCountQuery = cantidadDF.writeStream \
        .queryName("Caso1WordCount") \
        .format("console") \
        .outputMode("complete") \
        .start()
    ```

## Elementos

La idea básica al trabajar los datos en *streaming* es similar a tener una tabla de entrada de tamaño ilimitado, y conforme llegan nuevos datos, tratarlos como un nuevo conjunto de filas que se adjuntan a la tabla.

<figure style="align: center;">
    <img src="images/03streaming-datatable.png">
    <figcaption>Datos como registros</figcaption>
</figure>

A continuación vamos a repasar los elementos principales de un flujo en streaming, los cuales son la fuente de datos, las operaciones en *streaming* mediante las transformaciones, los modos de salida, *trigger* y los *sink* de datos.

!!! info "Hablemos del tiempo"

    <figure style="float: right;">
        <img src="images/03streaming-event-vs-processing.jpg" width="300">
        <figcaption>Eventos vs Procesamiento</figcaption>
    </figure>

    Existen dos tipos de tiempo, el tiempo del evento (***event time***) que representa cuando se crea el dato y el de procesado (***processing time***), que representa el momento en el que el motor de procesamiento/analítica de datos procesa el dato.
    Por ejemplo, si nos centramos en un escenario IoT, el tiempo del evento es cuando se toma el dato del sensor, y el de procesamiento cuando nuestro motor de *streaming* realiza la transformación/agregación sobre los datos del sensor.

    A la hora de trabajar con los datos, hemos de realizarlo siempre con el tiempo de los eventos, ya que representan el instante en el que se crean los datos. En un estado ideal, los datos llegan y se procesan casi de forma instantánea, pero la realidad es otra, y la latencia existente provoca la necesidad de descartar el tiempo de procesamiento.

    Para manejar los flujos de entrada ajenos a un flujo constante, una práctica muy común es dividir los datos en trozos utilizando el tiempo inicial y final como límites de una ventana temporal.

### Fuentes de Datos

Mientras que en el procesamiento *batch* las fuentes de datos son *dataset* estáticos que residen en un almacenamiento como pueda ser un sistema local, HDFS o S3, al hablar de procesamiento en *streaming* las fuentes de datos generan los datos de forma continuada, por lo que necesitamos otro tipo de fuentes.

*Structured Streaming* ofrece un conjunto predefinido de [fuentes de datos](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#input-sources) que se leen a partir de un [DataStreamReader](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.DataStreamReader.html). Los tipos existentes son:

* ^^Fichero^^: permite leer ficheros desde un directorio como un flujo de datos, con soporte para ficheros de texto, CSV, JSON, Parquet, ORC, etc...

    ``` python
    # Lee todos los ficheros csv de un directorio
    esquemaUsuario = StructType() \
        .add("nombre", "string").add("edad", "integer")
    csvDF = spark.readStream \
        .option("sep", ";") \
        .schema(esquemaUsuario) \
        .csv("/path/al/directorio")  # equivalente a format("csv").load("/path/al/directorio")
    ```

    Podemos configurar otras opciones como `maxFilesPerTrigger` con la cantidad de archivos a cargar en cada *trigger*, así como la política de lectura cuando su número sea mayor de uno mediante la propiedad booleana `latestFirst`.

* ^^Kafka^^: para leer datos desde brokers *Kafka* (versiones 0.10 o superiores). Realizaremos un par de ejemplos en los siguientes apartados.

    ``` python
    kafkaDF = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
        .option("subscribe", "iabd-topic") \
        .load()
    ```

* ^^Socket^^: lee texto UTF8 desde una conexión *socket* (es el que hemos utilizado en el caso de uso 1). Sólo se debe utilizar para pruebas ya que no ofrece garantía de tolerancia de fallos de punto a punto.

    ``` python
    socketDF = spark.readStream \
        .format("socket") \
        .option("host", "localhost") \
        .option("port", 9999) \
        .load()
    ```

* ^^Rate^^: Genera datos indicando una cantidad de filas por segundo, donde cada fila contiene un *timestamp* y el valor de un contador secuencial (la primera fila contiene el 0). Esta fuente también se utiliza para la realización de pruebas y *benchmarking*.

    ``` python
    socketDF = spark.readStream \
        .format("rate") \
        .option("rowsPerSecond", 1)
        .load()
    ```

* ^^Tabla^^ (desde *Spark 3.1*): Carga los datos desde una tabla temporal de *SparkSQL*, la cual podemos utilizar tanto para cargar como para persistir los cálculos realizados. Más información en la [documentación oficial](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#streaming-table-apis).

    ``` python
    tablaDF = spark.readStream \
        .table("clientes")
    ```

### *Sinks*

De la misma manera, también tenemos un conjunto de [*Sinks*](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#output-sinks) predefinidos como destino de los datos, que se escriben a partir de un [DataStreamWriter](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.DataStreamWriter.html) mediante el interfaz [`writeStream`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.writeStream.html):

* ^^Fichero^^: Podemos almacenar los resultados en un sistema de archivos, HDFS o S3, con soporte para los formatos CSV, JSON, ORC y Parquet.

    ``` python
    # Otros valores pueden ser "json", "csv", etc...
    df.writeStream.format("parquet") \        
        .option("path", "/path/al/directorio") \ 
        .start()
    ```

* ^^Kafka^^: Envía los datos a un clúster de *Kafka*:

    ``` python
    df.writeStream.format("kafka") \        
        .option("kafka.bootstrap.servers", "host1:port1,host2:port2")
        .option("topic", "miTopic")
        .start()
    ```

* ^^Foreach^^ y ^^ForeachBatch^^: permiten realizar operaciones y escribir lógica sobre la salida de una consulta de *streaming*, ya sea a nivel de fila (*foreach*) como a nivel de micro-batch (*foreachBatch*). Más información en la [documentación oficial](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#using-foreach-and-foreachbatch).
* ^^Consola^^: se emplea para pruebas y depuración y permite mostrar el resultado por consola.

    ``` python
    df.writeStream.format("console") \        
        .start()
    ```

    Admite las opciones `numRows` para indicar las filas a mostrar y `truncate` para truncar los datos si las filas son muy largas.

* ^^Memoria^^: se emplea para pruebas y depuración, ya que sólo permite un volumen pequeño de datos para evitar un problema de falta de memoria en el driver para almacenar la salida. Los datos se almacenan en una tabla temporal a la cual podemos acceder desde *SparkSQL*:

    ``` python
    df.writeStream.format("memory") \  
        .queryName("nombreTabla")  
        .start()
    ```

### Modos de salida

El [modo de salida](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#output-modes) determina cómo salen los datos a un sumidero de datos. Existen tres opciones:

* Añadir (*`append`*): para insertar los datos, cuando sabemos que no vamos a modificar ninguna salida anterior, y que cada *batch* únicamente escribirá nuevos registros. Es el modo por defecto.
* Modificar (*`update`*): similar a un *upsert*, donde veremos solo registros que, bien son nuevos, bien son valores antiguos que debemos modificar.
* Completa (*`complete`*): para sobrescribir completamente el resultado, de manera que siempre recibimos la salida completa.

En el caso 1 hemos utilizado el modo de salida completa, de manera que con cada dato nuevo, se mostraba como resultado todas las palabras y su cantidad. Si hubiésemos elegido el modo *update*, en cada micro-batch solo se mostraría el resultado acumulado de cada *batch*.

Por ejemplo, si introducimos:

``` text
Spark Streaming en el Severo Ochoa
El Severo Ochoa está en Elche
```

Dependiendo del modo de salida, al introducir la segunda frase con la siguiente consulta:

=== "Complete"

    ``` python hl_lines="3"
    wordCountQuery = cantidadDF.writeStream \
        .format("console") \
        .outputMode("complete") \
        .start()
    ```

    Aparece la cuenta de todas las palabras:

    ``` text
    +---------+-----+
    |  palabra|count|
    +---------+-----+
    |    Spark|    1|
    |    Elche|    1|
    |    Ochoa|    2|
    |       El|    1|
    |       en|    2|
    |Streaming|    1|
    |     está|    1|
    |   Severo|    2|
    |       el|    1|
    +---------+-----+
    ```

=== "Update"

    ``` python hl_lines="3"
    wordCountQuery = cantidadDF.writeStream \
        .format("console") \
        .outputMode("update") \
        .start()
    ```

    Sólo aparecen las palabras del segundo micro-batch:

    ``` text
    +-------+-----+
    |palabra|count|
    +-------+-----+
    |     El|    1|
    |  Ochoa|    2|
    |  Elche|    1|
    | Severo|    2|
    |   está|    1|
    |     en|    2|
    +-------+-----+
    ```

Con este ejemplo, el modo *append* no tiene sentido (ya que para contar las palabras necesitamos las anteriores), y *Spark* es tan listo que cuando realizamos agregaciones no permite su uso y lanza una excepción del tipo `AnalysisException`:

``` bash
AnalysisException: Append output mode not supported when there are streaming aggregations on streaming DataFrames/DataSets without watermark;
Aggregate [palabra#59], [palabra#59, count(1) AS count#63L]
```

Si permitiera el modo `append`, sólo deberían aparecer las palabra `El`, `está` y `Elche`, ya que son los elementos que no existían previamente.

En resumen, el modo `append` es sólo para inserciones, `update` para modificaciones e inserciones y finalmente `complete` sobrescribe los resultados previos.

Además, no todos los tipos de salida se pueden aplicar siempre, va a depender del tipo de operaciones que realicemos. Volveremos a tratarlos cuando veamos las marcas de agua en el apartado [Watermarking](#watermarking).

### Transformaciones

Dentro de *Spark Structured Streaming* tenemos dos tipos de transformaciones:

* Sin estado (*stateless*): los datos de cada *micro-batch* son independientes de los anteriores, y por tanto, podemos realizar las transformaciones `select`, `filter`, `map`, `flatMap`, `explode`. Es importante destacar que estas transformaciones no soportan el modo de salida *complete*, por lo que sólo podemos utilizar los modos *append* o *update*.
* Con estado (*stateful*): aquellas que implica realizar agrupaciones, agregaciones, *windowing* y/o *joins*, ya que mantienen el estado entre los diferentes *micro-batches*. Destacar que un abuso del estado puede causar problemas de falta de memoria, ya que el estado se almacena en la memoria de los ejecutores (*executors*). Por ello, *Spark* ofrece dos tipos de operaciones con estado:

    * Gestionadas (*managed*): *Spark* gestiona el estado y libera la memoria conforme sea necesario.
    * Sin gestionar (*unmanaged*): permite que el desarrollador defina las políticas de limpieza del estado (y su liberación de memoria), por ejemplo, a partir de políticas basadas en el tiempo. A día de hoy, las transformación sin gestionar sólo están disponibles mediante *Java* o *Scala*.

Además, hay que tener en cuenta que no todas las operaciones que realizamos con *DataFrames* están soportadas al trabajar en *streaming*, como pueden ser `show`, `describe`, `count` (aunque sí que podemos contar sobre agregaciones/funciones ventana), `limit`, `distinct`, `cube` o `sort` (podemos ordenar en algunos casos después de haber realizado una agregación), ya que los datos no están acotados y provocará una excepción del tipo `AnalysisException`.

### Triggers

Un [trigger](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#triggers) define el intervalo (*timing*) temporal de procesamiento de los datos en *streaming*, indicando si la consulta se ejecutará como un *micro-batch* mediante un intervalo fijo o con una consulta con procesamiento continuo.

Así pues, un trigger es un mecanismo para que el motor de Spark SQL determine cuando ejecutar la computación en *streaming*.

Los posibles tipos son:

* *Sin especificar*, de manera que cada micro-batch se va a ejecutar tan pronto como lleguen datos.
* *Por intervalo de tiempo*, mediante la propiedad `processingTime`. Si indicamos un intervalo de un minuto, una vez finalizado un job, si no ha pasado un minuto, se esperará a ejecutarse. Si el micro-batch tardase más de un minuto, el siguiente se ejecutaría inmediatamente. Así pues, de esta manera, Spark permite colectar datos de entrada y procesarlos de manera conjunta (en vez de procesar individualmente cada registro de entrada).
* *Un intervalo*, mediante la propiedad `once`, de manera que funciona como un proceso *batch* estándar, creando un único proceso *micro-batch*, o con la propiedad `availableNow` para leer todos los datos disponibles hasta el momento mediante múltiples *batches*.
* *Continuo*, mediante la propiedad `continuous`, para permitir latencias del orden de milisegundos mediante [Continuous Processing](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#continuous-processing). Se trata de una opción experimental desde la versión 2.3 de Spark.

Los triggers se configuran al persistir el *DataFrame*, tras indicar el modo de salida mediante el método [trigger](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.DataStreamWriter.trigger.html?highlight=trigger):

``` python hl_lines="4"
wordCountQuery = cantidadDF.writeStream \
    .format("console") \
    .outputMode("complete") \
    .trigger(processingTime="1 minute") \
    .start()
```

<!--
### Ejecución

FIXME: start() materializes the complete job description into a streaming computation and initiates the internal scheduling process that results in data being consumed from the source, processed, and produced to the sink. start() returns a StreamingQuery object, which is a handle to manage the individual life cycle of each query. This means that we can simultaneously start and stop multiple queries independently of one other within the same sparkSession.
-->

## Caso 2: Facturas

En este caso de uso vamos a poner en práctica algunos de los conceptos que acabamos de ver.

Vamos a suponer que tenemos un empresa compuesta de diferentes sucursales. Cada una de ellas, cada 5 minutos genera un fichero con los datos de las facturas ([*invoices.zip*](resources/invoices.zip)) que han generado. Cada una de las facturas contiene una o más líneas de factura, las cuales queremos separar en facturas simples.

Así pues, vamos a partir de documentos JSON con la siguiente estructura:

``` json
{
    "InvoiceNumber":"51402977",
    "CreatedTime":1595688900348,
    "StoreID":"STR7188",
    "PosID":"POS956",
    "CashierID":"OAS134",
    "CustomerType":"PRIME",
    "CustomerCardNo":"4629185211",
    "TotalAmount":11114.0,
    "NumberOfItems":4,
    "PaymentMethod":"CARD",
    "TaxableAmount":11114.0,
    "CGST":277.85,
    "SGST":277.85,
    "CESS":13.8925,
    "DeliveryType":"TAKEAWAY",
    "InvoiceLineItems":[
        {"ItemCode":"458","ItemDescription":"Wine glass","ItemPrice":1644.0,"ItemQty":2,"TotalValue":3288.0},
        {"ItemCode":"283","ItemDescription":"Portable Lamps","ItemPrice":2236.0,"ItemQty":1,"TotalValue":2236.0},
        {"ItemCode":"498","ItemDescription":"Carving knifes","ItemPrice":1424.0,"ItemQty":2,"TotalValue":2848.0},
        {"ItemCode":"523","ItemDescription":"Oil-lamp clock","ItemPrice":1371.0,"ItemQty":2,"TotalValue":2742.0}]}
```

Y a partir de él, generaremos 4 documentos (uno por cada línea de factura) con la siguiente estructura:

``` json
{
    "InvoiceNumber":"51402977",
    "CreatedTime":1595688900348,
    "StoreID":"STR7188",
    "PosID":"POS956",
    "CustomerType":"PRIME",
    "PaymentMethod":"CARD",
    "DeliveryType":"TAKEAWAY",
    "ItemCode":"458",
    "ItemDescription":"Wine glass",
    "ItemPrice":1644.0,
    "ItemQty":2,
    "TotalValue":3288.0
}
```

### Cargando los datos

Las facturas que nos envían las colocan en una carpeta a la que tenemos acceso (para este ejercicio, podemos descargar los archivos y colocarlos en la carpeta `entrada`), de manera que primero crearemos la sesión y realizaremos la lectura desde dicha carpeta. Es importante destacar que para que funcione la inferencia de la estructura del documento, debemos disponer de algún archivo en nuestra carpeta de `entrada` y activar la propiedad `spark.sql.streaming.schemaInference`:

``` python
from pyspark.sql import SparkSession
spark = SparkSession \
        .builder \
        .appName("Streaming de Ficheros") \
        .master("local[2]") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.sql.shuffle.partitions", 3) \
        .config("spark.sql.streaming.schemaInference", "true") \
        .getOrCreate()

raw_df = spark.readStream \
        .format("json") \
        .option("path", "entrada") \
        .load()

raw_df.printSchema()
# root
#  |-- CESS: double (nullable = true)
#  |-- CGST: double (nullable = true)
#  |-- CashierID: string (nullable = true)
#  |-- CreatedTime: long (nullable = true)
#  |-- CustomerCardNo: string (nullable = true)
#  |-- CustomerType: string (nullable = true)
#  |-- DeliveryAddress: struct (nullable = true)
#  |    |-- AddressLine: string (nullable = true)
#  |    |-- City: string (nullable = true)
#  |    |-- ContactNumber: string (nullable = true)
#  |    |-- PinCode: string (nullable = true)
#  |    |-- State: string (nullable = true)
#  |-- DeliveryType: string (nullable = true)
#  |-- InvoiceLineItems: array (nullable = true)
#  |    |-- element: struct (containsNull = true)
#  |    |    |-- ItemCode: string (nullable = true)
#  |    |    |-- ItemDescription: string (nullable = true)
#  |    |    |-- ItemPrice: double (nullable = true)
#  |    |    |-- ItemQty: long (nullable = true)
#  |    |    |-- TotalValue: double (nullable = true)
#  |-- InvoiceNumber: string (nullable = true)
#  |-- NumberOfItems: long (nullable = true)
#  |-- PaymentMethod: string (nullable = true)
#  |-- PosID: string (nullable = true)
#  |-- SGST: double (nullable = true)
#  |-- StoreID: string (nullable = true)
#  |-- TaxableAmount: double (nullable = true)
#  |-- TotalAmount: double (nullable = true)
```

Aunque en este caso hemos realizado la inferencia de la estructura de los datos de entrada, lo normal es indicar el esquema de los datos.

### Proyectando

El siguiente paso es seleccionar los datos que nos interesan. Para ello, tras revisar la estructura de salida que deseamos, realizamos una selección de las columnas y utilizaremos la función `explode` para desenrollar el array de facturas `InvoiceLineItems`:

``` python
explode_df = raw_df.selectExpr("InvoiceNumber", "CreatedTime", "StoreID",
                                 "PosID", "CustomerType",
                                 "PaymentMethod", "DeliveryType",
                                 "explode(InvoiceLineItems) as LineItem")
explode_df.printSchema()
# root
#  |-- InvoiceNumber: string (nullable = true)
#  |-- CreatedTime: long (nullable = true)
#  |-- StoreID: string (nullable = true)
#  |-- PosID: string (nullable = true)
#  |-- CustomerType: string (nullable = true)
#  |-- PaymentMethod: string (nullable = true)
#  |-- DeliveryType: string (nullable = true)
#  |-- LineItem: struct (nullable = true)
#  |    |-- ItemCode: string (nullable = true)
#  |    |-- ItemDescription: string (nullable = true)
#  |    |-- ItemPrice: double (nullable = true)
#  |    |-- ItemQty: long (nullable = true)
#  |    |-- TotalValue: double (nullable = true)
```

!!! question "Direcciones de las facturas"
    Cuando el tipo de entrega no es `TAKEAWAY`, tendremos rellenada la dirección de los pedidos. En ese caso, podemos asignar los campos y aunque haya documentos que no tengan dichos elementos, nuestro pipeline funcionará para ambos casos.

    ``` python
    explode_df = raw_df.selectExpr("InvoiceNumber", "CreatedTime", "StoreID", "PosID",
        "CustomerType", "PaymentMethod", "DeliveryType", "DeliveryAddress.City",
        "DeliveryAddress.State",
        "DeliveryAddress.PinCode", "explode(InvoiceLineItems) as LineItem")
    ```

Tras ello, vamos a renombrar los campos para quitar los campos anidados (creando columnas nuevas con el nombre deseando y eliminando la columna `LineItem`):

``` python
from pyspark.sql.functions import expr
limpio_df = explode_df \
    .withColumn("ItemCode", expr("LineItem.ItemCode")) \
    .withColumn("ItemDescription", expr("LineItem.ItemDescription")) \
    .withColumn("ItemPrice", expr("LineItem.ItemPrice")) \
    .withColumn("ItemQty", expr("LineItem.ItemQty")) \
    .withColumn("TotalValue", expr("LineItem.TotalValue")) \
    .drop("LineItem")
limpio_df.printSchema()
# root
#  |-- InvoiceNumber: string (nullable = true)
#  |-- CreatedTime: long (nullable = true)
#  |-- StoreID: string (nullable = true)
#  |-- PosID: string (nullable = true)
#  |-- CustomerType: string (nullable = true)
#  |-- PaymentMethod: string (nullable = true)
#  |-- DeliveryType: string (nullable = true)
#  |-- ItemCode: string (nullable = true)
#  |-- ItemDescription: string (nullable = true)
#  |-- ItemPrice: double (nullable = true)
#  |-- ItemQty: long (nullable = true)
#  |-- TotalValue: double (nullable = true)
```

### Guardando el resultado

Una vez tenemos el proceso de transformación de datos, sólo nos queda crear el *WriterQuery* para escribir el resultado del flujo de datos. En este caso, vamos a almacenarlo también como ficheros en la carpeta `salida` en formato *JSON* a intervalos de un minuto:

``` python
facturaWriterQuery = limpio_df.writeStream \
    .format("json") \
    .queryName("Facturas Writer") \
    .outputMode("append") \
    .option("path", "salida") \
    .option("checkpointLocation", "chk-point-dir") \
    .trigger(processingTime="1 minute") \
    .start()
```

### Refinando

Una vez que vemos que todo funciona, podemos realizar unos ajustes de configuración.

Por ejemplo, vamos a configurar que sólo consuma un fichero cada vez. Para ello, en el *reader* configuramos la opción `maxFilesPerTrigger`, la cual permite limitar la cantidad de ficheros de cada micro-batch.

Otras opciones que se usan de manera conjunta son `cleanSource` y `sourceArchiveDir`, que permiten archivar los ficheros procesados de forma automática. La opción `cleanSource` puede tomar los valores `archive` o `delete`. Si decidimos archivar, mediante `sourceArchiveDir` indicamos el destino donde se moverán.

``` python
raw_df = spark.readStream \
    .format("json") \
    .option("path", "entrada") \
    .option("maxFilesPerTrigger", 1) \
    .option("cleanSource", "delete") \
    .load()
```

Hay que tener en cuenta, que tanto archivar como eliminar van a impactar negativamente en el rendimiento de cada micro-batch. Nosotros hemos de limpiar el directorio de entrada, eso es un hecho. Si ejecutamos *micro-batch* largos, podemos usar la opción `cleanSource`. En cambio, si nuestros *batches* son muy cortos y el utilizar `cleanSource` no es factible por la demora que introduce, debemos crear un proceso de limpieza separado que se ejecute cada X horas y que limpie nuestro directorio de entrada.

### Monitorización

Una vez hemos realizado una consulta, podemos obtener [información](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#managing-streaming-queries) sobre la misma de forma programativa:

``` python
facturaWriterQuery.explain() # muestra una explicación detalla del plan de ejecución
# == Physical Plan ==
# *(1) Project [InvoiceNumber#314, CreatedTime#308L, StoreID#319, PosID#317, CustomerType#310, PaymentMethod#316, DeliveryType#312, _extract_City#339 AS City#52, _extract_State#340 AS State#53, _extract_PinCode#341 AS PinCode#54, LineItem#55.ItemCode AS ItemCode#67, LineItem#55.ItemDescription AS ItemDescription#81, LineItem#55.ItemPrice AS ItemPrice#96, LineItem#55.ItemQty AS ItemQty#112L, LineItem#55.TotalValue AS TotalValue#129]
# ...
facturaWriterQuery.recentProgress # muestra una lista de los últimos progresos de la consulta
# [{'id': '3b6d37cf-6a3c-405e-a715-1dc787f34b00',
#   'runId': '3dc7c478-626a-4558-87ea-4912da55114d',
#   'name': 'Facturas Writer',
#   'timestamp': '2022-05-11T08:20:49.058Z',
#   'batchId': 0,
#   'numInputRows': 500,
#   'inputRowsPerSecond': 0.0,
#   'processedRowsPerSecond': 113.55893708834887,
#   'durationMs': {'addBatch': 2496,
# ...
facturaWriterQuery.lastProgress # muestra el último progreso
# {'id': '3b6d37cf-6a3c-405e-a715-1dc787f34b00',
#  'runId': '3dc7c478-626a-4558-87ea-4912da55114d',
#  'name': 'Facturas Writer',
#  'timestamp': '2022-05-11T08:33:00.001Z',
#  'batchId': 3,
#  'numInputRows': 0,
#  'inputRowsPerSecond': 0.0,
#  'processedRowsPerSecond': 0.0,
#  'durationMs': {'latestOffset': 5, 'triggerExecution': 8},
# ...
```

Estas mismas estadísticas las podemos obtener de forma gráfica. Al ejecutar procesos en Streaming, si accedemos a Spark UI, ahora podremos ver la pestaña *Structured Streaming* con información detallada de la cantidad datos de entrada, tiempo procesado y duración de los micro-batches:

<figure style="align: center;">
    <img src="images/03streaming-ui.png" width="500">
    <figcaption>Spark UI en Structured Streaming</figcaption>
</figure>

Además, podemos iniciar tantas consultas como queramos en una única sesión de Spark, las cuales se ejecutarán de forma concurrente utilizando los recursos del clúster de Spark.

## Tolerancia a fallos

Un aplicación en *streaming* se espera que se ejecute de forma ininterrumpida mediante un bucle infinito de micro-batches.

Realmente, un escenario de ejecución infinita no es posible, ya que la aplicación se detendrá por:

* un fallo, ya sea por un dato mal formado o un error de red.
* mantenimiento del sistema, para actualizar la aplicación o el hardware donde corre.

!!! info "Tipos de entrega"
    Cuando los datos llegar a un motor de *streaming* de datos, este es responsable de su procesado. Para tratar la tolerancia a fallos, existen tres escenarios posibles:

    <figure style="float: right">
        <img src="images/03streaming-delivery.jpg" width="300">
        <figcaption>Tipos de entrega de mensajes</figcaption>
    </figure>

    * Una vez como mucho (*at most once*): no se entrega más de una copia de un dato. Es decir, puede darse el caso de que no llegue, pero no habrá repetidos.
    * Una vez al menos (*at least once*): en este caso no habrá pérdidas, pero un dato puede llegar más de una vez. 
    * Una vez exacta (*exactly once*): se garantiza que cada dato se entrega una única vez, sin pérdidas ni duplicados.

Por ello, una aplicación *Spark Streaming* se debe reiniciar de forma transparente para mantener la característica de ***exactly-once*** la cual implica que:

1. No se pierde ningún registro
2. No crea registros duplicados.

Para ello, *Spark Structured Streaming* mantiene el estado de los micro-batches mediante [*checkpoints*](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#recovering-from-failures-with-checkpointing) que se almacenan en la carpeta indicada por la opción `checkpointLocation`:

``` python hl_lines="6"
facturaWriterQuery = limpio_df.writeStream \
    .format("json") \
    .queryName("Facturas Writer") \
    .outputMode("append") \
    .option("path", "salida") \
    .option("checkpointLocation", "chk-point-dir") \
    .trigger(processingTime="1 minute") \
    .start()
```

La localización de esta carpeta debería ser un sistema de archivo confiable y tolerante a fallos, como HDFS o Amazon S3.

Esta carpeta contiene dos elementos:

* Posición de lectura, que realiza la misma función que los *offset* en Kafka, y representa el inicio y el final del rango de datos procesados por el actual *micro-batch*, de manera que Spark conoce el progreso exacto del procesamiento. Una vez ha finalizado el *micro-batch*, Spark realiza un *commit* para indicar que se han procesado los datos de forma exitosa.
* Información del estado, que contiene los datos intermedios del *micro-batch*, como la cantidad total de palabras contadas.

De esta manera, Spark mantiene toda la información necesaria para reiniciar un micro-batch que no ha finalizado. Sin embargo, la capacidad de reiniciarse no tiene por qué garantizar la política *exactly-once*. Para ello, es necesario cumplir los siguientes requisitos:

1. Reiniciar la aplicación con el mismo `checkpointLocation`. Si se elimina la carpeta o se ejecuta la misma consulta sobre otro directorio de *checkpoint* es como si realizásemos una consulta desde 0.
2. Utilizar una fuente de datos que permita volver a leer los datos incompletos del *micro-batch*, por ejemplo, tanto los ficheros de texto como *Kafka* permiten volver a leer los datos desde un punto determinado. Sin embargo, los datos que provienen de un socket no permite volver a leerlos.
3. Asegurar que la lógica de aplicación, dados los mismos datos de entrada, produce siempre el mismo resultado (aplicación determinista). Si por ejemplo, nuestra lógica de aplicación utilizará alguna dependencia basada en fechas o el tiempo, ya no obtendríamos el mismo resultado.
4. El destino (*sink*) debe ser capaz de identificar los elementos duplicados e ignorarlos o actualizar la copia antigua con el mismo registro, es decir, son idempotentes.

## Caso 3: Consumiendo *Kafka*

Cuando el tiempo de procesamiento debe ser inferior del orden de minutos, trabajar con ficheros deja de ser una opción.

Para este caso, vamos a simular el caso anterior, pero en vez de ficheros, vamos a cargar los datos desde [*Kafka*](https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html) y seguiremos generando los datos en un sistema de archivos.

<figure style="align: center;">
    <img src="images/03spark-caso3.png" width="600">
    <figcaption>Arquitectura caso 3</figcaption>
</figure>

Antes de comenzar, necesitamos configurar el paquete `spark-sql-kafka` en *Spark*. De manera similar a como realizamos al arrancar *PySpark*, necesitamos arrancarlo pasándole el paquete con la librería:

``` bash
pyspark --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1
```

Una vez arrancado, creamos la sesión y el *DataFrame* de lectura:

``` python hl_lines="9-12"
from pyspark.sql import SparkSession
spark = SparkSession \
    .builder \
    .appName("Kafka Streaming") \
    .master("local[3]") \
    .getOrCreate()

kafkaDFS = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "iabd-virtualbox:9092") \
    .option("subscribe", "facturas") \
    .option("startingOffsets", "earliest") \
    .load()
```

De esta manera nos subscribimos al topic `facturas` y realizamos la lectura desde el inicio.

Antes de poder ejecutar el *reader*, hemos de arrancar Kafka y crear el topic `facturas`. Para ello, una vez estamos en la carpeta de instalación de Kafka (en nuestro caso `/opt/kafka_2.13-2.8.1`), ejecutaremos los siguientes comandos:

``` bash
zookeeper-server-start.sh ./config/zookeeper.properties
kafka-server-start.sh ./config/server.properties
kafka-topics.sh --create --topic facturas --bootstrap-server iabd-virtualbox:9092
```

Si mostramos el esquema tenemos:

``` python
kafkaDFS.printSchema()
# root
#  |-- key: binary (nullable = true)
#  |-- value: binary (nullable = true)
#  |-- topic: string (nullable = true)
#  |-- partition: integer (nullable = true)
#  |-- offset: long (nullable = true)
#  |-- timestamp: timestamp (nullable = true)
#  |-- timestampType: integer (nullable = true)
```

Donde podemos ver que cada mensaje tiene una `key` y un `value`, así como otros campos relativos a *Kafka* que *Spark* utilizará para gestionar la tolerancia a fallos.

Es importante destacar que el campo `value` es de tipo binario, por lo que necesitamos pasarlo a formato JSON.

### Leyendo datos

Para poder leer los datos, necesitamos indicar el esquema del campo `value`. Para ello, primero definimos el esquema:

``` python
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType, IntegerType, ArrayType
esquema = StructType([
    StructField("InvoiceNumber", StringType()),
    StructField("CreatedTime", LongType()),
    StructField("StoreID", StringType()),
    StructField("PosID", StringType()),
    StructField("CashierID", StringType()),
    StructField("CustomerType", StringType()),
    StructField("CustomerCardNo", StringType()),
    StructField("TotalAmount", DoubleType()),
    StructField("NumberOfItems", IntegerType()),
    StructField("PaymentMethod", StringType()),
    StructField("CGST", DoubleType()),
    StructField("SGST", DoubleType()),
    StructField("CESS", DoubleType()),
    StructField("DeliveryType", StringType()),
    StructField("DeliveryAddress", StructType([
        StructField("AddressLine", StringType()),
        StructField("City", StringType()),
        StructField("State", StringType()),
        StructField("PinCode", StringType()),
        StructField("ContactNumber", StringType())
    ])),
    StructField("InvoiceLineItems", ArrayType(StructType([
        StructField("ItemCode", StringType()),
        StructField("ItemDescription", StringType()),
        StructField("ItemPrice", DoubleType()),
        StructField("ItemQty", IntegerType()),
        StructField("TotalValue", DoubleType())
    ]))),
])
```

Una vez que tenemos el esquema, necesitamos realizar un *casting* de la columna para cargarla como si fuese un *string* y deserializar los datos a formato JSON mediante [`from_json`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.from_json.html):

!!! tip "Kafka Source - CSV y Avro"
    Si los datos estuviesen en formato *CSV* usaremos [`from_csv`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.from_csv.html) o si el formato fuese *Avro* utilizaríamos [`from_avro`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.avro.functions.from_avro.html).

    Más información sobre *Avro* y *Spark* en la [documentación oficial](https://spark.apache.org/docs/latest/sql-data-sources-avro.html).

``` python
from pyspark.sql.functions import from_json, col
valueDF = kafkaDFS.select(from_json(col("value").cast("string"), esquema).alias("value"))
valueDF.printSchema()
# root
#  |-- value: struct (nullable = true)
#  |    |-- InvoiceNumber: string (nullable = true)
#  |    |-- CreatedTime: long (nullable = true)
#  |    |-- StoreID: string (nullable = true)
#  |    |-- PosID: string (nullable = true)
#  |    |-- CashierID: string (nullable = true)
#  |    |-- CustomerType: string (nullable = true)
#  |    |-- CustomerCardNo: string (nullable = true)
#  |    |-- TotalAmount: double (nullable = true)
#  |    |-- NumberOfItems: integer (nullable = true)
#  |    |-- PaymentMethod: string (nullable = true)
#  |    |-- CGST: double (nullable = true)
#  |    |-- SGST: double (nullable = true)
#  |    |-- CESS: double (nullable = true)
#  |    |-- DeliveryType: string (nullable = true)
#  |    |-- DeliveryAddress: struct (nullable = true)
#  |    |    |-- AddressLine: string (nullable = true)
#  |    |    |-- City: string (nullable = true)
#  |    |    |-- State: string (nullable = true)
#  |    |    |-- PinCode: string (nullable = true)
#  |    |    |-- ContactNumber: string (nullable = true)
#  |    |-- InvoiceLineItems: array (nullable = true)
#  |    |    |-- element: struct (containsNull = true)
#  |    |    |    |-- ItemCode: string (nullable = true)
#  |    |    |    |-- ItemDescription: string (nullable = true)
#  |    |    |    |-- ItemPrice: double (nullable = true)
#  |    |    |    |-- ItemQty: integer (nullable = true)
#  |    |    |    |-- TotalValue: double (nullable = true)
```

De la misma manera que hicimos en el caso anterior, vamos a realizar la operación `explode` para desenrollar las líneas de facturas (en este caso, con los campos de dirección incluidos) y luego renombramos los campos:

``` json
from pyspark.sql.functions import expr

explodeDF = valueDF.selectExpr("value.InvoiceNumber", "value.CreatedTime",
    "value.StoreID", "value.PosID", "value.CustomerType",
    "value.PaymentMethod", "value.DeliveryType", "value.DeliveryAddress.City",
    "value.DeliveryAddress.State", "value.DeliveryAddress.PinCode",
    "explode(value.InvoiceLineItems) as LineItem")

limpioDF = explodeDF \
    .withColumn("ItemCode", expr("LineItem.ItemCode")) \
    .withColumn("ItemDescription", expr("LineItem.ItemDescription")) \
    .withColumn("ItemPrice", expr("LineItem.ItemPrice")) \
    .withColumn("ItemQty", expr("LineItem.ItemQty")) \
    .withColumn("TotalValue", expr("LineItem.TotalValue")) \
    .drop("LineItem")
```

### Comprobando el resultado

Y finalmente creamos la consulta de *streaming*:

``` python
facturaWriterQuery  = limpioDF.writeStream \
    .format("json") \
    .queryName("Facturas Kafka Writer") \
    .outputMode("append") \
    .option("path", "salida") \
    .option("checkpointLocation", "chk-point-dir") \
    .trigger(processingTime="1 minute") \
    .start()

facturaWriterQuery.awaitTermination()
```

Una vez lanzado, volvemos a un terminal y creamos un productor:

``` bash
kafka-console-producer.sh --topic facturas --bootstrap-server iabd-virtualbox:9092
```

Y sobre el terminal, le pegamos una factura:

``` json
{"InvoiceNumber":"51402977","CreatedTime":1595688900348,"StoreID":"STR7188","PosID":"POS956","CashierID":"OAS134","CustomerType":"PRIME","CustomerCardNo":"4629185211","TotalAmount":11114.0,"NumberOfItems":4,"PaymentMethod":"CARD","TaxableAmount":11114.0,"CGST":277.85,"SGST":277.85,"CESS":13.8925,"DeliveryType":"TAKEAWAY","InvoiceLineItems":[{"ItemCode":"458","ItemDescription":"Wine glass","ItemPrice":1644.0,"ItemQty":2,"TotalValue":3288.0},{"ItemCode":"283","ItemDescription":"Portable Lamps","ItemPrice":2236.0,"ItemQty":1,"TotalValue":2236.0},{"ItemCode":"498","ItemDescription":"Carving knifes","ItemPrice":1424.0,"ItemQty":2,"TotalValue":2848.0},{"ItemCode":"523","ItemDescription":"Oil-lamp clock","ItemPrice":1371.0,"ItemQty":2,"TotalValue":2742.0}]}
```

Si nos vamos a la carpeta `salida`, veremos que ha creado un fichero con tantos documentos como líneas de factura tiene el documento anterior:

``` json
{"InvoiceNumber":"51402977","CreatedTime":1595688900348,"StoreID":"STR7188","PosID":"POS956","CustomerType":"PRIME","PaymentMethod":"CARD","DeliveryType":"TAKEAWAY","ItemCode":"458","ItemDescription":"Wine glass","ItemPrice":1644.0,"ItemQty":2,"TotalValue":3288.0}
{"InvoiceNumber":"51402977","CreatedTime":1595688900348,"StoreID":"STR7188","PosID":"POS956","CustomerType":"PRIME","PaymentMethod":"CARD","DeliveryType":"TAKEAWAY","ItemCode":"283","ItemDescription":"Portable Lamps","ItemPrice":2236.0,"ItemQty":1,"TotalValue":2236.0}
{"InvoiceNumber":"51402977","CreatedTime":1595688900348,"StoreID":"STR7188","PosID":"POS956","CustomerType":"PRIME","PaymentMethod":"CARD","DeliveryType":"TAKEAWAY","ItemCode":"498","ItemDescription":"Carving knifes","ItemPrice":1424.0,"ItemQty":2,"TotalValue":2848.0}
{"InvoiceNumber":"51402977","CreatedTime":1595688900348,"StoreID":"STR7188","PosID":"POS956","CustomerType":"PRIME","PaymentMethod":"CARD","DeliveryType":"TAKEAWAY","ItemCode":"523","ItemDescription":"Oil-lamp clock","ItemPrice":1371.0,"ItemQty":2,"TotalValue":2742.0}
```

Si nos dedicamos a pegar diferentes facturas (tienes más en [`facturasKafka.json`](resources/facturasKafka.json)), cada minuto se generará un nuevo archivo.

!!! caution "Limpieza"
    Recuerda que si quieres volver a ejecutar el código, debes eliminar la carpeta `chk-point-dir` así como la carpeta de `salida`.

## Caso 4: Produciendo a *Kafka*

Vamos a plantear que en vez de los ficheros de datos que generábamos con las líneas de las facturas, queremos crear un documento que contenga:

* código del cliente: `CustomerCardNo`
* cantidad total: `TotalAmount`
* puntos de fidelidad obtenidos: `EarnedLoyaltyPoints`, el cual se obtiene a partir de `TotalAmount` * `0.2`

<figure style="align: center;">
    <img src="images/03spark-caso4.png" width="600">
    <figcaption>Arquitectura caso 4</figcaption>
</figure>

Además, este documento que generamos lo queremos enviar a un nuevo *topic* de Kafka (`notificaciones`) para que lo consuma otra aplicación, indicando como clave el número de factura (`InvoiceNumber`) y como valor el documento creado.

Comenzamos de la misma forma que el caso anterior, creando los recursos de Kafka en diferentes terminales:

``` bash
zookeeper-server-start.sh ./config/zookeeper.properties
kafka-server-start.sh ./config/server.properties
kafka-topics.sh --create --topic facturas --bootstrap-server iabd-virtualbox:9092
kafka-topics.sh --create --topic notificaciones --bootstrap-server iabd-virtualbox:9092
```

A continuación, en nuestro cuaderno *Jupyter*, creamos la sesión y conectamos con Kafka:

``` python hl_lines="9-12"
from pyspark.sql import SparkSession
spark = SparkSession \
        .builder \
        .appName("Kafka Streaming Sink") \
        .master("local[3]") \
        .getOrCreate()

kafkaDFS = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "iabd-virtualbox:9092") \
        .option("subscribe", "facturas") \
        .option("startingOffsets", "earliest") \
        .load()
```

Y volvemos a definir el esquema:

``` python
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType, IntegerType, ArrayType
esquema = StructType([
    StructField("InvoiceNumber", StringType()),
    StructField("CreatedTime", LongType()),
    StructField("StoreID", StringType()),
    StructField("PosID", StringType()),
    StructField("CashierID", StringType()),
    StructField("CustomerType", StringType()),
    StructField("CustomerCardNo", StringType()),
    StructField("TotalAmount", DoubleType()),
    StructField("NumberOfItems", IntegerType()),
    StructField("PaymentMethod", StringType()),
    StructField("CGST", DoubleType()),
    StructField("SGST", DoubleType()),
    StructField("CESS", DoubleType()),
    StructField("DeliveryType", StringType()),
    StructField("DeliveryAddress", StructType([
        StructField("AddressLine", StringType()),
        StructField("City", StringType()),
        StructField("State", StringType()),
        StructField("PinCode", StringType()),
        StructField("ContactNumber", StringType())
    ])),
    StructField("InvoiceLineItems", ArrayType(StructType([
        StructField("ItemCode", StringType()),
        StructField("ItemDescription", StringType()),
        StructField("ItemPrice", DoubleType()),
        StructField("ItemQty", IntegerType()),
        StructField("TotalValue", DoubleType())
    ]))),
])

```

### Creando las notificaciones

Una vez hemos recuperado los datos con el esquema, vamos a elegir las columnas que necesitamos y posteriormente vamos a transformar el *DataFrame* para crear **solo dos columnas** (este es el requisito de los mensajes de *Kafka*), una formada por la clave que llamaremos `key` y que contendrá el campo `InvoiceNumber`, y otra columna que llamaremos `value` y contendrá el documento JSON serializado con los campos que nos interesan enviar al *topic* de `notificaciones`:

``` python
from pyspark.sql.functions import from_json, col, expr
valueDF = kafkaDFS.select(from_json(col("value").cast("string"), esquema).alias("value"))

notificationDF = valueDF.select("value.InvoiceNumber", "value.CustomerCardNo", "value.TotalAmount") \
    .withColumn("LoyaltyPoints", expr("TotalAmount * 0.2"))

# Transformamos las cuatro columnas en lo que espera Kafka, un par de (key, value)
kafkaTargetDF = notificationDF.selectExpr("InvoiceNumber as key",
        """to_json(named_struct(
        'CustomerCardNo', CustomerCardNo,
        'TotalAmount', TotalAmount,
        'EarnedLoyaltyPoints', TotalAmount * 0.2)) as value""")
```

La función `named_struct` crea un mapa formado por múltiples pares de (clave, valor), los cuales recibe de forma secuencial. Pues ver ejemplos de su uso de la mano de [`to_json`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.to_json.html) en la [documentación oficial](https://spark.apache.org/docs/latest/sql-ref-functions-builtin.html#json-functions).

!!! tip "Kafka Sink - CSV y Avro"
    Del mismo modo que hemos explicado antes, si queremos trabajar con CSV podemos utilizar la función [`to_csv`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.to_csv.html). En cambio, si el formato de nuestros datos fuera *Avro* utilizaríamos la función [`to_avro`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.avro.functions.to_avro.html).

Finalmente, lanzamos la consulta, destacando que para indicar el *topic* ahora utilizaremos la opción `topic` (en vez de `subscribe` que utilizamos en el *reader*) :

```  python hl_lines="4-6"
notificacionWriterQuery = kafkaTargetDF \
    .writeStream \
    .queryName("Notificaciones Writer") \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "iabd-virtualbox:9092") \
    .option("topic", "notificaciones") \
    .outputMode("append") \
    .option("checkpointLocation", "chk-point-dir") \
    .start()

notificacionWriterQuery.awaitTermination()
```

Para comprobar que funciona correctamente, una vez lanzada la consulta, volvemos a un terminal y creamos un consumidor que quede a la escucha del *topic* `notificaciones`:

``` bash
kafka-console-consumer.sh --topic notificaciones --from-beginning --bootstrap-server iabd-virtualbox:9092
```

Y tras ello, lanzamos un productor al *topic* `facturas`:

``` bash
kafka-console-producer.sh --topic facturas --bootstrap-server iabd-virtualbox:9092
```

Y sobre el terminal, le pegamos una factura al productor:

``` json
{"InvoiceNumber":"51402977","CreatedTime":1595688900348,"StoreID":"STR7188","PosID":"POS956","CashierID":"OAS134","CustomerType":"PRIME","CustomerCardNo":"4629185211","TotalAmount":11114.0,"NumberOfItems":4,"PaymentMethod":"CARD","TaxableAmount":11114.0,"CGST":277.85,"SGST":277.85,"CESS":13.8925,"DeliveryType":"TAKEAWAY","InvoiceLineItems":[{"ItemCode":"458","ItemDescription":"Wine glass","ItemPrice":1644.0,"ItemQty":2,"TotalValue":3288.0},{"ItemCode":"283","ItemDescription":"Portable Lamps","ItemPrice":2236.0,"ItemQty":1,"TotalValue":2236.0},{"ItemCode":"498","ItemDescription":"Carving knifes","ItemPrice":1424.0,"ItemQty":2,"TotalValue":2848.0},{"ItemCode":"523","ItemDescription":"Oil-lamp clock","ItemPrice":1371.0,"ItemQty":2,"TotalValue":2742.0}]}
```

Y veremos como el consumidor nos muestra el documento con las diferentes notificaciones:

``` json
{"CustomerCardNo":"4629185211","TotalAmount":11114.0,"EarnedLoyaltyPoints":2222.8}
{"CustomerCardNo":"2762345282","TotalAmount":8272.0,"EarnedLoyaltyPoints":1654.4}
{"CustomerCardNo":"2599848717","TotalAmount":3374.0,"EarnedLoyaltyPoints":674.8000000000001}
{"CustomerCardNo":"4629185211","TotalAmount":11114.0,"EarnedLoyaltyPoints":2222.8}
```

Más información en la [documentación oficial](https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html) sobre integración de *Kafka* con *Spark Streaming*.

## Referencias

* Documentación oficial sobre [Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
* [Stream Processing with Apache Spark](https://learning.oreilly.com/library/view/stream-processing-with/9781491944233/)
* [Beginning Apache Spark 3: With DataFrame, Spark SQL, Structured Streaming, and Spark Machine Learning Library](https://link.springer.com/book/10.1007/978-1-4842-7383-8)
* [Real-Time Stream Processing Using Apache Spark 3 for Python Developers](https://www.packtpub.com/product/real-time-stream-processing-using-apache-spark-3-for-python-developers-video/9781803246543)

## Actividades

1. Realiza el caso de uso 1 e introduce datos para generar 5 *micro-batchs*. Accede al Spark UI y comprueba los *jobs* y *stages* creados, y justifica su cantidad.

2. Realiza el caso de uso 2, adjuntado capturas de la carpeta `salida` tras la colocación de los datos de cada archivo de facturas en la carpeta de `entrada`. Finalmente muestra un resumen de las estadísticas tanto del plan de ejecución como de los últimos progresos.

3. Realiza los casos de uso 3 y 4 en un único cuaderno *Jupyter*, de manera que sólo haya un *reader*, pero creando dos *WriterQuery*. Hay dos aspectos que debes tener en cuenta:

    1. En vez de indicar en cada escritor que espere a que finalice:

        ``` python
        facturaWriterQuery.awaitTermination()
        notificacionWriterQuery.awaitTermination()
        ```

        Le diremos a *Spark* que espere que termine alguno de ellos mediante [awaitAnyTermination](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.streaming.StreamingQueryManager.awaitAnyTermination.html):

        ``` python
        spark.streams.awaitAnyTermination()
        ```

    2. Deberás configurar diferentes carpetas para `checkpointLocation` (cada *WriterQuery* debe tener su propia carpeta para los *checkpoints*)

4. El archivo [bizums.zip](resources/bizums.zip) contiene una simulación de datos de *bizum* que llegan a nuestra cuenta. Crea una aplicación de *Spark Streaming* que muestre para cada persona, cual es *bizum* más alto.

    Para ello, disponemos de un *script* *Python* que, al ejecutarlo, se encarga de simular el envío de *bizums*:

    ``` bash
    python3 Bizums.py
    ```

    El formato de estos datos es CSV formado por el `Nombre;Cantidad;Concepto` (dos nombres en mayúsculas y en minúsculas son de la misma persona). Un ejemplo de un *bizum* recibido sería similar a:

    ``` csv
    Aitor;25;Cena restaurante
    ```

    Muestra el resultado completo por consola.

<!--

(opcional) coger el dataset de iot de ventanas deslizantes de 15 minutos, y utilizar Kafka para leer los datos, mostrar temperatura máxima de los últimos 5 minutos

https://blog.coeo.com/databricks-structured-streaming-part2

https://www.mongodb.com/docs/spark-connector/master/python/write-to-mongodb/

Coger el ejercicio de Bizum, y generar los datos mediante Faker, poniendo la fecha del envío

-->