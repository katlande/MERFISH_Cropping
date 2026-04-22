#!/usr/bin/env nextflow
nextflow.enable.dsl=2


/*
 * --------------------
 * User parameters
 * --------------------
 */
params.inputPath  = "./"
params.outputPath = "./"
params.image      = ""
params.convFile   = ""
params.areaSize   = 500


/*
* 3 Python scrips in steps:
* Step 1: Find the probe density across a MERFISH image, saves the data in small area sizes, and queries the most dense areas using a user-defined raster size
* Step 2: Pull the top areas by probe density and return them as cropped images.
* Step 3: Overlay the cropped images with segmentation polygons and return them as images.
*/

/*
 * --------------------
 * Processes
 * --------------------
 */

/*
 * Bash process that creates the output folder
 */
process Setup {
	script:
	"""
	mkdir -p ${params.outputPath}/MERFISH_QC
	"""
}


process PythonDensity {
	conda params.condaEnv
	publishDir "${params.outputPath}", mode: 'copy'
	
	output:
	path "MERFISH_QC/MoleculeDensityHistogram.jpg", emit: img1
	path "MERFISH_QC/MoleculeDensityHeatmap.jpg",   emit: img2
	path "MERFISH_QC/MoleculeDensity.csv",          emit: crop
	
	
	script:
	"""
	mkdir -p MERFISH_QC
	python ${projectDir}/scripts/step1.py --input ${params.inputPath} --size ${params.areaSize} --output ./
	"""
}


process PythonCrop {
	conda params.condaEnv
	publishDir "${params.outputPath}", mode: 'copy'
	
	input:
	path crop
	
	output:
	path "MERFISH_QC/CroppedImage.jpg", emit: img
	
	script:
	"""
	mkdir -p MERFISH_QC
	python ${projectDir}/scripts/step2.py --image ${params.image} --con ${params.convFile} --output ./
	"""
}

process PythonOverlay {
	conda params.condaEnv
	publishDir "${params.outputPath}", mode: 'copy'
	
	input:
	path dense_areas
	path img
	
	output:
	path "MERFISH_QC/PolygonOverlay.jpg"
	
	script:
	"""
	mkdir -p MERFISH_QC
	python ${projectDir}/scripts/step3.py --input ${params.inputPath} --img ${img} --output ./
	"""
}

/*
 * --------------------
 * Workflow definition
 * --------------------
 */

workflow {
    Setup()
    density_ch = PythonDensity()
    crop_ch    = PythonCrop(density_ch.crop)
    PythonOverlay(density_ch.crop, crop_ch.img)
}