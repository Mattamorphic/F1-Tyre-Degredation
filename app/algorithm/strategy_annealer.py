'''
    Simulated Annealing

    Author:
        Matthew Barber <mfmbarber@gmail.com>
'''

import time
from simanneal import Annealer

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
