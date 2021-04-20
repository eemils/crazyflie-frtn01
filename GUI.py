import tkinter as tk
from tkinter import *
import datetime as dt

import threading
import time

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

continuePlotting = False

def change_state():
    global continuePlotting
    if continuePlotting == True:
        continuePlotting = False
    else:
        continuePlotting = True

def real_time_plotters(gui):
    while continuePlotting:
        print("Hej")

        [new_pos, new_ctrl_sgnl, new_ref_sgnl] = gui.read_data()

        # Add x and y to lists
        gui.t_axis.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
        gui.pos_plot_data.append(new_pos)

        # Limit x and y lists to 20 items
        gui.t_axis = gui.t_axis[-20:]
        gui.pos_plot_data = gui.pos_plot_data[-20:]
        gui.ref_plot_data = gui.ref_plot_data[-20:]
        gui.ctrl_plot_data = gui.ctrl_plot_data[-20:]

        # Draw x and y lists
        gui.ax.clear()
        gui.ax.plot(gui.t_axis, gui.pos_plot_data)
        time.sleep(1)

class GUI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        self.root.title("Playing with the drone")
        self.root.geometry("700x600")

        self.L1 = Label(self.root,text = "Hej David!", font=("Arial Bold", 20))
        self.L1.grid(column=0,row=0)


        self.B1 = Button(self.root,text="Flyg i en fyrkant",bg="yellow", fg="black", command = self.click)
        self.B1.grid(column=0,row=1)

        self.start_stop_plotting_thread = Button(self.root, text= "Start plotting threads",
            command = self.start_stop_plotting_thread_action)
        self.start_stop_plotting_thread.grid(column=0,row=2)

        # Plot
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("X axis")
        self.ax.set_ylabel("Y axis")
        self.ax.grid()
        self.graph = FigureCanvasTkAgg(self.fig, master=self.root)
        self.graph.get_tk_widget().grid(row=4, column=4, columnspan=4)
        self.ref_plot_data = []
        self.pos_plot_data = []
        self.ctrl_plot_data = []
        self.t_axis = []


        self.chk = BooleanVar()
        self.chk.set (True)
        self.chk = Checkbutton(self.root, text="Lurad", var=self.chk)
        self.chk.grid(column=0, row=3)

        self.spin = Spinbox(self.root, from_=0, to=100, width=5)
        self.spin.grid(column=3,row=2)

        self.root.mainloop()

    def click(self):
        self.ref = self.spin.get()
        print("ref is" + self.ref)

    def start_stop_plotting_thread_action(self):
        change_state()
        threading.Thread(target=real_time_plotters, args=(self,)).start()

    def get_ref(self):
        return self.ref

    def set_regul(self,regulator):
        self.regulator = regulator

    def read_data(self):
        return [3, 3, 3]

if __name__ == '__main__':
    myGUI = GUI()
    while True:
        pass
