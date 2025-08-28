# show segmentation in a region:
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import geopandas as gpd
from shapely import wkb
import warnings
from shapely.affinity import scale, rotate
from PIL import Image
import argparse
import sys
warnings.simplefilter('ignore', Image.DecompressionBombWarning)
Image.MAX_IMAGE_PIXELS = 5_000_000_000 # set max image size

def main(argv):
    parser = argparse.ArgumentParser(description="Plotting segmentation polygons in a region, optionally overlaying them on top of a cropped image.")
    # Main inputs
    parser.add_argument("-i", "--img", required=False, default='', help="Path to image")
    parser.add_argument("-d", "--dir", required=False, default='', help="MERFISH directory (directory containing cell meta data and parquet files)")
    parser.add_argument("-s", "--seg", required=False, default='cell_boundaries.parquet', help="segmentation file name (default: cell_boundaries.parquet)")
    parser.add_argument("-m", "--meta", required=False, default='cell_metadata.csv', help="cell metadata file name (default: cell_metadata.csv)")
    
    # Cropping boundaries
    parser.add_argument("-l", "--left", type=int, help="xmin in microns, left boundary for cropping")
    parser.add_argument("-r", "--right", type=int, help="xmax in microns, right boundary for cropping")
    parser.add_argument("-b", "--bottom", type=int, help="ymin in microns, bottom boundary for cropping")
    parser.add_argument("-t", "--top", type=int, help="ymax in microns, top boundary for cropping")
    # Transformations
    parser.add_argument("-a", "--angle", type=int, default=0, help="Rotation angle of the polygon image (default: 0)")
    parser.add_argument("-x", "--revx", type=bool, default=False, help="Transform the x axis of the polygon image (default: False)")
    parser.add_argument("-y", "--revy", type=bool, default=False, help="Transform the y axis of the polygon image (default: False)")
    parser.add_argument("-k", "--keepcells", default='', help="Optional headerless text file containing a list of cells to retain in the image. Can contain cells outside of cropping boundaries without affecting the image.")
    # Output settings
    parser.add_argument("-o", "--output", default="SegImage.jpg", help="Output file name (default: SegImage.jpg)")
    parser.add_argument("-q", "--quality_dpi", type=int, default=1000, help="Output file name dpi (default: 1000)")
    parser.add_argument("-c", "--col", default='', help="Polygon outline colour (default: blue if plotted without an image, cyan if overlaid)")
    parser.add_argument("-f", "--fill", default='', help="Polygon fill colour (default: lightblue if plotted without an image; always NULL if overlaid)")
    parser.add_argument("-w", "--lw", type=float, default=0.1, help="Linewidth of polygons (default: 0.1)")
    
    args = parser.parse_args()
    mfpath=args.dir
    overlay_image=args.img
    parq=args.seg
    met=args.meta
    xmin=args.left
    xmax=args.right
    ymin=args.bottom
    ymax=args.top
    rotation=args.angle
    reverse_x=args.revx
    reverse_y=args.revy
    cells_keep=args.keepcells
    outputfile=args.output
    outputdpi=args.quality_dpi
    polygon_color=args.col
    polygon_lw=args.lw
    face_col=args.fill
    
    print("Loading polygons...")
    df_boundaries = pd.read_parquet(mfpath+'/'+parq)
    df_metadata = pd.read_csv(mfpath+'/'+met)
    merged_df = pd.merge(df_boundaries, df_metadata, on='EntityID', how='inner') # merge
    # filter df by area:
    merged_df = merged_df[merged_df['center_x'] > xmin]
    merged_df = merged_df[merged_df['center_x'] < xmax]
    merged_df = merged_df[merged_df['center_y'] > ymin]
    merged_df = merged_df[merged_df['center_y'] < ymax]
    
    # if included, a filtered cell list can be added to remove garbage cells:
    if not cells_keep == '':
        prev = len(merged_df)
        df_cells = pd.read_table(cells_keep, header=None)
        merged_df = merged_df[merged_df['EntityID'].isin(df_cells[0])]
        print("Filtered out", (prev-len(merged_df)), "cells of", prev)
    
    merged_df["Geometry"] = merged_df["Geometry"].apply(wkb.loads) # get segmentation polygons for plotting
    gdf = gpd.GeoDataFrame(merged_df, geometry="Geometry")
    sx = -1 if reverse_x else 1 # reverse x axis if true
    sy = -1 if reverse_y else 1 # reverse y axis if true
    xmid = (xmin + xmax) / 2
    ymid = (ymin + ymax) / 2
    gdf["Geometry"] = gdf["Geometry"].apply(lambda geom: scale(geom, xfact=sx, yfact=sy, origin=(xmid, ymid)))

    # rotate if non-zero angle is supplied:
    if rotation != 0:
        gdf["Geometry"] = gdf["Geometry"].apply(lambda geom: rotate(geom, angle=rotation, origin=(xmid, ymid)))
    
    # add an overlay image behind the plot if one is provided:
    fig, ax = plt.subplots() # subplot
    if not overlay_image == '':
        face_col="none"
        print("Overlaying segmentation onto image...")
        overlay = mpimg.imread(overlay_image)
        ax.imshow(overlay, extent=[xmin, xmax, ymin, ymax])
        if polygon_color == '':
            polygon_color="cyan"
    else:
        if polygon_color == '':
            polygon_color="blue"
        if face_col == '':
            face_col="lightblue"
    
    print("Creating final plot...")
    gdf.plot(ax=ax, edgecolor=polygon_color, facecolor=face_col, lw=polygon_lw)
    ax.set_axis_off()
    
    print("Saving output image...")
    plt.savefig(outputfile, dpi=outputdpi, bbox_inches="tight", pad_inches=0)
    
if __name__ == "__main__":
   main(sys.argv[1:])

