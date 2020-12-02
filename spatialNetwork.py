#!/usr/bin/python3
import pandas as pd
import networkx as nx
from functools import reduce
import geopy.distance as distanceCoordinates

from datasetProcess import getNearCities, MAX_DISTANCE, MAIN_CITY, mainCityCoordinate

# Constants
# How many persons a node represent
PERSON_PER_NODE = 100
# Expected degree of connection inside community (porcentage)
Z_IN = 0.8

# Global variables

citiesPopulationDf = pd.read_csv('./dataset/brazil_population_2019.csv')


def calculateZout(city, city_neighborhood):
    """
    Given 2 cities calculate expected degree of connections between communities
    """
    distance = distanceCoordinates.distance(
        (float(city['lat']), float(city['long'])),
        (float(city_neighborhood['lat']), float(city_neighborhood['long']))
    ).km
    return Z_IN*(1-distance/(2*MAX_DISTANCE))


def getFullCityInfo(cityLocation):
    """
    From city location obtain population and
    generate a dictionary that contain all necessary
    city information
    """
    cityName = cityLocation[2]
    lat = cityLocation[3]
    long = cityLocation[4]
    population = citiesPopulationDf[citiesPopulationDf['city']
                                    == cityName]['population']
    # Population data not found
    if len(population) == 0:
        return None

    numNodes = int(population.values[0]/PERSON_PER_NODE)
    return {'name': cityName, 'nodes': numNodes, 'lat': lat, 'long': long}


def generateSpatialGraph():
    """
    Generate a Graph that contains communities that represent cities
    the expected degree of connections inside community is constant
    the expected degree of connections between communities depends on distance
    and is given by the function calculateZout
    """
    cities = getNearCities().values.tolist()
    citiesFullInfo = list(filter(lambda notNone: notNone,
                                 map(getFullCityInfo, cities)))

    probabilityMatrix = []
    for city in citiesFullInfo:
        probabilityMatrix.append([])
        for city_neighborhood in citiesFullInfo:
            probabilityMatrix[-1].append(calculateZout(
                city, city_neighborhood)/city['nodes'])

    communitySizes = list(map(lambda city: city['nodes'], citiesFullInfo))
    #Try use the random_geometric_graph model
    return nx.generators.stochastic_block_model(communitySizes, probabilityMatrix, sparse=False, directed=True)


if __name__ == "__main__":
    # Generate spatial network with communities
    generateSpatialGraph()
    pass
