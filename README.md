This is my personal Python project that retrieves weather forecasts using the 'geopy' library in combination with Open-Meteo's Free Open Source Weather API.

'geopy' library converts location names to longitude/latitude coordinates which is then used with the API.

I originally created a web scraper but was uncertain about permission to scrape, so I opted to do an API version as well.

To run the this program you need to:
1. install openmeteo_requests by running this command:
    "pip install openmeteo-requests"
2. install the other requirements by running this:
    "pip install -r requirements.txt"
3. Run the "Main.py" script

You can enter locations multiple times (though only one at a time).
After that you can choose whether you want a .csv file with the data, print the data in the console or just exit the program.