import requests

def get_location_information(city, country):
    """
    returns location details of a city in given country
    :param city: name of city as a string
    :param country: name of country as a string
    """
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    geocoding_params = {
        "name": f"{city}, {country}",
        "count": 1,
        "language": "en"
    }

    geocoding_response = requests.get(
        geocoding_url,
        params=geocoding_params)

    geocoding_data = geocoding_response.json()
    return geocoding_data

def get_weather(city, country, start_date, end_date):
    """
    returns the information about the weather of a city in given country from start_date to end_date
    :param city: name of city as a string
    :param country: name of country as a string
    :param start_date: date string in YYYY-MM-DD format
    :param end_date: date string in YYYY-MM-DD format
    :return: dictionary containing weather data for each day from start_date to end_date
    """
    # Get the longitude and latitude using the city and country
    geocoding_data = get_location_information(city, country)

    # No matching city found
    if "results" not in geocoding_data:
        return None

    location = geocoding_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # Request weather for trip dates
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "precipitation_probability_max,"
            "rain_sum,"
            "snowfall_sum"
        ),
        "timezone": "auto"
    }

    weather_response = requests.get(
        weather_url,
        params=weather_params)

    weather_data = weather_response.json()

    return weather_data["daily"]

if __name__ == "__main__":
    weather = get_weather(
        "Edmonton",
        "Alberta",
        "2026-08-24",
        "2026-09-09")

    print(weather)