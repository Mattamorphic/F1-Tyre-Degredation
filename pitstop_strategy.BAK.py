'''
    Simulating Race Strategies Based On Tyre Degreadation

    Author:
        Matthew Barber (3019756)
'''

import random
from matplotlib import pyplot as plt
from simanneal import Annealer
# import deap
import random
import time
from datetime import timedelta

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

    def fuelEffect(self, initial_fuel, current_fuel):
        '''
            Determine the effect that fuel is having on the car

            Args:
                current_fuel (float): The current fuel onboard

            Returns:
                (float)
        '''
        return (current_fuel / (6 * initial_fuel)) + 0.83

    def addLap(self, initial_fuel, current_fuel, grip_loss_factor):
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
        self.grip -= (self.deg * self.fuelEffect(initial_fuel, current_fuel)) * grip_loss_factor
        return self.grip

    def calculateLapTime(self, initial_fuel, current_fuel, base_lap_time, lap_time_factor):
        '''
            Calculates and returns the laptime based on the current fuel level and state of the tyre.

            Args:
                fuel            (float): The current fuel on board
                lap_time_factor (float): Used to simulate quicker cars

            Returns:
                float
        '''
        lap_time = (
            (base_lap_time * lap_time_factor)
            - (100 - ((100 / initial_fuel) * current_fuel))
            * (2 / initial_fuel)
        )
        return (
            lap_time + 2 if self.grip < self.GRIP_LIMIT
            else lap_time - self.grip
        )

    def reset(self):
        '''
            Resets the tyre to its initial state
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

class Track:

    def __init__(self, track_name, race_laps, lap_time, pit_duration, initial_fuel, fuel_consumption_per_lap):
        self.track_name = track_name
        self.race_laps = race_laps
        self.lap_time = lap_time
        self.pit_duration = pit_duration
        self.initial_fuel = initial_fuel
        self.fuel_consumption_per_lap = fuel_consumption_per_lap

    @staticmethod
    def sampleTrack():
        return Track(
            "Sample",
            60,
            90,
            24,
            105,
            1.72
        )

    def monaco():
        return Track(
            "Monaco",
            78,
            78,
            24,
            105,
            1.72
        )


class Car:
    '''
        F1 Car Model

        Args:
            track           (Track):    The track to run the simulation on
            initial_tyre    (Tyre):     The initital tyre for the strategy
            pit_laps        (list):     A list of ints representing laps to stop on
            pit_tyres       (list):     A list of tyres to map to the pit laps
            lap_time_factor (float):    A lap time factor to model car speed
            grip_loss_factor(float):    A lap titme factor to model grip loss
    '''

    '''
        Immutable constants
    '''
    # INITIAL_FUEL = 105
    # RACE_LAPS = 60
    # LAP_TIME = 90 # seconds
    # PIT_DURATION = 24 # seconds
    # FUEL_USE_RATE_PER_LAP = 1.72 # kg
    START_LAP_OFFSET = 5

    def __init__(self, track, initial_tyre, pit_laps, pit_tyres, lap_time_factor=1.0, grip_loss_factor=1.0):
        self.track = track
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
            and self.pit_laps[-1] < self.track.race_laps # The last stop can't be on the last lap
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
        for lap_number in range(0, self.track.race_laps):
            # calculate lap time
            lap_time = tyre.calculateLapTime(
                self.track.initial_fuel,
                fuel,
                self.track.lap_time,
                self.lap_time_factor
            )
            # add wear to the tyre
            tyre.addLap(self.track.initial_fuel, fuel, self.grip_loss_factor)
            fuel -= self.track.fuel_consumption_per_lap
            # Are we pitting at the end of the lap?
            if lap_number in pit_laps:
                lap_time += self.track.pit_duration
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
            self.track.initial_fuel,
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
            self.pit_tyres[random.randint(0, len(self.pit_laps)-1)] = self.chooseRandomTyre()

    def changeStartCompound(self):
        '''
            Change the start compound to a random compound
        '''
        self.initial_tyre = self.chooseRandomTyre()

    def changeLap(self):
        '''
            Choose a random pit lap, from the available laps and either increment, or decrementt
        '''
        change = 1 if random.randint(0, 1) == 0 else -1
        self.pit_laps[random.randint(0, len(self.pit_laps) - 1)] += change

    def move(self, withInitialTyre = False):
        '''
            Used in simulated annealing determine whether to change a tyre compound or a lap number
        '''
        options = 2 if withInitialTyre else 1
        choice = random.randint(0, options)

        if choice == 0:
            self.changeCompound()
        elif choice == 1:
            self.changeLap()
        else:
            self.changeStartCompound()

    @staticmethod
    def mercedes(track, initial_tyre, pit_laps, pit_tyres):
        return Car(
            track,
            initial_tyre,
            pit_laps,
            pit_tyres,
            0.987,
            0.966
        )

    @staticmethod
    def ferrari(track, initial_tyre, pit_laps, pit_tyres):
        return Car(
            track,
            initial_tyre,
            pit_laps,
            pit_tyres,
            0.99,
            0.99
        )

    @staticmethod
    def redbull(track, initial_tyre, pit_laps, pit_tyres):
        return Car(
            track,
            initial_tyre,
            pit_laps,
            pit_tyres,
            0.991,
            0.982
        )



class StrategyAnnealer(Annealer):
    '''
        Used for simulated annealing
        Wraps around the car class

        Args:
            car (Car): The car object to run the annealer against
    '''

    def __init__(self, car):
        super(StrategyAnnealer, self).__init__(car)
        self.include_initial_tyre_in_move = False

    def move(self):
        '''
            Make a small change to the simulation
        '''
        self.state.move(self.include_initial_tyre_in_move)
        time.sleep(0.001)

    def energy(self):
        '''
            Return the energy of the result, lower is better

            Returns:
                float
        '''
        return self.state.energy()

    def setIncludeInitialTyreInMove(self, include):
        '''
            Allow us to choose whether to include the initial tyre in the calculations

            Args:
                include (bool): Should include initial tyre in move
        '''
        self.include_initial_tyre_in_move = include



class Grapher:
    '''
        A wrapper class for creating the graphs

        Args:
            plt (matplotlib.plot): The global plotter object
    '''

    def __init__(self, plt):
        self.plt = plt

    def createPlots(self, title, columns, rows):
        '''
            Create a new canvas with a configuration of plots

            Args:
                title (str): The title for the window
                columns (int): The amount of graphs in columns
                rows (int): The amount of graphs in rows
        '''
        fig, plts = plt.subplots(rows, columns, figsize=(10,10))
        fig.canvas.set_window_title(title)
        fig.tight_layout(pad=5.0, w_pad=5.0, h_pad=10.0)
        return plts

    def degredation(self, track, tyres):
        '''
            Sample method to plot degredation

            Args:
                tyres               (list):     A list of tyres to map
                laps                (int):      The amount of laps to test for
                fuel                (int):      Starting fuel
                fuel_consumption    (float):    The fuel consumption rate per lap
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
        current_fuel = track.initial_fuel
        # Simulate a test of the tyres
        for i in range(0, track.race_laps):
            for tyre in tyres:
                tyre_data[tyre.type].addData(
                    tyre.grip,
                    tyre.calculateLapTime(
                        track.initial_fuel,
                        current_fuel,
                        track.lap_time,
                        1.0
                    )
                )
                tyre.addLap(track.initial_fuel, current_fuel, 1.0)
            current_fuel -= track.fuel_consumption_per_lap

        # Plot the results for each tyre
        (grip_plt, lap_time_plt) = self.createPlots("Testing the simulation", 2, 1)
        grip_plt.set_title('Degredation of all three compounds grip')
        grip_plt.set(xlabel="lap", ylabel="grip")
        lap_time_plt.set_title('Degredation of all three compounds lap time')
        lap_time_plt.set(xlabel="lap", ylabel="lap_time")
        for type, data in tyre_data.items():
            grip_plt.plot(data.grip, label=type)
            lap_time_plt.plot(data.lap_times, label=type)
        grip_plt.legend()
        lap_time_plt.legend()


    def graphStrategy(self, title, *cars):
        '''
            Using a car object graph a strategy

            Args:
                title   (str):      A title for the window
                cars    (iterable): Args making up cars
        '''

        if len(cars) == 1:
            columns, rows = (1, 1)
        else:
            columns, rows = (2, round(len(cars) / 2))
        plts = self.createPlots(title, columns, rows)
        # Convert cars into an iterable object, so we can fetch without worrying about index
        cars = iter(cars)
        for r in range(rows):
            for c in range(columns):
                try:
                    self.plotStrategy(plts[c, r] if rows > 1 else plts[c] if columns > 1 else plts, next(cars))
                except StopIteration:
                    break

    def plotStrategy(self, plt, car):
            '''
                Given a plot and a car, plot the strategy

                Args:
                    plt (subplot):  A sub plot to plot the data against
                    car (Car):      The car to simulate
            '''
            racetime = car.simulateRace()
            plt.plot(car.lap_times, label="lap times")
            xlabel, ylabel = self.strategyAxesLabels(car)
            plt.set_xlabel(xlabel, horizontalalignment="left", x=0)
            plt.set_ylabel(ylabel, horizontalalignment="left", y=0)
            plt.set_title(self.strategyTitle(racetime, car))
            plt.legend()

    def strategyTitle(self, racetime, car):
        '''
            Helper method to clean up the methods above

            Args:
                racetime    (float):    Racetime
                car         (Car):      A Car

            Returns:
                str
        '''
        return (
            f"{len(car.pit_laps)} stop Strategy\n"
            f"Race Time: {self.convertFloatToTimedelta(racetime)}"
        )

    def strategyAxesLabels(self, car):
        '''
            Helper method to clean up the method above, returns a tuple of strings

            Args:
                car (Car): A car

            Returns:
                tuple(str)
        '''
        return (
            "Lap Number \n"
            + f"Start: {car.initial_tyre.type.capitalize()} compound\n"
            + '\n'.join([
                f'Lap {car.pit_laps[i]} pit for {tyre.type.capitalize()} compound'
                for i, tyre in enumerate(car.pit_tyres)
            ]),
            "Lap Times"
        )

    def convertFloatToTimedelta(self, value):
        '''
            Converts a float into a timedelta

            Args:
                value (float): Float representing a duration of time in seconds
        '''
        # Seconds are just the value as an integer
        seconds = int(value)
        # Calulate the microseconds from the original value
        microseconds = (value * 1000000) % 1000000
        # Express as a timedelta (HH:MM:SS.ms)
        return timedelta(0, seconds, microseconds)


