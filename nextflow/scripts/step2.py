#!/usr/bin/env python
# imports:
import sys, getopt
import pandas as pd
from PIL import Image
import pyvips
import warnings
import argparse
warnings.simplefilter('ignore', Image.DecompressionBombWarning)

# python scripts/step2.py  --image ${image} --con ${convFile} --output ${outputPath}

# set max image size:
Image.MAX_IMAGE_PIXELS = 5_000_000_000 

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

# script:
def main(argv):
    parser = argparse.ArgumentParser(description="Crop MERFISH images using micron coordinates and a conversion file.")
    
    # Required inputs
    parser.add_argument("-c", "--con", required=True, help="Path to micron_to_mosaic_pixel_transform.csv")
    parser.add_argument("-i", "--image", required=True, help="Path to image")
    
    # Transformations
    parser.add_argument("-f", "--flip_axes", type=bool, default=False, help="Flip the x & y axes (default: False)")
    parser.add_argument("-x", "--revx", type=bool, default=False, help="Transform the x axis (default: False)")
    parser.add_argument("-y", "--revy", type=bool, default=False, help="Transform the y axis (default: False)")
    
    # Output settings
    parser.add_argument("-o", "--output", required=True, help="Output path")
    parser.add_argument("-j", "--filetype", default="jpg", help="Output file extension (default: jpg)")
    args = parser.parse_args()
    
    # access everything as attributes:
    conv=args.con
    image=args.image
    coord_flip=args.flip_axes
    reverse_x=args.revx
    reverse_y=args.revy
    outputname=args.output
    outputfiletype=args.filetype
   # sys.exit()
    
    # read in micron_to_mosaic_pixel_transform.csv and perform the aff transformation:
    df = pd.read_table(conv, sep=" ", header=None, index_col=False)
    # Read in areas by size:
    mols = pd.read_csv(outputname+"/MoleculeDensity.csv")
    mols = mols.sort_values(by='MolsPerMicron', ascending=False)
    rowChoose=int(len(mols)*0.1) # use a region at the ~90th percentile for transcript density
    
    # get x/y coordinates of sample area:
    xmin = mols.iloc[rowChoose]['xmin']
    xmax = mols.iloc[rowChoose]['xmax']
    ymin = mols.iloc[rowChoose]['ymin']
    ymax = mols.iloc[rowChoose]['ymax']
    
    # user inputs are strings, convert them to booleans:
    if not isinstance(coord_flip, bool):
        coord_flip=str2bool(coord_flip)
    if not isinstance(reverse_x, bool):
        reverse_x=str2bool(reverse_x)
    if not isinstance(reverse_y, bool):
        reverse_y=str2bool(reverse_y)
    
    # get the total sizes of the input image in px:
    with Image.open(image) as completeimage:
        totalwidth, totalheight = completeimage.size
    
    # convert x and y coordinates from uM to px, swapping x and y if designated by user:
    if coord_flip == True:
        print("Swapping axes...")
        newYmin = (df.at[0,0]*xmin) + (df.at[0,2])
        newXmin = (df.at[1,1]*ymin) + (df.at[1,2])
        newYmax = (df.at[0,0]*xmax) + (df.at[0,2])
        newXmax = (df.at[1,1]*ymax) + (df.at[1,2])
        if newXmax > totalwidth or newYmax > totalheight: # safeguard against erroneous axis flipping
            print("Axes swap caused an input value to exceed the image size! Swapping back...")
            newXmin = (df.at[0,0]*xmin) + (df.at[0,2])
            newYmin = (df.at[1,1]*ymin) + (df.at[1,2])
            newXmax = (df.at[0,0]*xmax) + (df.at[0,2])
            newYmax = (df.at[1,1]*ymax) + (df.at[1,2])
            
    else:
        newXmin = (df.at[0,0]*xmin) + (df.at[0,2])
        newYmin = (df.at[1,1]*ymin) + (df.at[1,2])
        newXmax = (df.at[0,0]*xmax) + (df.at[0,2])
        newYmax = (df.at[1,1]*ymax) + (df.at[1,2])
        if newXmax > totalwidth or newYmax > totalheight: # auto-flips axes where appropraite
            print("At least one input value exceeds the image size! Swapping axes...")
            newYmin = (df.at[0,0]*xmin) + (df.at[0,2])
            newXmin = (df.at[1,1]*ymin) + (df.at[1,2])
            newYmax = (df.at[0,0]*xmax) + (df.at[0,2])
            newXmax = (df.at[1,1]*ymax) + (df.at[1,2])
    
    # impossible coordinates error:
    if newXmax > totalwidth or newYmax > totalheight:
        print("At least one input value exceeds the image size! Ensure input values are all within image bounds and that the correct image is being used.")
        sys.exit()
    
    # reverse x-axis values if reverse_x is true:
    if reverse_x == True:
        print("Reversing x axis...")
        tmp_xmax = totalwidth-newXmin
        tmp_xmin = totalwidth-newXmax
        newXmin = tmp_xmin
        newXmax = tmp_xmax
    
    # reverse y-axis values if reverse_x is true:
    if reverse_y == True:
        print("Reversing y axis...")
        tmp_ymax = totalheight-newYmin
        tmp_ymin = totalheight-newYmax
        newYmin = tmp_ymin
        newYmax = tmp_ymax
    
    print("Final x-coordinates in pixels:", int(newXmin), "/", int(newXmax))
    print("Final y-coordinates in pixels:", int(newYmin), "/", int(newYmax))
    # crop the image using newYmin, newYmax, newXmin, newXmax
    finaloutputname=outputname+"/MERFISH_QC/CroppedImage."+outputfiletype # Set final file name
    image = pyvips.Image.new_from_file(image) # Load image
    cropped_image = image.crop(newXmin, newYmin, (newXmax-newXmin), (newYmax-newYmin)) # Crop image
    print("Writing output image to:", finaloutputname)
    cropped_image.write_to_file(finaloutputname) # Save the output image
    
if __name__ == "__main__":
   main(sys.argv[1:])