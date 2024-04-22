from flask import Flask,render_template,url_for,request, jsonify
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation,PillowWriter
import numpy as np
import os
import io
import base64
import tempfile
from numpy import sin, cos
from scipy.integrate import odeint

app = Flask(__name__)

# define the equation and parameters
def func(theta,l):
    global thetastr
    thetastr=theta
    global g
    g=9.81
    global newlength
    newlength=l
    global theta0
    theta0=np.radians(thetastr)
    global w
    w=np.sqrt(g/l)
    return w

def equations(y0,t0):
    theta, x=y0
    f=[x,-(g/newlength)*sin(theta)]
    return f

def plot_results1(time,theta1,theta2):
    fig1 = plt.figure(figsize=(10,5))
    ax1 = fig1.subplots()
    ax1.plot(time,theta1[:,0],color="blue")
    ax1.plot(time,theta2,color="red")
    
    s='(Initial Angle='+str(thetastr)+' degrees)'
    ax1.set_title('Pendulum Angular Solutions' + s)
    ax1.set_xlabel('time(s)')
    ax1.set_ylabel('angle(rad)')
    ax1.legend(['nonlinear','linear'],loc='lower right')
    img = io.BytesIO()
    fig1.savefig(img, format='png')
    img.seek(0)
    # Encode bytes as base64 string
    image_path = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return image_path
    
def plot_results2():
    N=int(fs)
    l=newlength+1
    fig = plt.figure(figsize=(10,5))
    ax = fig.subplots()
    line1, = ax.plot(x1[0],y1[0],'o',color="blue")
    line2, = ax.plot([0.0,x1[0]],[0.0,y1[0]],color="blue")
    line3, = ax.plot(x2[0],y2[0],'o',color="red")
    line4, = ax.plot([0.0,x2[0]],[0.0,y2[0]],color="red")
    fr_number = ax.annotate(
    "0",
    (-l, -0.5),
    ha="left",
    va="top", 
    animated=True,
)
    ax.set_title('Pendulum Motion')
    ax.set_xlim(-l,l)
    ax.set_ylim(l,-1)
    ax.set_xlabel('x-axis(m)')
    ax.set_ylabel('y-axis(m)')
    ax.legend(['Nonlinear','','Linear',''],loc='lower right')

    # Function to update the plot in each frame of the animation
    def update(frame):
        line1.set_data(x1[frame],y1[frame])
        line2.set_data([0.0,x1[frame]],[0.0,y1[frame]])
        line3.set_data(x2[frame],y2[frame])
        line4.set_data([0.0,x2[frame]],[0.0,y2[frame]])
        fr_number.set_text(f"Frame: {frame}")
        return line1,line2,line3,line4,fr_number

    # Create the animation
    ani = FuncAnimation(fig, update, frames=range(N), repeat=False)

    # Show the plot
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as temp_file:
        writer = animation.PillowWriter(fps=int(1/time_step), metadata=dict(artist="Me",loop=0), bitrate=-1)
        ani.save(temp_file.name, writer=writer)

        # Read the file contents into a BytesIO object
        temp_file.seek(0)
        img = io.BytesIO(temp_file.read())
        
    # Don't forget to delete the temporary file
    os.remove(temp_file.name)

    # Encode bytes as base64 string
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url


@app.route('/',methods=["POST", "GET"])
def index():
    if request.method=="POST":
        return render_template('index2.html')
    else:
        return render_template('index2.html')
        

@app.route("/plotshow", methods=["POST", "GET"])
def plotshow():
   
    if request.method == "POST":
        #initial parameters and conditions
        newlength = float(request.form["length"])
        initial_angle = float(request.form["angle"])
        global time_step
        time_step=float(request.form['tstep'])
        
        new_funct=func(initial_angle,newlength)
        time_final=4*np.pi/w
        global time
        time=np.arange(0, time_final, time_step)
        global thetasol
        thetasol=[theta0*np.cos(w*t) for t in time]
        global fs
        fs=len(time)-1
        x0=np.radians(0.0)
    
        #find the solution to the nonlinear problem
    
        theta1=odeint(equations,[theta0,x0], time)
        global x1
        x1=newlength*sin(theta1[:,0])
        global y1
        y1=newlength*cos(theta1[:,0])
        
        #find the solution for the linear problem
    
        theta2=thetasol
        global x2
        x2=newlength*sin(theta2)
        global y2
        y2=newlength*cos(theta2)
 
        # plot the results
        pr=plot_results1(time,theta1,theta2)
       
        url=plot_results2()
        
        return render_template("plot2.html",image_url=pr,plot_url=url)
    else:
        return render_template("index2.html")
    

if __name__=="__main__":
    app.run()