import ndlib.models.ModelConfig as mc
import ndlib.models.CompositeModel as gc
import networkx.algorithms.community as nxcom

from spatialNetwork import *
from ndlib.utils import multi_runs
from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
from ndlib.models.ContinuousModel import ContinuousModel
from ndlib.models.compartments.NodeStochastic import NodeStochastic

### Constants
PATH_RESULT="result/"
S_CONS = "Susceptible"
I_CONS = "Infected"
R_CONS = "Removed"

initial_status = {
    S_CONS: 0,
    I_CONS: 1,
    R_CONS: 2
}

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

    return model, config

def epidemicSimulation(model, iteration):
    iterations = model.iteration_bunch(iteration)
    #iterations = model.iteration_bunch(iteration, node_status=False)
    trends = model.build_trends(iterations)

    return iterations, trends 

def multEpidemicSimulation(model, n_execution, n_iteration, infection_sets, n_processes):
    return multi_runs(model, execution_number=n_execution, iteration_number=n_iteration, infection_sets=infection_sets, nprocesses=n_processes)

def view(model, trends):
    viz = DiffusionTrend(model, trends)
    viz.plot(PATH_RESULT+"diffusion.pdf", percentile=90)

def findCommunities(g):
    # Find the communities
    communities = sorted(nxcom.greedy_modularity_communities(g), key=len, reverse=True)
    # Count the communities
    print("The network has", len(communities), "communities.")

if __name__ == "__main__":
    #boot variables
    mult_executions = False
    beta = 0.02
    gamma = 0.01
    fraction_infected = 0.1
    n_iterations = 200 #iterations at model

    # Generate spatial network with communities
    g = generateSpatialGraph()
    
    #findCommunities(g)
    model, config = configureModel(g, beta, gamma, fraction_infected)
    trends = None
    if mult_executions:
        n_execution = 10
        infection_sets = None
        n_processes = 1
        trends = multEpidemicSimulation(model, n_execution, n_iterations, infection_sets, n_processes)
    else:
        iterations, trends = epidemicSimulation(model, n_iterations)    
    
    view(model, trends)

    print("Simulation completed.")
    pass