'''
    Factory for creating and running ssimulations against optimization tools

    Author:
        Matthew Barber <mfmbarber@gmail.com>
'''
from .strategy_annealer import StrategyAnnealer
from .strategy_deap import StrategyDeap


class CalulateStrategyWith:
    @staticmethod
    def Annealing(car, include_initial_tyre=False, iterations=100000):
        '''
            Use simulated annealing to determine the best strategy

            Args:
                car                     (Car):     An initial car to test with
                include_initial_tyre    (bool):    Include the initial tyre in moves
                iterations              (int):     Iteration limit

            Returns:
                Car
        '''
        sim = StrategyAnnealer(car)
        sim.setIncludeInitialTyreInMove(include_initial_tyre)
        sim.steps = iterations
        state, e = sim.anneal()
        return state

    @staticmethod
    def geneticAlgorithm(car, include_initial_tyre=False, generations=1000):
        '''
            Use genetic evolution to determine the best strategy

            Args:
                car                     (Car):     An initial car to test with
                include_initial_tyre    (bool):    Include the initial tyre in moves
                generations              (int):    Evolution generation limit

            Returns:
                Car
        '''
        return StrategyDeap(car, include_initial_tyre, generations).run()
