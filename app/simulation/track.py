'''
    A Track class allowing us to model different tracks

    Author:
        Matthew Barber
'''

class Track:
    '''
        A track is populated with specific attributes
        name, laps, lap_time, etc.

        Args:
            track_name                  (str):      The name of the track
            race_laps                   (int):      The number of laps
            lap_titme                   (int):      The average lap time
            pit_duration                (int):      The average pit duration (enter:pit:exit)
            initial_fuel                (float):    The initial fuel for the track
            fuel_consumption_per_lap    (float):    Fuel usage per lap
    '''
    def __init__(
        self,
        track_name,
        race_laps,
        lap_time,
        pit_duration,
        initial_fuel,
        fuel_consumption_per_lap
    ):
        self.track_name = track_name
        self.race_laps = race_laps
        self.lap_time = lap_time
        self.pit_duration = pit_duration
        self.initial_fuel = initial_fuel
        self.fuel_consumption_per_lap = fuel_consumption_per_lap

    @staticmethod
    def sampleTrack():
        '''
            Static method to generate a sample track

            Returns:
                Track
        '''
        return Track(
            "Sample",
            60,
            90,
            24,
            105,
            1.72
        )

    def monaco():
        '''
            Static method to generate monaco

            Returns:
                Track
        '''
        return Track(
            "Monaco",
            78,
            78,
            24,
            105,
            1.72
        )
