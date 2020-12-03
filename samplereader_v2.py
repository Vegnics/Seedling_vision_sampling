from libseedlingdb import seedling_sample,seedling_dataset
from Sampling_app import Sample
from stream import colorize
import cv2
import pickle
import numpy as np


folder="/home/labinm_robotica/sampling_example/"
my_ds=seedling_dataset(folder)
print(my_ds.samplenum)
sample=my_ds.read_sample(0)
"""
with open(folder+"Sample{}.pkl".format(6),"rb") as file:
    Sample=pickle.load(file)
    print(folder+Sample.rgbtop)
    print(Sample.quality)
"""
print(sample.quality)
#depth_rgb=cv2.imread(folder+sample.sidergb,1)
#depth=np.load(folder+sample.depth)
#colorized=colorize(depth,resize=False)
#cv2.imshow("",colorized)
#cv2.imwrite("outdoorprobe.jpg",colorized)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
