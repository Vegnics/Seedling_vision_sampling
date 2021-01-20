#!/home/labinm_robotica/.virtualenvs/cv/bin/python
import pickle
import cv2
#from Sampling_app import Sample,colorize
import libseedlingdb as seedb
from libseedlingdb import Sample
import os
import time
import numpy as np
import pyrealsense2 as rs

process = True

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
        print("X= {x}, Y={y}, Z={z}, H={h}, S={s}".format(x=100 * point[0], y=100 * point[1], z=100 * point[2],h=hsv_img[y,x,0],s=hsv_img[y,x,1])) #
    return

def nearest_pixel_contour(px,cnt):
    distances=np.abs(cnt[:,0]-px[1])+np.abs(cnt[:,1]-px[0])
    min_idx = np.argmin(distances)
    idx = cnt[min_idx,::-1]
    return tuple(idx)

def merge_contours(contours):
    cnt_total = np.array(contours[0]).reshape(len(contours[0]), 2)
    for i in range(len(contours)-1):
        cnt = np.array(contours[i+1]).reshape(len(contours[i+1]), 2)
        cnt_total = np.vstack((cnt_total,cnt))
    return cnt_total


#Set the dataset folder
folder="/home/amaranth/Desktop/Robot_UPAO/seedling_dataset_11_01_20/"

#GUI and mouse
cv2.namedWindow("depthimage")
cv2.setMouseCallback("depthimage", click_depth_rgb)

#Set the sample number
sample_num=45

#Open the sample
DB=seedb.seedling_dataset(folder)
sample=DB.read_sample(sample_num)
depth_orig=sample.depth
depth_rgb=sample.toprgb
hsv_img = cv2.cvtColor(depth_rgb,cv2.COLOR_BGR2HSV)

depth= np.zeros(depth_orig.shape)
depth[450:,380:1150] = depth_orig[450:,380:1150]

#colorized=colorize(depth)

#Segment rgb image using depth information
binarized_coords=zip(*np.where((depth<0.41)&(depth>0.28)))# pixels between 3cm and 33 cm
binarized_coords=list(binarized_coords)

invalid_coloured_coords=zip(*np.where((depth<0.28)&(hsv_img[:,:,0]<60)&(hsv_img[:,:,0]>22)))
invalid_coloured_coords=list(invalid_coloured_coords)

binarized_rgb=np.zeros(depth_rgb.shape,dtype=np.uint8)
mask=np.zeros(depth.shape,dtype=np.uint8)
invalid_pixels=[]

for coord in binarized_coords:
    #binarized_rgb[coord[0],coord[1]]= depth_rgb[coord[0],coord[1]]
    mask[coord[0],coord[1]]=255

contours,hier = cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
new_cont=[]

if process == True:

    for cnt in contours:
        if len(cnt)>100:
            new_cont.append(cnt)

    print(len(new_cont))
    merged_contour = merge_contours(new_cont)
    #nearest_pixel_contour([500,100],merged_contour)
    for px in invalid_coloured_coords:
        depth[px] = depth[nearest_pixel_contour(px,merged_contour)]

    binarized_coords=zip(*np.where((depth<0.41)&(depth>0.28)))# pixels between 3cm and 33 cm
    binarized_coords=list(binarized_coords)

    for coord in binarized_coords:
        binarized_rgb[coord[0],coord[1]]= depth_rgb[coord[0],coord[1]]
        #mask[coord[0],coord[1]]=255

    rgb_new= np.zeros(binarized_rgb.shape,dtype=np.uint8)
    rgb_new[450:,380:1150] = binarized_rgb[450:,380:1150]


    #Show the results
    #binarized_rgb=cv2.bitwise_or(depth_rgb,depth_rgb,mask=mask)
    cv2.imshow("original",depth_rgb)
    cv2.imshow("depthimage",rgb_new)
    #cv2.imshow("mask",mask)
    #cv2.imwrite("segmented_images/mask{}.jpg".format(sample_num),mask)
    #cv2.imwrite("segmented_images/seedlingimg{}.jpg".format(sample_num),depth_rgb)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    cv2.imshow("original", depth_rgb)
    cv2.imshow("depthimage", mask)
    # cv2.imshow("mask",mask)
    # cv2.imwrite("segmented_images/mask{}.jpg".format(sample_num),mask)
    # cv2.imwrite("segmented_images/seedlingimg{}.jpg".format(sample_num),depth_rgb)
    cv2.waitKey(0)
    cv2.destroyAllWindows()