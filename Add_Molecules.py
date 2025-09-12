#!/usr/bin/env python
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
import geopandas as gpd
import warnings
import numpy as np
import os
from PIL import Image
import argparse
import sys
warnings.simplefilter('ignore', Image.DecompressionBombWarning)
Image.MAX_IMAGE_PIXELS = 5_000_000_000_000 # set max image size

def transform_points(df, xmin, xmax, ymin, ymax, reverse_x=False, reverse_y=False, rotation=0):
    # Apply flips and rotation to coordinates in df (global_x, global_y):
    df = df.copy()
    # x and y center:
    xmid = (xmin+xmax)/2
    ymid = (ymin+ymax)/2
    #reverse x/y if TRUE:
    if reverse_x:
        df["global_x"] = 2*xmid - df["global_x"]
    if reverse_y:
        df["global_y"] = 2*ymid - df["global_y"]
    # Counterclockwise rotation if rotation is supplied:
    if rotation != 0:
        theta = np.radians(rotation)
        cos_t, sin_t = np.cos(theta), np.sin(theta)
        # Translate to origin, rotate, translate back
        x = df["global_x"] - xmid
        y = df["global_y"] - ymid
        df["global_x"] = x * cos_t - y * sin_t + xmid
        df["global_y"] = x * sin_t + y * cos_t + ymid
    return df

def main(argv):
    parser = argparse.ArgumentParser(description="Plotting segmentation polygons in a region, optionally overlaying them on top of a cropped image.")
    # Main inputs
    parser.add_argument("-i", "--img", required=False, default='', help="Path to image")
    parser.add_argument("-d", "--transcripts", required=False, default='detected_transcripts.csv', help="transcript csv name (default: detected_transcripts.csv)")
    parser.add_argument("-m", "--mol", required=False, default='all', help="Which transcripts to plot? Either 'all', a single gene name mathcing the 'gene' column of detected_transcripts.csv, or a path to a headerless, newline-delimited text file containing multiple transcript names (default: 'all')")
    
    # Cropping boundaries
    parser.add_argument("-l", "--left", type=int, help="xmin in microns, left boundary for cropping")
    parser.add_argument("-r", "--right", type=int, help="xmax in microns, right boundary for cropping")
    parser.add_argument("-b", "--bottom", type=int, help="ymin in microns, bottom boundary for cropping")
    parser.add_argument("-t", "--top", type=int, help="ymax in microns, top boundary for cropping")
    # Transformations
    parser.add_argument("-a", "--angle", type=int, default=0, help="Rotation angle of the polygon image (default: 0)")
    parser.add_argument("-x", "--revx", type=bool, default=False, help="Transform the x axis of the polygon image (default: False)")
    parser.add_argument("-y", "--revy", type=bool, default=False, help="Transform the y axis of the polygon image (default: False)")
    parser.add_argument("-o", "--output", default="MolImage.jpg", help="Output file name (default: MolImage.jpg)")
    parser.add_argument("-q", "--quality_dpi", type=int, default=1000, help="Output file name dpi (default: 1000)")
    parser.add_argument("--ptcol", default='red', help="Transcript color, if plotting all transcripts or a single transcript")
    parser.add_argument("--ptsize", default=1, type=float, help="Transcript point size")
    parser.add_argument("--ptalpha", default=0.5, type=float, help="Transcript alpha value")
    parser.add_argument("--allmolecules", type=bool, default=True, help="Whether to include all detected molecules (True) or only molecules inside cells (False); (default: True)")
    
    args = parser.parse_args()
    overlay_image=args.img
    mols=args.transcripts
    mol_file=args.mol
    xmin=args.left
    xmax=args.right
    ymin=args.bottom
    ymax=args.top
    rotation=args.angle
    reverse_x=args.revx
    reverse_y=args.revy
    outputfile=args.output
    outputdpi=args.quality_dpi
    pt_color=args.ptcol
    pt_size=args.ptsize
    pt_alpha=args.ptalpha
    allmols=args.allmolecules
    
    print("Loading molecules...")
    df_mols = pd.read_csv(mols)
    # filter df by area:
    df_mols["global_x"] = pd.to_numeric(df_mols["global_x"], errors="coerce")
    df_mols["global_y"] = pd.to_numeric(df_mols["global_y"], errors="coerce")
    df_mols = df_mols[df_mols['global_x'] > xmin]
    df_mols = df_mols[df_mols['global_x'] < xmax]
    df_mols = df_mols[df_mols['global_y'] > ymin]
    df_mols = df_mols[df_mols['global_y'] < ymax]
    #print(df_mols.head())
    
    # filter transcripts if not using all of them:
    if not mol_file == 'all':
        if os.path.exists(mol_file): # if it is a file, read in file:
            transcripts = pd.read_table(mol_file, header=None)
            df_mols = df_mols[df_mols['gene'].isin(transcripts[0])]
            single_colour = False
        else:
            df_mols = df_mols[df_mols['gene'] == mol_file]
            single_colour = True
    else:
        single_colour = True
    
    if allmols == False:
        df_mols = df_mols[df_mols['cell_id'] != -1]
    
    # apply any transformations:
    df_mols = transform_points(df_mols, xmin, xmax, ymin, ymax, reverse_x=reverse_x, reverse_y=reverse_y, rotation=rotation)
    
    # add an overlay image behind the plot
    print("Overlaying segmentation onto image...")
    fig, ax = plt.subplots() # subplot
    overlay = mpimg.imread(overlay_image)
    ax.imshow(overlay, extent=[xmin, xmax, ymin, ymax])
    if single_colour == True:
        ax.scatter(df_mols["global_x"], df_mols["global_y"], s=pt_size, color=pt_color, alpha=pt_alpha)
    else:
        codes, uniques = pd.factorize(df_mols['gene'].astype(str)) # genes to factor
        n = len(uniques)
        cmap = mpl.colormaps['Dark2'] if n <= 8 else mpl.colormaps['hsv']
        colors = cmap(codes / (n - 1) if n > 1 else 0.0) # convert codes to RGBA colors
        ax.scatter(df_mols["global_x"], df_mols["global_y"], s=pt_size, c=colors, alpha=pt_alpha)
        # optional legend
        handles = [mpatches.Patch(color=cmap(i / (n-1) if n>1 else 0.0), label=g) for i, g in enumerate(uniques)]
        ax.legend(handles=handles, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    ax.set_axis_off()
    
    print("Saving output image...")
    plt.savefig(outputfile, dpi=outputdpi, bbox_inches="tight", pad_inches=0)
    
if __name__ == "__main__":
   main(sys.argv[1:])