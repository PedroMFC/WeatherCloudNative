import os
import pmdarima as pm
import pandas as pd
import numpy

from datetime import datetime, timedelta  
from pymongo import MongoClient
from statsmodels.tsa.arima_model import ARIMA

db_url    = os.getenv('DB_URL')
db_port   = os.getenv('DB_PORT')
db_name   = os.getenv('DB_NAME')
coll_name = os.getenv('COLL_NAME')

class ForecastARIMA:

    def __init__(self, train_size):
        self.model_humidity    = None
        self.model_temperature = None
        self.train_size        = train_size

    def get_mongo(self):
        client = MongoClient(db_url, int(db_port))
        db = client[db_name]
        cursor = db[coll_name].find({}, {'_id':0})

        # Expand the cursor and construct the DataFrame
        df =  pd.DataFrame(list(cursor))

        return df

    def get_hours(self, interval):
        present_time = datetime.now()  

        init = datetime(present_time.year , present_time.month, present_time.day)

        datetimes = [init.strftime('%Y-%m-%d %H:%M')]
        for i in range(1, interval):
            datetimes.append((init + timedelta(hours=i)).strftime('%Y-%m-%d %H:%M'))

        return datetimes

    def train_arima(self):
        # Humidity
        df = self.get_mongo()
        df_humidity = df[['DATE', 'HUM']].head(self.train_size)

        self.model_humidity = pm.auto_arima(df_humidity['HUM'], start_p=1, start_q=1,
                                test='adf',       # use adftest to find optimal 'd'
                                max_p=3, max_q=3, # maximum p and q
                                m=1,              # frequency of series
                                d=None,           # let model determine 'd'
                                seasonal=False,   # No Seasonality
                                start_P=0, 
                                D=0, 
                                trace=True,
                                error_action='ignore',  
                                suppress_warnings=True, 
                                stepwise=True)

        # Temperature
        df_temperature = df[['DATE', 'TEMP']].head(self.train_size)

        self.model_temperature = pm.auto_arima(df_temperature['TEMP'].head(self.train_size), start_p=1, start_q=1,
                                test='adf',       # use adftest to find optimal 'd'
                                max_p=3, max_q=3, # maximum p and q
                                m=1,              # frequency of series
                                d=None,           # let model determine 'd'
                                seasonal=False,   # No Seasonality
                                start_P=0, 
                                D=0, 
                                trace=True,
                                error_action='ignore',  
                                suppress_warnings=True, 
                                stepwise=True)

    def get_prediction(self, interval):

        humidity, confint_hum    = self.model_humidity.predict(n_periods=interval, return_conf_int=True)
        temperature, confint_tem = self.model_temperature.predict(n_periods=interval, return_conf_int=True)

        forecast = {
            'time': self.get_hours(interval),
            'humidity': humidity.tolist(),
            'temperature': temperature.tolist()
        }

        return forecast




