#For sample reading it's only necessary to use the libseedlingdb library

from libseedlingdb import Sample,seedling_sample,seedling_dataset

folder="/home/amaranth/Desktop/Robot_UPAO/seedling_dataset_11_01_20/" #put the dataset folder here
sample_number = 0

my_ds=seedling_dataset(folder)
print(my_ds.samplenum) # Print the number of samples inside de dataset
sample=my_ds.read_sample(sample_number) # read the a sample.
rgb_image = sample.toprgb # read the RGB image of the sample.
quality = sample.quality #read the seedlings' quality present in the image.
print(sample.quality)

