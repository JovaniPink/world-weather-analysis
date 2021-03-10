# World Weather Analysis

> World weather analysis.

## Data Sources

- https://openweathermap.org/current
- https://www.ncdc.noaa.gov/cdo-web/
- https://www.weather.gov/help-past-weather
- https://www.weather.gov/

- New York City

  - https://www.ncdc.noaa.gov/cdo-web/datasets/GHCND/stations/GHCND:USW00094728/detail
  - https://www1.nyc.gov/site/planning/data-maps/open-data/districts-download-metadata.page
  -

- https://www.climate.gov/maps-data/dataset/past-weather-zip-code-data-table

## Overview

- API Retrieval (OpenweatherMap API)
- Statistical Analyses
- Visualizations
- Weather Understanding

Understand the domain https://en.wikipedia.org/wiki/Weather

Task: Collect and analyze weather data across cities worldwide. Collect New York Cities weather in DETAIL.
Purpose: Understanding weather data and in specific understanding New City's weather for another analysis project.
Method: Create a Pandas DataFrame with 1000+ or more of the world's unique cities and their weather data in real time. This process will entail collecting, analyzing, and visualizing the data in Python, Tableau, and D3.
Analysis: Data will be split into three main data building stages.

### Collect the Data

- Use the NumPy module to generate more than 1,500 random latitudes and longitudes.
- Use the citipy module to list the nearest city to the latitudes and longitudes.
- Use the OpenWeatherMap API to request the current weather data from each unique city in your list.
- Parse the JSON data from the API request.
- Collect the following data from the JSON file and add it to a DataFrame:
  - "City","Country","Date"
  - "Lat","Lng"
  - "Temp","Min Temp","Max Temp"
  - "Current Description", "Current Details"
  - "Humidity"
  - "Cloudiness"
  - "Wind Speed"

### Exploratory Analysis with Visualization

- Create scatter plots of the weather data for the following comparisons:
  - Latitude versus temperature
  - Latitude versus humidity
  - Latitude versus cloudiness
  - Latitude versus wind speed
- Determine the correlations for the following weather data:
  - Latitude and temperature
  - Latitude and humidity
  - Latitude and cloudiness
  - Latitude and wind speed
- Create a series of heatmaps using the Google Maps and Places API that showcases the following:
  - Latitude and temperature
  - Latitude and humidity
  - Latitude and cloudiness
  - Latitude and wind speed

### Visualize Travel Data

- Create a heatmap with pop-up markers that can display information on specific cities based on a customer's travel preferences. Complete these steps:
  - Filter the Pandas DataFrame based on user inputs for a minimum and maximum temperature.
  - Create a heatmap for the new DataFrame.
  - Find a hotel from the cities' coordinates using Google's Maps and Places API, and Search Nearby feature.
  - Store the name of the first hotel in the DataFrame.
  - Add pop-up markers to the heatmap that display information about the city, current maximum temperature, and a hotel in the city.

### New York City

- https://en.wikipedia.org/wiki/Climate_of_New_York_City

## Summary

Grabbing Weather from an API using:

- Jupyter Notebook
- Python
- Pandas
- PandasGUI
- CitiPy
- Requests
- APIs
- Google Maps
- OpenWeather API
- JSON Traversals

### Weather Datasets

### Analysis

## Todo Checklist

A helpful checklist to gauge how your README is coming on what I would like to finish:

- [ ]

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
