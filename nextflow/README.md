# Basic run
nextflow run main.nf \
--inputPath /path/to/data \
--outputPath /path/to/output/folder \
--image /path/to/images/mosaic_DAPI_z3.tif \
--convFile /path/to/images/micron_to_mosaic_pixel_transform.csv \
--condaEnv /path/to/miniconda3/envs/MFcropping # optional -- path to premade conda env from yaml, may fail if not pre-run

* inputPath: dir containing: detected_transcripts.csv, cell_boundaries.parquet, cell_metadata.csv
* outputPath: dir for output files
* image: image to crop
* convFile: micron_to_mosaic_pixel_transform.csv for image
* condaEnv: path to MFcropping environment, if not specified loads from yaml

# Workflow steps:
* MoleculeDensity.py, then rank the area sizes by density and choose a high density area to plot boundaries for each area
* crop_image.py for one high density area
* overlay polygons with show_segmentation.py on selected area

# For IGC users:
* Run on Cask
* Set --condaEnv /vast/igc/tools/miniconda3/envs/MFcropping
