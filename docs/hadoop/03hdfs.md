---
title: HDFS, acceso y gestión. HDFS y Python. Formatos de datos Avro y Parquet.
description: Funcionamiento de HDFS, estudiando los procesos de lectura y escritura, los comandos de administración y el uso de Snapshots. Almacenamiento de datos en formatos Avro y Parquet mediante Python.
---

# HDFS

## Funcionamiento de HDFS

En la sesión anterior hemos estudiado los diferentes componentes que forman parte de HDFS: *namenode* y *datanodes*. En esta sesión veremos los procesos de lectura y escritura, aprenderemos a interactuar con HDFS mediante comandos, el uso de instantáneas y practicaremos con los formatos de datos más empleados en *Hadoop*, como son *Avro* y *Parquet*.

### Procesos de lectura

Vamos a entender como fluyen los datos en un proceso de lectura entre el cliente y HDFS a partir de la siguiente imagen:

<figure style="align: center;">
    <img src="images/03hdfs-read.png">
    <figcaption>Proceso de lectura</figcaption>
</figure>

1. El cliente abre el fichero que quiere leer mediante el método `open()` del sistema de archivos distribuido.
2. Éste llama al *namenode* mediante una RPC (llamada a procedimiento remoto) el cual le indica la localización del primer bloque del fichero. Para cada bloque, el *namenode* devuelve la dirección de los *datanodes* que tienen una copia de ese bloque. Además, los *datanodes* se ordenan respecto a su proximidad con el cliente (depende de la topología de la red y despliegue en *datacenter/rack/nodo*). Si el cliente en sí es un *datanode*, la lectura la realizará desde su propio sistema local.
3. El sistema de ficheros distribuido devuelve al cliente un *FSDataInputStream* (un flujo de entrada que soporta la búsqueda de ficheros), sobre el cual se invoca la lectura mediante el método `read()`. Este flujo, que contiene las direcciones de los *datanodes* para los primeros bloques del fichero, conecta con el *datanode* más cercano para la lectura del primer bloque.
4. Los datos se leen desde el *datanode* con llamadas al método `read()`. Cuando se haya leído el bloque completo, el flujo de entrada cerrará la conexión con el *datanode* actual y buscará el mejor *datanode* para el siguiente bloque.
5. Se repite el paso anterior (siempre de manera transparente para el cliente, el cual solo está leyendo datos desde un flujo de datos continuo).
6. Cuando el cliente finaliza la lectura, cierra la conexión con el flujo de datos.

Durante la lectura, si el flujo encuentra un error al comunicarse con un *datanode* (o un error de *checksum*), intentará el proceso con el siguiente nodo más cercano (además, recordará los nodos que han fallado para no realizar reintentos en futuros bloques y/o informará de los bloque corruptos al *namenode*)

!!! importante "Namenode sin datos"
    Recordad que los datos nunca pasan por el *namenode*. El cliente que realiza la conexión con HDFS es el que hace las operaciones de lectura/escritura directamente con los *datanodes*.
    Este diseño permite que HDFS escale de manera adecuada, ya que el tráfico de los clientes se esparce por todos los *datanodes* de nuestro clúster.

### Proceso de escritura

El proceso de escritura en HDFS sigue un planteamiento similar. Vamos a analizar la creación, escritura y cierre de un archivo con la siguiente imagen:

<figure style="align: center;">
    <img src="images/03hdfs-write.png">
    <figcaption>Proceso de escritura</figcaption>
</figure>

1. El cliente crea el fichero mediante la llamada al método `create()` del *DistributedFileSystem*.
2. Este realiza una llamada RPC al *namenode* para crear el fichero en el sistema de ficheros del *namenode*, sin ningún bloque asociado a él. El *namenode* realiza varias comprobaciones para asegurar que el fichero no existe previamente y que el usuario tiene los permisos necesarios para su creación. Tras ello, el *namenode* determina la forma en que va a dividir los datos en bloques y qué *datanodes* utilizará para almacenar los bloques.
3. El *DistributedFileSystem* devuelve un *FSDataOutputStream*  el cual gestiona la comunicación con los datanodes y el *namenode* para que el cliente comience a escribir los datos de cada bloque en el *namenode* apropiado.
4. Conforme el cliente escribe los datos, el flujo obtiene del *namenode* una lista de datanodes candidatos para almacenar las réplicas. La lista de nodos forman un *pipeline*, de manera que si el factor de replicación es 3, habrá 3 nodos en el *pipeline*. El flujo envía los paquete al primer datanode del pipeline, el cual almacena cada paquete y los reenvía al segundo datanode del *pipeline*. Y así sucesivamente con el resto de nodos del pipeline.
5. Cuando todos los nodos han confirmado la recepción y almacenamiento de los paquetes, envía un paquete de confirmación al flujo.
6. Cuando el cliente finaliza con la escritura de los datos, cierra el flujo mediante el método `close()` el cual libera los paquetes restantes al pipeline de datanodes y queda a la espera de recibir las confirmaciones. Una vez confirmado, le indica al *namenode* que la escritura se ha completado, informando de los bloques finales que conforman el fichero (puede que hayan cambiado respecto al paso 2 si ha habido algún error de escritura).

