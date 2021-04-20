# Starting the threads
from regulator import Regulator
from CFClient import CFClient
from threading import Thread
import time
#from GUI import MyFirstGUI

URI = 'radio://0/80/2M' # Link to the radio
# Starting some threads

# The regulator thread is started when the connection is set up
regul = Regulator(URI)

#regul.set_ref_gen("Temp") # Should take GUI as parameter
#gui.set_regul(regul)


#gui.start();

while True:
    pass
