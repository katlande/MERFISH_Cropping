# Example Data

## Image Cropping
Given our example image below, we'd like to zoom in on the tip of the image. In our processed object, this area spans (1000,1800)µM on the x-axis and (1000,1800)µM on the y-axis.

<img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/Image.jpg" alt="Main Image" width="400" height="400">

We run the following code:
```
python crop_image.py -c test/test_conversion_matrix.csv -i test/Image.jpg -l 1000 -r 1800 -b 1000 -t 1800 -o test/CroppedImage
```

We recieve the following crop:

<img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/CroppedImage.jpg" alt="Main Image" width="400" height="400">


## Segmentation Polygons
Image.jpg comes from a larger DAPI image, cropped with the coordinates: x(1500,3500), y(10000,12000). We can plot the segmentation at this region using our example parquet. 
```
python show_segmentation.py -d test -l 1500 -r 3500 -t 12000 -b 10000 -o test/SegTest_noImg.jpg -s example.parquet -m example_metadata.csv
```
We recieve the following polygons:

<img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/SegTest_noImg.jpg" alt="Main Image" width="400" height="400">


We can also overlay the segmentation on top of Image.jpg. Because the segmentation is flipped vertically with respect to the DAPI image, we have to include a y-axis transformation argument to get the overlay to line up properly:
```
python show_segmentation.py -d test -l 1500 -r 3500 -t 12000 -b 10000 -o test/SegTest_withImg.jpg -s example.parquet -m example_metadata.csv -i test/Image.jpg -y True
```
We recieve the following overlay:

<img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/SegTest_withImg.jpg" alt="Main Image" width="400" height="400">

