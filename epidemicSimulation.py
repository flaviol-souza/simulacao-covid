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
    viz.plot(PATH_RESULT+"diffusion.pdf", percentile=90)

def viewGif(g, iterations, variable):
    C_model = ContinuousModel(g)
    model.add_status(S_CONS)
    model.add_status(I_CONS)
    model.add_status(R_CONS)

    # Compartment definition
    c1 = NodeStochastic(0.02, triggering_status=I_CONS)
    c2 = NodeStochastic(0.01)

    # Rule definition
    model.add_rule(S_CONS, I_CONS, c1)
    model.add_rule(I_CONS, R_CONS, c2)

    # Visualization config
    visualization_config = {
        'plot_interval': 5,
        'plot_variable': variable,
        'variable_limits': {
            variable: [0, 0.8]
        },
        'show_plot': True,
        'plot_output': PATH_RESULT+'/model_animation.gif',
        'plot_title': 'Animated network',
    }

    C_model.configure_visualization(visualization_config)
    i = C_model.iteration_bunch(200)
    C_model.visualize(i)

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
    n_iterations = 200 #iterations

    # Generate spatial network with communities
    g = generateSpatialGraph()
    
    #findCommunities(g)
    model = configureModel(g, beta, gamma, fraction_infected)

    iterations, trends = epidemicSimulation(model, n_iterations)
    
    view(model, trends)
    #viewGif(g, iterations, I_CONS)
    
    pass