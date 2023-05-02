import pandas as pd
import mysql.connector
import boto3

import datetime as dt
from datetime import timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def consultaMariaDB():
    conn = mysql.connector.connect(
        user="admin",
        password="adminadmin",
        host="rdsiabd.cypxda1kh3tc.us-east-1.rds.amazonaws.com",
        port=3306,
        database="retail_db"
    )    
    df=pd.read_sql("select customer_fname, customer_lname, customer_zipcode from customers",conn)
    df.to_parquet('/tmp/customers.parquet')
    print("-------Datos creados------")

def consultaMariaDBHook():
    mysql_hook = MySqlHook(mysql_conn_id='MariaDBid')
    conn = mysql_hook.get_conn()
    df = pd.read_sql("select customer_fname, customer_lname, customer_zipcode from customers", conn)
    df.to_parquet('/tmp/customers.parquet')
    print("-------Datos creados------")

def envioS3():
    s3r = boto3.resource('s3', region_name='us-east-1')

    nombreBucket = "iabd-s8a"
    bucket = s3r.Object(nombreBucket, 'customers.parquet')
    bucket.upload_file('/tmp/customers.parquet')

def envioS3Hook():
    s3_hook = S3Hook(aws_conn_id='AWSid')
    s3_hook.load_file(
        filename='/tmp/customers.parquet',
        key='customers.parquet',
        bucket_name='iabd-s8a'
    )

default_args = {
    'owner': 'aitor-medrano',
    'start_date': dt.datetime(2022, 5, 1),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
}

with DAG('dag-mariadb-s3',
         default_args=default_args,
         schedule_interval=timedelta(minutes=5),      
         ) as dag:

    recuperaDatos = PythonOperator(task_id='QueryMariaDB',
         python_callable=consultaMariaDBHook)

    persisteDatos = PythonOperator(task_id='PersistDataS3',
         python_callable=envioS3)

recuperaDatos >> persisteDatos

# consultaMariaDB()
# envioS3()