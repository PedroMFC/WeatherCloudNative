import bottle 
import os
import json

import forecast_arima


arima = forecast_arima.ForecastARIMA(int(os.getenv('TRAIN_SIZE')))

app = bottle.app()


@app.get('/servicio/v1/prediccion/24')
def index24():
    bottle.response.headers['Content-Type'] = 'application/json'
    return json.dumps(arima.get_prediction(24))

@app.get('/servicio/v1/prediccion/48')
def index48():
    bottle.response.headers['Content-Type'] = 'application/json'
    return json.dumps(arima.get_prediction(48))

@app.get('/servicio/v1/prediccion/72')
def index72():
    bottle.response.headers['Content-Type'] = 'application/json'
    return json.dumps(arima.get_prediction(72))

if __name__ == '__main__':

    arima.train_arima()

    port = os.getenv('PORT_APIV1')
    host = os.getenv('HOST_APIV1')

    # Si no hay nada ponemos unos valores por defecto
    if port == "":
        port = '8082'
    if host == "":
        host = '0.0.0.0'

    app.run(host=host, port=port)
