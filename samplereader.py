import pickle
import cv2
from Sampling_app import Sample,colorize
import os
import time
import numpy as np
import pyrealsense2 as rs

#It's possible to click on the depth image in order to know the spatial position of a pixel.
def click_depth_rgb(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        d_image = depth_scale * (depth.astype(np.float))
        point = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], d_image[y, x])
        print("X= {x}, Y={y}, Z={z}".format(x=100 * point[0], y=100 * point[1], z=100 * point[2])) #
    return


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

#Set the dataset folder
folder="/home/labinm_robotica/new_seed_db/"

#GUI and mouse
cv2.namedWindow("depthimage")
cv2.setMouseCallback("depthimage", click_depth_rgb)

#Set the sample number
sample_num=1

#Open the sample
with open(folder+"Sample{}.pkl".format(sample_num),"rb") as file:
    Sample=pickle.load(file)
    print(folder+Sample.depthrgb)
depth_rgb=cv2.imread(folder+Sample.depthrgb,1)
depth=depth_scale*np.load(folder+Sample.depth)
colorized=colorize(depth,resize=False)

#Segment rgb image using depth information
binarized_coords=zip(*np.where((depth<0.36)&(depth>0.25)))# pixels between 3cm and 33 cm
binarized_coords=list(binarized_coords)
binarized_rgb=np.zeros(depth_rgb.shape,dtype=np.uint8)
for coord in binarized_coords:
    binarized_rgb[coord[0],coord[1]]= depth_rgb[coord[0],coord[1]]

#Show the results
cv2.imshow("depthimage",binarized_rgb)
cv2.waitKey(0)
cv2.destroyAllWindows()
