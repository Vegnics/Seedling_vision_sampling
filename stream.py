import cv2
import numpy as np
import usb.core as usbcore
import threading,time
import pyudev
import pyrealsense2 as rs
from PIL import Image,ImageTk
#RGB cameras max. resolution at 3264X2448 @ 15fps
#RGB allowed parameters  Brightness, Contrast, Saturation,Sharpness, Gamma, Gain, White balance, Hue,Backlight Contrast, Exposure
_canvas_size=(256,192)#width,height
_distance=0.4 #ground distance or max distance
_seedlingheight=0.15
_depthscale=9.999999747378752e-05
_cropregion=[(32,245),(707,1000)]
_RGBTOPPORT=3
_RGBSIDEPORT=4
_DEPTHPORT=1
_RGBid=[0x5a3,0x8830]
_DEPTHid=[0x8086,0xb07]
_BLANK = np.zeros((480, 640, 3), dtype=np.uint8)
_no_side_frame = cv2.putText(_BLANK, "SIDE CAMERA NOT FOUND", (50, 50), fontFace=cv2.FONT_HERSHEY_PLAIN,
                                     fontScale=1, color=(255, 0, 0), thickness=2)
_BLANK = np.zeros((480, 640, 3), dtype=np.uint8)
_no_top_frame= cv2.putText(_BLANK, "TOP CAMERA NOT FOUND", (50, 50), fontFace=cv2.FONT_HERSHEY_PLAIN,
                                      fontScale=1, color=(255, 0, 0), thickness=2)
_BLANK = np.zeros((480, 640, 3), dtype=np.uint8)
_no_depth_frame=cv2.putText(_BLANK, "DEPTH CAMERA NOT FOUND", (50, 50), fontFace=cv2.FONT_HERSHEY_PLAIN,
                                      fontScale=1, color=(255, 0, 0), thickness=2)

def colorize(depth_image,resize=True):
    d_image=_depthscale*(depth_image.astype(np.float))
    _min=_distance-_seedlingheight
    _max=_distance
    normalized=255.0*(d_image-_min)/(_max-_min)
    normalized=np.clip(normalized,0,255).astype(np.uint8)
    colorized=cv2.applyColorMap(normalized,cv2.COLORMAP_JET)
    if resize:
        colorized=cv2.resize(colorized,_canvas_size,interpolation=cv2.INTER_LINEAR)
    return colorized

class RepeatedTimer:
    def __init__(self, interval, function):
        self.function = function
        self.interval = interval
        self._timer=None
        self.keep=True
        self.start()
    def start(self):
        self.function()
        self._timer=threading.Timer(self.interval,self.start)
        self._timer.start()
    def cancel(self):
        self._timer.cancel()

