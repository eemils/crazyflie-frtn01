import tkinter as tk
from tkinter import *
from tkinter import messagebox
import datetime as dt
from regulator import Regulator
import numpy as np

import threading
import time

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
style.use("ggplot")

fig = Figure()
ax_thrust = fig.add_subplot(111)
ax_thrust.set_title("Thrust")
ax_thrust.set_xlabel("X axis")
ax_thrust.set_ylabel("Y axis")

continuePlotting=False
def start_plotting():
    global continuePlotting
    continuePlotting=True
def stop_plotting():
    global continuePlotting
    continuePlotting=False


def z_plotting(i, gui):
    if continuePlotting==True:
        [z_ref, z_pos, ctrl_sgnl] = gui.regulator.get_thrust_plot_data()
        length = len(gui.z_ref_plot_data)
        if length<50:
            gui.z_ref_plot_data = np.append(gui.z_ref_plot_data,float(z_ref))
            gui.z_pos_plot_data = np.append(gui.z_pos_plot_data,float(z_pos))
            gui.thrust_ctrl_sgnl_plot_data = np.append(gui.thrust_ctrl_sgnl_plot_data,float(ctrl_sgnl/60000))
        else:
            gui.z_ref_plot_data[0:49] = gui.z_ref_plot_data[1:50]
            gui.z_pos_plot_data[0:49] = gui.z_pos_plot_data[1:50]
            gui.thrust_ctrl_sgnl_plot_data[0:49] = gui.thrust_ctrl_sgnl_plot_data[1:50]

            gui.z_ref_plot_data[49] = float(z_ref)
            gui.z_pos_plot_data[49] = float(z_pos)
            gui.thrust_ctrl_sgnl_plot_data[49] = float(ctrl_sgnl)
        ax_thrust.clear()
        length = len(gui.z_ref_plot_data)
        ax_thrust.plot(np.arange(0,length), gui.z_ref_plot_data)
        ax_thrust.plot(np.arange(0,length), gui.z_pos_plot_data)
        ax_thrust.plot(np.arange(0,length),gui.thrust_ctrl_sgnl_plot_data)
        ax_thrust.set_xlim([length-50,length])
        ax_thrust.legend(['Reference','Position','Control Signal'])

class GUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        self.run()

    def callback(self):
        self.quit()

    def run(self):
        self.protocol("WM_DELETE_WINDOW", self.callback)

        self.title("Playing with the drone")
        self.geometry("800x700")

        # Thrust controller parameters
        self.thrust_lab = Label(self,text = "Thrust controller", font=("Arial Bold", 12))
        self.thrust_lab.grid(column=0,row=0, columnspan = 2)
        self.thrust_K_text = Label(self,text="K = ", font=("Arial",11))
        self.thrust_K_text.grid(column=0,row=1)
        self.thrust_K_input = Entry(self)
        self.thrust_K_input.grid(column=1, row=1)

        self.thrust_Td_text = Label(self,text="Td = ", font=("Arial",11))
        self.thrust_Td_text.grid(column=0,row=2)
        self.thrust_Td_input = Entry(self)
        self.thrust_Td_input.grid(column=1, row=2)

        self.thrust_N_text = Label(self,text="N = ", font=("Arial",11))
        self.thrust_N_text.grid(column=0,row=3)
        self.thrust_N_input = Entry(self)
        self.thrust_N_input.grid(column=1, row=3)


        # Roll and yaw controller parameters
        self.roll_yaw_lab = Label(self,text = "Roll and pitch controllers", font=("Arial Bold", 12))
        self.roll_yaw_lab.grid(column=0,row=5, columnspan = 2)
        self.roll_yaw_K_text = Label(self,text="K = ", font=("Arial",11))
        self.roll_yaw_K_text.grid(column=0,row=6)
        self.roll_yaw_K_input = Entry(self)
        self.roll_yaw_K_input.grid(column=1, row=6)
        self.roll_yaw_Td_text = Label(self,text="Td = ", font=("Arial",11))
        self.roll_yaw_Td_text.grid(column=0,row=7)
        self.roll_yaw_Td_input = Entry(self)
        self.roll_yaw_Td_input.grid(column=1, row=7)
        self.roll_yaw_N_text = Label(self,text="N = ", font=("Arial",11))
        self.roll_yaw_N_text.grid(column=0,row=8)
        self.roll_yaw_N_input = Entry(self)
        self.roll_yaw_N_input.grid(column=1, row=8)

        # Apply parameters to controllers button
        self.apply_params_button = Button(self,text="Apply parameters", command = self.apply_params_button_action)
        self.apply_params_button.grid(column=0,row=10, columnspan=2)

        self.continuePlotting = False
        # Start plotting button
        self.start_plotting = Button(self, text= "Start plotting",
            command = self.start_plotting_action)
        self.start_plotting.grid(column=3,row=0)

        # Stop plotting button
        self.stop_plotting = Button(self, text= "Stop plotting",
            command = self.stop_plotting_action)
        self.stop_plotting.grid(column=4,row=0)

        self.thrust_ctrl_sgnl_plot_data = np.array([])
        self.z_ref_plot_data = np.array([])
        self.z_pos_plot_data = np.array([])

        self.thrust_plot_canvas = FigureCanvasTkAgg(fig, master=self)
        self.thrust_plot_canvas.draw()
        self.thrust_plot_canvas.get_tk_widget().grid(row=1, column=3, columnspan=3, rowspan=3)


        #self.after(self.plotting_period, self.z_plot_data)
        #self.animation= animation.FuncAnimation(fig, z_plot_data, interval=self.plotting_period)

    def validate_int_input(self, input):
        if input == "": return True
        try:
            value = int(input)
        except ValueError:
            return False
        print(value)
        return value

    def apply_params_button_action(self):
        try:
            self.regulator.thrust_ctrl.set_params(K = float(self.thrust_K_input.get()),
                Td = float(self.thrust_Td_input.get()), N = float(self.thrust_N_input.get()))

            self.regulator.roll_ctrl.set_params(K = float(self.roll_yaw_K_input.get()),
                Td = float(self.roll_yaw_Td_input.get()), N = float(self.roll_yaw_N_input.get()))
            self.regulator.pitch_ctrl.set_params(K = float(self.roll_yaw_K_input.get()),
                Td = float(self.roll_yaw_Td_input.get()), N = float(self.roll_yaw_N_input.get()))
        except ValueError:
            messagebox.showerror("Input Error", "Controller variables must be numbers.")

    def set_regul(self,regulator):
        self.regulator = regulator
        self.thrust_K_input.insert(0, str(self.regulator.thrust_ctrl.K))
        self.thrust_Td_input.insert(0, str(self.regulator.thrust_ctrl.Td))
        self.thrust_N_input.insert(0, str(self.regulator.thrust_ctrl.N))
        self.roll_yaw_K_input.insert(0, str(self.regulator.roll_ctrl.K))
        self.roll_yaw_Td_input.insert(0, str(self.regulator.roll_ctrl.Td))
        self.roll_yaw_N_input.insert(0, str(self.regulator.roll_ctrl.N))

    def start_plotting_action(self):
        start_plotting()

    def stop_plotting_action(self):
        stop_plotting()


if __name__ == '__main__':
    regul = Regulator("radio://0/80/2M")
    plotting_period =250 # In ms
    gui = GUI()
    gui.set_regul(regul)
    z_ani=animation.FuncAnimation(fig, z_plotting,fargs=(gui,), interval=plotting_period)

    gui.mainloop()
