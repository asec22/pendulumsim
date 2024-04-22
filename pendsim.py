import tkinter as tk
import random
from math import pi, sin, cos

G = 9.81


class SimplePendulum():
    def __init__(self, length, initial_theta, delta):
        self.length = length
        self.initial_theta = initial_theta
        self.delta = delta
        self.period = 2 * pi * (self.length/G)**(1/2)
        self.time = 0
        self.theta = None
        
        self.frame = tk.Frame(root)
        self.scl_length = tk.Scale(self.frame, from_=25, to=350, length= 300, tickinterval=50, label= 'Length of Pendulum', troughcolor='yellow', orient=tk.HORIZONTAL)
        self.scl_length.set(length)
           
    def grid_widgets(self):
        self.frame.grid(row=0, column=1, rowspan=3)
        self.scl_length.grid(row=0,column=0, padx=10, pady=5)

    def incr_theta(self):
        self.initial_theta += pi/8
        if self.initial_theta >= pi:
            self.initial_theta = pi - pi/8
        self.time = 0

    def decr_theta(self):
        self.initial_theta -= pi/8
        if self.initial_theta < 0:
            self.initial_theta = 0
        self.time = 0

    def update_pendulum(self, pivot_x, pivot_y):
        self.length = self.scl_length.get()
        self.theta = self.initial_theta * cos((2*pi/self.period)*self.time)
        pend_x = pivot_x + self.length * sin(self.theta)
        pend_y = pivot_y + self.length * cos(self.theta)
        self.time += self.delta
        
        if self.time >= self.period:
            self.time = self.time - self.period
        
        return pend_x, pend_y 

class DoublePendulum():
    def __init__(self, mass_1, mass_2, length_1, length_2, theta_1, theta_2, delta):
        self.mass_1 = mass_1
        self.mass_2 = mass_2
        self.length_1 = length_1
        self.length_2 = length_2
        self.theta_1 = theta_1
        self.theta_2 = theta_2
        self.delta = delta
        self.deriv_theta_1 = 0
        self.deriv_theta_2 = 0

        self.frame = tk.Frame(root)
        self.scl_length_1 = tk.Scale(self.frame, from_=25, to=175, length= 300, tickinterval=50, label= 'Length of Pendulum 1', troughcolor='yellow', orient=tk.HORIZONTAL)
        self.scl_length_1.set(length_1)
        self.scl_length_2 = tk.Scale(self.frame, from_=25, to=175, length= 300, tickinterval=50, label= 'Length of Pendulum 2', troughcolor='yellow', orient=tk.HORIZONTAL)
        self.scl_length_2.set(length_1)

        self.grid_widgets()

    def grid_widgets(self):
        self.frame.grid(row=0, column=1, rowspan=3)
        self.scl_length_1.grid(row=0,column=0, padx=10, pady=5)
        self.scl_length_2.grid(row=1,column=0, padx=10, pady=5)
        
    def update_pendulum(self, pivot_x, pivot_y):
        self.length_1 = self.scl_length_1.get()
        self.length_2 = self.scl_length_2.get()
        # Compenents for the 2nd derivative of theta for pendulum 1 (https://www.myphysicslab.com/pendulum/double-pendulum-en.html)
        comp_1 = -G*(2*self.mass_1 + self.mass_2)*sin(self.theta_1) - self.mass_2*G*sin(self.theta_1 - 2*self.theta_2)
        comp_2 = 2*sin(self.theta_1 - self.theta_2)*self.mass_2*(self.deriv_theta_2**2*self.length_2 + self.deriv_theta_1**2*self.length_1*cos(self.theta_1-self.theta_2))
        comp_3 = self.length_1*(2*self.mass_1 + self.mass_2 - self.mass_2*cos(2*self.theta_1-2*self.theta_2))
        sec_deriv_theta_1 = (comp_1 - comp_2)/comp_3
        # Compenents for the 2nd derivative of theta for pendulum 2 
        comp_1 = 2*sin(self.theta_1-self.theta_2)
        comp_2 = self.deriv_theta_1**2*self.length_1*(self.mass_1 + self.mass_2) + G*(self.mass_1+self.mass_2)*cos(self.theta_1) + self.deriv_theta_2**2*self.length_2*self.mass_2*cos(self.theta_1-self.theta_2)
        comp_3 = self.length_2*(2*self.mass_1 + self.mass_2 - self.mass_2*cos(2*self.theta_1-2*self.theta_2))
        sec_deriv_theta_2 = (comp_1 * comp_2)/comp_3

        self.deriv_theta_1 += sec_deriv_theta_1 * self.delta
        self.deriv_theta_2 += sec_deriv_theta_2 * self.delta
        self.theta_1 += self.deriv_theta_1 * self.delta
        self.theta_2 += self.deriv_theta_2 * self.delta

        pend_1_x = pivot_x + self.length_1*sin(self.theta_1)
        pend_1_y = pivot_y + self.length_1*cos(self.theta_1)
        pend_2_x = pend_1_x + self.length_2*sin(self.theta_2)
        pend_2_y = pend_1_y + self.length_2*cos(self.theta_2)
        
        return pend_1_x, pend_1_y, pend_2_x, pend_2_y

