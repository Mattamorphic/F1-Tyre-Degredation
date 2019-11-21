import random
from matplotlib import pyplot as plt
from simanneal import Annealer
# import deap
import random
import time

class Tyre:
    '''
        Class representing an F1 tyre

        Args:
            type (str)          : The type of the tyre
            initial_grip (float): The initital grip for the tyre
            initial_deg  (float): The standard degredation
            switch_point (float): The wear point where the grip falls off
            switch_deg   (float): A multiplier applied to degredation
    '''
    GRIP_LIMIT = 0.3

    def __init__(self, type, initial_grip, initial_deg, switch_point, switch_deg=1.25):
        self.type = type
        self.grip = initial_grip
        self.initial_grip = initial_grip
        self.deg = initial_deg
        self.initial_deg = initial_deg
        self.switch_point = switch_point
        self.switch_deg = switch_deg

    def __eq__(self, tyre):
        '''
            Tyres are equal if the properties are the same

            Args:
                tyre (Tyre): Compare tyre
        '''
        if not isinstance(Tyre, type):
            raise ValueError('operands must be of type Tyre')
        return (
            self.initial_grip == tyre.initial_grip
            and self.initial_deg == tyre.initial_deg
            and self.switch_point == tyre.switch_point
            and self.switch_deg == tyre.switch_deg
        )

    def fuelEffect(self, current_fuel):
        '''
            Determine the effect that fuel is having on the car

            Args:
                current_fuel (float): The current fuel onboard

            Returns:
                (float)
        '''
        return (current_fuel / (6 * Car.INITIAL_FUEL)) + 0.83

    def addLap(self, current_fuel, grip_loss_factor):
        '''
            Simulates the wear of the tyre after another lap has been completed.
            self.grip -= (self.deg * self.switch_deg) scaled by -> self.fuelEffect

            Args:
                current_fuel        (float): The current fuel on board
                grip_loss_factor    (float): Used for adjusting based on car

            Returns:
                (float)
        '''
        if self.grip < self.GRIP_LIMIT:
            self.grip = 0
            return self.grip
        if self.grip < self.switch_point:
            self.deg = self.deg * self.switch_deg
        self.grip -= (self.deg * self.fuelEffect(current_fuel)) * grip_loss_factor
        return self.grip

    def calculateLapTime(self, fuel, lap_time_factor):
        '''
        Calculates and returns the laptime based on the current fuel level and state of the tyre. The calculation starts off with the base lap time being scaled by the lap time factor (allows us to simulate faster and slower cars) and is adjusted as follows:
            – if the grip is above or equal 0.3 then subtract the grip from the laptime
            – if the grip falls below 0.3 then add 2 seconds as the tyre is considered to be unsafe and about to destroy itself.
            – reduce the laptime according to 2 times the fuel load. at 105Kg there should be zero reduction in time. at 0Kg you should be subtracting 2 seconds.
        '''
        lap_time = (
            (Car.LAP_TIME * lap_time_factor)
            - (100 - ((100 / Car.INITIAL_FUEL) * fuel))
            * (2 / Car.INITIAL_FUEL)
        )
        return (
            lap_time + 2 if self.grip < self.GRIP_LIMIT
            else lap_time - self.grip
        )

    def reset(self):
        '''
        resets the tyre to its initial state
        '''
        self.grip = self.initial_grip
        self.deg = self.initial_deg

    @staticmethod
    def softTyre():
        '''
            Static function to generate a soft tyre

            Returns:
                (Tyre)
        '''
        return Tyre(
            type='soft',
            initial_grip=2.0,
            initial_deg=0.03,
            switch_point=1.8
        )

    @staticmethod
    def mediumTyre():
        '''
            Static function to generate a medium tyre

            Returns:
                (Tyre)
        '''
        return Tyre(
            type='medium',
            initial_grip=1.5,
            initial_deg=0.02,
            switch_point=1.2
        )

    @staticmethod
    def hardTyre():
        '''
            Static function to generate a hard tyre

            Returns:
                (Tyre)
        '''
        return Tyre(
            type='hard',
            initial_grip=1.0,
            initial_deg=0.01,
            switch_point=0.75
        )

    @staticmethod
    def allTyres():
        '''
            Static function to generate a soft tyre

            Returns:
                (Tyre[])
        '''
        return [
            Tyre.softTyre(),
            Tyre.mediumTyre(),
            Tyre.hardTyre()
        ]


