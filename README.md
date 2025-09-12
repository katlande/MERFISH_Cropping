# MERFISH Cropping
Full, high-resolution tissue images from MERFISH experiments can be many gb in size. Zooming in on specific areas of slides can be especially challenging, as Vizgen reports cell coordinates in µM rather than pixels. Furthermore, the conversion between microns and pixels in MERFISH data is not always straightforward, as the micron coordinate system may be offset from the 0,0 mark of the pixel coordinate system. To simplify analysis, this repo allows users to crop large images from the command line using the micron-based coordinate system.

## Setup
##### The cropping script runs in python3, and requires the following minimum dependencies:
* numpy
* pandas
* pyvips
* Pillow
##### To also work with segmentation polygons and molecules, these additional dependencies are required:
* geopandas
* matplotlib
* pyarrow

A minimal conda environment for cropping only can be setup with:
```
conda env create --name MERFISH_IMAGES --file=environment.yml
```
Or a complete conda environment that allows users to run all scripts can be setup with:
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

<p align="center">
  <img src="https://github.com/katlande/MERFISH_Cropping/blob/main/web_assets/example_main.jpeg" width="400" height="400" />
  <img src="https://github.com/katlande/MERFISH_Cropping/blob/main/web_assets/cropped_example.jpeg" width="400" height="400" />
</p>


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



# Adding Segmentation Polygons
Segmentation polygons can also be visualized using micron-space coordinates. Users can choose to either visualize the polygons alone, or to overlay them on top of a cropped image. Two input files are required for segmentation, both are found within 'output' folder of a MERFISH run:
* The segmentation information in parquet form (typically 'cell_boundaries.parquet')
* The cell metadata (typically 'cell_metadata.csv')
* *To overlay the segmentation on an image, the cropped image is also required as an input*

A minimal run example overlaying segmentation on a cropped DAPI image:
```
python show_segmentation.py \
	-i CroppedImageTest.jpg \ # using the cropped DAPI image generated above
	-d /path/to/output/folder \ # the merfish output folder containing cell metadata and segmentation files
	-l 1500 \ # xmin, same as CroppedImageTest.jpg
	-r 3500 \ # xmax, same as CroppedImageTest.jpg
	-t 12000 \ # ymax, same as CroppedImageTest.jpg
	-b 10000 \ # ymin, same as CroppedImageTest.jpg
	-y True \ # y-axis flip=TRUE; typically the segmentation and image files are mirror flipped along the y-axis
	-o SegImageTest.jpg # output file name
```

A minimal run example with no overlay:
```
python show_segmentation.py \
	-d /path/to/output/folder \ # the merfish output folder containing cell metadata and segmentation files
	-l 1500 \ # xmin
	-r 3500 \ # xmax
	-t 12000 \ # ymax
	-b 10000 \ # ymin
	-o SegImageTest.jpg # output file name
```


<p align="center">
  <img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/SegTest_noImg.jpg" width="400" height="400" />
  <img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/SegTest_withImg.jpg" width="400" height="400" />
</p>


#### Optional Arguments

Input options:
* -s: If the segmentation file is not called "cell_boundaries.parquet," pass its name with this argument
* -m: If the metadata file is not called "cell_metadata.csv," pass its name with this argument
* -k: Optional header-less .txt file containing a list of filtered cells, removes filtered polygons from the segmentation image

Image transformations, all are FALSE by default, but may be relevant if the image has been modified in some way. Often images are mirror-flipped relative to polygons, as in the example above, in which case a transformation argument would be necessary for overlaying:
* -a: Integer, angle at which to rotate the polygons
* -x: Boolean, whether or not to mirror-flip the coordinates of the x axis for the polygons only
* -y: Boolean, whether or not to mirrorflip the coordinates of the y axis for the polygons only

Output options:
* -q: image quality in dpi
* -c: line colour of segmentation polygons
* -f: fill colour of segmentation polygons (only in non-overlaid images)
* -w: linewidth of segmentation polygons



# Overlaying Transcripts
We can also overlay detected transcripts directly on top of microscopy or polygon images. Users have a choice to plot all transcripts (default), a single gene's transcripts, or the transcripts from a set of genes supplied as a plain text file.

