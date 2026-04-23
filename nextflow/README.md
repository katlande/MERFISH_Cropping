Simple nextflow pipeline to automate MERFISH QC for one sample,

# Outputs:
### (1) Probe Density Information
* MoleculeDensityHeatmap.jpg - mean probes/uM across tissue image in rasters
<img src="https://github.com/katlande/MERFISH_Cropping/blob/main/web_assets/MoleculeDensityHeatmap.jpg" alt="Main Image" width="300" height="300">

* MoleculeDensityHistogram.jpg - density plot of mean probes/uM in all rasters in image
<img src="https://github.com/katlande/MERFISH_Cropping/blob/main/web_assets/MoleculeDensityHistogram.jpg" alt="Main Image" width="300" height="300">

* MoleculeDensity.csv - molecule density information in plaintext

### (2) Example Tissue Image
* CroppedImage.jpg - a quadrant from a good quality area estimated by probe density to QC tissue makeup. 
<img src="https://github.com/katlande/MERFISH_Cropping/blob/main/web_assets/CroppedImage.jpg" alt="Main Image" width="400" height="400">

### (3) Segmentation Overlay
* PolygonOverlay.jpg - CroppedImage.jpg overlaid with segmentation polygons to QC segmentation accuracy. 
<img src="https://github.com/katlande/MERFISH_Cropping/blob/main/web_assets/PolygonOverlay.jpg" alt="Main Image" width="400" height="400">

# Basic run
nextflow run main.nf \
--inputPath /path/to/data \
--outputPath /path/to/output/folder \
--image /path/to/images/mosaic_DAPI_z3.tif \
--convFile /path/to/images/micron_to_mosaic_pixel_transform.csv \
--condaEnv /path/to/miniconda3/envs/MFcropping \
--areaSize 500

* inputPath: dir containing: detected_transcripts.csv, cell_boundaries.parquet, cell_metadata.csv
* outputPath: dir for output files
* image: image to crop
* convFile: micron_to_mosaic_pixel_transform.csv for image
* condaEnv: path to MFcropping environment, if not specified loads from yaml
* areaSize: diameter of cropped area in uM, default=500

# Workflow steps:
* MoleculeDensity.py, then rank the area sizes by density and choose a high density area to plot boundaries for each area
* crop_image.py for one high density area
* overlay polygons with show_segmentation.py on selected area

# For IGC users:
* Run on Cask
* Set --condaEnv /vast/igc/tools/miniconda3/envs/MFcropping
