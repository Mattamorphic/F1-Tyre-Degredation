'''
    A threaded loader with context support

    Author:
        Matthew Barber <mfmbarber@gmail.com>
'''
import sys
import time
import threading
import subprocess

class Loader:
    '''
        Worker thread to create a spinner in the terminal

        Args:
                delay (float): The delay time on the spinner
    '''
    isBusy = False
    delay = 0.1

    BARS = '▁▂▃▄▅▆▇█▇▆▅▄▃▁'
    SPINNER = '/-|-\|'

    @staticmethod
    def loadingCursor():
        '''
            Static method to yield each phase of the spinner

            Yields:
                (str)
        '''
        while 1:
            for cursor in Loader.BARS: yield cursor

    def __init__(self, delay=None, progress=None):
        self.loadingGenerator = self.loadingCursor()
        self.progress = progress
        if delay and float(delay): self.delay = delay

    def loadingTask(self):
        '''
            The task to run in the thread
        '''
        while self.isBusy: # Will execute until interrupted
            progress = self.progress if self.progress else ''
            print(f"{next(self.loadingGenerator)} {progress}")
            self.clearLine()


    def clearLine(self):
        '''
            Remove the last print, and reset the cursor
        '''
        time.sleep(self.delay)
        sys.stdout.write("\033[F") #back to previous line
        sys.stdout.write("\033[K") #clear line
        sys.stdout.flush()

    def __enter__(self):
        '''
            A magic method to help use the `with` context
        '''
        self.isBusy = True
        # Create a thread with the spinnerTask
        threading.Thread(target=self.loadingTask).start()

    def __exit__(self, exception, value, tb):
        '''
            Once the with code block has exeucted, exit
            Interrupting the threaed
        '''
        self.isBusy = False
        self.clearLine()
        if exception is not None:
            return False


class Progress:
    '''
        A reference object used to print progress
    '''
    def __init__(self, initial_value, total_value):
        self.value = initial_value
        self.total = total_value
        self.additional_data = ''

    def update(self, value):
        self.value = value

    def additionalData(self, *data):
        self.additional_data = ', '.join(data)

    def __str__(self):
        return f"{round(self.value * (100 / self.total), 2)}% {self.additional_data}"
