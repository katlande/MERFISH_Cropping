# Example Data
Given our example image below, we'd like to zoom in on the tip of the image. In our processed object, this area spans (1000,1800)µM on the x-axis and (1000,1800)µM on the y-axis.

pathtoimage

We run the following code:
```
python crop_image.py -c test/test_conversion_matrix.csv -i test/test.jpg -l 1000 -r 1800 -b 1000 -t 1800 -o test/crop
```

We recieve the following crop:

pathtoimage2
