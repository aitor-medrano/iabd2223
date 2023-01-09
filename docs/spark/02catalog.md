---
title: Spark Catalog. DeltaLake. 
description: Acceso a bases de datos relacionales mediante JDBC en Spark.
---

# Spark JDBC y uso del catálogo

## Conectando con bases de datos

Para conectar desde [Spark con una base de datos relacional](https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html) (*RDBMS*) necesitamos:

* un driver JDBC compatible
* las [propiedades de conexión](https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html#data-source-option) a la base de datos.

En *PySpark*, el *driver* lo podemos añadir directamente a la carpeta `jars` disponible en `$SPARK_HOME`, o a la hora de lanzar *Spark* utilizando la opción `--jars <fichero1.jar>,<fichero2.jar>` o `--packages <groupId:artifactId:version>`.

Así pues, para conectar con nuestra base de datos `retail_db` que tenemos configurada en la máquina virtual, primero copiaremos el [driver de MySQL](resources/mysql-connector-j-8.0.31.jar) en la carpeta `$SPARK_HOME/jars`.

Si tuviéramos problemas a la hora de crear la conexión con la base de datos, indicaremos en la configuración qué archivos añadimos al *classpath*:

``` python
spark = SparkSession.builder.appName("s8a-dataframes-jdbc") \
    .config('spark.driver.extraClassPath', 'mysql-connector-j-8.0.31.jar') \
    .getOrCreate()
```

El siguiente paso es configurar la conexión a la base de datos:

``` python
url = "jdbc:mysql://localhost/retail_db"
propiedades = {
    "driver": "com.mysql.cj.jdbc.Driver",
    "user": "iabd",
    "password": "iabd"
}
```

!!! tip "Spark y MySQL con Docker"

    Para poder acceder a MySQL desde la imagen de Spark, necesitamos que formen parte de la misma red. Para ello, lo más cómodo es utilizar *Docker Compose* y definir las dependencias:

    ``` yaml
    services:
        spark:
            image: jupyter/pyspark-notebook
            container_name: iabd-spark
            ports:
                - "8888:8888"
                - "4040:4040"
                - "4041:4041"
            links:
                - mysql
            volumes:
                - ./:/home/jovyan/work
                - ./mysql-connector-j-8.0.31.jar:/usr/local/spark/jars/mysql-connector-j-8.0.31.jar
        mysql:
            image: mysql:latest
            container_name: iabd-mysql
            command: --default-authentication-plugin=mysql_native_password
            ports:
              - "3306:3306"
            environment:
              TZ: Europe/Madrid
              MYSQL_ROOT_PASSWORD: iabd
              MYSQL_DATABASE: retail_db
              MYSQL_USER: iabd
              MYSQL_PASSWORD: iabd
    ```

    Una vez colocado el [driver de MySQL](resources/mysql-connector-j-8.0.31.jar) en la misma carpeta, lanzamos *docker-compose*:

    ``` bash
    docker-compose -p iabd-spark-mysql up -d
    ```

    Tras arrancar los contenedores, la primera vez, deberemos cargar la [base de datos](resources/create_db.sql):

    ``` bash
    docker exec -i iabd-mysql mysql -h 0.0.0.0 -P 3306 -uiabd -piabd retail_db < create_db.sql
    ```

    A partir de aquí, es importante destacar que la *url* de conexión a la base de datos, en vez de acceder a `localhost`, lo hace al nombre del contenedor `iabd-mysql`:

    ``` python
    url = "jdbc:mysql://iabd-mysql/retail_db"
    ```

### Leyendo datos

Para finalmente cargar los datos mediante el método [`read.jdbc`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameReader.jdbc.html):

``` python
df = spark.read.jdbc(url=url,\
    table="customers",\
    properties=propiedades) 
```

Y sobre el *dataframe*, ya podemos obtener su esquema y realizar las transformaciones que necesitemos:

``` python
df.printSchema()
# root
#  |-- customer_id: integer (nullable = true)
#  |-- customer_fname: string (nullable = true)
#  |-- customer_lname: string (nullable = true)
#  |-- customer_email: string (nullable = true)
#  |-- customer_password: string (nullable = true)
#  |-- customer_street: string (nullable = true)
#  |-- customer_city: string (nullable = true)
#  |-- customer_state: string (nullable = true)
#  |-- customer_zipcode: string (nullable = true)
df.show(2)
# +-----------+--------------+--------------+--------------+-----------------+--------------------+-------------+--------------+----------------+
# |customer_id|customer_fname|customer_lname|customer_email|customer_password|     customer_street|customer_city|customer_state|customer_zipcode|
# +-----------+--------------+--------------+--------------+-----------------+--------------------+-------------+--------------+----------------+
# |          1|       Richard|     Hernandez|     XXXXXXXXX|        XXXXXXXXX|  6303 Heather Plaza|  Brownsville|            TX|           78521|
# |          2|          Mary|       Barrett|     XXXXXXXXX|        XXXXXXXXX|9526 Noble Embers...|    Littleton|            CO|           80126|
# +-----------+--------------+--------------+--------------+-----------------+--------------------+-------------+--------------+----------------+
# only showing top 2 rows
```

Si necesitamos configurar en más detalle la forma de recoger los datos, es mejor acceder mediante el método `format` (cuidado con el nombre de la tabla que ahora utiliza el atributo `dbtable`):

``` python hl_lines="1 3"
df_format = spark.read.format("jdbc") \
  .option("url", url_iabd) \
  .option("dbtable", "customers") \
  .option("user", "iabd") \
  .option("password", "iabd") \
  .load()
```

Un caso particular es cuando queremos asignarle a un *dataframe* el resultado de una consulta. Para ello, podemos indicarle en el parámetro `query` la consulta SQL con la información a recoger:

``` python
df_query = spark.read.format("jdbc") \
  .option("url", url_iabd) \
  .option("query", "(select customer_id, customer_fname, customer_lname from customers where customer_city='Las Vegas')") \
  .option("user", "iabd") \
  .option("password", "iabd") \
  .load()

df_query.printSchema()
# root
#  |-- customer_id: integer (nullable = true)
#  |-- customer_fname: string (nullable = true)
#  |-- customer_lname: string (nullable = true)
df_query.show(3)
# +-----------+--------------+--------------+
# |customer_id|customer_fname|customer_lname|
# +-----------+--------------+--------------+
# |         99|         Betty|         Munoz|
# |        204|          Mary|         Smith|
# |        384|       Mildred|    Cunningham|
# +-----------+--------------+--------------+
# only showing top 3 rows
```

!!! info "Más opciones"
    Más información sobre todas las opciones disponibles en la [documentación oficial](https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html#data-source-option).

### Escribiendo datos

Si lo que queremos es almacenar el resultado en una base de datos, utilizaremos el método [write.jdbc](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameWriter.jdbc.html) o `write.format('jdbc')` finalizando con [`save`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameWriter.save.html):

=== "write.jdbc()"

    ``` python
    df.write.jdbc(url=url, \
            table="<nueva_tabla>", \
            properties=propiedades) 
    ```

=== "write.format('jdbc')"

    ``` python
    df.write.format("jdbc") \
      .option("url", "<jdbc_url>") \
      .option("dbtable", "<nueva_tabla>") \
      .option("user", "<usuario>") \
      .option("password", "<contraseña>") \
      .save()
    ```

Por ejemplo, vamos a crear una copia del dataframes de clientes con sólo tres columnas, y almacenaremos este DataFrame en una nueva tabla:

``` python hl_lines="13 17"
jdbcSelectDF = jdbcDF.select("customer_id", "customer_fname", "customer_lname")
jdbcSelectDF.show(3)
# +-----------+--------------+--------------+
# |customer_id|customer_fname|customer_lname|
# +-----------+--------------+--------------+
# |          1|       Richard|     Hernandez|
# |          2|          Mary|       Barrett|
# |          3|           Ann|         Smith|
# +-----------+--------------+--------------+
# only showing top 3 rows
jdbcSelectDF.count()
# 12435
jdbcSelectDF.write.format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", "jdbc:mysql://iabd-mysql") \
    .option("dbtable", "retail_db.clientes") \
    .option("user", "iabd") \
    .option("password", "iabd") \
    .save()
```

Si accedemos a *MySQL*, podremos comprobar cómo se han insertado 12435 registros.

Si volvemos a realizar la persistencia de los datos, obtendremos un error porque la tabla ya existe. Para evitar este error, podemos añadir los datos a una tabla existente mediante el método [`mode`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameWriter.mode.html) con valor `append`, o para machacarlos con el valor `overwrite`:

``` python hl_lines="87"
jdbcSelectDF.write \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", "jdbc:mysql://localhost/retail_db") \
    .option("dbtable", "clientes2") \
    .option("user", "iabd") \
    .option("password", "iabd") \
    .mode("append") \
    .save()
```

!!! warning "overwrite borra la tabla"
    Mediante `mode("overwrite")`, la tabla se elimina y se vuelven a cargar los datos desde cero.
    Si queremos que se vuelvan a cargar los datos pero no se cree de nuevo la tabla (por que no queremos que se borren las claves ni los índices existentes), hemos de añadirle la opción `option("truncate", "true")` para que limpie la tabla pero sin eliminarla ni volver a crearla.

### Utilizando Databricks

Si trabajamos con *Databricks* y queremos [recuperar o almacenar datos via JDBC](https://docs.databricks.com/external-data/jdbc.html), ya tenemos parte del trabajo hecho porque tiene los *drivers* instalados (pero utiliza los *drivers* de *MariaDB* en vez de *MySQL*).

Así pues, por ejemplo, para recuperar los datos de una base de datos remota (por ejemplo, la base de datos que creamos en la sesión de [cloud con RDS](../cloud/06datos.md)) haríamos:

``` python
driver = "org.mariadb.jdbc.Driver"

database_host = "iabd-retail.cdexqeikfdkr.us-east-1.rds.amazonaws.com"
database_port = "3306"
database_name = "retail_db"
table = "customers"
user = "admin"
password = "adminadmin"

url = f"jdbc:mysql://{database_host}:{database_port}/{database_name}"

df_remoto = (spark.read
  .format("jdbc")
  .option("driver", driver)
  .option("url", url)
  .option("dbtable", table)
  .option("user", user)
  .option("password", password)
  .load()
)
```

Desde la versión 12 de *Databricks*, podemos utilizar directamente el formato `mysql` (o `postgresql` si fuera el caso):

``` python
df_remoto_mysql = (spark.read.format("mysql")
  .option("dbtable", table)
  .option("host", database_host)
  .option("port", 3306)
  .option("database", database_name)
  .option("user", user)
  .option("password", password)
  .load()
)
```

## Spark SQL Catalog

Los catálogos de datos son un elemento esencial dentro de una organización, al ofrecer una vista de los datos disponibles, los cuales se pueden extender para describir su creación (persona, equipo u organización). Este catálogo lo gestionan los ***data stewards***, un rol muy específico de los equipos *big data* que no solo se encargan de administrar el uso y los enfoques de los datos en la empresa, sino que tratan de asegurar la calidad de la información, el cumplimiento de las políticas de privacidad, la correcta comunicación entre los diferentes departamentos y la educación informática y tecnológica de los empleados relacionada con el mundo del dato.

Volviendo al catálogo de datos, el cual al final es un conjunto de metadatos, actúa como un contrato público que se establece durante la vida del dato, definiendo el cómo, cuándo y el porqué se consume un determinado dato, por ejemplo, indicando la disponibilidad de cada campo (por ejemplo, si tendrá un valor por defecto o nulo), así como reglas sobre la gobernanza y acceso de cada campo, etc...

El catálogo de datos por excelencia es el que forma parte de *Apache Hive*, y se conoce como el ***Hive Metastore***, el cual ofrece una fuente veraz para describir la localización, codificación de los datos (texto, Parquet, ORC, ...), el esquema de las columnas, y estadísticas de las tablas almacenadas para facilitar su uso a todos los roles que interactúan con los datos (ingenieros de datos, analistas, ingenieros de ML, ...)

### Bases de datos

El catálogo se organiza, en su primer nivel, en **bases de datos**, la cuales agrupan y categorizan las tablas que utiliza nuestro equipo de trabajo, permitiendo identificar su propietario y restringir el acceso. Dentro del *Hive Metastore*, una base de datos funciona como un prefijo dentro de una ruta física dentro de nuestro *data warehouse*, evitando colisiones entre nombres de tablas.

!!! tip "Una base de datos por equipo"
    Es conveniente que cada equipo de trabajo o unidad de negocio utilice sus propias bases de datos en Spark.

#### Accediendo al catálogo

En nuestra máquina virtual ya tenemos configurado el uso del *Hive Metastore* como catálogo de *Spark*. A partir de la sesión de *Spark*, podemos acceder al objeto [`catalog`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/catalog.html) que contiene un conjunto de métodos para interactuar con él.

Podemos comprobar su uso mediante una consulta a `show databases` o accediendo al método [`listDatabases()`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Catalog.listDatabases.html) del [`catalog`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/catalog.html):

``` python
spark.sql("show databases;").show()
# +---------+
# |namespace|
# +---------+
# |  default|
# |     iabd|
# +---------+
spark.catalog.listDatabases()
# [Database(name='default', description='Default Hive database', locationUri='hdfs://iabd-virtualbox:9000/user/hive/warehouse'),
#  Database(name='iabd', description='', locationUri='hdfs://iabd-virtualbox:9000/user/hive/warehouse/iabd.db')]
```

De manera que obtenemos las bases de datos que está utilizando actualmente (como puedes observar, son las bases de datos que hemos creado previamente en la sesión de [Hive](../hadoop/06hive.md)).

Si queremos vel cual nuestra base de datos activa, utilizaremos el método [`currentDatabase`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Catalog.currentDatabase.html):

``` python
spark.catalog.currentDatabase()
# 'default'
```

#### Creando una base de datos

De la misma manera que hemos creado sentencias SQL en Spark, podemos generar sentencias DDL y DML. Así pues, para crear una base de datos, hemos de hacer uso del API SQL y utilizar la sentencia DDL de [`CREATE DATABASE`](https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-create-database.html). Por ejemplo, vamos a crear una base de datos `s8a` donde colocaremos las tablas que crearemos en esta sesión:

``` python
spark.sql("create database if not exists s8a")
```

Una vez creada, la activamos mediante `use`:

``` python
spark.sql("use s8a")
```

FIXME: continuar https://learning.oreilly.com/library/view/modern-data-engineering/9781484274521/html/505711_1_En_6_Chapter.xhtml#PC17

### Trabajando con tablas

Vamos a suponer que tenemos el *DataFrame* de clientes que hemos cargado previamente desde JDBC, y creamos una vista sobre él:

``` python
jdbcDF = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", "jdbc:mysql://localhost") \
    .option("dbtable", "retail_db.customers") \
    .option("port", "3306") \
    .option("user", "iabd") \
    .option("password", "iabd") \
    .load()
jdbcDF.createOrReplaceTempView("clientes")
```

Si comprobamos las tablas de nuestra base de datos mediante el método [`listTables`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Catalog.listTables.html), aparecerá la vista como una tabla temporal (`TEMPORARY`), lo que significa que sólo está disponible en memoria:

``` python
spark.catalog.listTables()
# [Table(name='clientes', database=None, description=None, tableType='TEMPORARY', isTemporary=True)]
```

Al ser temporal, al detener *Spark*, dicha tabla desaparecerá. Si queremos que la tabla esté disponible en nuestro *data lake* y que podamos consultarla desde el catálogo del *Hive Metastore*, necesitamos persistirla.

#### Persistiendo tablas

Cuando tenemos un *DataFrame* lo podemos persistir como una tabla, lo que en terminología de *Hive* sería una tabla interna o gestionada, mediante [`saveAsTable`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameWriter.saveAsTable.html):

``` python
jdbcDF.write.mode("errorIfExists") \  # (1)!
      .saveAsTable("clientes")
```

1. Hemos configurado el modo de escritura a `errorIfExists` para asegurarnos que no borramos ningún datos de nuestro *datalake*.

Si volvemos a comprobar las tablas, podemos ver como la nueva tabla ahora forma parte de la base de datos `s8a` y que tu tipo es `MANAGED`:

``` python
spark.catalog.listTables()
# [Table(name='clientes', database='s8a', description=None, tableType='MANAGED', isTemporary=False),
#  Table(name='clientes', database=None, description=None, tableType='TEMPORARY', isTemporary=True)]
```

Podemos configurar diferentes opciones a la hora de persistir las tablas. Por ejemplo, si queremos persistir la tabla en formato JSON sobrescribiendo los datos hemos de indicarlo con `format('json')` y `mode('overwrite')`:

``` python
jdbcDF.write.format("json").mode("overwrite").saveAsTable("clientesj")
```

!!! info "Por defecto en formato Parquet"
    Por defecto, al persistir una tabla, se realiza en formato *Parquet* y comprimido mediante *Snappy*.

#### Tablas externas

FIXME: revisar y reescribir ... probar con la MV

Si queremos crear una tabla no gestionada, también conocida como tabla externa, la cual puede que se almacenen como [tablas en Hive](https://spark.apache.org/docs/latest/sql-data-sources-hive-tables.html),necesitamos indicar la ruta de los datos en el momento de creación:

``` python
spark.sql("""CREATE TABLE ventasext(ProductID INT, Date STRING, 
  Zip STRING, Units INT, Revenue DOUBLE, Country STRING) 
  USING csv OPTIONS (PATH 
  '/pdi_sales_small.csv')""")
```

Para ello, necesitamos colocar el archivo de datos dentro del almacén del *metastore*, que en nuestro caso es `spark-warehouse/s8a.db/`

También podemos crear la tabla indicando la [opción `path`](https://spark.apache.org/docs/latest/sql-data-sources-load-save-functions.html#saving-to-persistent-tables):

``` python
df.write.option("path", "/user/iabd/clientes").saveAsTable("clientes_ext")
```

#### Cargando tablas

Una vez las tablas ya están persistidas, en cualquier momento podemos recuperarlas y asociarlas a un nuevo *DataFrame* mediante el método [`table`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameReader.table.html):

``` python
df_clientes = spark.table("clientes")
df_clientes.printSchema()
# root
#  |-- customer_id: integer (nullable = true)
#  |-- customer_fname: string (nullable = true)
#  |-- customer_lname: string (nullable = true)
#  |-- customer_email: string (nullable = true)
#  |-- customer_password: string (nullable = true)
#  |-- customer_street: string (nullable = true)
#  |-- customer_city: string (nullable = true)
#  |-- customer_state: string (nullable = true)
#  |-- customer_zipcode: string (nullable = true)
```

#### Cacheando tablas

En la [sesión anterior](02agregaciones.md#persistencia) estudiamos cómo persistir los *DataFrames* y vimos como también podemos persistir una vista, incluso cómo comprobar su estado en el Spark UI.

Para cachear tablas, usaremos el método [`cacheTable`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Catalog.cacheTable.html):

``` python
spark.catalog.cacheTable("clientes")
```

Si por el contrario, queremos liberar la memoria de una tabla que ha sido cacheada, usaremos el método [`uncacheTable`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Catalog.uncacheTable.html):

``` python
spark.catalog.uncacheTable("clientes")
```

Si queremos limpiar toda la caché, disponemos del método [`clearCache`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Catalog.clearCache.html):

``` python
spark.catalog.clearCache()
```

!!! tip "Refrescando la caché"
    Un caso muy común al trabajar con datos cacheados es que desde una aplicación externa se actualicen los datos y la caché contenga una copia obsoleta.

    Para refrescar los datos, podemos utilizar el método [`refreshTable`](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Catalog.refreshTable.html):

    ``` python
    spark.catalog.refreshTable("clientes")
    ```

    Un punto a destacar es que si una aplicación Spark sobrescribe una tabla que habíamos cacheado, Spark directamente invalidará la caché local, de manera que no será necesario que en nuestra lógica de aplicación refresquemos las tablas de forma explícita.
    
    Sólo lo haremos si la sobrescritura de los datos la realiza una aplicación ajena a Spark sobre una tabla externa.

#### Borrando tablas

Si dejamos de utilizar una tabla y la queremos eliminar del *Metastore*, podemos realizarlo directamente mediante su sentencia de DDL [`DROP TABLE`](https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-drop-table.html#drop-table):

``` python
spark.sql("DROP TABLE IF EXISTS cliente")
```

### Descubriendo datos

FIXME: hacer con la MV

<https://learning.oreilly.com/library/view/modern-data-engineering/9781484274521/html/505711_1_En_6_Chapter.xhtml#:-:text=Databases%20and%20Tables%20in%20the%20Hive%20Metastore>

REVISAR la asignación de comentarios a las tablas y a las columnas
Cuaderno Jupyter Catalog de Docker

## DeltaLake

https://learning.oreilly.com/library/view/delta-lake-up/9781098139711/ch01.html#delta_lake


En 2019, DataBricks liberó el proyecto DeltaLake como open source para persistencia de datos.

Las características principales de DeltaLake son:

* Transacciones ACID, asegurando la integridad y fiabilidad en las transacciones sobre los archivos.
* Escalabilidad de los metadatos
* Time Travel, facilitando la creación de *snapshots* sobre los datos.
* Formato Parquet
* Permite trabajar en batch y streaming
* Historial de cambios
* Permite el borrados y *upserts* sobre los datos.
* 100% compatible con Apache Spark

Al arrancar Spark, le pone como package io.delta:delta-core_2.12:1.1.0

A la hora de escribir un df, le indicamos como format("delta")

!!! info "Probando DeltaLake"
    Para poder realizar los ejemplos y practicar *DeltaLake*, en esta sesión nos vamos a centrar en la máquina virtual o mediante *DataBricks*, ya que no existe (de momento) una imagen que *DeltaLake* para *Docker*.

### vacuum

Cuando hacemos un overwrite de los datos, cada vez guarda una copia de lo que había y lo nuevo ... esto puede provocar que se llene el disco de los workers .... para eso está el vacuum, por ejemplo, 7 días, y significa que va a guardar el histórico de los últimos 7 días.

Por cada 10 operaciones que aparezca en los logs con json, se crea un archivo Parquet.

<!--
Spark DeltaLake:
https://towardsdatascience.com/from-data-lakes-to-data-reservoirs-aa2efebb4f25

https://delta.io/learn/getting-started

https://www.datio.com/bbdd/potenciando-los-datos-con-delta-lake/
https://learn.microsoft.com/es-es/azure/databricks/delta/

Spark - Minio
https://rhuanca.medium.com/on-premise-delta-lake-con-minio-da87f5f2b331
-->


## Referencias

* [Modern Data Engineering with Apache Spark - Scott Haines - Apress](https://learning.oreilly.com/library/view/modern-data-engineering/9781484274521/)
* [Delta Lake: Up and Running - Bennie Haelen - O'Reilly](https://learning.oreilly.com/library/view/delta-lake-up/9781098139711/)

## Actividades

1. Cargar un par de tablas desde retail_db. Realizar un join en un nuevo DataFrame. Persistir en una nueva tabla de la BD.
2. Crear una tabla gestionada a partir del ejercicio anterior. Añadir un comentario a la tabla y a todas las columnas.
Cachear la tabla.
3. Crear un ejemplo básico con DeltaLake