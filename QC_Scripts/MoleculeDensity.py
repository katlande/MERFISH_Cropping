#!/usr/bin/env python
import pandas as pd
import numpy as np
import os
import argparse
import sys
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors

def main(argv):
    parser = argparse.ArgumentParser(description="Check the transcript denisty around a slice.")
    
    # Input
    parser.add_argument("-d", "--transcripts", required=False, default='detected_transcripts.csv', help="transcript csv name (default: detected_transcripts.csv)")
    parser.add_argument("-l", "--len", type=int, required=False, default=100, help="sample area size in uM (length of one side of the square). Smaller length = larger number of sample bins; default = 100uM")
    
    args = parser.parse_args()
    mols = args.transcripts
    binsize = args.len
    
    print("Loading molecules...")
    df_mols = pd.read_csv(mols)
    # remove blanks:
    df_mols = df_mols[~df_mols['gene'].str.contains('Blank-', case=False, na=False)]
    # filter df by area:
    df_mols["global_x"] = pd.to_numeric(df_mols["global_x"], errors="coerce")
    df_mols["global_y"] = pd.to_numeric(df_mols["global_y"], errors="coerce")
    # total area of sample:
    xmin = df_mols['global_x'].min()
    xmax = df_mols['global_x'].max()
    ymin = df_mols['global_y'].min()
    ymax = df_mols['global_y'].max()
    
    print("Creating sample grid...")
    # get x indices
    rngx = list(range(math.floor(xmin), math.ceil(xmax)))
    ranges_x = [rngx[i:i + binsize] for i in range(0, len(rngx), binsize)]
    xmin_coords=[min(col) for col in ranges_x]
    xmax_coords=[max(col) for col in ranges_x]
    #get y indicies
    rngy = list(range(math.floor(ymin), math.ceil(ymax)))
    ranges_y = [rngy[i:i + binsize] for i in range(0, len(rngy), binsize)]
    ymin_coords=[min(col) for col in ranges_y]
    ymax_coords=[max(col) for col in ranges_y]
    
    # make a df of all squares and get total area:
    for i in range(len(ymin_coords)):
        indices = {
            'xmin': xmin_coords,
            'xmax': xmax_coords,
            'ymin': [ymin_coords[i]]*len(xmin_coords),
            'ymax': [ymax_coords[i]]*len(xmin_coords)
        }
        
        if i == 0:
            indices_df = pd.DataFrame(indices)
        else:
            indices_df = pd.concat([indices_df, pd.DataFrame(indices)], ignore_index=True)
    
    indices_df.insert(4, 'Area_uM', abs((indices_df['xmax']-indices_df['xmin'])*(indices_df['ymin']-indices_df['ymax'])))
    
    print("Calculating grid densities...")
    x_edges = np.unique(np.r_[indices_df["xmin"].values, indices_df["xmax"].values])
    y_edges = np.unique(np.r_[indices_df["ymin"].values, indices_df["ymax"].values])
    
    # Assign each molecule to a bin
    x_bin = np.digitize(df_mols["global_x"].values, x_edges) - 1
    y_bin = np.digitize(df_mols["global_y"].values, y_edges) - 1
    # Count molecules per (x_bin, y_bin)
    counts = (
        pd.DataFrame({"x_bin": x_bin, "y_bin": y_bin})
        .groupby(["x_bin", "y_bin"])
        .size()
        .reset_index(name="count")
    )
    
    # Map indices_df rows to their bins
    indices_df = indices_df.reset_index().rename(columns={"index": "cell_id"})
    indices_df["x_bin"] = np.searchsorted(x_edges, indices_df["xmin"].values, side="left")
    indices_df["y_bin"] = np.searchsorted(y_edges, indices_df["ymin"].values, side="left")
    # Merge counts
    indices_with_counts = indices_df.merge(counts, on=["x_bin", "y_bin"], how="left").fillna(0)
    indices_with_counts.insert(9, 'MolsPerMicron', (indices_with_counts['count']/indices_with_counts['Area_uM']))
    
    print("Saving output file...")
    indices_with_counts.to_csv('MoleculeDensity.csv', index=False)
    
    print("Making QC figures...")
    # heatmap of transcript density:
    fig, ax = plt.subplots(figsize=(8, 8))
    cmap = plt.cm.coolwarm  
    norm = mcolors.Normalize(vmin=indices_with_counts["MolsPerMicron"].min(), vmax=indices_with_counts["MolsPerMicron"].max())
    
    for _, row in indices_with_counts.iterrows():
        rect = patches.Rectangle(
            (row["xmin"], row["ymin"]),
            row["xmax"] - row["xmin"],
            row["ymax"] - row["ymin"],
            linewidth=0.5,
            edgecolor="black",
            facecolor=cmap(norm(row["MolsPerMicron"]))
        )
        ax.add_patch(rect)
    
    ax.set_xlim(indices_with_counts["xmin"].min(), indices_with_counts["xmax"].max())
    ax.set_ylim(indices_with_counts["ymin"].min(), indices_with_counts["ymax"].max())
    ax.set_aspect("equal")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Molecules/uM^2")
    plt.savefig("MoleculeDensityHeatmap.jpg", dpi=200, bbox_inches="tight", pad_inches=0)
    
    # histogram
    if int(len(indices_with_counts)/100) > 20:
        bs = int(len(indices_with_counts)/200)
    else:
        bs = 20
    counts, edges = np.histogram(indices_with_counts["MolsPerMicron"], bins=bs)
    density = counts / bs
    centers = (edges[:-1] + edges[1:]) / 2
    plt.figure(figsize=(4,4))
    plt.plot(centers, density, lw=1.5)
    plt.xlabel("Molecules/µM^2")
    plt.yscale('log') 
    plt.savefig("MoleculeDensityHistogram.jpg", dpi=100, bbox_inches="tight", pad_inches=0)
    
if __name__ == "__main__":
   main(sys.argv[1:])

