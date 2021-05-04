from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

import csv
import os
import json
import pandas as pd

csv_temperature_path = '/tmp/cc-p2/temperature.csv'
csv_humidity_path    = '/tmp/cc-p2/humidity.csv'
csv_data_path        = '/tmp/cc-p2/data.csv'
csv_columns          = ['DATE','TEMP','HUM']

db_url    = 'localhost'
db_port   = 27017
db_name   = 'CC'
coll_name = 'SanFrancisco_Weather'

'''
Limpieza de datos: nos queadmos con las columnas que necestiamos y luego las almacenamos en un CSV
'''
def capture_data():
    df_temperature = pd.DataFrame(pd.read_csv(csv_temperature_path)).dropna()
    df_humidity    = pd.DataFrame(pd.read_csv(csv_humidity_path)).dropna()

    temperature = df_temperature[['datetime', 'San Francisco']]
    humidity    = df_humidity[['datetime', 'San Francisco']]

    data = temperature.merge(humidity, on='datetime')
    data.columns = csv_columns 


    data.to_csv(csv_data_path, index=False)

'''
Guardar el archivo CSV con los datos preparados en mongo
'''
def store_mongo():
    client = MongoClient(db_url, int(db_port))
    db = client[db_name]
    coll = db[coll_name]
    data = pd.read_csv(csv_data_path)
    payload = json.loads(data.to_json(orient='records'))
    coll.drop() #Por si hay registros previos
    coll.insert_many(payload)



'''
DEFINICIÓN DEL GRAFO
'''
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

#Inicialización del grafo DAG de tareas para el flujo de trabajo
dag = DAG(
    'Practica_2',
    default_args=default_args,
    description='Flujo para un servicio Cloud Native',
    schedule_interval=timedelta(days=1),
    tags=['practica2']
)



Environment = BashOperator(
    task_id="Environment",
    depends_on_past=False,
    bash_command="mkdir -p /tmp/cc-p2",
    dag=dag
)

DownloadCompose = BashOperator(
    task_id="DownloadCompose",
    depends_on_past=False,
    bash_command="curl -o /tmp/cc-p2/docker-compose.yml https://raw.githubusercontent.com/PedroMFC/WeatherCloudNative/main/docker-compose.yml",
    dag=dag
)

MongoDBStart = BashOperator(
    task_id="MongoDBStart",
    depends_on_past=False,
    bash_command="docker-compose -f /tmp/cc-p2/docker-compose.yml up -d mongo mongo-express",
    dag=dag
)

DownloadHumidity = BashOperator(
    task_id="DownloadHumidity",
    depends_on_past=False,
    bash_command="curl -o /tmp/cc-p2/humidity.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/humidity.csv.zip",
    dag=dag
)

DownloadTemperature = BashOperator(
    task_id="DownloadTemperature",
    depends_on_past=False,
    bash_command="curl -o /tmp/cc-p2/temperature.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/temperature.csv.zip",
    dag=dag
)

UnZipHumidity = BashOperator(
    task_id="UnZipHumidity",
    depends_on_past=False,
    bash_command="unzip -u /tmp/cc-p2/humidity.csv.zip -d /tmp/cc-p2/",
    dag=dag
)


UnZipTemperature = BashOperator(
    task_id="UnZipTemperature",
    depends_on_past=False,
    bash_command="unzip -u /tmp/cc-p2/temperature.csv.zip -d /tmp/cc-p2/",
    dag=dag
)

CaptureData = PythonOperator(
	task_id="CaptureData",
    depends_on_past=False,
    python_callable=capture_data,
    dag=dag
)

StoreMongo = PythonOperator(
	task_id="StoreMongo",
    depends_on_past=False,
    python_callable=store_mongo,
    dag=dag
)


DownloadCode = BashOperator(
    task_id="DownloadCode",
    depends_on_past=False,
    bash_command="curl -o /tmp/cc-p2/Dockerfile.api1 https://raw.githubusercontent.com/PedroMFC/WeatherCloudNative/main/Dockerfile.api1;" +
                 "curl -o /tmp/cc-p2/Dockerfile.api2 https://raw.githubusercontent.com/PedroMFC/WeatherCloudNative/main/Dockerfile.api2;" +
                 "curl -o /tmp/cc-p2/Dockerfile.test https://raw.githubusercontent.com/PedroMFC/WeatherCloudNative/main/Dockerfile.test;" +
                 "curl -o /tmp/cc-p2/requirements.txt https://raw.githubusercontent.com/PedroMFC/WeatherCloudNative/main/requirements.txt;" +
                 "curl -o /tmp/cc-p2/.dockerignore https://raw.githubusercontent.com/PedroMFC/WeatherCloudNative/main/.dockerignore;" +
                 "svn export --force https://github.com/PedroMFC/WeatherCloudNative/trunk/code /tmp/cc-p2/code",
    dag=dag
)

StartApiV1 = BashOperator(
    task_id="StartApiV1",
    depends_on_past=False,
    bash_command="docker-compose -f /tmp/cc-p2/docker-compose.yml up --build api_v1",
    dag=dag
)


StartApiV2 = BashOperator(
    task_id="StartApiV2",
    depends_on_past=False,
    bash_command="docker-compose -f /tmp/cc-p2/docker-compose.yml up --build api_v2",
    dag=dag
)

Test = BashOperator(
    task_id="Test",
    depends_on_past=False,
    bash_command="docker-compose -f /tmp/cc-p2/docker-compose.yml up --build test",
    dag=dag
)


#Dependencias
Environment >> DownloadCompose >> MongoDBStart >> [DownloadHumidity >> UnZipHumidity, DownloadTemperature >> UnZipTemperature] >> CaptureData >> StoreMongo >> DownloadCode >> Test >> [StartApiV1, StartApiV2]
#StartApiV1 >> StartApiV2