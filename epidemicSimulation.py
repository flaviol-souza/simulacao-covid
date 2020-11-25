import ndlib.models.ModelConfig as mc
import ndlib.models.CompositeModel as gc
import networkx.algorithms.community as nxcom

from spatialNetwork import *
from ndlib.utils import multi_runs
from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
from ndlib.models.ContinuousModel import ContinuousModel
from ndlib.models.compartments.NodeStochastic import NodeStochastic

S_CONS = "Susceptible"
I_CONS = "Infected"
R_CONS = "Removed"

def configureModel(g, beta, gamma, fraction_infected):
    # Composite Model instantiation
    #model = DynamicCompositeModel(g)
    model = gc.CompositeModel(g)
    #model = ContinuousModel(g)

    # Model statuses
    model.add_status(S_CONS)
    model.add_status(I_CONS)
    model.add_status(R_CONS)

    # Compartment definition
    c1 = NodeStochastic(beta, triggering_status=I_CONS)
    c2 = NodeStochastic(gamma)

    # Rule definition
    model.add_rule(S_CONS, I_CONS, c1)
    model.add_rule(I_CONS, R_CONS, c2)

    # Model initial status configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', fraction_infected)
    model.set_initial_status(config)

    return model

def epidemicSimulation(model, iteration):
    # Simulation execution
    iterations = model.iteration_bunch(iteration)
    #model.visualize(iterations)
    #iterations = model.iteration_bunch(iteration, node_status=False)
    trends = model.build_trends(iterations)

    return iterations, trends 

def view(model, trends):
    #Visualizacao
    viz = DiffusionTrend(model, trends)
    viz.plot("result/diffusion.pdf", percentile=90)

def findCommunities(g):
    # Find the communities
    communities = sorted(nxcom.greedy_modularity_communities(g), key=len, reverse=True)
    # Count the communities
    print("The network has", len(communities), "communities.")

if __name__ == "__main__":
    #init variable
    beta = 0.02
    gamma = 0.01
    fraction_infected = 0.1
    iterations = 200 #iterations

    # Generate spatial network with communities
    g = generateSpatialGraph()
    
    #findCommunities(g)
    model = configureModel(g, beta, gamma, fraction_infected)
    iterations, trends = epidemicSimulation(model, iterations)
    view(model, trends)
    
    pass