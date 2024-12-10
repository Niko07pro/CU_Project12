from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_URL = 'https://dataservice.accuweather.com/'
LOCATION_URL = 'locations/v1/cities/search'
TEMP_URL = 'currentconditions/v1/'
RAIN_URL = 'forecasts/v1/daily/1day/'
API_KEY = 'F2DL9K75WzJtsKa5BvvbusJgApGA59SI'


def get_weather(city_name):
    try:
        location_data = requests.get(API_URL + LOCATION_URL, params={
            'q': city_name,
            'apikey': API_KEY
        }).json()
        if not location_data:
            return None, f"Город '{city_name}' не найден."
        location_key = location_data[0]['Key']
        weather_data = requests.get(
            API_URL + TEMP_URL + location_key,
            params={'apikey': API_KEY, 'details': 'true'}
        ).json()
        if not weather_data:
            return None, f"Данные о погоде для города '{city_name}' не найдены."
        data_rain = requests.get(
            API_URL + RAIN_URL + location_key,
            params={'details': 'true', 'apikey': API_KEY}
        ).json()
        if not data_rain:
            return None, f"Данные об осадках для города '{city_name}' не найдены."
        weather_info = {
            'temperature': weather_data[0]['Temperature']['Metric']['Value'],
            'humidity': weather_data[0]['RelativeHumidity'],
            'wind': weather_data[0]['Wind']['Speed']['Metric']['Value'],
            'rain': data_rain['DailyForecasts'][0]['Day']['RainProbability'],
            'status': 'Погодные условия плохие'
        }
        if 0 < weather_info['temperature'] < 35 and weather_info['wind'] < 50 and weather_info['rain'] < 70:
            weather_info['status'] = 'Погодные условия хорошие'
        return weather_info, None
    except Exception as e:
        return None, f"Ошибка при получении данных из API: {e}."


@app.route("/", methods=["GET", "POST"])
def index():
    weather_city1, weather_city2 = None, None
    error_city1, error_city2 = None, None
    city1, city2 = None, None
    if request.method == "POST":
        city1 = request.form.get("city1")
        city2 = request.form.get("city2")
        if city1:
            weather_city1, error_city1 = get_weather(city1)
        if city2:
            weather_city2, error_city2 = get_weather(city2)
    return render_template("index.html",
                           weather_city1=weather_city1, weather_city2=weather_city2,
                           error_city1=error_city1, error_city2=error_city2,
                           city1=city1, city2=city2)


if __name__ == "__main__":
    app.run(debug=True)
