import json, pyvisa, types, math, os, time
import numpy as np

from datetime import datetime
from os.path import exists
from os import mkdir

from telnetlib import Telnet
from matplotlib.backend_bases import key_press_handler
## Helper functions

def send_ctc_msg(msg): 
# This function is responsible for translating commands into valid format & sending commands to the CTC device
    
    response=None
    i=10
    while(not to_abort_trigger and i>=0):
        try:
            ctc_device.write((msg+'\n').encode())
            response=ctc_device.read_until(b"\n",1).decode('ascii')
            break
        except:
            print("couldn't send message to ctc, trying again...")
            i-=1
            pass
    if(i<0):
        print("Couldn't send message to ctc even after max number of tries(10)")
    
    return response

def get_ctc_temp():
# Function to return the current temperature.
    i=20
    while(not to_abort_trigger and i>=0):
        try:
            return float(send_ctc_msg('"channel.'+ctc_in+'?"'))
        except:
            i-=1
            pass
    raise Exception("Couldn't get temperature from ctc!")

def Achieving_And_Stabilizing_temp(Temperature,tolerance): 
# Waits until the desired setpoint temp has been achieved and stabilises it for 100 seconds in 10 intervals.
    
    global ctc_out,ctc_in,ctc_high_limit,ctc_increase_limit,ctc_max_limit

    print(Temperature," Achieving temp")

    send_ctc_msg('"'+ctc_out+'.PID.Setpoint" '+str(Temperature))
    send_ctc_msg('"'+ctc_out+'.Hi lmt" '+str(ctc_high_limit))

    set_limit=ctc_high_limit
    i=0
    prev_temp=get_ctc_temp()
    while(not to_abort_trigger):
        t=get_ctc_temp()
        if( t>=Temperature-0.3 and t<=Temperature+0.3): break
        else:
            print(Temperature," Wait for achieve... ,current temp=",t)
            time.sleep(3)
            i+=1
            if(i>=10):
                i=0
                if(set_limit+ctc_increase_limit<=ctc_max_limit):
                    if(int(t)<=int(prev_temp)):
                        set_limit+=ctc_increase_limit
                        send_ctc_msg('"'+ctc_out+'.Hi lmt" '+str(set_limit))
                        print(Temperature," Temperature not achieved, increasing High Limit by "+str(ctc_increase_limit)," New High Limit= ",set_limit,"...",t)
                    prev_temp=t
                elif(set_limit>ctc_max_limit):
                    set_limit=ctc_max_limit
                    send_ctc_msg('"'+ctc_out+'.Hi lmt" '+str(set_limit))
                    print(Temperature," High Limit Altered during trigger, new High Value= ",set_limit)
    
    print(Temperature," Stabilizing temp")

    while((not to_abort_trigger)):
        t_min=get_ctc_temp()
        t_max=t_min
        i=0
        while((not to_abort_trigger) and i<10):
            i+=1
            T=get_ctc_temp()
            print(" stabilize T=",T)

            if(T>t_max):
                t_max=T
            if(T<t_min):
                t_min=T
            
            j=0
            while(not to_abort_trigger and j<10):
                j+=1
                time.sleep(1)

        print("checking stabilize, delta T=",t_max-t_min,"tolerance=",tolerance,)
        if(t_max-t_min<tolerance):
            break
        else:
            print(" Not yet stable, retrying...")


