import random
# from app.simulation.car import Car
from app.render import Loader, Progress
from deap import base, creator, tools

class StrategyDeap:
    '''
        Used for Analysing cars with a Genetic Algoritm

    Args:

    '''
    # constants that define the likely hood of two individuals having crossover
    # performed and the probability that a child will be mutated
    CXPB = 0.5
    MUTPB = 0.2

    def __init__(
        self,
        car,
        with_initial_tyre,
        generations,
        population_size = 300
    ):
        self.car = car
        self.class_name = car.__class__
        self.generations = generations
        self.population_size = population_size
        self.with_initial_tyre = with_initial_tyre

    @staticmethod
    def evaluate(individual):
        '''
            Args:
                individual (car): The car that we are evaluating the fitness of
        '''
        return individual.simulateRace(),

    def init(self, class_name):
        car = class_name(
            self.car.track,
            self.car.initial_tyre,
            self.car.pit_laps,
            self.car.pit_tyres,
            self.car.lap_time_factor,
            self.car.grip_loss_factor,
            self.car.team,
            self.car.colour
        )
        car.move(self.with_initial_tyre)
        return car

    @staticmethod
    def crossover(ind1, ind2):
        child1 = ind1.__class__(ind1.track, ind1.initial_tyre, [], [])
        child2 = ind2.__class__(ind2.track, ind2.initial_tyre, [], [])
        child1.pit_laps = ind1.pit_laps
        child1.pit_tyres = ind2.pit_tyres
        child2.pit_laps = ind2.pit_laps
        child2.pit_tyres = ind1.pit_tyres
        return (child1, child2)

    @staticmethod
    def mutate(ind, indpb):
        if random.random() < indpb:
            ind.move() # TODO : Is this a small mutation?

    def getReferenceStrings(self):
        '''
            As the deap creator attaches references to the global
            we need to make sure that the individual and fitness we use is unique

            Returns:
                Tuple
        '''
        id = f"{self.car.team}_{random.randint(0, 99999)}"
        while id in globals():
            id = f"{self.car.team}_{random.randint(0, 99999)}"
        globals()[id] = True
        return (
            f"{id}_pop",
            f"{id}_ind",
            f"{id}_fit"
        )


    def buildToolbox(self, pop_id, ind_id, fit_id):
        '''
            Create a new fitness class in the creator
            Create a new car class in the creator (an individual)
            Generate a toolbox and register the behaviour

            Args:
                pop_id (str): A unique name for the population
                ind_id (str): A unique name for the individual
                fit_id (str): A unique name for the fitness

            Returns:
                deap.base.toolbox
        '''
        creator.create(fit_id, base.Fitness, weights=(-1.0,))
        creator.create(ind_id, self.car.__class__, fitness=getattr(creator, fit_id))
        toolbox = base.Toolbox()
        toolbox.register("individual", self.init, getattr(creator, ind_id))
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", StrategyDeap.evaluate)
        toolbox.register("mate", StrategyDeap.crossover)
        toolbox.register("mutate", StrategyDeap.mutate, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)
        return toolbox

    def run(self):
        '''
            Runs the genetic algorithm simulation

            Returns:
                Car (individual)
        '''
        toolbox = self.buildToolbox(*self.getReferenceStrings())
        population = toolbox.population(n=self.population_size)
        # Calculate the fitnesses for the population and attach these to the
        # individuals
        fitnesses = list(map(toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        fits = [ind.fitness.values[0] for ind in population]


        print(f"Running simulation for {self.car.team} on {len(self.car.pit_laps)} stop strategy based on {self.generations} generations")
        progress = Progress(0, self.generations)
        with Loader(0.2, progress):
            for generation in range(self.generations):
                progress.update(generation)
                # select the fittest parents for the next generation
                parents = toolbox.select(population, len(population))

                # take a full copy of the parents as we will use these instances to perform our crossover
                # and mutations
                offspring = list(map(toolbox.clone, parents))

                # choose the crossovers at random
                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    # test to see if we will do a crossover between two parents
                    if random.random() < self.CXPB:
                        # do the crossover and delete the fitness values as they refer to the parent fitness
                        # and not the children
                        toolbox.mate(child1, child2)
                        del child1.fitness.values
                        del child2.fitness.values

                # for each child in the offspring see if we will mutate it
                for mutant in offspring:
                    if random.random() < self.MUTPB:
                        toolbox.mutate(mutant)
                        del mutant.fitness.values

                # go through each child in the offspring. if they have an invalid fitness then reevaluate
                # their fitness
                for individual in offspring:
                    if not individual.fitness.valid:
                        individual.fitness.values = toolbox.evaluate(individual)

                # replace the population with the offspring
                population[:] = offspring

                # print out some stats about fitness of the population
                fits = []
                strongest_ind = population[0]
                for ind in population:
                    fitness = ind.fitness.values[0]
                    fits.append(fitness)
                    if fitness < strongest_ind.fitness.values[0]:
                        strongest_ind = ind
                length = len(population)
                mean = sum(fits) / length
                sum2 = sum(x*x for x in fits)
                std = abs(sum2 / length - mean ** 2)**0.5
                progress.additionalData(
                    f"Generation: {generation}",
                    f"Min: {min(fits)}",
                    f"Max: {max(fits)}",
                    f"Avg: {mean}",
                    f"Std: {std}",
                )

        print(
            f"Team: {strongest_ind.team}, ",
            f"Pit Laps: {strongest_ind.pit_laps},",
            f"Pit Tyres: {', '.join([tyre.type for tyre in strongest_ind.pit_tyres])},",
            f"Racetime: {strongest_ind.fitness.values[0]}"
        )
        return strongest_ind
