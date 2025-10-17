FixMolSlot <- function(obj){
  
  # for each image...
  for(img in names(obj@images)){
    message(paste("Fixing", img, "FOV..."))
    
    
    # convert the molecules slot to a df:
    lapply(obj@images[[img]]$molecules, function(x){
      data.frame(x@coords)
    }) -> test
    for(i in 1:length(test)){
      test[[i]]$gene <- names(test)[i]
    }
    test <- data.table::rbindlist(test)
    
    # get the FOV edges from
    xmin <- obj@images[[img]]$centroids@bbox[1,1]
    xmax <- obj@images[[img]]$centroids@bbox[1,2]
    ymin <- obj@images[[img]]$centroids@bbox[2,1]
    ymax <- obj@images[[img]]$centroids@bbox[2,2]
    
    orig <- nrow(test)
    test <- subset(test, x >= xmin & x <= xmax & y >= ymin & y <= ymax)
    new <- nrow(test)
    message(paste0("Removed ", formatC((orig-new)/orig*100, digits=3), "% of molecules from image slot (", orig-new, ")!\n"))
    
    
    fov <- obj@images[[img]]
    fov[["molecules"]] <- CreateMolecules(coords = test)
    obj@images[[img]] <- fov
  }
  
  return(obj)
}