class Car:
    '''
        Immutable constants
    '''
    INITIAL_FUEL = 105
    RACE_LAPS = 60
    LAP_TIME = 90 # seconds
    PIT_DURATION = 24 # seconds
    FUEL_USE_RATE_PER_LAP = 1.72 # kg
    START_LAP_OFFSET = 5

    def __init__(self, initial_tyre, pit_laps, pit_tyres, lap_time_factor=1.0, grip_loss_factor=1.0):
        '''
            F1 Car Model

            Args:
                initial_tyre    (Tyre):     The initital tyre for the strategy
                pit_laps        (list):     A list of ints representing laps to stop on
                pit_tyres       (list):     A list of tyres to map to the pit laps
                lap_time_factor (float):    A lap time factor to model car speed
                grip_loss_factor(float):    A lap titme factor to model grip loss
        '''
        self.initial_tyre = initial_tyre
        self.pit_laps = pit_laps
        self.number_of_stops = len(pit_laps)
        self.pit_tyres = pit_tyres
        self.lap_times = []
        self.lap_time_factor = lap_time_factor
        self.grip_loss_factor = grip_loss_factor

    def isValidStrategy(self):
        '''
            Determines if this is a valid race strategy
        '''
        # First let's check compounds
        compounds = self.pit_tyres + [self.initial_tyre]
        # Create a set of unique values, and base this off the initial grip
        if len(set([tyre.initial_grip for tyre in compounds])) < 2:
            return False
        return (
            self.number_of_stops > 0 # There's at least one stop
            and len(self.pit_tyres) == len(self.pit_laps) # Equal amount of tyres to stops
            and self.pit_laps[0] > 1 # The first stop can't be on lap 1
            and self.pit_laps[-1] < self.RACE_LAPS # The last stop can't be on the last lap
            and len(self.pit_laps) == len(set(self.pit_laps)) # The pit_laps have to be unique
        )

    def resetCar(self):
        '''
            A helper method to reset the car for each simulation
        '''
        self.lap_times = []
        for tyre in self.pit_tyres:
            tyre.reset()
        self.initial_tyre.reset()

    def runRace(self, fuel, tyre, pit_laps, available_tyres):
        '''
            Given car specific parameters
            Run the race on these, and return a racetime

            Args:
                fuel (float):               The current fuel on board
                tyre (Tyre):                The starting tyre
                pit_laps (list):            A list of laps to stop on
                available_tyres (Iterable): The tyres for each stop

            Returns:
                    int
        '''
        racetime = self.START_LAP_OFFSET
        for lap_number in range(0, self.RACE_LAPS):
            # calculate lap time
            lap_time = tyre.calculateLapTime(fuel, self.lap_time_factor)
            # add wear to the tyre
            tyre.addLap(fuel, self.grip_loss_factor)
            fuel -= self.FUEL_USE_RATE_PER_LAP
            # Are we pitting at the end of the lap?
            if lap_number in pit_laps:
                lap_time += self.PIT_DURATION
                # Get the next available tyre
                tyre = next(available_tyres)
            self.lap_times.append(lap_time)
            racetime += lap_time
        return racetime

    def simulateRace(self):
        '''
            Simulate a race

            Returns:
                int
        '''
        # Validate thet strategy
        if not self.isValidStrategy():
            return 10000
        # Reset the car
        self.resetCar()
        # Run the race
        return self.runRace(
            self.INITIAL_FUEL,
            self.initial_tyre,
            self.pit_laps,
            iter(self.pit_tyres)
        )

    def energy(self):
        '''
            Used in simulated annealing and returns a simulated race
        '''
        return self.simulateRace()

    def chooseRandomTyre(self):
        '''
            Equally likely to return any one of the three tyre compounds

            Returns:
                Tyre
        '''
        return Tyre.allTyres()[random.randint(0, 2)]

    def changeCompound(self):
        '''
            Change a compound on one of the pit stops

            If this is a single stop, we change the tyre to a random compound
            If this is a multi-stop, we pick one of them, and change the compound for this specific stop
        '''

        if self.number_of_stops == 1:
            self.pit_tyres = [self.chooseRandomTyre()]
        else:
            self.pit_laps[random.randint(0, len(self.pit_laps)-1)] = self.chooseRandomTyre()


    def changeLap(self):
        '''
            Choose a random pit lap, from the available laps and either increment, or decrementt
        '''
        change = 1 if random.randint(0, 1) == 0 else -1
        self.pit_laps[random.randint(0, len(self.pit_laps) - 1)] += change

    def move(self):
        '''
            Used in simulated annealing determine whether to change a tyre compound or a lap number
        '''
        if random.randint(0, 1) == 0:
            self.changeCompound()
        else:
            self.changeLap()


