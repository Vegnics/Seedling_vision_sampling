import pyrealsense2 as rs
import cv2
import numpy as np
from math import fabs
import time
_distance=0.40 #ground distance or max distance
_seedlingheight=0.15
_depthscale=9.999999747378752e-05

def colorize(depth_image):
    d_image=_depthscale*(depth_image.astype(np.float))
    _min=_distance-_seedlingheight
    _max=_distance
    normalized=255.0*(d_image-_min)/(_max-_min)
    normalized=np.clip(normalized,0,255).astype(np.uint8)
    colorized=cv2.applyColorMap(normalized,cv2.COLORMAP_JET)
    return colorized
def init_depth(pipeline,config):
    pipeline_profile = pipeline.start(config)
    depth_sensor = pipeline_profile.get_device().first_depth_sensor()
    depth_sensor.set_option(rs.option.emitter_enabled, 1)
    depth_sensor.set_option(rs.option.laser_power, 180)
    depth_sensor.set_option(rs.option.depth_units, 0.0001)
    device=pipeline_profile.get_device()
    print(device.sensors[0].get_info(rs.camera_info.physical_port))
def restart_depth():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    init_depth(pipeline,config)
    time.sleep(0.05)
    pipeline.stop()
    time.sleep(0.05)
    init_depth(pipeline,config)
    return pipeline

depth_error=False
pipeline=restart_depth()
while(1):
    try:
        if(depth_error):
            try:
                pipeline.stop()
            except:
                pass
            pipeline=restart_depth()
            depth_error=False
        print("good")
        frames = pipeline.wait_for_frames(timeout_ms=2000)
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image= np.asanyarray(color_frame.get_data())
        colorized=colorize(depth_image)
        colorized=cv2.resize(colorized,(-1,-1),fx=0.5,fy=0.5)
        cv2.imshow(" ", colorized)
        k = cv2.waitKey(1)
        if k is ord("q"):
            break
    except Exception as e:
        depth_error=True