Two input files are required for overlaying molecules:
* An image to overlay the molecules on (the output of show_segmentation.py or crop_image.py)
* The detected_transcripts.csv file found within 'output' folder of a MERFISH run


A minimal run example using one gene, on top of our polygon image (this would would work the same way with the DAPI image, as long as the image is properly transformed with '-y True').
```
python Add_Molecules.py \
	-i SegTest_noImg.jpg \ # our overlay background image
	-d detected_transcripts.csv \
	-m "Pdcd1" \ # our gene of interest
	-l 1500 \ # xmin, same as SegTest_noImg.jpg
	-r 3500 \ # xmax, same as SegTest_noImg.jpg
	-t 12000 \ # ymax, same as SegTest_noImg.jpg
	-b 10000 \ # ymin, same as SegTest_noImg.jpg
	-o TestMols.jpg \ # output file name
	--ptsize 2 \ # size of individual dots
	--ptalpha 1 \ alpha value for individual dots
```

To plot multiple genes, the -m option needs to be set to a headerless plain text file containing a new-line separated list of gene names:
```
python Add_Molecules.py \
	-i SegTest_noImg.jpg \ # our overlay background image
	-d detected_transcripts.csv \
	-m example_molecules.txt \ # example in test folder
	-l 1500 \ # xmin, same as SegTest_noImg.jpg
	-r 3500 \ # xmax, same as SegTest_noImg.jpg
	-t 12000 \ # ymax, same as SegTest_noImg.jpg
	-b 10000 \ # ymin, same as SegTest_noImg.jpg
	-o TestMols_file.jpg \ # output file name
	--ptsize 2 \ # size of individual dots
	--ptalpha 1 \ alpha value for individual dots
```


<p align="center">
  <img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/TestMols.jpg" height="300" />
  <img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/TestMols_file.jpg" height="300" />
</p>


#### Optional Arguments

Image transformations, all are FALSE by default, but may be relevant if the image has been modified in some way. Often microscopy images are mirror-flipped relative to data files, in which case a transformation argument would be necessary for overlaying:
* -a: Integer, angle at which to rotate the polygons
* -x: Boolean, whether or not to mirror-flip the coordinates of the x axis for the polygons only
* -y: Boolean, whether or not to mirrorflip the coordinates of the y axis for the polygons only

Output options:
* -q: Image quality in dpi
* --ptcol: Line colour of dots, only if plotting all transcripts or a single transcript
* --ptsize: Point size
* --ptalpha: Point alpha value (0-1)
* --allmolecules: Boolean, whether or include all detected molecules (True) or only molecules inside cells (False)



# Finding the Correct Orientation
* The microscopy images and data information (cell polygons, transcript locations), typically cannot be directly overlaid, and need to be transformed. 
⋅⋅⋅ * While this transformation may change between institutions or runs, I find that generally speaking, the data is flipped along the y-axis relative to microscopy images. Setting the -y option to True when overlaying polygons or molecules on top of microscopy images.⋅⋅
⋅⋅⋅ * Polygons and molecules will always be in the same orientation unless one file has been externally modified. When overlaying only polygons and molecules in absence of a microscopy image, either apply NO image transformation options, or apply the same image transformation options to generate images.⋅⋅
⋅⋅⋅ * When overlaying molecules on a DAPI image already overlaid with polygons, apply the same transformation was was used for show_segmentation.py⋅⋅

* Sanity checking: if you are unsure what transformations to apply, identify an area with a distinct shape (e.g., along a tissue edge), and play around with polygon overlays using various transformation options until you find one that matches perfectly. 

* The x & y coordinates in Seurat object metadata are the same as those used for image boundary l/r & b/t values. However, note that Seurat's ImageDimPlot() swaps the x & y coordinates for plotting. Hence, any "x" and "y" values supplied to the Crop() function will actually by the b/t and l/r limits, respectively.



# Common Errors:
* Supplying cropping boundaries outside the actual image limits will cause an error. This is especially noticible when slides are tightly packed. If cropping fails with strange errors, try shrinking the bounds of the image.