class CalulateStrategyWith:

    @staticmethod
    def Annealing(car, include_initial_tyre = False, iterations = 100000):
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



# MAIN

# Allows us to model different tracks
track = Track.sampleTrack()
monaco = Track.monaco()

grapher = Grapher(plt)
grapher.degredation(track, Tyre.allTyres())
grapher.graphStrategy(
    "Sample Strategies",
    Car(track, Tyre.softTyre(), [20], [Tyre.hardTyre()]),
    Car(track, Tyre.softTyre(), [10, 30], [Tyre.softTyre(), Tyre.mediumTyre()]),
    Car(track, Tyre.hardTyre(), [30, 45], [Tyre.softTyre(), Tyre.softTyre()])
)

grapher.graphStrategy(
    "Monaco Strategies",
    Car(monaco, Tyre.softTyre(), [20], [Tyre.hardTyre()]),
    Car(monaco, Tyre.softTyre(), [10, 30], [Tyre.softTyre(), Tyre.mediumTyre()]),
    Car(monaco, Tyre.hardTyre(), [30, 45], [Tyre.softTyre(), Tyre.softTyre()])
)

grapher.graphStrategy(
    "Annealing Strategies",
    CalulateStrategyWith.Annealing(
        Car(track, Tyre.softTyre(), [0], [Tyre.softTyre()])
    ),
    CalulateStrategyWith.Annealing(
        Car(track, Tyre.softTyre(), [18, 36], [Tyre.softTyre(), Tyre.mediumTyre()])
    ),
)

grapher.graphStrategy(
    "Annealing Monaco Strategies",
    CalulateStrategyWith.Annealing(
        Car(monaco, Tyre.softTyre(), [0], [Tyre.softTyre()])
    ),
    CalulateStrategyWith.Annealing(
        Car(monaco, Tyre.softTyre(), [18, 36], [Tyre.softTyre(), Tyre.mediumTyre()])
    ),
)
#
# grapher.graphStrategy(
#     "Annealing Monaco Strategies",
#     CalulateStrategyWith.Annealing(
#         Car(monaco, Tyre.softTyre(), [0], [Tyre.softTyre()])
#     )
# )

plt.show()
