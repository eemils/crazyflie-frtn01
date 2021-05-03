# Starting the threads
from regulator import Regulator
from CFClient import CFClient
from threading import Thread
from GUI import GUI, z_plotting, fig
from matplotlib import animation
import cflib
import time
#from GUI import MyFirstGUI

URI = 'radio://0/80/2M' # Link to the radio
# Starting some threads
cflib.crtp.init_drivers(enable_debug_driver=False)

# The regulator thread is started when the connection is set up
regul = Regulator(URI)
plotting_period =1000 # In ms

# GUI
gui = GUI()
gui.set_regul(regul)
#Starting the plotting threads
z_ani=animation.FuncAnimation(fig, z_plotting, fargs=(gui,), interval=plotting_period)
gui.mainloop()
#regul.set_ref_gen("Temp") # Should take GUI as parameter
#gui.set_regul(regul)

while True:
    pass
