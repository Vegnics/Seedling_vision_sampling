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
from skimage.measure import label

class hole_region():
    def __init__(self):
        self.points = None
        self.contour = None

def find_holes_regions(mask):
    contours, hier = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    labeled_img = label(mask)
    holes = []
    for lab in range(np.max(labeled_img)+1):
        hole = hole_region()
        for cnt in contours:
            if labeled_img[cnt[0][0][1],cnt[0][0][0]] == lab and len(cnt)>=4:
                contour_pnts=[]
                for pnt in cnt:
                    contour_pnts.append([pnt[0][1],pnt[0][0]])
                hole_pnts = zip(*np.where(labeled_img == lab))
                hole_pnts = list(hole_pnts)
                hole.contour = contour_pnts
                hole.points = hole_pnts
                holes.append(hole)
                break
    return holes

def find_valid_neighbor(depth,pnt):
    neighbors=[[False,0],[False,0],[False,0],[False,0]]
    if (pnt[0] - 1 >= 0):
        neighbors[0]=[True,depth[pnt[0]-1,pnt[1]]]
    if (pnt[0] + 1 < depth.shape[0]):
        neighbors[1]=[True,depth[pnt[0] + 1, pnt[1]]]
    if (pnt[1] + 1 < depth.shape[1]):
        neighbors[2] = [True,depth[pnt[0], pnt[1] + 1]]
    if (pnt[1] - 1 >= 0):
        neighbors[3] = [True,depth[pnt[0], pnt[1] - 1]]

    for neigh in neighbors:
        if neigh[0] is True:
            if neigh[1]>0.25 and neigh[1]<0.5:
                return True,neigh[1]
    return False,0



def fill_holes(depth,holes):
    new_depth=depth
    for hole in holes:
        #print(hole.points)
        #print(hole.contour)
        depth_neighbors=[]
        for pnt in hole.contour:
            ret,val = find_valid_neighbor(depth,pnt)
            if ret is True:
                depth_neighbors.append(val)
        if len(depth_neighbors)>0:
            mean_depth = np.mean(depth_neighbors)
        else:
            mean_depth = 0
        for coords in hole.points:
            print(mean_depth)
            new_depth[coords[0],coords[1]]=mean_depth
    return new_depth


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
        d_image = new_depth.astype(np.float)
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
sample_num=38

#Open the sample
DB=seedb.seedling_dataset(folder)
sample=DB.read_sample(sample_num)
depth_orig=sample.depth
depth_rgb=sample.toprgb
hsv_img = cv2.cvtColor(depth_rgb,cv2.COLOR_BGR2HSV)

depth= np.ones(depth_orig.shape)
depth[450:,380:1150] = depth_orig[450:,380:1150]

#colorized=colorize(depth)

#Segment rgb image using depth information
binarized_coords=zip(*np.where((depth<0.41)&(depth>0.28)))# pixels between 3cm and 33 cm
binarized_coords=list(binarized_coords)

invalid_coloured_coords=zip(*np.where((depth<0.28)&(hsv_img[:,:,0]<80)&(hsv_img[:,:,0]>22)&(hsv_img[:,:,1]>0)))
invalid_coloured_coords=list(invalid_coloured_coords)

binarized_rgb=np.zeros(depth_rgb.shape,dtype=np.uint8)
mask=np.zeros(depth.shape,dtype=np.uint8)
invalid_pixels=[]

for coord in invalid_coloured_coords:
    #binarized_rgb[coord[0],coord[1]]= depth_rgb[coord[0],coord[1]]
    mask[coord[0],coord[1]]=255

contours,hier = cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
holes = find_holes_regions(mask)
print(len(holes))
new_depth = fill_holes(depth,holes)

binarized_coords=zip(*np.where((new_depth<0.41)&(new_depth>0.28)))# pixels between 3cm and 33 cm
binarized_coords=list(binarized_coords)

for coord in binarized_coords:
    binarized_rgb[coord[0],coord[1]]= depth_rgb[coord[0],coord[1]]

contoured_img = cv2.drawContours(depth_rgb,contours,-1,[0,0,255],3)
cv2.imshow("original", depth_rgb)
cv2.imshow("depthimage", binarized_rgb)
#cv2.imshow("contours_show",contoured_img)
# cv2.imshow("mask",mask)
# cv2.imwrite("segmented_images/mask{}.jpg".format(sample_num),mask)
# cv2.imwrite("segmented_images/seedlingimg{}.jpg".format(sample_num),depth_rgb)
cv2.waitKey(0)
cv2.destroyAllWindows()