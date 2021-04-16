import threading
import time
from PController import PController


class Regulator(threading.Thread):
    '''The regulator class calls the controllers so '''
    def __init__(self, cf_client):
        self.cf_client = cf_client
        threading.Thread.__init__(self)

        self.period =10 # How long between every loop of the

        # Creating one controller for each dimension of freedome
        self.thrust_ctrl = PController()
        self.thrust_ctrl.set_params(K = 5, beta = 1, h = self.period)

        # Contructing the controllers



    def set_ref_gen(self, ref_gen):
        self.ref_gen = ref_gen

    def run(self):
        try:
            self.cf_client.reset_estimator()
            self.cf_client.make_position_sanity_check();


            while True:
                time_start = time.time()
                self.cf_client.cf.commander.send_setpoint(0, 0, 0,0)
                #print("Drar igång thrust-motorn ett par sekunder")
                self.cf_client.cf.commander.send_setpoint(0, 0, 0, 20000)
                print(self.cf_client.pos)
                time.sleep(3)
                print(self.cf_client.pos)
                self.cf_client.cf.commander.send_setpoint(0, 0, 0,0)
                # Read some inputs and write some outputs on every degree of
                # freedome. Synchronize every read and write on the instance of
                # the controller

                self.loop_sleep(time_start)
        except Exception as e:
            print("Exception in regulator: " + str(e))

    def loop_sleep(self, time_start):
        """ Puts the thread on sleep so that it takes at least self.h seconds
        between loop executions """
        duration = self.period-(time.time()-time_start)
        if duration>0:
            time.sleep(duration)
        else:
            print("Could not make the regulator loop deadline")



if __name__=="__main__":
    regul1 = Regulator()
    regul1.start()
    while True:
        pass
