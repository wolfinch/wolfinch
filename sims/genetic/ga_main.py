#! /usr/bin/env python
# '''
#  OldMonk Auto trading Bot
#  Desc:  Genetic Optimizer
# Copyright 2019, Joshith Rayaroth Koderi, OldMonk Bot. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
creator.create("Individual", dict, fitness=creator.FitnessMax)

toolbox = base.Toolbox()


toolbox.register("strat_gen", ga_ops.strategyGenerator)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.strat_gen)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

  
    
toolbox.register("evaluate", ga_ops.selectOneMax)
toolbox.register("mate", ga_ops.createOffSpring)
toolbox.register("mutate", ga_ops.createMutant, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
    random.seed()
    
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
    
    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=100, stats=stats,
                        halloffame=hof)

    print ("stats:\n%s\nhof:\n%s"%(str(stats), str(hof)))
    return pop, stats, hof

if __name__ == "__main__":
    main()
    
#EOF    