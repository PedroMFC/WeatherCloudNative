import json, requests
import os
import sys 

API_KEY = os.getenv('API_KEY')
url_base = os.getenv('URL_BASE')
city = os.getenv('CITY')

def get_fromAPI(days):
    url  = url_base + 'key=' + API_KEY + '&q=' + city + '&days=6' +'&aqi=no&alerts=no'

    data = requests.get(url).json()

    date = []
    temperature = []
    humidity = []

    for day in range(days): # range(1) -- 24 horas, range(2) --> 48 horas
        for lists in data['forecast']['forecastday'][day]['hour']:
            temperature.append(lists['temp_c'])
            humidity.append(lists['humidity'])
            date.append(lists['time'])

    forecast = {
        'time': date,
        'humidity': humidity,
        'temperature': temperature
    }

    return forecast