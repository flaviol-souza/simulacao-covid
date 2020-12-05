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
citiesPopulationDf = pd.read_csv('./dataset/brazil_population_2019.csv')
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


def plotCitiesCases(citiesName):
    """
    Plot confirmed COVID-19 cases for Array of cities name
    """
    mainCityCasesDf = citiesCasesDf[citiesCasesDf["name"] == MAIN_CITY]
    
    soma = 0
    for city in citiesName :
        soma += citiesPopulationDf[citiesPopulationDf['city']==city]['population'].values.tolist()[0]
    print('soma',
    soma)

    x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in mainCityCasesDf.date]
    dates = list(mainCityCasesDf.date)
    y = list(mainCityCasesDf.cases)

    # print('dates',dates)
    # print('y',y)

    for cityName in citiesName:
        if cityName != MAIN_CITY:
            cityCasesDf = citiesCasesDf[citiesCasesDf["name"] == cityName]
            for dateIndex in range(len(dates)):
                y[dateIndex]+=cityCasesDf[cityCasesDf['date']==dates[dateIndex]].cases.values[0]
    # print(len(y))
    # print(len(x))

    for p in range(len(y)):
        y[p]/=soma
    
    # # df = pd.pivot_table( citiesCasesDf, columns= 'name' , index = {'date':'Data'}, values= 'cases')
    # # df = df.loc[:,citiesName].sum(axis =1)

    # # plt.title("Casos confirmados de COVID na região")
    # # plt.ylabel("Casos")
    # # plt.xlabel("Data")
    # # df.rename( index={'date': 'Data'}).plot()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=15))
    plt.plot(x,y)
    plt.gcf().autofmt_xdate()
    plt.title("Casos confirmados COVID")
    plt.ylabel("Casos (%)")

    plt.show()

if __name__ == "__main__":

    ### Plot covid cases for the main city
    #plotMainCityCases()

    ### Get near cities of main city
    print(getNearCities())
    pass