class StrategyAnnealer(Annealer):
    '''
        Used for simulated annealing
        Wraps around the car class
    '''
    def __init__(self, car):
        super(StrategyAnnealer, self).__init__(car)

    def move(self):
        self.state.move()
        time.sleep(0.001)

    def energy(self):
        return self.state.energy()


def graph_degredation(tyres, laps, fuel, fuel_consumption, grip_plt, lap_time_plt):
    '''
        Sample method to function to plot degredation

        Args:
            tyres               (list):     A list of tyres to map
            laps                (int):      The amount of laps to test for
            fuel                (int):      Starting fuel
            fuel_consumption    (float):    The fuel consumption rate per lap
            grip_plt            (plot):     A plot for grip data
            lap_time            (plot):     A plot for lap time
    '''
    class DegredationData:
        '''
            Degredation data helper
        '''
        def __init__(self):
            self.grip = []
            self.lap_times = []

        def addData(self, grip, lap_time):
            '''
                Add data to our instance variables

                Args:
                    grip        (float): grip data
                    lap_time    (float): lap time
            '''
            self.grip.append(grip)
            self.lap_times.append(lap_time)

    # Dictionary for degredation data
    tyre_data = {tyre.type: DegredationData() for tyre in tyres}

    # Simulate a test of the tyres
    for i in range(0, laps):
        for tyre in tyres:
            tyre_data[tyre.type].addData(tyre.grip, tyre.calculateLapTime(fuel, 1.0))
            tyre.addLap(fuel, 1.0)

    # Plot the results for each tyre
    for type, data in tyre_data.items():
        grip_plt.plot(data.grip, label=type)
        lap_time_plt.plot(data.lap_times, label=type)


def graph_strategy(car, plt, title):
    '''
        Using a car object graph a strategy

        Args:
            car     (Car):  A car object
            plt     (Plot): A plot
            title   (str):  A plot title
    '''
    racetime = car.simulateRace()
    plt.plot(car.lap_times, label="lap times")
    plt.set_title(f"{title} overall time {racetime}")


def run_simulated_annealing_strategy(iterations = 100000):
    '''
        Use simulated annealing to determine the best strategy
    '''
    sim = StrategyAnnealer(Car(Tyre.softTyre(), [59], []))
    sim.steps = iterations
    state, e = sim.anneal()
    return state, e


# Configure the plots
_, ((grip_plt, lap_time_plt), (sample_one_stop_plt, simulated_one_stop_plt)) = plt.subplots(2, 2, figsize=(10,10))

grip_plt.set_title('Degredation of all three compounds grip')
grip_plt.set(xlabel="grip", ylabel="lap")
lap_time_plt.set_title('Degredation of all three compounds lap time')
lap_time_plt.set(xlabel="lap time", ylabel="lap")
sample_one_stop_plt.set(xlabel="lap", ylabel="lap time")
simulated_one_stop_plt.set(xlabel="lap", ylabel="lap time")

# Graph degredation tests and affects on lap times
graph_degredation(
    [Tyre.softTyre(), Tyre.mediumTyre(), Tyre.hardTyre()],
    Car.RACE_LAPS,
    Car.INITIAL_FUEL,
    Car.FUEL_USE_RATE_PER_LAP,
    grip_plt,
    lap_time_plt
)

# Graph an example strategy to test the simulation
graph_strategy(
    Car(Tyre.hardTyre(), [12], [Tyre.mediumTyre()]),
    sample_one_stop_plt,
    "Sample lap times (1 stop)"
)


# car, e = run_simulated_annealing_strategy()
# print(e)
# print(car.initial_tyre.type, [tyre.type for tyre in car.pit_tyres], car.pit_laps)
# graph_strategy(
#     car,
#     simulated_one_stop_plt,
#     "Simulated Annealing Strategy"
# )


plt.legend()
plt.show()