class videostream:
    def __init__(self):
        self.devnums={"RGBtop":-1,"RGBside":-1,"Depth":-1}
        self.videonodes={"RGBtop":None,"RGBside":None,"Depth":None}
        self.thread=None
        self.interval=0.1
        self.rgbsideframe=_no_side_frame
        self.rgbtopframe=_no_top_frame
        self.depthimage=_no_depth_frame
        self.depthrgb=_no_depth_frame
        self.sidepresent=False
        self.toppresent=False
        self.depthpresent=False
        self.delay = 0.05 #0.2
        self.discardframes=5
        self.depthintrinsics=None
        self.cropdepth=False
        self.colorized=_no_depth_frame
        self.depth_initialized=False
        self.topinicialized=False
        self.sideinicialized=False
        self.canvas=None
        self.rgbtopcam=None
        self.rgbsidecam=None
        self.align=rs.align(rs.stream.color) #NEW
    def init_depth_cam(self):
        self.pipeline_profile = self.pipeline.start(self.config)
        self.depth_sensor = self.pipeline_profile.get_device().first_depth_sensor()
        self.depth_sensor.set_option(rs.option.emitter_enabled, 1)
        self.depth_sensor.set_option(rs.option.laser_power, 250)
        self.depth_sensor.set_option(rs.option.depth_units, 0.0001)
        self.temp_filter=rs.temporal_filter()
        self.temp_filter.set_option(rs.option.filter_smooth_alpha,0.8)
        self.temp_filter.set_option(rs.option.filter_smooth_delta,10)
        self.temp_filter.set_option(rs.option.holes_fill,4)
        self.spatial_filter=rs.spatial_filter()
        self.spatial_filter.set_option(rs.option.holes_fill,4)
        device = self.pipeline_profile.get_device()
        #print(device.sensors[0].get_info(rs.camera_info.physical_port))
    def restart_depth_cam(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        self.init_depth_cam()
        time.sleep(0.05)
        self.pipeline.stop()
        time.sleep(0.05)
        self.init_depth_cam()
        self.depth_initialized=True
    def init_rgb_top(self):
        self.rgbtopcam = cv2.VideoCapture(self.videonodes["RGBtop"])
        self.rgbtopcam .set(cv2.CAP_PROP_BRIGHTNESS, 0.2)
        self.rgbtopcam .set(cv2.CAP_PROP_CONTRAST, 0.3)
        self.rgbtopcam .set(cv2.CAP_PROP_FRAME_WIDTH, 3264)
        self.rgbtopcam .set(cv2.CAP_PROP_FRAME_HEIGHT, 2448)
        time.sleep(self.delay)
        self.topinicialized=True
    def init_rgb_side(self):
        self.rgbsidecam  = cv2.VideoCapture(self.videonodes["RGBside"])
        self.rgbsidecam .set(cv2.CAP_PROP_BRIGHTNESS, 0.2)
        self.rgbsidecam .set(cv2.CAP_PROP_CONTRAST, 0.3)
        self.rgbsidecam .set(cv2.CAP_PROP_FRAME_WIDTH, 3264)
        self.rgbsidecam .set(cv2.CAP_PROP_FRAME_HEIGHT, 2448)
        time.sleep(self.delay)
        self.sideinicialized = True
    def checkcams(self):
        self.devnums={"RGBtop":-1,"RGBside":-1,"Depth":-1}
        self.videonodes={"RGBtop":-1,"RGBside":-1,"Depth":-1}
        self.sidepresent=False
        self.toppresent=False
        self.depthpresent=False
        rgbdev=list(usbcore.find(find_all=True,idVendor=_RGBid[0],idProduct=_RGBid[1]))
        depthdev=list(usbcore.find(find_all=True,idVendor=_DEPTHid[0],idProduct=_DEPTHid[1]))
        for d in rgbdev:
            if d.port_number is _RGBTOPPORT:
                self.devnums["RGBtop"]=d.address
            elif d.port_number is _RGBSIDEPORT:
                self.devnums["RGBside"]=d.address
        for d in depthdev:
            if d.port_number is _DEPTHPORT:
                self.devnums["Depth"]=d.address
        c = pyudev.Context()
        for device in c.list_devices(subsystem='video4linux'):
            try:
                info=str(device).find("usb1")
                port=int(str(device)[info+7])
                node = int(str(device.device_node)[10:])
                if (node!=0 and (node%2==0) and (port ==_RGBTOPPORT) and (self.devnums["RGBtop"] !=-1)):
                    self.videonodes["RGBtop"]=node
                    self.toppresent=True
                elif (node!=0 and (node%2==0) and (port ==_RGBSIDEPORT) and (self.devnums["RGBside"] !=-1)):
                    self.videonodes["RGBside"] = node
                    self.sidepresent=True
            except:
                pass
        if(self.devnums["Depth"] is not -1):
            self.depthpresent=True
        else:
            self.depth_initialized=False

        if(self.devnums["RGBtop"]) is not -1:
            self.toppresent = True
        else:
            self.topinicialized = False

        if (self.devnums["RGBside"]) is not -1:
            self.sidepresent = True
        else:
            self.sideinicialized = False

    def get_frame(self):
        if self.topinicialized is False or self.sideinicialized is False or self.depth_initialized is False:
            self.checkcams()
        if self.videonodes["RGBtop"] is not -1:
            if self.topinicialized is False:
                self.init_rgb_top()
            try:
                for i in range(self.discardframes):
                    ret,frame=self.rgbtopcam.read()
                ret,frame=self.rgbtopcam.read()
                if(ret):
                    self.rgbtopframe=frame
                else:
                    print("TopCameraError")
                    self.rgbtopframe=_no_top_frame
                #cam.release()
            except:
                self.rgbtopframe = _no_top_frame
                self.topinicialized = False
                self.toppresent = False
                try:
                    self.rgbtopcam.release()
                    #cam.release()
                except:
                    pass
        else:
            self.rgbtopframe = _no_top_frame
            self.topinicialized = False
            self.toppresent = False
            try:
                self.rgbtopcam.release()
                # cam.release()
            except:
                pass

        if self.videonodes["RGBside"] is not -1:
            if self.sideinicialized is False:
                self.init_rgb_side()
            try:
                for i in range(self.discardframes):
                    ret,frame=self.rgbsidecam.read()
                ret, frame = self.rgbsidecam.read()
                if (ret):
                    self.rgbsideframe = frame
                else:
                    print("SideCameraError")
                    self.rgbsideframe = _no_side_frame
                #cam.release()
            except:
                self.rgbsideframe = _no_side_frame
                self.sideinicialized = False
                self.sidepresent = False
                try:
                    self.rgbsidecam.release()
                except:
                    pass
        else:
            self.rgbsideframe=_no_side_frame
            self.sideinicialized = False
            self.sidepresent = False
            try:
                self.rgbsidecam.release()
            except:
                pass

        if self.depthpresent is True:
            if self.depth_initialized is False:
                self.restart_depth_cam()
            try:
                self.intrinsics = self.pipeline_profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()
                frames = self.pipeline.wait_for_frames(timeout_ms=2000)
                aligned_frames = self.align.process(frames) #NEW
                for i in range(self.discardframes):
                    depth_frame = aligned_frames.get_depth_frame() #From frames.get_depth_frame()
                    depth_frame = self.spatial_filter.process(depth_frame)
                    depth_frame = self.temp_filter.process(depth_frame)
                #    color_frame = frames.get_color_frame()
                depth_frame = aligned_frames.get_depth_frame() #From frames.get_depth_frame()
                depth_frame = self.temp_filter.process(depth_frame)
                color_frame = aligned_frames.get_color_frame() #From frames.get_color_frame()
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image= np.asanyarray(color_frame.get_data())
                if self.cropdepth:
                    depth_image_crop = np.zeros(depth_image.shape, dtype=np.int)
                    depth_image_crop[_cropregion[0][0]:_cropregion[1][0],_cropregion[0][1]:_cropregion[1][1]] = depth_image[_cropregion[0][0]:_cropregion[1][0],_cropregion[0][1]:_cropregion[1][1]]
                    depth_image=depth_image_crop
                self.depthimage=depth_image
                self.colorized=colorize(depth_image)
                self.depthrgb=color_image
            except Exception as e:
                print(e)
                self.colorized=_no_depth_frame
                self.depthrgb=_no_depth_frame
                self.depth_initialized = False
        else:
            self.colorized = _no_depth_frame
            self.depthrgb = _no_depth_frame
            self.depth_initialized = False
    def start_streaming(self):
        self.thread=RepeatedTimer(self.interval,self.get_frame)
    def stop_streaming(self):
        self.thread.cancel()

if __name__=="__main__":
    mystream = videostream()
    mystream.start_streaming()

    while (True):
        k = cv2.waitKey(1)
        if k is not -1:
            break
    print("EXIT")
    mystream.stop_streaming()
    exit(0)
