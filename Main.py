import os
import openmeteo_requests
import requests_cache
import pandas
import ssl
import certifi
import geopy
from retry_requests import retry
from datetime import datetime
from geopy.geocoders import Nominatim

def get_weather_data():
    # Create SSL_Context so that Nominatim can be used
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ssl_context
    geolocator = Nominatim(user_agent="Weather_App")

    # Settings from Open-Meteo API documentation
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    file_data = []
    first_iteration = True
    while True:
        user_area = input("Enter area you want to see forecast for: ")
        location = geolocator.geocode(user_area)

        if user_area == "stop":
            break

        if location is None:
            print("Couldn't find the area, please try again.")
            continue

        # Parameters according to Open-Meteo documentation
        parameters = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "hourly": "apparent_temperature",
            "timezone": "auto"
        }

        url = "https://api.open-meteo.com/v1/forecast"
        responses = openmeteo.weather_api(url, params=parameters)
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {"date": pandas.date_range(
            start=pandas.to_datetime(hourly.Time(), unit="s"),
            end=pandas.to_datetime(hourly.TimeEnd(), unit="s"),
            freq=pandas.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ), "temperature": hourly_temperature}

        # Create DataFrame containing the hourly_data dictionary (contains date and temperature columns)
        hourly_dataframe = pandas.DataFrame(data=hourly_data)

        # Keep track of index so that we can update the same row if multiple inputs
        index = 0


        if first_iteration:
            file_data.append(f";{location}")
        else:
            file_data[index] += f";{location}"

        # Iterate through DataFrame rows and combine date and temperature
        for _, row in hourly_dataframe.iterrows():
            index += 1
            if first_iteration:
                file_data.append(f"{row['date']};{round(row['temperature'], 1)}")
            else:
                file_data[index] += f";{round(row['temperature'], 1)}"

        first_iteration = False
        print("Weather forecast from location added.\n")

        user_input = input("Write 'stop' to stop, write anything else to add more locations: ")
        if user_input == "stop":
            break

    return file_data


def create_file(file_data):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_home_directory = os.path.expanduser('~')
    file_name = "Weather_Forecast_" + current_datetime + ".csv"

    with open(user_home_directory + "/" + file_name, 'w') as file:
        file.write(f"7-Day Weather Forecast - Hourly Intervals - Degrees in Celsius - From Open-Meteo ({current_datetime})\n")
        for line in file_data:
            file.write(line + '\n')

    print(f"File saved to: {user_home_directory}")


def print_data(weather_data):
    for line in weather_data:
        print(line)


def main():
    print("This is a weather forecast application that extracts forecast data from locations.")
    print("Write 'stop' to cancel.\n")
    weather_data = get_weather_data()

    print("\nDo you want a .csv file with the data, print the data in console or exit the program?")
    user_input = input("Enter 'file', 'print' or 'exit': ")

    while user_input not in ('file', 'print', 'exit'):
        user_input = input("Enter 'file', 'print' or 'exit': ")

    if user_input == 'exit':
        exit()

    if user_input == 'file':
        create_file(weather_data)

    if user_input == 'print':
        print_data(weather_data)


if __name__ == "__main__":
    main()