class MainApplication(tk.Tk):
    def __init__(self, master, pendulum_params, double_pendulum_params):
        self.master = master
        self.frm_upper = tk.Frame(self.master)
        self.btn_simple = tk.Button(self.frm_upper,text="Simple Pendulum", command=lambda: self.switch(1))
        self.btn_double = tk.Button(self.frm_upper,text="Double Pendulum", state=tk.DISABLED,command= lambda: self.switch(0))
        self.frm_canvas = tk.Frame(self.master)
        self.canvas = tk.Canvas(self.frm_canvas, height=800, width=800, bg="black")
        self.frm_lower = tk.Frame(self.master)
        self.chk_trace = tk.Checkbutton(self.frm_lower, text="Trace", command=self.start_trace)
        self.btn_clear = tk.Button(self.frm_lower, text="Clear Trace", command=self.clear_trace)
        self.btn_pause = tk.Button(self.frm_lower, text="Pause", width=7, command=self.pause)
        
        self.pendulum = SimplePendulum(**pendulum_params)
        self.double_pendulum = DoublePendulum(**double_pendulum_params)
        self.pivot_x = int(self.canvas['width'])/2 # Location of pendulum pivot on canvas
        self.pivot_y = 300 
        self.btn_randomize = self.btn_randomize = tk.Button(self.double_pendulum.frame, text="Randomize (Initial Theta)", command=self.randomize)
        self.bool_trace = False
        self.bool_pause = False
        self.bool_display = False # False = Simple Pendulum, True = Double Pendulum
        self.all_traces = []
        self.curr_trace = []
        self.grid_pack_widgets()
        self.draw_double_pendulum()
        
        
    def grid_pack_widgets(self):
        self.frm_upper.grid(row=0, column=0)
        self.frm_canvas.grid(row=1, column=0)
        self.frm_lower.grid(row=2, column=0)
        self.btn_simple.pack(side=tk.LEFT)
        self.btn_double.pack(side=tk.LEFT)
        self.canvas.pack()
        self.chk_trace.pack(side=tk.LEFT)
        self.btn_clear.pack(side=tk.LEFT)
        self.btn_pause.pack(side=tk.LEFT) 
        self.btn_randomize.grid(row=2,column=0, padx=10, pady=5)

    def draw_simple_pendulum(self):
        if self.bool_pause:
            tk.after_id = self.canvas.after(15,self.draw_simple_pendulum)
        else:
            self.canvas.delete("pendulum")
            self.canvas.delete("line")
            self.canvas.delete("trace")
            self.simple_motion()
            tk.after_id = self.canvas.after(15, self.draw_simple_pendulum)

    def simple_motion(self):
        (x, y) = self.pendulum.update_pendulum(self.pivot_x, self.pivot_y)
        radius = 10
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, tag="pendulum", fill="white")
        self.canvas.create_line(self.pivot_x, self.pivot_y, x, y, width=3, tag="line", fill="white")
        
        if self.bool_trace:
            self.curr_trace.append((x,y,x,y))
        if self.all_traces:
            for trace in self.all_traces:
                self.canvas.create_line(trace, tag="trace", fill="white")
        if self.curr_trace:        
            self.canvas.create_line(self.curr_trace, tag="trace", fill="white")
       
    def draw_double_pendulum(self):
        if self.bool_pause:
            tk.after_id = self.canvas.after(15,self.draw_double_pendulum)
        else:
            self.canvas.delete("pendulum")
            self.canvas.delete("line")
            self.canvas.delete("trace")
            self.double_motion()
            tk.after_id = self.canvas.after(15, self.draw_double_pendulum)

    def double_motion(self):
        (x, y, x2, y2) = self.double_pendulum.update_pendulum(self.pivot_x, self.pivot_y)
        radius = 10
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, tag="pendulum", fill="white")
        self.canvas.create_oval(x2 - radius, y2 - radius, x2 + radius, y2 + radius, tag="pendulum", fill="white")

        self.canvas.create_line(self.pivot_x, self.pivot_y, x, y, width=3, tag="line", fill="white")
        self.canvas.create_line(x, y, x2, y2, width=3, tag="line", fill="white")

        if self.bool_trace:
            self.curr_trace.append((x2,y2,x2,y2))
        if self.all_traces:
            for trace in self.all_traces:
                self.canvas.create_line(trace, tag="trace", fill="white")
        if self.curr_trace:        
            self.canvas.create_line(self.curr_trace, tag="trace", fill="white")       
            
    def start_trace(self):
        if self.curr_trace:
            self.all_traces.append(self.curr_trace)
        self.curr_trace = []
        self.bool_trace = not self.bool_trace

    def clear_trace(self):
        self.curr_trace = []
        self.all_traces = []
        self.canvas.delete('trace')
    
    def pause(self):
        if self.bool_pause:
            self.btn_pause['text'] = "Pause"
            self.bool_pause = False
        else:
            self.btn_pause['text'] = "Resume"
            self.bool_pause = True

    def switch(self, val):
        if val is 1: # Switch to Simple Pendulum
            self.btn_simple['state'] = tk.DISABLED
            self.btn_double['state'] = tk.ACTIVE
            self.canvas.delete('all')
            self.canvas.after_cancel(tk.after_id)
            self.simple_motion()
            self.curr_trace = []
            self.all_traces = []
            self.double_pendulum.frame.grid_forget()
            self.pendulum.grid_widgets()
            self.draw_simple_pendulum()
        else: # Switch to Double Pendulum
            self.btn_simple['state'] = tk.ACTIVE
            self.btn_double['state'] = tk.DISABLED
            self.canvas.delete('all')
            self.canvas.after_cancel(tk.after_id)
            self.double_motion()
            self.curr_trace = []
            self.all_traces = []
            self.pendulum.frame.grid_forget()
            self.double_pendulum.grid_widgets()
            self.btn_randomize.grid(row=2,column=0, padx=10, pady=5)
            self.draw_double_pendulum()

    def randomize(self):
        if self.curr_trace:
            self.all_traces.append(self.curr_trace)
        self.curr_trace = []
        self.double_pendulum.theta_1 = random.uniform(-pi,pi)
        self.double_pendulum.deriv_theta_1 = 0
        self.double_pendulum.theta_2 = random.uniform(-pi,pi)
        self.double_pendulum.deriv_theta_2 = 0


if __name__ == '__main__':

    pend_params = {

        'length' : 300.0,
        'initial_theta' : pi/2,
        'delta' : .1

    }

    dub_pend_params = {
        'length_1' : 150,
        'length_2' : 150,
        'mass_1' : 5,
        'mass_2' : 5,
        'theta_1' : pi/2,
        'theta_2' : 3*pi/4,
        'delta' : .1,

    }

    root = tk.Tk()
    root.title("Pendulum Simulation")
    root.resizable(False,False)
    root.columnconfigure(1, weight=1)
    app = MainApplication(root, pend_params, dub_pend_params)
    root.mainloop()
pythontkinter