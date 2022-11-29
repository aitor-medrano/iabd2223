# AWS Elastic Map Reduce


Es un servicio de Amazon Web Services que permite crear clusters Hadoop a demanda.
• Utiliza una distribución propia de Amazon que permite seleccionar los componentes que van a
lanzarse en el cluster (Hive, Spark, etc.).
• Ofrece elasticidad: modificar dinámicamente el dimensionamiento del cluster según necesidades.
• Se ejecuta sobre máquinas EC2 (IaaS).
• Pago por uso: el coste asociado es el alquiler de las máquinas por horas más un sobrecoste de
aproximadamente el 25%.
• Ejemplo de coste aproximado:
20 nodos con 122 Gb RAM, 16 vCPU: 32 €/h.
Para ejecutar una tarea de 10h: 320 €.
Con 200 nodos: duración = 1 hora, coste = 320 €.

Arrancar EMR con instancias m4.large
Seguridad: vockey

Descargar claves:
Conectar mediante SSH

``` bash
ssh -i labsuser.pem hadoop@ec2-75-101-186-154.compute-1.amazonaws.com
The authenticity of host 'ec2-75-101-186-154.compute-1.amazonaws.com (75.101.186.154)' can't be established.
ECDSA key fingerprint is SHA256:ZDeS9KrmmJP1vCdPDgRXUMZUpMuuOiLSGvX8qERbFaI.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'ec2-75-101-186-154.compute-1.amazonaws.com,75.101.186.154' (ECDSA) to the list of known hosts.
Last login: Thu Nov 24 12:19:03 2022

       __|  __|_  )
       _|  (     /   Amazon Linux 2 AMI
      ___|\___|___|

https://aws.amazon.com/amazon-linux-2/
22 package(s) needed for security, out of 32 available
Run "sudo yum update" to apply all updates.

EEEEEEEEEEEEEEEEEEEE MMMMMMMM           MMMMMMMM RRRRRRRRRRRRRRR
E::::::::::::::::::E M:::::::M         M:::::::M R::::::::::::::R   
EE:::::EEEEEEEEE:::E M::::::::M       M::::::::M R:::::RRRRRR:::::R
  E::::E       EEEEE M:::::::::M     M:::::::::M RR::::R      R::::R
  E::::E             M::::::M:::M   M:::M::::::M   R:::R      R::::R
  E:::::EEEEEEEEEE   M:::::M M:::M M:::M M:::::M   R:::RRRRRR:::::R
  E::::::::::::::E   M:::::M  M:::M:::M  M:::::M   R:::::::::::RR
  E:::::EEEEEEEEEE   M:::::M   M:::::M   M:::::M   R:::RRRRRR::::R
  E::::E             M:::::M    M:::M    M:::::M   R:::R      R::::R
  E::::E       EEEEE M:::::M     MMM     M:::::M   R:::R      R::::R
EE:::::EEEEEEEE::::E M:::::M             M:::::M   R:::R      R::::R
E::::::::::::::::::E M:::::M             M:::::M RR::::R      R::::R
EEEEEEEEEEEEEEEEEEEE MMMMMMM             MMMMMMM RRRRRRR      RRRRRR
```

``` bash
sudo chmod 777 /etc/hadoop/conf/hdfs-site.xml
```

nano /etc/hadoop/conf/hdfs-site.xml

Editamos la propiedad dfs.webhdfs.enabled y la ponemos a true:ç

``` xml
 <property>
    <name>dfs.webhdfs.enabled</name>
    <value>false</value>
  </property>
```

Reiniciamos el servicios HDFS:

``` bash
sudo systemctl restart hadoop-hdfs-namenode
```

Ahora desde el interfaz de HDFS ya podemos navegar por las carpetas y ver el contenido:
`

Ahora vamos a cambiar la configuración de Hue para indicarle la ruta de HDFS y poder navegar:

``` bash
sudo chmod 777 /etc/hue/conf/hue.ini
```


```
nano /etc/hue/conf/hue.ini
``

Y ponemos bien el puerto al 50070

webhdfs_url = http://ip-172-31-60-228.ec2.internal:50070/webhdfs/v1

``` bash
sudo systemctl restart hue
```


CREATE TABLE impressions2 (
requestBeginTime string,
adId string,
impressionId string,
referrer string,
userAgent string,
userCookie string,
ip string)
PARTITIONED BY (dt string)
ROW FORMAT  serde 'org.apache.hive.hcatalog.data.JsonSerDe' with serdeproperties
('paths'='requestBeginTime, adId, impressionId, referrer, userAgent, userCookie, ip')
LOCATION '${SAMPLE}/tables/impressions';