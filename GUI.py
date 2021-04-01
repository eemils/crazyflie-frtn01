from tkinter import *
import threading

class MyFirstGUI:

    def __init__(self,window):
        self.window = window
        self.window.title("Playing with the drone")
        self.window.geometry("700x600")

        self.L1 = Label(self.window,text = "Hej David!", font=("Arial Bold", 20))
        self.L1.grid(column=0,row=0)

        self.B1 = Button(self.window,text="April", fg="red", command = self.click)
        self.B1.grid(column=0,row=1)

        self.chk = BooleanVar()
        self.chk.set (True)
        self.chk = Checkbutton(self.window, text="Lurad", var=self.chk)
        self.chk.grid(column=0, row=2)

        self.spin = Spinbox(self.window, from_=0, to=100, width=5)
        self.spin.grid(column=3,row=2)


    def click(self):
        self.ref = self.spin.get()
        print("ref is" + self.ref)

    def get_ref(self):
        return self.ref






root = Tk()
myGUI = MyFirstGUI(root)
root.mainloop()
