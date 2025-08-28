# MERFISH Cropping
Full, high-resolution tissue images from MERFISH experiments can be many gb in size. Zooming in on specific areas of slides can be especially challenging, as Vizgen reports cell coordinates in µM rather than pixels. Furthermore, the conversion between microns and pixels in MERFISH data is not always straightforward, as the micron coordinate system may be offset from the 0,0 mark of the pixel coordinate system. To simplify analysis, this repo allows users to crop large images from the command line using the micron-based coordinate system.

<p align="center">
  <img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/Image.jpg" width="400" height="400" />
  <img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/CroppedImage.jpg" width="400" height="400" />
</p>

## Setup
##### The cropping script runs in python3, and requires the following minimum dependencies:
* numpy
* pandas
* pyvips
* Pillow
* 
##### To also work with segmentation polygons, these additional dependencies are required:
* geopandas
* matplotlib
* pyarrow

A minimal conda environment for cropping only can be setup with:
```
conda env create --name MERFISH_IMAGES --file=environment.yml
```
Or a complete conda environment that allows users to work with segmentation polygons in addition can be setup with:
```
conda env create --name MERFISH_IMAGES --file=environment_extended.yml
```
*Older machines may have trouble with the extended environment.*


## Cropping images
Two input files are required for image cropping, both are found within the 'images' folder of the processed MERFISH data
* The source image, e.g., 'mosaic_DAPI_z3.tif'
* The micron to pixel transformation matrix, 'micron_to_mosaic_pixel_transform.csv'

A minimal run example:
```
python crop_image.py \
	-c micron_to_mosaic_pixel_transform.csv \
	-i mosaic_DAPI_z3.tif \
	-l 1500 \ # minimum x coordinate value in microns, "left"
	-r 3500 \ # maximum x coordinate value in microns, "right"
	-b 10000 \ # minimum y coordinate value in microns, "bottom"
	-t 12000 \ # maximum y coordinate value in microns, "top"
	-o CroppedImageTest # output file prefix
```

#### Optional Arguments

Image transformations, all are FALSE by default and should only be relevant if the image has been previously modified in some way:
* -f: Boolean, whether or not to swap the x and y axes
* -x: Boolean, whether or not to mirror-flip the coordinates of the x axis
* -y: Boolean, whether or not to mirrorflip the coordinates of the y axis

Output options:
* -j: file extension of the output. Automatically set to 'jpg,' but other image formats can be set. jpg maintains image resolution and it is recommended not to mess with this setting.


## Increasing Processing Speed
While it is not necessary for the crop_image script to run, it will dramatically increase the cropping speed if the output mosaic files are converted into pyramidal images. A .tif can be converted to pyramidal format on commandline with vips:

```
vips tiffsave mosaic_DAPI_z3.tf mosaic_DAPI_z3_pyramidal.tif --tile --pyramid --compression jpeg --Q 100
```











