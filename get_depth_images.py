import cv2
import pyrealsense2 as rs
import time
import numpy as np

#Create constants
distance=0.359

def colorize(depth_image):
    _min=distance-0.1
    _max=distance
    normalized=255.0*(depth_image-_min)/(_max-_min)
    normalized=np.clip(normalized,0,255).astype(np.uint8)
    colorized=cv2.applyColorMap(normalized,cv2.COLORMAP_JET)
    return colorized

#Start by setting-up the camera
pipeline=rs.pipeline()
config=rs.config()
config.enable_stream(rs.stream.depth,1280,720,rs.format.z16,30)
config.enable_stream(rs.stream.color,1280,720,rs.format.bgr8,30)

#Start streaming
pipeline_profile=pipeline.start(config)
depth_sensor=pipeline_profile.get_device().first_depth_sensor()
depth_sensor.set_option(rs.option.emitter_enabled,1)
depth_sensor.set_option(rs.option.laser_power,280)
depth_scale=depth_sensor.get_depth_scale()
time.sleep(1)


#Get intrinsics
intrinsics=pipeline_profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
print(intrinsics)

#Get frames
frames = pipeline.wait_for_frames()
depth_frame=frames.get_depth_frame()
color_frame=frames.get_color_frame()
depth_image=np.asanyarray(depth_frame.get_data())
dist_img=0.0010000000474974513*(depth_image.astype(np.float))
dist_img_cropped=np.zeros(dist_img.shape,dtype=np.float)
depth_image_crop=np.zeros(dist_img.shape,dtype=np.int)
depth_image_crop[32:707,245:1000]=depth_image[32:707,245:1000]
dist_img_cropped[32:707,245:1000]=dist_img[32:707,245:1000]
colorized=colorize(dist_img)
cv2.imshow("image",colorized)
cv2.waitKey(0)
cv2.destroyAllWindows()
print(intrinsics.width)
intrinsics.width=1780
print(depth_scale)
