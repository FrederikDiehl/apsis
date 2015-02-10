__author__ = 'Frederik Diehl'

from sklearn import datasets
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error
from sklearn.cross_validation import cross_val_score
from apsis.assistants.experiment_assistant import PrettyExperimentAssistant
from apsis.models.parameter_definition import *
from apsis.assistants.lab_assistant import BasicLabAssistant, PrettyLabAssistant
import math
from sklearn.svm import NuSVC, SVC
import logging
from apsis.optimizers.bayesian.acquisition_functions import ProbabilityOfImprovement
from apsis.utilities.benchmark_functions import branin_func
import numpy as np

def test_function():
    param_defs = {
        "x": MinMaxNumericParamDef(-5, 10),
        "y": MinMaxNumericParamDef(0, 15)
    }

    #logging.basicConfig(level=logging.DEBUG)

    LAss = PrettyLabAssistant()

    LAss.init_experiment("rand", "RandomSearch", param_defs, minimization=True)
    LAss.init_experiment("bay", "BayOpt", param_defs, minimization=True, optimizer_arguments={"initial_random_runs": 5})
    #LAss.init_experiment("bay_mcmc", "BayOpt", param_defs, minimization=True, optimizer_arguments={"initial_random_runs": 5, "mcmc": True})

    results = []

    #evaluate all experiments one step at the time.
    for i in range(50):
        to_eval = LAss.get_next_candidate("rand")
        result = branin_func(to_eval.params["x"], to_eval.params["y"])
        results.append(result)
        to_eval.result = result
        print(to_eval)
        LAss.update("rand", to_eval)

        to_eval = LAss.get_next_candidate("bay")
        result = branin_func(to_eval.params["x"], to_eval.params["y"])
        results.append(result)
        to_eval.result = result
        print(to_eval)
        LAss.update("bay", to_eval)

        #to_eval = LAss.get_next_candidate("bay_mcmc")
        #result = branin_func(to_eval.params["x"], to_eval.params["y"])
        #results.append(result)
        #to_eval.result = result
        #print(to_eval)
        #LAss.update("bay_mcmc", to_eval)

    print("Best bay score:  %s" %LAss.get_best_candidate("bay").result)
    print("Best bay:  %s" %LAss.get_best_candidate("bay"))
    print("Best rand score: %s" %LAss.get_best_candidate("rand").result)
    print("Best rand:  %s" %LAss.get_best_candidate("rand"))
    #print("Best mcmc score: %s" %LAss.get_best_candidate("bay_mcmc").result)
    #print("Best mcmc:  %s" %LAss.get_best_candidate("bay_mcmc"))
    #x, y, z = BAss._best_result_per_step_data()
    print(LAss.exp_assistants["rand"].experiment.to_csv_results())
    LAss.plot_result_per_step(["rand", "bay"], plot_min=0, plot_max=10)


def test_boston():
    boston_data = datasets.load_boston()
    regressor = SVC(kernel="poly")
    param_defs = {
        "C": MinMaxNumericParamDef(0,10),
        "degree": FixedValueParamDef([1,2,3]),
        "gamma": MinMaxNumericParamDef(0, 10),
        "coef0": MinMaxNumericParamDef(0,10)
    }

    LAss = PrettyLabAssistant()

    LAss.init_experiment("rand", "RandomSearch", param_defs, minimization=False)
    LAss.init_experiment("bay", "BayOpt", param_defs, minimization=False)


    for i in range(20):
        to_eval = LAss.get_next_candidate("rand")
        print("rand" + str(to_eval.params))
        regressor.set_params(**to_eval.params)
        scores = cross_val_score(regressor, boston_data.data, boston_data.target,
                                 scoring="mean_squared_error", cv=3)
        result = scores.mean()
        to_eval.result = result
        LAss.update("rand", to_eval)

        to_eval = LAss.get_next_candidate("bay")
        print("bay" + str(to_eval.params))
        regressor.set_params(**to_eval.params)
        scores = cross_val_score(regressor, boston_data.data, boston_data.target,
                                 scoring="mean_squared_error", cv=3)
        result = scores.mean()
        to_eval.result = result
        LAss.update("bay", to_eval)

    print("================================")
    print("RAND")
    print(LAss.exp_assistants["rand"].experiment.candidates_finished)
    print("===================================")
    print("BAY")
    print(LAss.exp_assistants["bay"].experiment.candidates_finished)
    print("===================================")
    print("Best bay score:  %s" %LAss.get_best_candidate("bay").result)
    print("Best rand score: %s" %LAss.get_best_candidate("rand").result)
    #x, y, z = BAss._best_result_per_step_data()
    LAss.plot_result_per_step(["rand", "bay"])

if __name__ == '__main__':
    #test_boston()
    test_function()