### HDFS por dentro

HDFS utiliza de un conjunto de ficheros que gestionan los cambios que se producen en el clúster.

Primero entramos en `$HADOOP_HOME/etc/hadoop` y averiguamos la carpeta de datos que tenemos configurada en `hdfs-site.xml` para el *namenode*:

``` xml title="hdfs-site.xml"
<property>
    <name>dfs.name.dir</name>
    <value>file:///opt/hadoop-data/hdfs/namenode</value>
</property>
```

Desde nuestro sistema de archivos, accedemos a dicha carpeta y vemos que existe una carpeta `current` que contendrá un conjunto de ficheros cuyos prefijos son:

* `edits_000NNN`: histórico de cambios que se van produciendo.
* `edits_inprogress_NNN`: cambios actuales en memoria que no se han persistido.
* `fsimagen_000NNN`: *snapshot* en el tiempo del sistema de ficheros.

<figure align="center">
    <img src="images/03hdfsPorDentro.png">
    <figcaption>HDFS por dentro</figcaption>
</figure>

Al arrancar HDFS se carga en memoria el último fichero `fsimage` disponible junto con los `edits` que no han sido procesados. Mediante el *secondary namenode*, cuando se llena un bloque, se irán sincronizando los cambios que se producen en `edits_inprogress` creando un nuevo `fsimage` y un nuevo `edits`.

Así pues, cada vez que se reinicie el *namenode*, se realizará el *merge* de los archivos `fsimage` y `edits log`.

## Trabajando con HDFS

Para interactuar con el almacenamiento desde un terminal, se utiliza el comando `hdfs`. Este comando admite un segundo parámetro con diferentes opciones.

Antes la duda, es recomendable consultar la [documentación oficial](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HDFSCommands.html)

``` bash
hdfs comando
```

!!! info "hadoop fs"
    <figure style="float: left; padding-right: 20px">
        <img src="images/03hdfsdfs.png" width="250">
        <figcaption>HDFS DFS</figcaption>
    </figure>

    `hadoop fs` se relaciona con un sistema de archivos genérico que puede apuntar a cualquier sistema de archivos como local, HDFS, FTP, S3, etc. En versiones anteriores se utilizaba el comando `hadoop dfs` para acceder a HDFS, pero ya quedado obsoleto en favor de `hdfs dfs`.

En el caso concreto de interactuar con el sistema de ficheros de Hadoop se utiliza el comando `dfs`, el cual requiere de otro argumento (empezando con un guión) el cual será uno de los comandos Linux para interactuar con el shell. Podéis consultar la lista de comandos en la [documentación oficial](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/FileSystemShell.html).

``` bash
hdfs dfs -comandosLinux
```

Por ejemplo, para mostrar todos los archivos que tenemos en el raíz haríamos:

``` bash
hdfs dfs -ls
```

Los comandos más utilizados son:

* `put`: Coloca un archivo dentro de HDFS
* `get`: Recupera un archivo de HDFS y lo lleva a nuestro sistema *host*.
* `cat` / `text` / `head` / `tail`: Visualiza el contenido de un archivo.
* `mkdir` / `rmdir`: Crea / borra una carpeta.
* `count`: Cuenta el número de elementos (número de carpetas, ficheros, tamaño y ruta).
* `cp` / `mv` / `rm`: Copia / mueve-renombra / elimina un archivo.

!!! question "Autoevaluación"

    ¿Sabes qué realiza cada uno de los siguientes comandos?

    ``` bash
    hdfs dfs -mkdir /user/iabd/datos
    hdfs dfs -put ejemplo.txt /user/iabd/datos/
    hdfs dfs -put ejemplo.txt /user/iabd/datos/ejemploRenombrado.txt
    hdfs dfs -ls datos
    hdfs dfs -count datos
    hdfs dfs -mv datos/ejemploRenombrado.txt /user/iabd/datos/otroNombre.json
    hdfs dfs -get /datos/otroNombre.json /tmp
    ```

