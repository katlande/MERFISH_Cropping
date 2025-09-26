# QC Scripts


## Transcript Density
The number of molecules detected in a given area in an important QC metric that can be hard to reliably calculate due to tissue holes, edges, and empty space on slides. To get a general estimate over a grid, we can run the following code:

```
python QC_Scripts/MoleculeDensity.py -d test/example_transcripts.csv -l 70 # using a grid where of 70uM x 70uM squares
```

We recieve the following figures:

<p align="center">
  <img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/MoleculeDensityHeatmap.jpg" width="400" height="400" />
  <img src="https://github.com/katlande/MERFISH_Cropping/blob/main/test/MoleculeDensityHistogram.jpgg" width="400" height="400" />
</p>

Here we can see the relative transcript density in out test image, as well as a distribution of those densities. In real data, we expect the histogram to be more Gaussian, however in our down-sampled testing dataset the distribution is quite messy.
