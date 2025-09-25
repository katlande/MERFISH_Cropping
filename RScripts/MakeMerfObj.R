MakeMerfObj <- function(dir, sample, ncores=12, transcripts=NULL, verbose.seurat=F){
  
  message("Creating polygon object...")
  polygon <- LoadVizgen(data.dir = dir, 
                    fov = sample,  
                    assay = "RNA", metadata = c("volume", "fov"), 
                    type = c("segmentations", "centroids"),  
                    z = 3L, add.zIndex = TRUE,  
                    update.object = TRUE, 
                    use.BiocParallel = TRUE,
                    workers.MulticoreParam = ncores, 
                    verbose = verbose.seurat)
  
  message("Adding x,y coordinates to meta data...")
  centroid <- ReadVizgen(dir, type = 'centroids')$centroids
  centroid <- unique(subset(centroid, cell %in% row.names(polygon@meta.data)))
  
  if(identical(centroid$cell, row.names(polygon@meta.data))){
    polygon@meta.data <- cbind(polygon@meta.data, centroid[! colnames(centroid) == "cell"])
  } else {
    warning("Centroid and polygon cell names do not match! Could not add centroids to meta data.")
  }
  
  polygon$orig.ident <- sample
  polygon <- NormalizeData(object = polygon) # log normalize 
  message("SCT Transforming (with cell size regression)")
  polygon <- SCTransform(polygon, verbose = verbose.seurat, vars.to.regress = "volume", ncell=ncol(polygon))
 
  message("Reading in transcript information...")
  if(is.null(transcripts)){
    mols <- read.csv(paste0(dir, "/detected_transcripts.csv"))
  } else {
    mols <- read.csv(transcripts)
  }
  
  message("Creating new molecule slot...")
  mols <- setNames(mols[colnames(mols) %in% c("global_x", "global_y", "gene")], c("x", "y", "gene"))
  mols <- subset(mols, !grepl("Blank\\-", mols$gene))
  fov <- polygon@images[[sample]]
  fov[["molecules"]] <- CreateMolecules(coords = mols)
  polygon@images[[sample]] <- fov
  
  return(polygon)
}

# dir: directory to Seurat input files
# sample: sample name (as character)
# ncores: # threads to use for processing polygons (default=12)
# transcripts: transcript file to use if not simply "detected_transcripts.csv" in dir, otherwise NULL 
# verbose.seurat: whether or not to show the verbose output for internal seurat functions

# This function will create a working seurat object containing polygon segmentation, centroids in the meta data, and ALL molecules in the images slot.
