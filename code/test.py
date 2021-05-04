import unittest
import api_v1
import api_v2
from webtest import TestApp
import forecast_api
from unittest.mock import patch, MagicMock

class TestStringMethods(unittest.TestCase):
    @patch('forecast_arima.ForecastARIMA')
    def test_bottle_v1_24(self, mockARIMA):
        app = TestApp(api_v1.app)
        api_v1.arima.get_prediction = MagicMock(return_value={})
        self.assertEqual(app.get('/servicio/v1/prediccion/24').status, '200 OK')

    @patch('forecast_arima.ForecastARIMA')
    def test_bottle_v1_48(self, mockARIMA):
        app = TestApp(api_v1.app)
        api_v1.arima.get_prediction = MagicMock(return_value={})
        self.assertEqual(app.get('/servicio/v1/prediccion/48').status, '200 OK')

    @patch('forecast_arima.ForecastARIMA')
    def test_bottle_v1_72(self, mockARIMA):
        app = TestApp(api_v1.app)
        api_v1.arima.get_prediction = MagicMock(return_value={})
        self.assertEqual(app.get('/servicio/v1/prediccion/48').status, '200 OK')

    def test_bottle_v2_24(self):
        app = TestApp(api_v2.app)
        forecast_api.get_fromAPI = unittest.mock.Mock(return_value={})
        self.assertEqual(app.get('/servicio/v1/prediccion/24').status, '200 OK')

    def test_bottle_v2_48(self):
        app = TestApp(api_v2.app)
        forecast_api.get_fromAPI = unittest.mock.Mock(return_value={})
        self.assertEqual(app.get('/servicio/v1/prediccion/48').status, '200 OK')

    def test_bottle_v2_72(self):
        app = TestApp(api_v2.app)
        forecast_api.get_fromAPI = unittest.mock.Mock(return_value={})
        self.assertEqual(app.get('/servicio/v1/prediccion/72').status, '200 OK')


    

if __name__ == '__main__':
    unittest.main()