# Starting the threads
from regulator import Regulator

# Starting some threads

ref_gen = GUI()

regul = Regulator()
regul.set_ref_gen(ref_gen)


regul.start();

gui.start();

while True:
    pass
