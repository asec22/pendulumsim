from flask import Flask,render_template,url_for,request, jsonify
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import plotly.graph_objects as go
import numpy as np
import io
import os
import base64
from io import BytesIO
from numpy import sin, cos
from scipy.integrate import odeint

app = Flask(__name__)

# define the equation and parameters
def func(theta,nl):
    global thetastr
    thetastr=theta
    global g
    g=9.81
    global l
    l=nl
    global theta0
    theta0=np.radians(thetastr)
    global w
    w=np.sqrt(g/l)
    return w

def equations(y0,t0):
    theta, x=y0
    f=[x,-(g/l)*sin(theta)]
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
    # make figure
    fig_dict = {
        "data":[],
        "layout": {},
        "frames": []
    }

    # fill in most of layout
    fig_dict["layout"]["xaxis"] = {"range": [-l,l], "title": "X-Axis (m)"}
    fig_dict["layout"]["yaxis"] = {"range": [(l+1),-1], "title": "Y-Axis (m)"}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 0, "redraw": False},
                                    "fromcurrent": True, "transition": {"duration": (time_step*1000),
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Time:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": (time_step*1000), "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }
    j=0
    # make data
    for times in time:
        data_dict = {
            "x": x1,
            "y": y1,
            "mode":"lines",
            "line": {"width":0},
            "visible":True,
            "showlegend":False}
        data_dict2={
            "x": x2,
            "y": y2,
            "mode":"lines",
            "line": {"width":0},
            "visible":True,
            "showlegend":False}
        fig_dict["data"].append(data_dict)
        fig_dict["data"].append(data_dict2)
        j+=1


    # make frames
    k=0
    for times in time:
        frame = {"data": [], "name": str(round(times,2))}
        data_dict = {
                "x": [x1[k]],
                "y": [y1[k]],
                "mode": "markers",
                "marker": {"color":"red", "size":10},
                "name": "Nonlinear Solution",
                "showlegend":True}
        data_dict2 = {
            "x": [0,x1[k]],
            "y": [0,y1[k]],
            "mode": "lines",
            "line": {"color":"red", "width":2}}
        data_dict3={
                "x": [x2[k]],
                "y": [y2[k]],
                "mode": "markers",
                "marker": {"color":"blue", "size":10},
                "name": "Linear Solution",
                "showlegend":True}
        data_dict4={
                "x": [0,x2[k]],
                "y": [0,y2[k]],
                "mode": "lines",
                "line": {"color":"blue", "width":2}}
                
        frame["data"].append(data_dict)
        frame['data'].append(data_dict2)
        frame['data'].append(data_dict3)
        frame['data'].append(data_dict4)
    
        fig_dict["frames"].append(frame)
        k+=1
        slider_step = {"args": [
            [times],
            {"frame": {"duration": 0, "redraw": False},
             "mode": "immediate",
             "transition": {"duration": (time_step*1000) }}
        ],
            "label": str(round(times,2)),
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)


    fig_dict["layout"]["sliders"] = [sliders_dict]

    fig = go.Figure(fig_dict)

    fig.write_html('static/pendulum2.html',config={"displayModeBar": False})
    return fig    


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
        x1=l*sin(theta1[:,0])
        global y1
        y1=l*cos(theta1[:,0])
        
        #find the solution for the linear problem
    
        theta2=thetasol
        global x2
        x2=l*sin(theta2)
        global y2
        y2=l*cos(theta2)
 
        # plot the results
        pr=plot_results1(time,theta1,theta2)
       
        url=plot_results2()
        
    
        return render_template("plot4.html",image_url=pr)
    else:
        return render_template("index2.html")
    

if __name__=="__main__":
    app.run()