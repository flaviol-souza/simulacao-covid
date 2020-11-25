import ndlib.models.ModelConfig as mc
import ndlib.models.CompositeModel as gc
import networkx.algorithms.community as nxcom

from spatialNetwork import *
from ndlib.utils import multi_runs
from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
from ndlib.models.ContinuousModel import ContinuousModel
from ndlib.models.compartments.NodeStochastic import NodeStochastic

def configureModel(g):
    # Composite Model instantiation
    #model = DynamicCompositeModel(g)
    model = gc.CompositeModel(g)
    #model = ContinuousModel(g)

    # Model statuses
    model.add_status("Susceptible")
    model.add_status("Infected")
    model.add_status("Removed")

    # Compartment definition
    c1 = NodeStochastic(0.02, triggering_status="Infected")
    c2 = NodeStochastic(0.01)

    # Rule definition
    model.add_rule("Susceptible", "Infected", c1)
    model.add_rule("Infected", "Removed", c2)

    # Model initial status configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.3)
    model.set_initial_status(config)

    return model

def epidemicSimulation(model):
    # Simulation execution
    iterations = model.iteration_bunch(200)
    #model.visualize(iterations)
    #iterations = model.iteration_bunch(100, node_status=False)
    trends = model.build_trends(iterations)

    return iterations, trends 

def visualizacao(model, trends):
    #Visualizacao
    viz = DiffusionTrend(model, trends)
    viz.plot("diffusion.pdf", percentile=90)

def findCommunities(g):
    # Find the communities
    communities = sorted(nxcom.greedy_modularity_communities(g), key=len, reverse=True)
    # Count the communities
    print("The karate club has", len(communities), "communities.")

if __name__ == "__main__":
    # Generate spatial network with communities
    g = generateSpatialGraph()
    findCommunities(g)
    pass