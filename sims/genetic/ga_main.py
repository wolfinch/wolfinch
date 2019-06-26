#! /usr/bin/env python
# '''
#  OldMonk Auto trading Bot
#  Desc:  exchange interactions Simulation
#  (c) Joshith
# '''

import random

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

from utils import getLogger
import ga_ops

# __name__ = "EA-BACKTEST"
log = getLogger (__name__)
log.setLevel (log.CRITICAL)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))

#TODO: FIXME: ideally, list should be a dict for strategy dict, working around some issues here. check ga_ops.py
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()


toolbox.register("strat_gen", ga_ops.strategyGenerator)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.strat_gen, 1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

  
    
toolbox.register("evaluate", ga_ops.selectOneMax)
toolbox.register("mate", ga_ops.createOffSpring)
toolbox.register("mutate", ga_ops.createMutant, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
    random.seed(64)
    
    pop = toolbox.population(n=300)
    
    log.debug ("pop: %s"%pop)
    # Numpy equality function (operators.eq) between two arrays returns the
    # equality element wise, which raises an exception in the if similar()
    # check of the hall of fame. Using a different equality function like
    # numpy.array_equal or numpy.allclose solve this issue.
    hof = tools.HallOfFame(4, similar=numpy.array_equal)
    
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    
    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=400, stats=stats,
                        halloffame=hof)

    return pop, stats, hof

if __name__ == "__main__":
    main()
    
#EOF    