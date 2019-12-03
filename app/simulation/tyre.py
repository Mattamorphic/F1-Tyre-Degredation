'''
    Tyre Class

    Author:
        Matthew Barber (mfmbarber@gmail.com)
'''
import random


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

    def __init__(self,
                 type,
                 initial_grip,
                 initial_deg,
                 switch_point,
                 switch_deg=1.25):
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
        return (self.initial_grip == tyre.initial_grip
                and self.initial_deg == tyre.initial_deg
                and self.switch_point == tyre.switch_point
                and self.switch_deg == tyre.switch_deg)

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
        self.grip -= (self.deg * self.fuelEffect(
            initial_fuel, current_fuel)) * grip_loss_factor
        return self.grip

    def calculateLapTime(self, initial_fuel, current_fuel, base_lap_time,
                         lap_time_factor):
        '''
            Calculates and returns the laptime based on the current fuel level and state of the tyre.

            Args:
                fuel            (float): The current fuel on board
                lap_time_factor (float): Used to simulate quicker cars

            Returns:
                float
        '''
        lap_time = ((base_lap_time * lap_time_factor) -
                    (100 - ((100 / initial_fuel) * current_fuel)) *
                    (2 / initial_fuel))
        return (lap_time + 2 if self.grip < self.GRIP_LIMIT else lap_time -
                self.grip)

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
        return Tyre(type='soft',
                    initial_grip=2.0,
                    initial_deg=0.03,
                    switch_point=1.8)

    @staticmethod
    def mediumTyre():
        '''
            Static function to generate a medium tyre

            Returns:
                (Tyre)
        '''
        return Tyre(type='medium',
                    initial_grip=1.5,
                    initial_deg=0.02,
                    switch_point=1.2)

    @staticmethod
    def hardTyre():
        '''
            Static function to generate a hard tyre

            Returns:
                (Tyre)
        '''
        return Tyre(type='hard',
                    initial_grip=1.0,
                    initial_deg=0.01,
                    switch_point=0.75)

    @staticmethod
    def allTyres():
        '''
            Static function to generate a soft tyre

            Returns:
                (Tyre[])
        '''
        return [Tyre.softTyre(), Tyre.mediumTyre(), Tyre.hardTyre()]