class Grapher: # this class controls the graph & it's ploting
    def __init__(self,r):
        self.line = None

        self.plot_data={}

        self.x_plot = "Temp"
        self.y_plot = "Resistance"

        
        self.frame=Frame(r)
        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.triggered=False
        
        self.ax=self.fig.add_subplot(1,1,1)
        self._clear()
        self.ax.set_xlabel("Temp")
        self.ax.set_ylabel("Resistance")
        

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)  # A tk.DrawingArea.
        self.canvas.draw_idle()
        self.canvas.set_cursor=lambda x:None # to avoid flickering
        self.canvas.get_tk_widget().pack(side=TOP, expand=1,fill="both")

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame) # toolbar

        self.toolbar.pan()

        self.toolbar.set_cursor=lambda x:None # to avoid flickering
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=TOP, expand=1)

        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.canvas.mpl_connect('scroll_event',self.mousewheel_move)

        self.canvas.mpl_connect("motion_notify_event", self.hover)

    def is_triggered(self,val): # checks if triggered, if so disables pan else enables pan
        self.triggered=val
        try:
            self.toolbar.pan()
        except: pass


    def _plot(self): # plots whatever changes are made to the graph data
        try:
            len_x=len(self.plot_data[self.x_plot])
            len_y=len(self.plot_data[self.y_plot])
            if( len_x< len_y):
                print("line 1")
                self.line, =self.ax.plot(np.array(self.plot_data[self.x_plot]),np.array(self.plot_data[self.y_plot][:len_x-1]),"-o")
            elif( len_x> len_y):
                print("line 2")
                self.line, =self.ax.plot(np.array(self.plot_data[self.x_plot][:len_y-1]),np.array(self.plot_data[self.y_plot]),"-o")
            else:
                print("line 3")
                self.line, =self.ax.plot(self.plot_data[self.x_plot],self.plot_data[self.y_plot],"-o")

            self.canvas.draw_idle()
        except Exception as e:
            print("cannot _plot, x_plot=",self.x_plot," y_plot=",self.y_plot,"error=",e)
            pass

    def _clear(self): # clears all previous plotted data
        self.ax.cla()
        self.ax.grid()
        self.ax.axhline(linewidth=2, color='black')
        self.ax.axvline(linewidth=2, color='black')

        self.annot = self.ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        

    def update_annot(self,ind): #updates the popup indicating x & y values
        x,y = self.line.get_data()
        self.annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        self.annot.set_text("x: {}\ny: {}".format(x[ind["ind"][0]], y[ind["ind"][0]]))
        self.annot.get_bbox_patch().set_alpha(0.4)

    def hover(self,event): #signals to show popup when hovering over any point
        if(self.line==None):
            return

        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.line.contains(event)
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()

    def mousewheel_move(self,event): #to allow scrolling for zooming in & out
        if(self.triggered):
            return

        self.ax=event.inaxes
        self.ax._pan_start = types.SimpleNamespace(
                lim=self.ax.viewLim.frozen(),
                trans=self.ax.transData.frozen(),
                trans_inverse=self.ax.transData.inverted().frozen(),
                bbox=self.ax.bbox.frozen(),
                x=event.x,
                y=event.y)
        if event.button == 'up':
            self.ax.drag_pan(3, event.key, event.x+10, event.y+10)
        else:
            self.ax.drag_pan(3, event.key, event.x-10, event.y-10)
        self.fig=self.ax.get_figure()
        self.fig.canvas.draw_idle()

    def on_key_press(self,event): #propogates every click even to their respective button in matplotlib
        key_press_handler(event, self.canvas, self.toolbar)


