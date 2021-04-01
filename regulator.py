import threading
import time

class Regulator(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self):
        # Creating the controllers

    def run(self):
        try:
            while True:
                print("Running")
                # Read some inputs and write some outputs on every degree of
                # freedome. Synchronize every read and write on the instance of
                # the controller.
        except:
            print("Something went wrong in the regulator.")
