# Using Simulated Annealing and Genetic Evolution to optimize pitstop strategy for competing F1 cars

## Overview
This project looks at calculating the optimal pit strategy for F1 cars based on tyre degredation, taking into account fuel effect, and the compound affect on grip across a race distance. The minima the different techniques in this case are looking for is overall racetime.

The first graphs created are those which test the underlying simulation by running the base tyres across a race distance to show the impact this has on grip over time, the other graph plots 3 graphs to the same window exploring three different strategies.

The graphs created as 2. and 3. provide samples of the simulations being run through the simulated annealing and genetic evolution strategies as a proof of concept, these take a test team and run these on comparative strategies.

4. Onwards deals with providing a number of scenarios and calculating the mapping the results of these to plots. Each scenario is passed through both simulated annealing and genetic evolution.


## Running the simulation

```
python3 pit_strategy.py
```

## Architecture
The project has been broken down into distinct modules and classes.

### pit_strategy
This is the entry point for the calculations and uses the custom modules and classes to calculate the optimal strategy. 

### Simulation  `app.simulation`
The simulation itself lives in the `app.simulation` module and is composed of three underlying classes namely, `car`, `track`, and `tyre`.

#### Car

The Car class represents an F1 car and is instantiated either directly with a Track, initial Tyre, a list of integers representing pit laps, and a list of Tyres that correspond with those pit laps, or through a static helper method such as `mercedes`, `ferrari`, or `redbull` which pre-populate some other the optional parameters and return a Car object.

These optional parameters are available at instantiation and allow you to configure the cars speed through the lap time factor, and how hard they run the tyres through the grip loss factor, as well as provide a team name and plot colour.

By using dependency injection for the Track and Tyres these can be abstracted out and tested independently. Mock objects can also be patched in.

#### Track

The Track class represents an F1 track that we are going to both simulate the race using, and provides context such as the race laps, the fuel required, the consumption per lap, the average lap time and the duration of a pitstop.

This can be instantiated directly or again through static methods. In the case of the above simulation the sampleTrack method provides the foundation for the calculations, however there is also a model of monaco available to use.

By creating this class and injecting this into the Car class this can be swapped out for other instances.

#### Tyre

The Tyre class represents an F1 cars tyre and is instantiated either directly with the type of the tyre, the initial grip, the initial degredation, the switch point (the point at which the tyre goes off), and the switch deg (the degredation factor to apply when the tyre goes off)

The logic for simulating tyre wear is handled here, the addLap method applies the wear of the tyre after the given lap providing the compound event, and updating the object attributes accordingly. The calculateLapTime method provides us with the timing based on the state of the current tyre, the average lap time, and current fuel on board.

There are a number of static methods available on the Tyre class that allow us to generate tyres of specific types (i.e. `Tyre.softTyre()` will create a soft tyre and return this)


### Algorithm `app.algorithm`
The algorithms that are run to calculate the strategy live in the `app.algorithm` module and is composed of the algorithms themselves (through approved libraries), as well as a factory for creating these


#### CalculateStrategyWith

This class acts as a factory (not quite - but close enough), with 2 static methods - one that uses simulated annealing, and one that uses genetic evolution, these both take equivalent parameters and return the same type of object, a Car.

#### StrategyAnnealer
This class extends from `Annealer` in the `simanneal` library, and uses the move and energy methods on the car class to calculate an optimal solution. There's an additional helper method we can apply here if we want to through the initial tyre into our simulation and the move call.

#### StrategyDeap
This class uses the `deap` library to perform genetic evolution on a population of individuals, the individuals in this case being instances of a car class with specific attributes. The default population size is 300, however upon instantiation the population and generations can be overridden. A car class is passed in to provide a base individual to model this population on.

### Render `app.render`
Render helpers are stored in this module, namely that for creating graphs, and a context enabled loader that can be used to update the command line / terminal on long running tasks.

#### Grapher
Working with matplotlib can involve a lot of repeated code, and it distracts from the calculations and logic, so extracting and abstracting this out makes a lot of sense. The Grapher class at instantiation takes an instance of `matplotlib.plot`

The public methods that are useful in this instance are:

1. `degredation` this method compares the given list of tyres against the given track and plot these to a single graph

2. `graphStrategy` this method takes in a title and uses the spread operator allowing us to provide any number of car parameters, creates a unique plot for each of these, it then runs the simulation for each car, and then maps the results to each unique plot (window)

3. `compareGraphStrategy` this method is similar to 2. however it will map multiple results from the simulation to the same plot allowing us to more easily compare the results.

#### Loader
Loader is a threaded loader with context support (see Pythons `with`), this operates on a separate thread when context is entered `__enter__` and runs the loadingTask method. This class is instantiated with an optional delay and an optional progress object. The delay allows us to optimise the rate at which this method is called, and the progress object allows us configuring of what is returned on each call in this separate thread.
