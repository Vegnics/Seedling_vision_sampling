from libseedlingdb import seedling_sample,seedling_dataset
from Sampling_app import Sample

my_ds=seedling_dataset("/home/labinm_robotica/sampling_example/")
print(my_ds.samplenum)
sample=my_ds.read_sample(0)
