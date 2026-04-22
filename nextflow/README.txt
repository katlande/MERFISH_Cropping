# run on cask as:
nextflow run main.nf --condaEnv /vast/igc/tools/miniconda3/envs/MFcropping

# workflow:
	> MoleculeDensity.py, then rank the area sizes by density and choose a high density area to plot boundaries for each area
	> crop_image.py for each area
	> overlay polygons with show_segmentation.py