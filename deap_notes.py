

'''
    First argument is an alias through which we can reference our custotm fitness latter
    The second argument is the superclass of our representattion of fitness (generall base.Fitness)
    The third argument is what direction to wight as a stronger fitness
    1.0 === Anything that comes into this parameter the higher value === higher fitness
    -1.0 === the inverse is true if we use -1.0 (F1 == -1.0)
'''
# creator.create("FitnessMax", base.Fitness, weights=(-1.0,))

'''
    Next we need to tell DEAP what an individual looks like
    Second argument is the superclass of thte individual
    The third argument represents what fitness function we will use to evaluate fitness

    Link individual with the fitness function
'''
# creator.create("individual", [], fitness=creator.FitnessMax)


'''
    Toolbox will do the majority of the work of producing generations.
    We will need to setup a number of aliases to map onto the toolbox
    for our custom functionality
'''
# toolbox = base.Toolbox()

'''
    In instances where thte base container classes are used we generally associate a parital genetic
    code generation function with the toolbox.

    We have an attribute that is boolean in nature
        Random int function is called
        between 0, and 1

    Say an individual has 100 values, this would be called 100 times
'''
# toolbox.register("attr_bool", random.randint, 0, 1)

'''
    In this case we are generating a single random integer 100 times
    This is getting appended on to the inidvidual registored by creator.create

    This produces the genettic code

    The storage for hte genetic code will be an instance of creator.individual

    which was astandard python list
    and in order to generate the code we will call the attr_bool functiton 100 titmes
'''
# toolbox.register("inidividual", tools.initRepeat, creator.individual, totolbox.attr_bool, 100)


'''
    generate individuals as members of the populatiton and store them in the list
    toolbox.individual is used to create each of the individuals in the population ^^^
'''
# toolbox.register("populatiton", totols.initRepease, list, toolbox.individual)

'''
    With the population, the next step is to be able to evaluate the fitness of the population

    The fitness function will retutrn a tuple
    weights returned by function must mattch ^^^^


    fitness function should have one parameter called individual!
'''

# def evalOneMax(individual):
#     return sum(individual), ¯# <--- this is a tuple

'''
    Call the fitness function through toolbox's evaluate
'''
# toolbox.register("evaluate", evalOneMax)

'''
    How to cross over functionality - mating

    F1, one child is going to get the tyres, one child is going to get the pit laps
'''
# toolbox.register("mate", callback) # predefined --- we'll have to write this ourself

'''
    How to mutate the child
    The second argument states that we want a 1 in 20 chance
        for each bit that it will flip

    independent probability (0.0 -> 1.0)
        What is the likelihood of mutation
        This defines how wide the search space is (5% -> 10%)

'''

# toolbox.register("mutate", callback, indpb=0.05)

'''
    Selecting parents for producing the next generation

    Selection tournament select a subset of solutions to be parents (throw in 3, 2 come out)
'''
# toolbox.register("select", tools.selTournament, tournsize=3)

'''
    Generate a random population and evaluate their initial fitness

    Generatte the initial population using the population alias in the toolbox we set earlier
    Higher the population, higher the complexity -> wider search space

    The fitnesses of the populatiton will then be produced by putting
    each member of the population through the evaluate fitness alias

    This is the FIRST GENERATION don't eexpect good results!
'''
# pop = toolbox.population(n=300)
# finesses = list(map(toolbox.evaluate, pop))

'''
    Each member of population is associated with it's fitness ready for tournament
    Zip merges individual, with fitness, into a tuple
'''
# for ind, fit in zip(pop, fitnesses):
#     int.fitness.values = fit

'''
    Create a list for all of the fitnesses for itteration / evaluation purposes
'''
# fits = [ind.fitness.values[0] for ind in pop]

'''
    Generation loop
'''
# generation = 0
# while max(fits) < 100 and generation < 1000:
#     generation += 1
#     print(f"========= Generation {generation} ====")

    '''
        Run the selection tournament to select the parents and will then produce the children from that

        We take a clone of the parents to make the offspring - so we don't tend up with pass by reference issues
    '''

    # parents = toolbox.select(pop, len(pop))
    # offspring = list(map(toolbox.clone, parents))

    '''

        CXPB - Cross over probability probability that a pair of parents will be mated
        MUTPB - Mutation probability of the child
    '''
    # CXPB = 0.5
    # MUTPB = 0.2
    '''
        Take each suuccess pair of parents and crossover them

        If probability passes the parents will undergo crossover ro produce children, we then replace the pair of parents with the children

        we also delete the fitness values for the children as they now have a different genetic code from the parents
    '''
    # for child1, child2 in zip(offspring[::2], offspring[1::2]):
    #     if random.random() < CXPB:
    #         toolbox.mate(child1, child2)
    #         del child1.fitness.values
    #         del child2.fitness.values

    '''
        Potential mutation

        Subject all solutions to potential mutation

        if the probability is statisfiesd here - then mutate this

        Delete the fitness values as thtey are no longer valid
    '''
    # for mutant in offspring:
    #     if random.random() < MUTPB:
    #         toolbox.mutate(mutant)
    #         del mutant.fitness.values


    '''

    '''
    # for individual in offspring:
    #         # If this has been deleted
    #         if not individual.fitness.valid:
    #             individual.fitness.values = toolbox.evalue(individual)

    '''
        Tracking progress with stats
    '''
    # pop[:] = offspring
    # fits = [ind.fitness.values[0] for ind in pop]
    # length = len(pop)
    # mean = sum(fits) / length
    # sum2 = sum(x*x for x in fits)
    # std = abs(sum2 / length -  mean ** 2) ** 0.5
    # print(f"min: {min(fits)}")
    # print(f"max: {max(fits)}")
    # print(f"avg: {mean}")
    # print(f"std: {std}")

# fits at the end will have the final generations
# {time: car} maybe? 
