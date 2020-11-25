#!/usr/bin/python3
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import geopy.distance as distanceCoordinates

# Constants

# Main city that will be analysed
MAIN_CITY = "Matão"
# Maximum distance in kilometer of main city that others cities can be
MAX_DISTANCE = 50

# Global variables

citiesCoordinatesDf = pd.read_csv('./dataset/brazil_cities_coordinates.csv')
citiesCasesDf = pd.read_csv('./dataset/brazil_covid19_cities.csv')
mainCityDf = citiesCoordinatesDf[citiesCoordinatesDf["city_name"] == MAIN_CITY]
mainCityCoordinate = (float(mainCityDf.lat.values[0]), float(mainCityDf.long.values[0]))

def getNearCities():
    """
    Return all cities that are at maximum MAX_DISTANCE kilometer from MAIN_CITY
    """

    isNear = citiesCoordinatesDf.apply(
            lambda row: distanceCoordinates.distance((float(row['lat']), float(row['long'])), mainCityCoordinate).km < MAX_DISTANCE,
            axis=1
        )
    return citiesCoordinatesDf[isNear]


def plotMainCityCases():
    """
    Plot confirmed COVID-19 cases for MAIN_CITY
    """
    mainCityCasesDf = citiesCasesDf[citiesCasesDf["name"] == MAIN_CITY]

    x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in mainCityCasesDf.date]
    y = mainCityCasesDf.cases

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=15))
    plt.plot(x,y)
    plt.gcf().autofmt_xdate()
    plt.title("Casos confirmados COVID em " + MAIN_CITY)
    plt.ylabel("Casos")

    plt.show()

if __name__ == "__main__":

    ### Plot covid cases for the main city
    #plotMainCityCases()

    ### Get near cities of main city
    #print(getNearCities())
    pass
