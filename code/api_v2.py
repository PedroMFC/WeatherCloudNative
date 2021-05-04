import bottle 
import json
import os

import forecast_api

app = bottle.app()

@app.get('/servicio/v2/prediccion/24')
def index24():
    bottle.response.headers['Content-Type'] = 'application/json'
    return json.dumps(forecast_api.get_fromAPI(1))

@app.get('/servicio/v2/prediccion/48')
def index48():
    bottle.response.status = 200
    bottle.response.headers['Content-Type'] = 'application/json'
    return json.dumps(forecast_api.get_fromAPI(2))

@app.get('/servicio/v2/prediccion/72')
def index72():
    bottle.response.status = 200
    bottle.response.headers['Content-Type'] = 'application/json'
    return json.dumps(forecast_api.get_fromAPI(3))

if __name__ == '__main__':
    
    port = os.getenv('PORT_APIV2')
    host = os.getenv('HOST_APIV2')

    # Si no hay nada ponemos unos valores por defecto
    if port == "":
        port = '8083'
    if host == "":
        host = '0.0.0.0'

    app.run(host=host, port=port)
