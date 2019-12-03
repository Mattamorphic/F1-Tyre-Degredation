'''
    Entry point for F1 Degredation Calculations

    Author:
        Matthew Barber <mfmbarber@gmail.com>
'''

from matplotlib import pyplot as plt

from app.algorithm import CalulateStrategyWith
from app.render.grapher import Grapher
from app.simulation import Car, Track, Tyre

if __name__ == "__main__":
    track = Track.sampleTrack()
    grapher = Grapher(plt)
    '''
    1. Write the simulation using the detail above and test it works by
    correlating your graphs against the ones above (50%)
    '''
    grapher.degredation(track, Tyre.allTyres())
    grapher.graphStrategy(
        "Sample Strategies",
        Car(track, Tyre.softTyre(), [20], [Tyre.hardTyre()]),
        Car(track, Tyre.softTyre(), [10, 30],
            [Tyre.softTyre(), Tyre.mediumTyre()]),
        Car(track, Tyre.hardTyre(), [30, 45],
            [Tyre.softTyre(), Tyre.softTyre()]))
    '''
    2. Map the simulation so it can run using simulated annealing to compute
    the ideal strategy (65%)
    '''
    grapher.graphStrategy(
        "Annealing Strategies",
        CalulateStrategyWith.Annealing(
            Car(track, Tyre.softTyre(), [0], [Tyre.softTyre()])),
        CalulateStrategyWith.Annealing(
            Car(track, Tyre.softTyre(), [18, 36],
                [Tyre.softTyre(), Tyre.mediumTyre()])),
    )
    '''
    3. Map the simulation so it can run using genetic algorithms to compute the
    ideal strategy (80%)
    '''
    grapher.graphStrategy(
        "Deap Strategies",
        CalulateStrategyWith.geneticAlgorithm(
            Car(track, Tyre.softTyre(), [10], [Tyre.softTyre()])),
        CalulateStrategyWith.geneticAlgorithm(
            Car(track, Tyre.softTyre(), [18, 36],
                [Tyre.softTyre(), Tyre.mediumTyre()])))
    '''
    4. Generate strategies using both simulated annealing and genetic algorithms
    for the following situations. You must detail what the best strategy is
    used (initial tyre, pitstop laps, and tyres used)for all three cars, write
    a small discussion of the strategy (time taken, any interesting effects,
    total discussion should be no more than 1,000 words). Also state which
    algorithm generated the result (100%)
        • All three qualified in the top 10 so will start the race on the soft and
        want to do a single stop
        • All three qualified in the top 10 so will start the race on the soft and
        want to do two stops
        • All three qualified in the top 10 but Mercedes is starting on the
        Medium while the others are on soft.
        • Ferrari and Red bull qualified in the top 10 starting on soft but
        Mercedes have a car starting at the back of the grid on the hard tyre.
        Ferrari and Red bull will do one stop while Mercedes will do two.
    '''
    '''
        Testing the simulation
    '''
    grapher.compareGraphStrategy(
        "One Stop Comparison Test Graph",
        Car.mercedes(track, Tyre.softTyre(), [20], [Tyre.hardTyre()]),
        Car.ferrari(track, Tyre.softTyre(), [19], [Tyre.hardTyre()]),
        Car.redbull(track, Tyre.softTyre(), [21], [Tyre.hardTyre()]),
    )
    '''
    • All three qualified in the top 10 so will start the race on the soft and
        want to do a single stop
    '''
    grapher.compareGraphStrategy(
        "Scenario 1: One Stop Comparison Annealing",
        CalulateStrategyWith.Annealing(
            Car.mercedes(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])),
        CalulateStrategyWith.Annealing(
            Car.ferrari(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])),
        CalulateStrategyWith.Annealing(
            Car.redbull(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])))
    grapher.compareGraphStrategy(
        "Scenario 1: One Stop Comparison Deap",
        CalulateStrategyWith.geneticAlgorithm(
            Car.mercedes(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])),
        CalulateStrategyWith.geneticAlgorithm(
            Car.ferrari(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])),
        CalulateStrategyWith.geneticAlgorithm(
            Car.redbull(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])))
    '''
    • All three qualified in the top 10 so will start the race on the soft and
        want to do two stops
    '''
    grapher.compareGraphStrategy(
        "Scenario 2: Multi Comparison Annealing",
        CalulateStrategyWith.Annealing(
            Car.mercedes(track, Tyre.softTyre(), [20, 40],
                         [Tyre.softTyre(), Tyre.mediumTyre()])),
        CalulateStrategyWith.Annealing(
            Car.ferrari(track, Tyre.softTyre(), [20, 40],
                        [Tyre.softTyre(), Tyre.mediumTyre()])),
        CalulateStrategyWith.Annealing(
            Car.redbull(track, Tyre.softTyre(), [20, 40],
                        [Tyre.softTyre(), Tyre.mediumTyre()])))
    grapher.compareGraphStrategy(
        "Scenario 2: Multi Stop Comparison Deap",
        CalulateStrategyWith.geneticAlgorithm(
            Car.mercedes(track, Tyre.softTyre(), [20, 40],
                         [Tyre.softTyre(), Tyre.mediumTyre()])),
        CalulateStrategyWith.geneticAlgorithm(
            Car.ferrari(track, Tyre.softTyre(), [20, 40],
                        [Tyre.softTyre(), Tyre.mediumTyre()])),
        CalulateStrategyWith.geneticAlgorithm(
            Car.redbull(track, Tyre.softTyre(), [20, 40],
                        [Tyre.softTyre(), Tyre.mediumTyre()])))
    '''
    • All three qualified in the top 10 but Mercedes is starting on the
        Medium while the others are on soft.
    '''
    grapher.compareGraphStrategy(
        "Scenario 3: One Stop Comparison Annealing",
        CalulateStrategyWith.Annealing(
            Car.mercedes(track, Tyre.mediumTyre(), [20], [Tyre.hardTyre()])),
        CalulateStrategyWith.Annealing(
            Car.ferrari(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])),
        CalulateStrategyWith.Annealing(
            Car.redbull(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])))
    grapher.compareGraphStrategy(
        "Scenario 3: One Stop Comparison Deap",
        CalulateStrategyWith.geneticAlgorithm(
            Car.mercedes(track, Tyre.mediumTyre(), [20], [Tyre.hardTyre()])),
        CalulateStrategyWith.geneticAlgorithm(
            Car.ferrari(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])),
        CalulateStrategyWith.geneticAlgorithm(
            Car.redbull(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])))
    '''
    Ferrari and Red bull qualified in the top 10 starting on soft but
    Mercedes have a car starting at the back of the grid on the hard tyre.
    Ferrari and Red bull will do one stop while Mercedes will do two.
    '''
    grapher.compareGraphStrategy(
        "Scenario 4: Mercedes on 2 stop, others on 1 stop",
        CalulateStrategyWith.Annealing(
            Car.mercedes(track, Tyre.hardTyre(), [30, 45],
                         [Tyre.softTyre(), Tyre.softTyre()])),
        CalulateStrategyWith.Annealing(
            Car.ferrari(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])),
        CalulateStrategyWith.Annealing(
            Car.redbull(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])))
    grapher.compareGraphStrategy(
        "Scenario 4: Mercedes on 2 stop, others on 1 stop",
        CalulateStrategyWith.geneticAlgorithm(
            Car.mercedes(track, Tyre.hardTyre(), [30, 45],
                         [Tyre.softTyre(), Tyre.softTyre()])),
        CalulateStrategyWith.geneticAlgorithm(
            Car.ferrari(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])),
        CalulateStrategyWith.geneticAlgorithm(
            Car.redbull(track, Tyre.softTyre(), [20], [Tyre.hardTyre()])))

plt.show()
