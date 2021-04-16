# Starting the threads
from regulator import Regulator
from CFClient import CFClient
from threading import Thread
import time
#from GUI import MyFirstGUI

# Setting
def start_regul(cf_client, regul):
    try:
        while cf_client.ready == False:
            print("Setting up connection...")
            time.sleep(2)
    except:
        pass
    regul.start()


URI = 'radio://0/80/2M' # Link to the radio
# Starting some threads

#gui = MyFirstGUI()
cf_client = CFClient(URI) # The regul will be started when cd_client is ready
regul = Regulator(cf_client)

regul.set_ref_gen("Temp") # Should take GUI as parameter
#gui.set_regul(regul)

# A way to run a method as a separate thread
Thread(target=start_regul, args = (cf_client,regul,)).start()

#regul.start();
#gui.start();

while True:
    pass
