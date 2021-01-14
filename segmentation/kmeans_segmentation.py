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
from sklearn.cluster import KMeans

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
        #print("X= {x}, Y={y}, Z={z}".format(x=100 * point[0], y=100 * point[1], z=100 * point[2]))
        print("X= {x}, Y={y}, Z={z}, H={h}, S={s}".format(x=y, y=x, z=point[2],h=cimage_hsv[y-pinit[0],x-pinit[1],0],s=cimage_hsv[y-pinit[0],x-pinit[1],1]))
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

#Segment rgb image using depth information
"""
binarized_coords=zip(*np.where((depth<0.41)&(depth>0.28)))# pixels between 3cm and 33 cm
binarized_coords=list(binarized_coords)

invalid_coords=zip(*np.where(depth<0.28))
invalid_coords=list(invalid_coords)

out_coords=zip(*np.where(depth>0.41))
out_coords=list(out_coords)

binarized_rgb=np.zeros(depth_rgb.shape,dtype=np.uint8)
mask=np.zeros(depth.shape,dtype=np.uint8)

for coord in binarized_coords:
    binarized_rgb[coord[0],coord[1]]= depth_rgb[coord[0],coord[1]]
    #mask[coord[0],coord[1]]=255

for coord in invalid_coords:
    binarized_rgb[coord[0],coord[1]]= [0,0,255]

for coord in out_coords:
    binarized_rgb[coord[0],coord[1]]= [255,0,0]
"""

pinit=[450,410]
#"""
#CREATING THE TRAINING MATRIX
cropped_rgb=depth_rgb[450:,410:1070]
cimage_hsv=cv2.cvtColor(cropped_rgb,cv2.COLOR_BGR2HSV)
print(cimage_hsv.shape)

X=[]
for i in range(cropped_rgb.shape[0]):
    for j in range(cropped_rgb.shape[1]):
        X.append([cimage_hsv[i,j,0],cimage_hsv[i,j,1],depth[i+pinit[0],j+pinit[1]]])

X=np.array(X)
print(X.shape)
np.save("cropped_data.npy",X)
#"""

#"""
#TRAINING THE MODEL
inits=np.array([[15,31,577-pinit[0],498-pinit[1],0.0],[13,46,533-pinit[0],535-pinit[1],0.574],[36,153,568-pinit[0],540-pinit[1],0.358],[53,43,578-pinit[0],758-pinit[1],0.3923],[38,119,571-pinit[0],953-pinit[1],0.3753]])
X=np.load("cropped_data.npy")
kmeans=KMeans(6,random_state=0).fit(X)
seg_img=np.resize(kmeans.labels_,(270,660,1))
#"""
"""
seg_img=np.resize(kmeans.labels_,(270,660,1))
image=np.zeros((270,660,3),dtype=np.uint8)
for i in X:
    region=kmeans.predict([i])
    if region[0]==0:
        image[int(i[2]),int(i[3]),:]=[30,40,15]
    elif region[0]==1:
        image[int(i[2]),int(i[3]),:]=[80,50,45]
    elif region[0]==2:
        image[int(i[2]),int(i[3]),:]=[10,140,150]
    elif region[0]==3:
        image[int(i[2]),int(i[3]),:]=[90,180,54]
    elif region[0]==4:
        image[int(i[2]),int(i[3]),:]=[63,87,190]
"""

#"""
B= np.where(seg_img==0,30,seg_img)
B= np.where(B==1,30,B)
B= np.where(B==2,100,B)
B= np.where(B==3,100,B)
B= np.where(B==4,150,B)
B= np.where(B==5,150,B)
print(B.shape)

R= np.where(seg_img==0,30,seg_img)
R= np.where(R==1,80,R)
R= np.where(R==2,100,R)
R= np.where(R==3,150,R)
R= np.where(R==4,200,R)
R= np.where(R==5,220,R)
print(R.shape)

G= np.where(seg_img==0,120,seg_img)
G= np.where(G==1,90,G)
G= np.where(G==2,60,G)
G= np.where(G==3,30,G)
G= np.where(G==4,0,G)
G= np.where(G==5,190,G)
print(G.shape)
#"""

image=cv2.merge((B,G,R))
image=image.astype(np.uint8)
print(image.dtype)


#Show the results
#binarized_rgb=cv2.bitwise_or(depth_rgb,depth_rgb,mask=mask)
cv2.imshow("original",depth_rgb)
cv2.imshow("depthimage",image)
#cv2.imshow("mask",mask)
#cv2.imwrite("segmented_images/mask{}.jpg".format(sample_num),mask)
#cv2.imwrite("segmented_images/seedlingimg{}.jpg".format(sample_num),depth_rgb)
cv2.waitKey(0)
cv2.destroyAllWindows()
