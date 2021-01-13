from tkinter import filedialog
import tkinter as tk
import time
import pickle
from PIL import Image,ImageTk
from stream import videostream,_canvas_size,colorize
import json
import os
import cv2
import numpy as np
EVEN=0
ODD=1
#farmbot_position: X:503, Y:413
class Sample:
    def __init__(self):
        self.rgbtop=None
        self.rgbside=None
        self.depth=None
        self.depthrgb=None
        self.timestamp=None
        self.parity=EVEN
        self.quality="a"

class app(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame=None
        self.stream = videostream()
        self.show_frame(Frame1)
    def show_frame(self,framename):
        frame=framename(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame=frame
        self._frame.pack_propagate(0)
        self._frame.pack()
    def exit(self):
        print("exiting...")
        self.stream.stop_streaming()
        exit(0)

class Frame1(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        parent.title("Sampling software")
        label=tk.Label(self,text="Seedling Database",font="Times 24 bold")
        label.pack()
        button1=tk.Button(self,text="Seedling sampler",command=lambda :parent.show_frame(Frame2))
        button1.pack()
        button2 = tk.Button(self, text="Database checker", command=lambda: parent.show_frame(Frame3))
        button2.pack()
        self.config(width=500,height=500)

class Frame2(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        parent.title("Seedling sampler")
        self.parent = parent
        self.seedlingnum=0
        self.samplenum=0
        self.quality="a"
        self.parity=EVEN
        self.selectionq=tk.IntVar()
        self.selectionp = tk.IntVar()
        self.config(width=800, height=800)
        self.folder_database=None
        self.doc=None
        self.dol=None
        #files of interest
        self.RGBtopimage=None
        self.RGBsideimage=None
        self.Depthimage=None
        self.Depthrgbimage=None
        self.Depthcolorized=None
        #flags
        self.rgb_captured=False
        self.depth_captured=False
        self.stop=False

        #Frames construction
        self.headerframe=tk.Frame(self,height=200,width=600)
        self.headerframe.grid(row=0,column=0)
        self.bodyframe=tk.Frame(self)
        self.bodyframe.grid(row=1,column=0)
        self.RGBframe=tk.Frame(self.bodyframe)
        self.RGBframe.grid(row=0,column=0)
        self.RGB_photoframe=tk.Frame(self.RGBframe,bg="gray",height=_canvas_size[1]+20,width=2*_canvas_size[0]+50)
        self.RGB_photoframe.grid_propagate(0)
        self.RGB_photoframe.grid(row=1,column=1)
        self.RGB_buttonframe=tk.Frame(self.RGBframe)
        self.RGB_buttonframe.grid(row=1,column=0)
        self.depthframe=tk.Frame(self.bodyframe)
        self.depthframe.grid(row=1,column=0)
        self.depth_photoframe=tk.Frame(self.depthframe,bg="gray",height=_canvas_size[1]+20,width=2*_canvas_size[0]+50)
        self.depth_photoframe.grid_propagate(0)
        self.depth_photoframe.grid(row=1,column=1)
        self.depth_buttonframe=tk.Frame(self.depthframe)
        self.depth_buttonframe.grid(row=1,column=0)
        self.quality_frame=tk.Frame(self.bodyframe)
        self.quality_frame.grid(row=0,column=1)
        self.special_buttons=tk.Frame(self.bodyframe)
        self.special_buttons.grid(row=1,column=1)
        self.logsframe=tk.Frame(self.bodyframe,bd=10,width=600,height=200)
        self.logsframe.grid_propagate(0)
        self.logsframe.grid(row=2,column=0)
        self.info_frame=tk.Frame(self.bodyframe)
        self.info_frame.grid(row=2,column=1)

        #Labels construction
        self.Seedling_label=tk.Label(self.headerframe,text="Processed Seedlings: {}".format(self.seedlingnum),font="Helvetica 24 bold")
        self.Seedling_label.grid(row=0,column=1)
        self.Samples_label=tk.Label(self.headerframe,text="Samples generated: {}".format(self.samplenum),font="Helvetica 24 bold")
        self.Samples_label.grid(row=0,column=2,padx=50)
        self.RGB_title=tk.Label(self.RGBframe,text="RGB Cameras",font="Times 14 underline")
        self.RGB_title.grid(row=0,column=0)
        self.depth_title=tk.Label(self.depthframe,text="Depth camera",font="Times 14 underline")
        self.depth_title.grid(row=0,column=0)
        self.quality_label=tk.Label(self.quality_frame,text="Quality", font="Helvetica 14 italic")
        self.quality_label.grid(row=0,column=1)
        self.logs=tk.Label(self.logsframe,font="Times 14 bold")
        self.logs.grid(row=0,column=0)

        #buttons construction
        self.rgb_position_button=tk.Button(self.RGB_buttonframe,text="Position",font="Times 12")
        self.rgb_position_button.grid(row=0,column=0)
        self.rgb_capture_button=tk.Button(self.RGB_buttonframe,text="Capture",font="Times 12",command=self.rgb_capture)
        self.rgb_capture_button.grid(row=1,column=0)
        self.rgb_clear_button=tk.Button(self.RGB_buttonframe,text="Clear",font="Times 12",command=self.rgb_clear)
        self.rgb_clear_button.grid(row=2,column=0)
        self.depth_position_button=tk.Button(self.depth_buttonframe,text="Position",font="Times 12")
        self.depth_position_button.grid(row=0,column=0)
        self.depth_capture_button=tk.Button(self.depth_buttonframe,text="Capture",font="Times 12",command=self.depth_capture)
        self.depth_capture_button.grid(row=1,column=0)
        self.depth_clear_button=tk.Button(self.depth_buttonframe,text="Clear",font="Times 12",command=self.depth_clear)
        self.depth_clear_button.grid(row=2,column=0)
        self.delete_last_button=tk.Button(self.special_buttons,text="Delete Last",font="Times 12")
        self.delete_last_button.grid(row=0,column=0)
        self.generate_button=tk.Button(self.special_buttons,text="Generate sample",font="Times 12",command=self.generate_sample)
        self.generate_button.grid(row=1,column=0)
        self.select_button=tk.Button(self.special_buttons,text="Select folder",font="Times 12",command=self.select)
        self.select_button.grid(row=2,column=0)
        self.exit_button=tk.Button(self.special_buttons,text="EXIT",fg="white",bg="red",font="Times 12 bold",command=self.exit2)
        self.exit_button.grid(row=3,column=0)

        #radio-buttons contruction
        self.quality_a_rb=tk.Radiobutton(self.quality_frame,text="A",variable=self.selectionq,value=0,command=self.selq)
        self.quality_b_rb = tk.Radiobutton(self.quality_frame, text="B", variable=self.selectionq, value=1,command=self.selq)
        self.quality_c_rb = tk.Radiobutton(self.quality_frame, text="C", variable=self.selectionq, value=2,command=self.selq)
        self.quality_a_rb.grid(row=1,column=0)
        self.quality_b_rb.grid(row=1, column=1)
        self.quality_c_rb.grid(row=1, column=2)

        self.canvas_top=tk.Label(self.RGB_photoframe,width=_canvas_size[0],height=_canvas_size[1])
        self.canvas_side = tk.Label(self.RGB_photoframe, width=_canvas_size[0], height=_canvas_size[1])
        self.canvas_depth = tk.Label(self.depth_photoframe, width=_canvas_size[0], height=_canvas_size[1])
        self.canvas_depthrgb = tk.Label(self.depth_photoframe, width=_canvas_size[0], height=_canvas_size[1])
        self.canvas_top.grid(row=0,column=0,padx=10,pady=10)
        self.canvas_side.grid(row=0, column=1,padx=10,pady=10)
        self.canvas_depth.grid(row=3, column=0,padx=10,pady=10)
        self.canvas_depthrgb.grid(row=3,column=2,padx=10,pady=10)
        parent.stream.start_streaming()
        self.refresh_canvas()
    def refresh_canvas(self):
        if self.rgb_captured is False:
            self.RGBtopimage=self.parent.stream.rgbtopframe
            self.RGBsideimage=self.parent.stream.rgbsideframe
        if self.depth_captured is False:
            self.Depthcolorized=self.parent.stream.colorized
            self.Depthrgbimage=self.parent.stream.depthrgb
            self.Depthimage=self.parent.stream.depthimage
        image = cv2.cvtColor(self.RGBtopimage, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image,_canvas_size,cv2.INTER_LINEAR)
        img = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.canvas_top.configure(image=img)
        self.canvas_top.image = img
        image = cv2.cvtColor(self.RGBsideimage, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, _canvas_size, cv2.INTER_LINEAR)
        img = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.canvas_side.configure(image=img)
        self.canvas_side.image = img
        image = cv2.cvtColor(self.Depthrgbimage, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, _canvas_size, cv2.INTER_LINEAR)
        img = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.canvas_depthrgb.configure(image=img)
        self.canvas_depthrgb.image = img
        image = cv2.cvtColor(self.Depthcolorized, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, _canvas_size, cv2.INTER_LINEAR)
        img = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.canvas_depth.configure(image=img)
        self.canvas_depth.image = img
        self.Seedling_label.configure(text="Processed Seedlings: {}".format(self.seedlingnum))
        self.Samples_label.configure(text="Samples generated: {}".format(self.samplenum))
        if self.stop is False:
            self.after(150, self.refresh_canvas)
    def rgb_capture(self):
        self.rgb_captured=True
        self.RGB_photoframe.configure(bg="green")
    def depth_capture(self):
        self.depth_captured=True
        self.depth_photoframe.configure(bg="green")
    def rgb_clear(self):
        self.rgb_captured = False
        self.RGB_photoframe.configure(bg="gray")
    def depth_clear(self):
        self.depth_captured = False
        self.depth_photoframe.configure(bg="gray")
    def generate_sample(self):
        if self.rgb_captured and self.depth_captured:
            if self.parity is EVEN:
                parity="even"
            elif self.parity is ODD:
                parity="odd"
            if self.quality is 0:
                quality="a"
            elif self.quality is 1:
                quality="b"
            elif self.quality is 2:
                quality="c"
            name="Sample_num"+"{}".format(self.samplenum)+"Q"+quality+"P"+parity
            cv2.imwrite(self.folder_database+"/RGBtop"+name+".jpg",self.RGBtopimage)
            cv2.imwrite(self.folder_database+"/RGBside"+name+".jpg",self.RGBsideimage)
            np.save(self.folder_database+"/Depth"+name+".npy",self.Depthimage)
            cv2.imwrite(self.folder_database+"/Depthrgb"+name+".jpg",self.Depthrgbimage)
            sample=Sample()
            sample.rgbtop="RGBtop"+name+".jpg"
            sample.rgbside="/RGBside"+name+".jpg"
            sample.depth="/Depth"+name+".npy"
            sample.depthrgb="/Depthrgb"+name+".jpg"
            sample.quality=quality
            sample.parity=parity
            file=open(self.folder_database+"/Sample{}.pkl".format(self.samplenum),"wb")
            pickle.dump(sample,file)
            secs=time.time()
            self.dol=time.ctime(secs)
            self.logs.configure(text="Sample {} generated succesfully".format(self.samplenum))
            self.samplenum+=1
            self.seedlingnum+=3
            self.create_json()
        else:
            self.logs.configure(text="Please capture from both cameras")
    def selq(self):
        self.quality=self.selectionq.get()
    def select(self):
        self.folder_database=filedialog.askdirectory(parent=self,title="Select database folder",initialdir="~/")
        self.logs.configure(text="Dabase folder is "+self.folder_database)
        for root, dir, files in os.walk(self.folder_database):
            if "db.json" in files:
                file=open(self.folder_database+"/db.json","r")
                database=json.load(file)
                self.seedlingnum=database["seedling_counter"]
                self.samplenum=database["sample_counter"]
                self.doc=database["doc"]
                self.dol=database["dol"]
                self.logs.configure(text="Database imported succesfully, last sample at {}".format(self.dol))
            else:
                sec=time.time()
                self.doc=time.ctime(sec)
                self.create_json()
    def create_json(self):
        database={"seedling_counter":self.seedlingnum,"sample_counter":self.samplenum,"doc":self.doc,"dol":self.dol}
        with open(self.folder_database+"/db.json","w") as file:
            json.dump(database,file)
    def exit2(self):
        self.parent.stream.stop_streaming()
        self.stop=True
        time.sleep(0.5)
        exit()

class Frame3(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        parent.title("Database checker")
        self.samplenum=0
        #frames construction
        self.totalsamples=0
        self.totalseedlings=0
        self.config(width=800, height=800)
        self.headerframe=tk.Frame(self)
        self.headerframe.grid(row=0,column=0)
        self.bodyframe=tk.Frame(self)
        self.bodyframe.grid(row=1,column=0)
        self.RGBframe = tk.Frame(self.bodyframe)
        self.RGBframe.grid(row=0, column=0)
        self.RGB_photoframe = tk.Frame(self.RGBframe, bg="gray", height=_canvas_size[1] + 20,width=2 * _canvas_size[0] + 50)
        self.RGB_photoframe.grid_propagate(0)
        self.RGB_photoframe.grid(row=1, column=1)
        self.depthframe = tk.Frame(self.bodyframe)
        self.depthframe.grid(row=1, column=0)
        self.depth_photoframe = tk.Frame(self.depthframe, bg="gray", height=_canvas_size[1] + 20,width=2 * _canvas_size[0] + 50)
        self.depth_photoframe.grid_propagate(0)
        self.depth_photoframe.grid(row=1, column=1)
        self.special_buttons=tk.Frame(self.bodyframe)
        self.special_buttons.grid(row=1,column=1)
        self.logsframe=tk.Frame(self.bodyframe,bd=10,width=600,height=200)
        self.logsframe.grid_propagate(0)
        self.logsframe.grid(row=2,column=0)
        self.info_frame=tk.Frame(self.bodyframe)
        self.info_frame.grid(row=2,column=1)

        #labels construction
        self.title=tk.Label(self.headerframe,text="Sample {}".format(self.samplenum),font="Helvetica 25")
        self.title.grid(row=0,column=1)
        self.RGB_title = tk.Label(self.RGBframe, text="RGB Cameras", font="Times 14 underline")
        self.RGB_title.grid(row=0, column=0)
        self.depth_title = tk.Label(self.depthframe, text="Depth camera", font="Times 14 underline")
        self.depth_title.grid(row=0, column=0)
        self.logs=tk.Label(self.logsframe)
        self.logs.grid(row=0,column=0)
        self.info_label=tk.Label(self.info_frame)
        self.info_label.grid(row=0,column=0)

        #canvas
        self.canvas_top = tk.Label(self.RGB_photoframe, width=_canvas_size[0], height=_canvas_size[1])
        self.canvas_side = tk.Label(self.RGB_photoframe, width=_canvas_size[0], height=_canvas_size[1])
        self.canvas_depth = tk.Label(self.depth_photoframe, width=_canvas_size[0], height=_canvas_size[1])
        self.canvas_depthrgb = tk.Label(self.depth_photoframe, width=_canvas_size[0], height=_canvas_size[1])
        self.canvas_top.grid(row=0, column=0, padx=10, pady=10)
        self.canvas_side.grid(row=0, column=1, padx=10, pady=10)
        self.canvas_depth.grid(row=3, column=0, padx=10, pady=10)
        self.canvas_depthrgb.grid(row=3, column=2, padx=10, pady=10)

        #buttons
        self.select_button = tk.Button(self.special_buttons, text="Select folder", font="Times 12", command=self.select)
        self.select_button.grid(row=0, column=0)
        self.next_button=tk.Button(self.special_buttons,text="Next", font="Times 12",command=self.next)
        self.next_button.grid(row=1,column=0)
        self.back_button=tk.Button(self.special_buttons,text="Back",font="Times 12",command=self.back)
        self.back_button.grid(row=2,column=0)
        self.exit_button=tk.Button(self.special_buttons,text="EXIT",fg="white",bg="red",font="Times 12 bold",command=self.exit3)
        self.exit_button.grid(row=3,column=0)
    def select(self):
        self.folder_database = filedialog.askdirectory(parent=self, title="Select database folder", initialdir="~/")
        for root, dir, files in os.walk(self.folder_database):
            if "db.json" in files:
                file = open(self.folder_database + "/db.json", "r")
                database = json.load(file)
                self.totalseedlings = database["seedling_counter"]
                self.totalsamples = database["sample_counter"]
                self.doc = database["doc"]
                self.dol = database["dol"]
                self.logs.configure(text="Database imported succesfully, last sample at {}".format(self.dol))
            else:
                self.logs.configure(text="No database found")
    def back(self):
        if self.samplenum > 0:
            self.samplenum-=1
            self.title.configure(text="Sample {}".format(self.samplenum))
            with open(self.folder_database+"/Sample{}.pkl".format(self.samplenum), "rb") as file:
                Sample = pickle.load(file)
            self.RGBtopimage = cv2.imread(self.folder_database+"/"+Sample.rgbtop, 1)
            self.RGBsideimage = cv2.imread(self.folder_database+"/"+Sample.rgbside, 1)
            self.Depthrgbimage = cv2.imread(self.folder_database+"/"+Sample.depthrgb, 1)
            depth = np.load(self.folder_database+"/"+Sample.depth)
            self.Depthcolorized = colorize(depth)
            self.refresh_canvas()

    def next(self):
        self.title.configure(text="Sample {}".format(self.samplenum))
        with open(self.folder_database + "/Sample{}.pkl".format(self.samplenum), "rb") as file:
            Sample = pickle.load(file)
        self.RGBtopimage = cv2.imread(self.folder_database + "/" + Sample.rgbtop, 1)
        self.RGBsideimage = cv2.imread(self.folder_database + "/" + Sample.rgbside, 1)
        self.Depthrgbimage = cv2.imread(self.folder_database + "/" + Sample.depthrgb, 1)
        depth = np.load(self.folder_database + "/" + Sample.depth)
        self.Depthcolorized = colorize(depth)
        self.refresh_canvas()
        self.samplenum+=1
        if self.samplenum > self.totalsamples -1 :
            self.samplenum-=1
    def refresh_canvas(self):
        image = cv2.cvtColor(self.RGBtopimage, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, _canvas_size, cv2.INTER_LINEAR)
        img = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.canvas_top.configure(image=img)
        self.canvas_top.image = img
        image = cv2.cvtColor(self.RGBsideimage, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, _canvas_size, cv2.INTER_LINEAR)
        img = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.canvas_side.configure(image=img)
        self.canvas_side.image = img
        image = cv2.cvtColor(self.Depthrgbimage, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, _canvas_size, cv2.INTER_LINEAR)
        img = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.canvas_depthrgb.configure(image=img)
        self.canvas_depthrgb.image = img
        image = cv2.cvtColor(self.Depthcolorized, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, _canvas_size, cv2.INTER_LINEAR)
        img = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.canvas_depth.configure(image=img)
        self.canvas_depth.image = img
    def exit3(self):
        exit()


if __name__=="__main__":
    app1=app()
    app1.mainloop()
