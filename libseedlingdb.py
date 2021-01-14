import pickle
import cv2
#from Sampling_app import Sample
import os
import time
import numpy as np
import pyrealsense2 as rs
import json


#GLOBAL VARIABLES
_depth_scale=9.999999747378752e-05
_intrinsics=rs.intrinsics()
_intrinsics.width=1280
_intrinsics.height=720
_intrinsics.ppx=639.399
_intrinsics.ppy=350.551
_intrinsics.fx=906.286
_intrinsics.fy=905.369
_intrinsics.model=rs.distortion.inverse_brown_conrady
_intrinsics.coeffs=[0.0,0.0,0.0,0.0,0.0]

EVEN=0
ODD=1

class Sample:
    def __init__(self):
        self.rgbtop=None
        self.rgbside=None
        self.depth=None
        self.depthrgb=None
        self.timestamp=None
        self.parity=EVEN
        self.quality="a"

class seedling_sample:
    def __init__(self):
        self.depth=None
        self.toprgb=None
        self.sidergb=None
        self.quality=None

class seedling_dataset:
    def __init__(self,folder):
        self.folder=folder
        self.creation_date=None
        self.last_date=None
        dbfile = open(self.folder+ "/db.json", "r")
        database = json.load(dbfile)
        self.seedlingnum = database["seedling_counter"]
        self.samplenum = database["sample_counter"]
        self.doc = database["doc"]
        self.dol = database["dol"]

    def read_sample(self,num):
        ssample=seedling_sample()
        with open(self.folder + "Sample{}.pkl".format(num), "rb") as file:
            print(file)
            sample = pickle.load(file)
        ssample.toprgb=cv2.imread(self.folder+sample.depthrgb,1)
        ssample.sidergb=cv2.imread(self.folder+sample.rgbside,1)
        ssample.depth=_depth_scale*np.load(self.folder+sample.depth)
        ssample.quality=sample.quality
        return ssample