def trigger(): # the actual algorithm for varying temp and reciving data

    global ctc_start_temp, ctc_stop_temp, ctc_interval, ctc_tolerance, ctc_delay, ctc_cycle, ctc_increase_limit, ctc_max_limit, ctc_high_limit, ctc_out, ctc_in, to_abort_trigger, start_DC_current, DC_current_interval


    # plot_freq_entry.config(state="disabled")
    settings_btn.config(state="disabled")
    sync_get_btn.config(state="disabled")
    # sync_set_btn.config(state="disabled")
    

    try:
        print("Triggering CTC...")
        
        ctc_start_temp=float(ctc_start_entry.get())
        ctc_stop_temp=float(ctc_stop_entry.get())
        ctc_interval=float(ctc_interval_entry.get())
        ctc_tolerance=float(ctc_tolerance_entry.get())
        ctc_delay=float(ctc_delay_entry.get())
        ctc_cycle=complete_cycle_var.get()
        ctc_increase_limit=float(ctc_increase_limit_entry.get())
        ctc_max_limit=float(ctc_max_limit_entry.get())
        ctc_high_limit=float(ctc_high_limit_entry.get())
        ctc_out=ctc_output_var.get()
        ctc_in=ctc_input_var.get()


        ##### setting properties buffer & files #####
        storage_dir=settings["output_dir"]+"/"+title_entry.get()+" TD resistance"+(" Complete_Cycle" if complete_cycle_var.get()==1 else "")+" "+datetime.now().strftime('%H_%M_%S %d-%B-%Y')+"/"
        mkdir(storage_dir)

        print("Made directory at ",storage_dir)

        graph.plot_data["Temp"]=[]


        file=open(storage_dir+title_entry.get()+" "+"resistance" +"-T "+ datetime.now().strftime('%H_%M_%S %d-%B-%Y')+".txt", 'w')
        file.write("T(k)\Resistance(Ohm)\t")
        graph.plot_data={}

        file.flush()
        os.fsync(file.fileno())

        print("Created File...")

        plot_property["values"]=["resistance"]
        plot_property_var.set("resistance")

        graph._set_plot("Temp","resistance")

        print("set dropdown")

        update_plot_freq(False)
        



        send_ctc_msg('outputEnable on')

        ##### Algo #####
        curr_cycle=0
        while((not to_abort_trigger) and curr_cycle<=ctc_cycle):
            direction=1
            curr_temp=ctc_start_temp
            end_temp=ctc_stop_temp

            if(curr_cycle):
                curr_temp=ctc_stop_temp
                end_temp=ctc_start_temp 

            if(ctc_start_temp>ctc_stop_temp):
                if(not curr_cycle): 
                    direction=-1
            elif(curr_cycle):
                direction=-1
            
            print("Collecting data between begin Temp=",curr_temp," end Temp=",end_temp," Cycle=",curr_cycle," direction=",("Temp increasing" if direction==1 else "Temp decreasing"))

            #### looping through temp
            while((not to_abort_trigger) and curr_temp * direction <=end_temp * direction):

                print("-------- ",curr_temp," --------")

                file.write("\n"+str(curr_temp)+"\t")
                file.flush()
                os.fsync(file.fileno())

                Achieving_And_Stabilizing_temp(curr_temp,ctc_tolerance)

                print(curr_temp,"Stable! Now Delaying...") # This delaying is for to check the volatge..

                j=0
                while(not to_abort_trigger and j<ctc_delay):
                    j+=1
                    time.sleep(1)

                reading = 0
                resistance_vals = []
                curr_DC = start_DC_current
                while(not to_abort_trigger and reading < 5):
                    ## Send a command to AC/DC souce to set the current to curr_DC
                    # Write the code....

                    # Send a command to get the Voltage value from the Nanovoltmeter and store it in positive_cycle_voltage
                    # Write the code....
                    resistance_vals.append(positive_cycle_voltage/curr_DC)

                    ## Send a command to AC/DC current source to change the direction of the current

                    ## Send a command to AC/DC souce to set the current to curr_DC
                    # Write the code....

                    # Send a command to get the Voltage value from the Nanovoltmeter and store it in negative_cycle_voltage
                    # Write the code....

                    ## Send a command to AC/DC current source to change the direction of the current


                    resistance_vals.append(negative_cycle_voltage/curr_DC)

                    curr_DC += DC_current_interval
                    reading += 1
                
                curr_average_resistance = sum(resistance_vals)/len(resistance_vals)
                file.write(curr_average_resistance+"\t")
                file.flush()
                os.fsync(file.fileno())
                
                
                graph.plot_data["resistance"].append(float(curr_average_resistance))

                if(not to_abort_trigger):
                    graph.plot_data["Temp"].append(curr_temp)
                    graph._plot(False)
                
                curr_temp += direction * ctc_interval

            curr_cycle += 1

        print(" Closing file...")
            
        file.close()

        ################
        send_ctc_msg('outputEnable off')


        if(to_abort_trigger):
            to_abort_trigger=False
            global abort_trigger_popup
            abort_trigger_popup.destroy()
            messagebox.showinfo("Alert", "Aborted Trigger!\n")

        else:
            messagebox.showinfo("Alert", "Trigger Complete!\nOutput File Generated at:\n"+settings["output_dir"])
        
    except Exception as e:
        print("error while ongoing trigger ==>",e)
        if(to_abort_trigger):
            messagebox.showinfo("Alert", "Unexpectedly Aborted Trigger!\n")
        else:
            messagebox.showinfo("Error", "Some unexpected error has occured with the machine(s)\nPlease check if the machine(s) is on & try again")

    trigger_btn.config(text="Trigger",command=start_trigger,bg="SystemButtonFace")
    graph.is_triggered(False)

    # plot_freq_entry.config(state="normal")
    settings_btn.config(state="normal")
    sync_get_btn.config(state="normal")
    # sync_set_btn.config(state="normal")
