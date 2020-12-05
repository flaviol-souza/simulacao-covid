#!/usr/bin/python3
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from functools import reduce
import geopy.distance as distanceCoordinates

from datasetProcess import getNearCities, MAX_DISTANCE, MAIN_CITY, mainCityCoordinate, plotCitiesCases

# Constants
# How many persons a node represent
PERSON_PER_NODE = 500
# Expected degree of connection inside community (integer)
Z_IN = 15
Z_OUT = 5

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
    return Z_OUT*(1-distance/(2*MAX_DISTANCE))


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

    
    # Calculate totoal population
    totalPopulation = 0
    for cityInfo in citiesFullInfo:
        totalPopulation += cityInfo['nodes']


    # calculate probability fos communities
    probabilityMatrix = []
    for city in citiesFullInfo:
        probabilityMatrix.append([])
        for city_neighborhood in citiesFullInfo:
            # Probability inside community
            if city_neighborhood == city:
                probabilityMatrix[-1].append(Z_IN/city['nodes'])
            else:
                probabilityMatrix[-1].append(calculateZout(
                    city, city_neighborhood)/((totalPopulation-city['nodes'])))

    communitySizes = list(map(lambda city: city['nodes'], citiesFullInfo))
    # Use random_geometric_graph model
    graph = nx.generators.stochastic_block_model(communitySizes, probabilityMatrix, sparse=False, directed=True)
    print('graph genereted')
    print('total cities', len(citiesFullInfo))
    
    # plot graph
    # print("start plotting")
    # color_map = []
    # typeColor = ['red', 'green','yellow','grey','blue', 'brown','black']
    # index = 0
    # for size in communitySizes:
    #     color_map+=[typeColor[index]]*size
    #     index+=1
    #     index = index%len(typeColor)
    # nx.drawing.nx_pylab.draw(graph,node_color=color_map, with_labels=True)
    # plt.show()

    return graph

def plotDegreeDistribution(graph):

    nodeDegree = graph.degree() # dictionary node:degree
    degree = [x[1] for x in nodeDegree]
    value = {}
    for i in degree:
        value[i] = degree.count(i)

    plt.figure()
    plt.grid(True)
    plt.plot(value.values(), '-')
    plt.xlabel('Grau')
    plt.ylabel('Quantidade de vértices')
    plt.title('Distribuição de Graus')
    plt.show()

def confirmedCasesInCitiesOfGraph():
    cities = getNearCities().values.tolist()
    citiesName = list(map(lambda cityinfo: cityinfo['name'],filter(lambda notNone: notNone,
                                 map(getFullCityInfo, cities))))
    print(len(citiesName))
    plotCitiesCases(citiesName)


if __name__ == "__main__":
    # Generate spatial network
    #generateSpatialGraph()
    # Generate spatial network with communities
    #plotDegreeDistribution(generateSpatialGraph())
    confirmedCasesInCitiesOfGraph()
    pass
