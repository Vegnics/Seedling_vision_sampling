import pickle
import cv2
import libseedlingdb as seedb
from libseedlingdb import Sample
import os
import time
import numpy as np
import pyrealsense2 as rs

_distance=0.46 #ground distance or max distance
_seedlingheight=0.28 #minimum distance

#set depth camera parameters
distance=0.359
depth_scale=9.999999747378752e-05
intrinsics=rs.intrinsics()
intrinsics.width=1280
intrinsics.height=720
intrinsics.ppx=639.399
intrinsics.ppy=350.551
intrinsics.fx=906.286
intrinsics.fy=905.369
intrinsics.model=rs.distortion.inverse_brown_conrady
intrinsics.coeffs=[0.0,0.0,0.0,0.0,0.0]

def colorize(depth_image):
    d_image=depth_image.astype(np.float)
    _min=_seedlingheight #_distance-_seedlingheight
    _max=_distance
    normalized=255.0*(d_image-_min)/(_max-_min)
    normalized=np.clip(normalized,0,255).astype(np.uint8)
    colorized=cv2.applyColorMap(normalized,cv2.COLORMAP_JET)
    return colorized

#It's possible to click on the depth image in order to know the spatial position of a pixel.
def click_depth_rgb(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        d_image = depth.astype(np.float)
        point = rs.rs2_deproject_pixel_to_point(intrinsics, [y, x], d_image[y, x])
        print("X= {x}, Y={y}, Z={z}".format(x=100 * point[0], y=100 * point[1], z=100 * point[2])) #
    return




#Set the dataset folder
folder="/home/amaranth/Desktop/Robot_UPAO/seedling_dataset_11_01_20/"

#GUI and mouse
cv2.namedWindow("depthimage")
cv2.setMouseCallback("depthimage", click_depth_rgb)

#Set the sample number
sample_num=57

#Open the sample
DB=seedb.seedling_dataset(folder)
sample=DB.read_sample(sample_num)
depth=sample.depth
depth_rgb=sample.toprgb
colorized=colorize(depth)