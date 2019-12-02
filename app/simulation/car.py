'''
    A model for an F1 Car

    Author:
        Matthew Barber
'''

import random
from .tyre import Tyre


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
    START_LAP_OFFSET = 5

    def __init__(
        self,
        track,
        initial_tyre,
        pit_laps,
        pit_tyres,
        lap_time_factor=1.0,
        grip_loss_factor=1.0,
        team='team',
        colour='blue'
    ):
        self.track = track
        self.initial_tyre = initial_tyre
        self.pit_laps = pit_laps
        self.number_of_stops = len(pit_laps)
        self.pit_tyres = pit_tyres
        self.lap_times = []
        self.lap_time_factor = lap_time_factor
        self.grip_loss_factor = grip_loss_factor
        self.team = team
        self.colour = colour

    def __copy__(self):
        obj = type(self).__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        return obj

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
            self.number_of_stops > 0
            and len(self.pit_tyres) == len(self.pit_laps)
            and self.pit_laps[0] > 1
            and self.pit_laps[-1] < self.track.race_laps
            and len(self.pit_laps) == len(set(self.pit_laps))
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

    def changeLap(self, variance):
        '''
            Choose a random pit lap, from the available laps and either increment, or decrementt
        '''
        pit_lap_index = random.randint(0, len(self.pit_laps) - 1)
        pit_lap = -1
        while pit_lap not in range(1, self.track.race_laps) or pit_lap == self.pit_laps[pit_lap_index]:
            pit_lap = self.pit_laps[pit_lap_index] + random.randint(0, variance)
        self.pit_laps[pit_lap_index] = pit_lap

    def move(self, withInitialTyre = False, variance = 1):
        '''
            Used in simulated annealing determine whether to change a tyre compound or a lap number
        '''
        options = 2 if withInitialTyre else 1
        choice = random.randint(0, options)

        if choice == 0:
            self.changeCompound()
        elif choice == 1:
            self.changeLap(variance)
        else:
            self.changeStartCompound()



    def __str__(self):
        return f"Car{self.team}, {self.intitial_tyre}"

    @staticmethod
    def mercedes(track, initial_tyre, pit_laps, pit_tyres):
        '''
            Static method to generate a mercedes

            Args:
                track           (Track):    The track we are simulating on
                initial_tyre    (Tyre):     The starting tyre
                pit_laps        (list):     The pit laps
                pit_tyres       (list):     The pit tyres
        '''
        return Car(
            track,
            initial_tyre,
            pit_laps,
            pit_tyres,
            0.987,
            0.966,
            'mercedes',
            'green'
        )

    @staticmethod
    def ferrari(track, initial_tyre, pit_laps, pit_tyres):
        '''
            Static method to generate a ferrari

            Args:
                track           (Track):    The track we are simulating on
                initial_tyre    (Tyre):     The starting tyre
                pit_laps        (list):     The pit laps
                pit_tyres       (list):     The pit tyres
        '''
        return Car(
            track,
            initial_tyre,
            pit_laps,
            pit_tyres,
            0.99,
            0.99,
            'ferrari',
            'red'
        )

    @staticmethod
    def redbull(track, initial_tyre, pit_laps, pit_tyres):
        '''
            Static method to generate a redbull

            Args:
                track           (Track):    The track we are simulating on
                initial_tyre    (Tyre):     The starting tyre
                pit_laps        (list):     The pit laps
                pit_tyres       (list):     The pit tyres
        '''
        return Car(
            track,
            initial_tyre,
            pit_laps,
            pit_tyres,
            0.991,
            0.982,
            'redbull',
            'blue'
        )
