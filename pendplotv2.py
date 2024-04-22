import numpy as np
from numpy import sin, cos
from scipy.integrate import odeint
import matplotlib.pyplot as plt 
import tkinter as tk

# define the equation and parameters


def equations(y0,t0):
    g = 9.8
    l = float(entry1.get())
    theta, x=y0
    f=[x,-(g/l)*sin(theta)]
    return f

def plot_results(time,theta1,theta2):
    angle=entry2.get()
    file_name = entry5.get()
    plt.plot(time,theta1[:,0])
    plt.plot(time,theta2)
    
    s='(Initial Angle='+str(angle)+' degrees)'
    plt.title('Pendulum Motion' + s)
    plt.xlabel('time(s)')
    plt.ylabel('angle(rad)')
    plt.legend(['nonlinear','linear'],loc='lower right')
    plt.savefig(file_name)
    plt.show()
    

def submit():
    g = 9.8
    l = float(entry1.get()) 
    initial_angle = float(entry2.get())
    time_final =float(entry3.get())
    time_step = float(entry4.get())
    
    
    #initial parameters and conditions
    
    time=np.arange(0, time_final, time_step)
    theta0=np.radians(initial_angle)
    x0=np.radians(0.0)
    
    #find the solution to the nonlinear problem
    
    theta1=odeint(equations,[theta0,x0], time)
    
    #find the solution for the linear problem
    
    w=np.sqrt(g/l)
    theta2=[theta0*cos(w*t) for t in time]
   
    # plot the results
    
    plot_results(time,theta1,theta2)
    

    
root = tk.Tk()
root.title("Pendulum Parameters for Plotting")

label1 = tk.Label(root, text="Length (m)")
label1.pack()

entry1 = tk.Entry(root)
entry1.pack()

label2 = tk.Label(root, text="Initial Angle (degrees)")
label2.pack()

entry2 = tk.Entry(root)
entry2.pack()

label3 = tk.Label(root, text="End Time (s)")
label3.pack()

entry3 = tk.Entry(root)
entry3.pack()

label4 = tk.Label(root, text="Time Step (s)")
label4.pack()

entry4 = tk.Entry(root)
entry4.pack()

label5 = tk.Label(root, text="Plot File Name")
label5.pack()

entry5 = tk.Entry(root)
entry5.pack()

submit_button = tk.Button(root, text="Plot", command=submit)
submit_button.pack()

root.mainloop()

