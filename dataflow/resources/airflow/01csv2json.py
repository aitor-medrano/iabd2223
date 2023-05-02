import datetime as dt
from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

import pandas as pd

def csvToJson():
    df=pd.read_csv('/opt/airflow/data/datos-faker.csv')
    for i,r in df.iterrows():
        print(r['nombre'])
    df.to_json('/opt/airflow/data/datos-airflow.json', orient='records')

default_args = {
    'owner': 'aitor-medrano',
    'start_date': dt.datetime(2023, 4, 18),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
}


with DAG('HolaAirflow-CSV',
         default_args=default_args,
         schedule_interval=timedelta(minutes=5),      # '0 * * * *',
         ) as dag:

    imprime_iniciando = BashOperator(task_id='iniciando',
                               bash_command='echo "Leyendo el csv..."')
    
    csvJson = PythonOperator(task_id='csv2json', python_callable=csvToJson)


imprime_iniciando >> csvJson
