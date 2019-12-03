'''
    A helper class to wrap around creating the plots

    Author:
        Matthew Barber
'''
from datetime import timedelta


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
        fig, plts = self.plt.subplots(rows, columns, figsize=(10, 10))
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
                    tyre.calculateLapTime(track.initial_fuel, current_fuel,
                                          track.lap_time, 1.0))
                tyre.addLap(track.initial_fuel, current_fuel, 1.0)
            current_fuel -= track.fuel_consumption_per_lap

        # Plot the results for each tyre
        (grip_plt, lap_time_plt) = self.createPlots("Testing the simulation",
                                                    2, 1)
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
                    self.singlePlotGraph(
                        plts[c, r]
                        if rows > 1 else plts[c] if columns > 1 else plts,
                        next(cars))
                except StopIteration:
                    break

    def compareGraphStrategy(self, title, *cars):
        '''
            Using multiple car objects, graph these on the same plot

            Args:
                title (str): The title for the plot
                cars  (iter): An iterable of cars
        '''
        self.multiPlotGraph(self.createPlots(title, 1, 1), *cars)

    def multiPlotGraph(self, plt, *cars):
        '''
            Given a plot and any number of cars, plot the strategy

            Args:
                plt (subplot):  A plot to plot the data against
                cars (iter):    The cars to simulate
        '''
        racetimes = {}
        pit_laps = None
        for car in cars:
            racetimes[car.team] = {
                "pit_laps": car.pit_laps,
                "time": car.simulateRace()
            }
            plt.plot(car.lap_times, color=car.colour, label=car.team)
            if not pit_laps:
                pit_laps = len(car.pit_laps)
        plt.set_title(self.strategyTitle(pit_laps, racetimes))
        plt.legend()

    def singlePlotGraph(self, plt, car):
        '''
                Given a plot and a car, plot the strategy

                Args:
                    plt (subplot):  A sub plot to plot the data against
                    car (Car):      The car to simulate
            '''
        racetime = {
            car.team: {
                "pit_laps": car.pit_laps,
                "time": car.simulateRace()
            }
        }
        plt.plot(car.lap_times, color=car.colour, label=car.team)
        xlabel, ylabel = self.strategyAxesLabels(car)
        plt.set_xlabel(xlabel, horizontalalignment="left", x=0)
        plt.set_ylabel(ylabel, horizontalalignment="left", y=0)
        plt.set_title(self.strategyTitle(len(car.pit_laps), racetime))
        plt.legend()

    def strategyTitle(self, stops, racetimes):
        '''
            Helper method to clean up the methods above

            Args:
                stops         (int):    Amount of stops
                racetimes     (dict):    Racetimes

            Returns:
                str
        '''

        return (f"{stops} stop Strategy\n" + "\n".join([
            team.capitalize() +
            f" Race Time: {self.convertFloatToTimedelta(data['time'])}" +
            f" pitting on laps {','.join([str(lap) for lap in data['pit_laps']])}"
            for team, data in racetimes.items()
        ]))

    def strategyAxesLabels(self, car):
        '''
            Helper method to clean up the method above, returns a tuple of strings

            Args:
                car (Car): A car

            Returns:
                tuple(str)
        '''
        return (
            "Lap Number \n" +
            f"Start: {car.initial_tyre.type.capitalize()} compound\n" +
            '\n'.join([
                f'Lap {car.pit_laps[i]} pit for {tyre.type.capitalize()} compound'
                for i, tyre in enumerate(car.pit_tyres)
            ]), "Lap Times")

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
