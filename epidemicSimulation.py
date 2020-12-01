import numpy as np
import ndlib.models.ModelConfig as mc
import ndlib.models.CompositeModel as gc
import networkx.algorithms.community as nxcom

from spatialNetwork import *
from ndlib.utils import multi_runs
from ndlibCustom.SWIRCustomModel import SWIRCustomModel
from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
from ndlib.models.ContinuousModel import ContinuousModel
from ndlib.models.compartments.NodeStochastic import NodeStochastic

### Constants
PATH_RESULT="result/"
S_CONS = "Susceptible"
I_CONS = "Infected"
R_CONS = "Removed"

def initial_status_I(node, graph, status, constants):
    return np.random.uniform(0, constants['fraction_infected'])

def update_S(node, graph, status, attributes, constants):
    return status[node][I_CONS] * constants['beta']

def update_I(node, graph, status, attributes, constants):
    return status[node][R_CONS] * constants['gamma']

def configureModel(g, beta, gamma,  fraction_infected, withContinuousModel, epidemicModel='SIR', mu=0.005, nu=0.005):
    constants = {
        'fraction_infected': fraction_infected,
        'beta': beta,
        'gamma': gamma
    }

    # Composite Model instantiation
    if epidemicModel == 'SWIR' :
        model = SWIRCustomModel(g)
    elif withContinuousModel:
        model = ContinuousModel(g, constants=constants)
    else:
        model = gc.CompositeModel(g)
  
    if epidemicModel == 'SIR' :
        # Model statuses
        model.add_status(S_CONS)
        model.add_status(I_CONS)
        model.add_status(R_CONS)

    # Model initial status configuration
    config = mc.Configuration()
    
    if type(model) is gc.CompositeModel:
        # Compartment definition
        c1 = NodeStochastic(beta, triggering_status=I_CONS)
        c2 = NodeStochastic(gamma)

        # Rule definition
        model.add_rule(S_CONS, I_CONS, c1)
        model.add_rule(I_CONS, R_CONS, c2)
        config.add_model_parameter('fraction_infected', fraction_infected)
        model.set_initial_status(config)    
    elif type(model) is ContinuousModel: #just to ContinuousModel
        condition = NodeStochastic(1)

        # Rules
        model.add_rule(S_CONS, update_S, condition, ['all'])
        model.add_rule(I_CONS, update_I, condition, ['all'])
        
        initial_status = {
            S_CONS: 1,
            I_CONS: initial_status_I,
            R_CONS: 1
        }
        model.set_initial_status(initial_status, config)
        visualization_config = {
            'layout': 'fr',
            'plot_interval': 5,
            'plot_variable': I_CONS,
            'variable_limits': {
                I_CONS: [0, 1]
            },
            'show_plot': False,
            'cmin': -1,
            'cmax': 1,
            'color_scale': 'RdBu',
            'plot_output': './result/animated.gif',
            'plot_title': 'Animated network',
        }
        model.configure_visualization(visualization_config)
    elif type(model) is SWIRCustomModel: #just to SWIRModel
        config.add_model_parameter('kappa', beta)
        config.add_model_parameter('mu', mu)
        config.add_model_parameter('nu', nu)
        config.add_model_parameter('gamma', gamma)
        config.add_model_parameter("fraction_infected", fraction_infected)
        model.set_initial_status(config)

    return model, config

def epidemicSimulation(model, iteration):
    iterations = model.iteration_bunch(iteration)
    trends = model.build_trends(iterations)

    return iterations, trends 

def multEpidemicSimulation(model, n_execution, n_iteration, infection_sets, n_processes):
    return multi_runs(model, execution_number=n_execution, iteration_number=n_iteration, infection_sets=infection_sets, nprocesses=n_processes)

def view(model, trends, iterations=None):
    if type(model) is gc.CompositeModel or type(model) is SWIRCustomModel:
        viz = DiffusionTrend(model, trends)
        viz.plot(PATH_RESULT+"diffusion.pdf", percentile=90)
    elif type(model) is ContinuousModel:
        model.visualize(iterations)

def findCommunities(g):
    # Find the communities
    communities = sorted(nxcom.greedy_modularity_communities(g), key=len, reverse=True)
    # Count the communities
    print("The network has", len(communities), "communities.")

if __name__ == "__main__":
    #boot variables
    withContinuousModel = True
    mult_executions = False
    epidemicModel='SWIR' #SIR ou SWIR
    gamma = 1/14 #I->R
    r0 = 0.88
    #https://flaviovdf.github.io/covid19/#sudeste
    kappa = r0 * gamma #S->I

    mu = kappa * 0.15 #S->W
    nu = mu #W->I
    
    
    fraction_infected = 0.01
    n_iterations = 40 #iterations at model

    # Generate spatial network with communities
    g = generateSpatialGraph()
    
    #findCommunities(g)
    model, config = configureModel(g, kappa, gamma, fraction_infected, withContinuousModel, epidemicModel, mu, nu)
    trends = None
    if mult_executions:
        n_execution = 10
        infection_sets = None
        n_processes = 1
        trends = multEpidemicSimulation(model, n_execution, n_iterations, infection_sets, n_processes)
        view(model, trends)
    else:
        iterations, trends = epidemicSimulation(model, n_iterations)    
        view(model, trends, iterations)
    
    print("Simulation completed.")
    pass