### Bloques

A continuación vamos a ver cómo trabaja internamente HDFS con los bloques. Para el siguiente ejemplo, vamos a trabajar con un archivo que ocupe más de un bloque, como puede ser [El registro de taxis amarillos de Nueva York - Enero 2020](https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2020-01.csv).

Comenzaremos creando un directorio dentro de HDFS llamado `prueba-hdfs`:

``` bash
hdfs dfs -mkdir /user/iabd/prueba-hdfs
```

Una vez creado subimos el archivo con los taxis:

``` bash
hdfs dfs -put yellow_tripdata_2020-01.csv  /user/iabd/prueba-hdfs
```

Con el fichero subido nos vamos al interfaz gráfico de Hadoop (<http://iabd-virtualbox:9870/explorer.html#/>), localizamos el archivo y obtenemos el *Block Pool ID* del *block information*:

<figure style="align: center;">
    <img src="images/03hdfs-blockid.png">
    <figcaption>Identificador de bloque</figcaption>
</figure>

Si desplegamos el combo de *block information*, podremos ver cómo ha partido el archivo CSV en 5 bloques (566 MB que ocupa el fichero CSV / 128 del tamaño del bloque).

Así pues, con el código del *Block Pool Id*, podemos confirmar que debe existir el directorio `current` del *datanode* donde almacena la información nuestro servidor (en `/opt/hadoop-data/):

``` bash
ls /opt/hadoop-data/hdfs/datanode/current/BP-481169443-127.0.1.1-1639217848073/current
```

Dentro de este subdirectorio existe otro `finalized`, donde *Hadoop* irá creando una estructura de subdirectorios `subdir` donde albergará los bloques de datos:

``` bash
ls /opt/hadoop-data/hdfs/datanode/current/BP-481169443-127.0.1.1-1639217848073/current/finalized/subdir0
```

Una vez en este nivel, vamos a buscar el archivo que coincide con el *block id* poniéndole como prefijo `blk_`:

``` bash
find -name blk_1073743451
```

En mi caso devuelve `./subdir6/blk_1073743451`. De manera que ya podemos comprobar como el inicio del documento se encuentra en dicho archivo:

``` bash
head /opt/hadoop-data/hdfs/datanode/current/BP-481169443-127.0.1.1-1639217848073/current/finalized/subdir0/subdir6/blk_1073743451
```

### Administración

Algunas de las opciones más útiles para administrar HDFS son:

* `hdfs dfsadmin -report`: Realiza un resumen del sistema HDFS, similar al que aparece en el interfaz web, donde podemos comprobar el estado de los diferentes nodos.
* `hdfs fsck`: Comprueba el estado del sistema de ficheros. Si queremos comprobar el estado de un determinado directorio, lo indicamos mediante un segundo parámetro: `hdfs fsck /datos/prueba`
* `hdfs dfsadmin -printTopology`: Muestra la topología, identificando los nodos que tenemos y al rack al que pertenece cada nodo.
* `hdfs dfsadmin -listOpenFiles`: Comprueba si hay algún fichero abierto.
* `hdfs dfsadmin -safemode enter`: Pone el sistema en modo seguro el cual evita la modificación de los recursos del sistema de archivos.

### *Snapshots*

Mediante las *snapshots* podemos crear una instantánea que almacena cómo está en un determinado momento nuestro sistema de ficheros, a modo de copia de seguridad de los datos, para en un futuro poder realizar una recuperación.

El primer paso es activar el uso de *snapshots*, mediante el comando de administración indicando sobre qué carpeta vamos a habilitar su uso:

``` bash
hdfs dfsadmin -allowSnapshot /user/iabd/datos
```

El siguiente paso es crear una *snapshot*, para ello se indica tanto la carpeta como un nombre para la captura (es un comando que se realiza sobre el sistema de archivos):

``` bash
hdfs dfs -createSnapshot /user/iabd/datos snapshot1
```

Esta captura se creará dentro de una carpeta oculta dentro de la ruta indicada (en nuestro caso creará la carpeta  `/user/iabd/datos/.snapshot/snapshot1/` la cual contendrá la información de la instantánea).

A continuación, vamos a borrar uno de los archivo creados anteriormente y comprobar que ya no existe:

``` bash
hdfs dfs -rm /user/iabd/datos/ejemplo.txt
hdfs dfs -ls /user/iabd/datos
```

Para comprobar el funcionamiento de los *snapshots*, vamos a recuperar el archivo desde la captura creada anteriormente.

``` bash
hdfs dfs -cp \
    /user/iabd/datos/.snapshot/snapshot1/ejemplo.txt \
    /user/iabd/datos
```

Si queremos saber que carpetas soportan las instantáneas:

``` bash
hdfs lsSnapshottableDir
```

Finalmente, si queremos deshabilitar las *snapshots* de una determinada carpeta, primero hemos de eliminarlas y luego deshabilitarlas:

``` bash
hdfs dfs -deleteSnapshot /user/iabd/datos snapshot1
hdfs dfsadmin -disallowSnapshot /user/iabd/datos
```

### HDFS UI

En la sesión anterior ya vimos que podíamos acceder al interfaz gráfico de Hadoop (<http://iabd-virtualbox:9870/explorer.html#/>) y navegar por las carpetas de HDFS.

Si intentamos crear una carpeta o eliminar algún archivo recibimos un mensaje del tipo *Permission denied: user=dr.who, access=WRITE, inode="/":iabd:supergroup:drwxr-xr-x*. Por defecto, los recursos via web los crea el usuario *dr.who*.

<figure style="align: center;">
    <img src="images/03hdfs-ui-error.png">
    <figcaption>Error al crear un directorio mediante Hadoop UI</figcaption>
</figure>

Si queremos habilitar los permisos para que desde este IU podamos crear/modificar/eliminar recursos, podemos cambiar permisos a la carpeta:

``` bash
hdfs dfs -mkdir /user/iabd/pruebas
hdfs dfs -chmod 777 /user/iabd/pruebas 
```

Si ahora accedemos al interfaz, sí que podremos trabajar con la carpeta `pruebas` via web, teniendo en cuenta que las operaciones las realiza el usuario `dr.who` que pertenece al grupo `supergroup`.

Otra posibilidad es modificar el archivo de configuración `core-site.xml` y añadir una propiedad para modificar el usuario estático:

``` xml title="core-site.xml"
<property>
    <name>hadoop.http.staticuser.user</name>
    <value>iabd</value>
</property>
```

Tras reiniciar *Hadoop*, ya podremos crear los recursos como el usuario `iabd`.

## HDFS y Python

Para el acceso mediante Python a HDFS podemos utilizar la librería HdfsCLI (<https://hdfscli.readthedocs.io/en/latest/>).

Primero hemos de instalarla mediante `pip`:

``` bash
pip install hdfs
```

Vamos a ver un sencillo ejemplo de lectura y escritura en HDFS:

``` python
from hdfs import InsecureClient

# Datos de conexión
HDFS_HOSTNAME = 'iabd-virtualbox'
HDFSCLI_PORT = 9870
HDFSCLI_CONNECTION_STRING = f'http://{HDFS_HOSTNAME}:{HDFSCLI_PORT}'

# En nuestro caso, al no usar Kerberos, creamos una conexión no segura
hdfs_client = InsecureClient(HDFSCLI_CONNECTION_STRING)

# Leemos el fichero de 'El quijote' que tenemos en HDFS
fichero = '/user/iabd/el_quijote.txt'
with hdfs_client.read(fichero) as reader:
    texto = reader.read()

print(texto)

# Creamos una cadena con formato CSV y la almacenamos en HDFS
datos="nombre,apellidos\nAitor,Medrano\nPedro,Casas"
hdfs_client.write("/user/iabd/datos.csv", datos)
```

En el mundo real, los formatos de los archivos normalmente serán *Avro* y/o *Parquet*, y el acceso lo realizaremos en gran medida mediante la librería de *Pandas*.

## Hue

[Hue](https://gethue.com) (*Hadoop User Experience*) es una interfaz gráfica de código abierto basada en web para su uso con *Apache Hadoop*. *Hue* actúa como front-end para las aplicaciones que se ejecutan en el clúster, lo que permite interactuar con las aplicaciones mediante una interfaz más amigable que el interfaz de comandos.

En nuestra máquina virtual ya lo tenemos instalado y configurado para que funcione con HDFS y Hive.

La ruta de instalación es `/opt/hue-4.10.0` y desde allí, arrancaremos Hue:

``` bash
./build/env/bin/hue runserver
```

Tras arrancarlo, nos dirigimos a `http://127.0.0.1:8000/`y visualizaremos el formulario de entrada, el cual entraremos con el usuario `iabd` y la contraseña `iabd`:

<figure style="align: center;">
    <img src="images/03hue-login.png">
    <figcaption>Login en Hue</figcaption>
</figure>

Una vez dentro, por ejemplo, podemos visualizar e interactuar con HDFS:

<figure style="align: center;">
    <img src="images/03hue-hdfs.png">
    <figcaption>HDFS en Hue</figcaption>
</figure>

## Referencias

* Documentación de [Apache Hadoop](https://hadoop.apache.org/docs/stable/).
* [Hadoop: The definitive Guide, 4th Ed - de Tom White - O'Reilly](https://www.oreilly.com/library/view/hadoop-the-definitive/9780596521974/)
* [HDFS Commands, HDFS Permissions and HDFS Storage](https://www.informit.com/articles/article.aspx?p=2755708)
* [Introduction to Data Serialization in Apache Hadoop](https://www.xenonstack.com/blog/data-serialization-hadoop)
* [Handling Avro files in Python](https://www.perfectlyrandom.org/2019/11/29/handling-avro-files-in-python/)
* [Native Hadoop file system (HDFS) connectivity in Python](https://wesmckinney.com/blog/python-hdfs-interfaces/)

## Actividades

Para los siguientes ejercicios, copia el comando y/o haz una captura de pantalla donde se muestre el resultado de cada acción.

1. Explica paso a paso  el proceso de lectura (indicando qué bloques y los datanodes empleados) que realiza HDFS si queremos leer el archivo `/logs/101213.log`:

    <figure style="align: center;">
        <img src="images/03hdfs-lectura-ejercicio.png">
        <figcaption>Proceso de lectura HDFS</figcaption>
    </figure>

2. En este ejercicio vamos a practicar los comandos básicos de HDFS. Una vez arrancado *Hadoop*:
    1. Crea la carpeta `/user/iabd/ejercicios`.
    2. Sube el archivo `el_quijote.txt` a la carpeta creada.
    3. Crea una copia en HDFS y llámala `el_quijote2.txt`.
    4. Recupera el principio del fichero `el_quijote2.txt`.
    5. Renombra `el_quijote2.txt` a `el_quijote_copia.txt`.
    6. Adjunta una captura desde el interfaz web donde se vean ambos archivos.
    7. Vuelve al terminal y elimina la carpeta con los archivos contenidos mediante un único comando.

3. (opcional) Vamos a practicar los comandos de gestión de instantáneas y administración de HDFS. Para ello:
    1. Crea la carpeta `/user/iabd/instantaneas`.
    2. Habilita las *snapshots* sobre la carpeta creada.
    3. Sube el archivo `el_quijote.txt` a la carpeta creada.
    4. Crea una copia en HDFS y llámala `el_quijote_snapshot.txt`.
    5. Crea una instantánea de la carpeta llamada `ss1`.
    6. Elimina ambos ficheros del quijote.
    7. Comprueba que la carpeta está vacía.
    8. Recupera desde `ss` el archivo `el_quijote.txt`.
    9. Crea una nueva instantánea de la carpeta llamada `ss2`.
    10. Muestra el contenido de la carpeta `/user/iabd/instantaneas` así como de sus *snapshots*.

4. (opcional) HDFS por dentro
    1. Accede al archivo de configuración `hdfs-site.xml` y averigua la carpeta donde se almacena el *namenode*.
    2. Muestra los archivos que contiene la carpeta `current` dentro del *namenode*
    3. Comprueba el id del archivo `VERSION`.
    4. En los siguientes pasos vamos a realizar un checkpoint manual para sincronizar el sistema de ficheros. Para ello entramos en modo *safe* con el comando `hdfs dfsadmin -safemode enter`, de manera que impedamos que se trabaje con el sistema de ficheros mientras lanzamos el *checkpoint*.
    5. Comprueba mediante el interfaz gráfico que el modo seguro está activo (*Safe mode is ON*).
    6. Ahora realiza el checkpoint con el comando `hdfs dfsadmin -saveNamespace`
    7. Vuelve a entrar al modo normal (saliendo del modo seguro mediante `hdfs dfsadmin -safemode leave`)
    8. Accede a la carpeta del *namenode* y comprueba que los *fsimage* del *namenode* son iguales.

FIXME: completar HDFS con documento 2 del MEC de SBD sobre teoría de discos RAID