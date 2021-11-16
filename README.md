# Options to Calculate a S1 Coherence on the VITO backend

* SLC data is on terrascope, could be reached via VM
* there is no CARD4L ARD standard yet, couldn't find a draft document
* [ISCE3 framework](https://github.com/isce-framework/isce3/) seems to be interesting but doesn't support S1 yet: "ISCE3 developments is driven by NISAR and therefore the software does not formally support Sentinel-1 yet. As we will add Sentinel-1 support to isce3 we can build other algorithms within isce3." [ISCE2](https://github.com/isce-framework/isce2) might.

## TODO
- [] try out OTB &  DiapOTB
- [] try pyroSAR
- [] try preprocessing, SAR2Cube

## Coherence

"Therefore, the phase noise changes from pixel to pixel due to the different impact of the random noise superposed on the random amplitudes of the pixels. Pixels with weak returns will show more dispersed interferometric phases; strong and stable scatterers will yield more reliable phases. In addition, there are important changes between the two acquisitions: temporal, due to the change in the off-nadir angle, and due to random noise. We now define the measure of this change γ, the coherence of the two SAR images (also called the complex correlation)." Ferretti, 2007.

<img src="https://render.githubusercontent.com/render/math?math=\hat{\gamma}=\frac{\displaystyle\sum_{i=1}^{N}u_{1i}u_{2i}^*}{\sqrt{{\sum_{i=1}^{N}\lvert u_{1i} \rvert}^2} \sqrt{{\sum_{i=1}^{N}\lvert u_{2i} \rvert}^2}}">

with <img src="https://render.githubusercontent.com/render/math?math=\hat{\gamma}"> being the coherence estimation, `*` being the complex conjugate.

A coherence correction is also discussed. Not sure which implementations consider this, it seems terrain dependent.

## Data at Terrascope

* [https://docs.terrascope.be/#/DataProducts/Sentinel-1/ProductsOverview](https://docs.terrascope.be/#/DataProducts/Sentinel-1/ProductsOverview)
* How is the data organized?
* How are sub-swaths and bursts handled?

## Needed Processing Steps

This should be a list of the needed processing steps from SLC level to a finished coherence product. Decisions can be made later as to what extent it might be useful to preprocess some of these steps. My guess would be that only doing _all_ steps on the fly will result in a flexible coherence workflow. This list might also be helpful to distinguish between steps that can be done using some library and steps that might need to be implemented.

### ASF Tutorial on Interferogram

found [here](https://asf.alaska.edu/how-to/data-recipes/create-an-interferogram-using-esas-sentinel-1-toolbox/). Byproduct is the coherence. Need to check if the coherence is influenced by all other processing steps and which of them are really needed.

Multiple sub-swaths are used by doing coregistration - deburst for each swath, then merging and doing remaining steps.

* Coregistration of the images into a stack
  * one reference and 1-n secondaries
  * select sub-swath (with TOPSAR-Split)
  * Apply orbit state vectors
  * Back-geocoding with DEM
  * extra output needed if ESD (Enhanced Spectral Diversity) is needed
* Coherence estimation (and interferogram formation in the tutorial)
  * flat-earth-phase removal
* TOPS-Deburst
  * to join bursts together
* Topographic phase removal
* Multi-looking 

### ESA, Skywatch Tutorial

"Sentinel-1 Toolbox TOPS Interferometry Tutorial", Braun & Veci. Basically the same as ASF tutorial.

* Coregistration
  * done in single steps
  * TOPS-Split: select needed bursts
  * Apply orbit info: S1 POD service
  * Back geocoding: Actual coregistration, DEM
  * ESD option (if more than one burst, additional corrections applied)
* Coherence estimation has a window size (10x3) by default
* TOPS-Deburst
* subsets: can only be chosen now, seems like whole bursts need to be processed for interferogram/coherence?

### VITO SNAP Workflow

* Read
* Apply Orbit File
* TOPSAR-Split of all three subswaths
* Back-Geocoding for all swaths
* ESD
* Coherence: no flat earth phase removal, 10x3
* TOPS-Deburst
* TOPSAR Merge (Swaths or diff. scenes)
* Terrain Correction (to 20x20m pixels)
* Write

### General Steps

1. Preprocessing
2. Coherence Estimation
3. Geocoding

### H. Zebker

* "Note that there is no technical case to be made for analyzing data on a regular grid rather than range-Doppler coordinates"
* the order of some processing steps can be altered 
* moving terrain correction and geocoding upstream before the interferogram formation
* mostly useful when all-to-all interferograms are needed (N*(N-1)) / 2 (not consecutive) -> what should the process allow? Use cases needed
* needs to be applied to all data beforehand
* if data would be hosted that way, InSAR would of course be faster
* could speed up OTF processing if all-to-all coherence is neede for some reason, but this might be only the case when interferograms are calculated, and then it could also be part of the interferogram processing which is of no issue here

## Implementation Options

### Orfeo Toolbox & diapOTB

Orfeo Operations include
* SARCoRegistration
* SARDeburst
* SARESD
* SARMultilook
-> **preprocessing steps are there**

DiapOTB
* seems to have applicable processing chains
* SARInterferogram **outputs an interferogram *and* the coherence**

### pyroSAR - SNAP

* could be used to do all processing in SNAP (therefore this **looks like the "safe" option**)
* seems that if the tasks are done 1 by 1 separately, the speed might be adequate or acceptable
* [readthedocs](https://pyrosar.readthedocs.io/en/latest/index.html)
* "SNAP’s Python API snappy is not used due to installation limitations and processing performance."
* see Truckenbrodt et al.: "Towards sentinel-1 SAR analysis-ready data: A best practices assessment on preparing backscatter data for the cube"

### SAR2Cube

* could the preprocessing steps be done on the fly?
* if yes, that + the existing coherence & geocoding workflow could also work
* tried the preprocess module, couldn't install jpy correctly (although without errors), "no module named jpyutil"

**Questions for SAR2Cube**
* Were there specific reasons for which steps were preprocessed and which weren't?
* What is missing for on-demand preprocessing?
* Were any bottlenecks identified?
* Which scenes were coregistered? Neighbouring scenes or all to one?

**Questions for the timeseries example process**
* Why an additional multilooking after the coherence? Calculating coherence already contains a window
* `rename_labels(dim = "bands")` is executed after `reduce_dimension("bands")`. This is logically flawed, there might be a `add_dimension()` missing?
* In the timeseries usecase, `reduce_dimension(reducer = sqrt(Intensity))` is calculated after the coherence process, why is that done? (coherence would be a value [0..1])

**Open Questions**
* Talk from DESCARTES Labs: some kind of "static terrain correction", how would that work?
* Fast burst access might be bottleneck
* Is ASF Vortex open-source?
* Coherence Formula explanation

## install OTB

Problems with python bindings, magic thing that worked: `sudo ln -s /usr/lib/x86_64-linux-gnu/libpython3.8.so /usr/lib libpython3.5m.so.rh-python35-1.0` from [here](https://gis.stackexchange.com/questions/220427/importing-otbapplication-in-python). + doing `source ./OTB-7.4.0-Linux64/otbenv.profile` once in a while

[S1 burst/swath tool](https://github.com/pbrotoisworo/s1-tops-split-analyzer)

[orfeo cookbook](https://www.orfeo-toolbox.org/CookBook/Applications.html)

[diapotb docs](https://gitlab.orfeo-toolbox.org/remote_modules/diapotb/-/wikis/Applications/app_SARDEMProjection)

[snap snapyy doc](https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface)

[sar2cube](https://sar2cube.netlify.app/)

```batch
cmake -D CMAKE_INSTALL_PREFIX=~/OTB/install ../otb/SuperBuild
cmake -DOTB_USE_QT=OFF
cmake -DOTB_USE_QT=OFF ../otb/SuperBuild
make
sudo apt install swig
make
```

* trying SARCoRegistration
* claims products do not inhibit the same physical space
* tried out in SNAP, coherence of 2 bursts in IW2, works good, product is a bit coarse but probably as expected..

## try pyroSAR

* "SNAP’s Python API snappy is not used due to installation limitations and processing performance."
* can run coherence process by first building a graph, then executing it. format "GeoTIFF". ESD not working, around 6 minutes with apply-orbit-file taking up about 18GB of RAM
* in SNAP for comparison: S1 TOPS coreg instead of Back-geocoding?
* SNAP needs 3 mins for same workflow..?
* produces close to same results when coherence window is given
* actually faster without groups, this might change for longer, more complex workflows..
* Can I automate IW and burst selection with this github repo? Add a merge step...
* ESD only needed with more than one burst
* maybe: create db with S1 scenes, filter db for matching input (what is returned by `load_collection`?), ...

Script: input SLC scene and shapefile, automatic swath and burst selection.
Run time for 3 bursts over 2 swaths:
* python: ~25min, ungrouped
* SNAP: 21min
* python: 9min, grouped

apply-orbit-file (applied on the whole file, topsar-split afterwards) and back-geocoding seem to take up the most time.
**Bottlenecks are: apply-orbit-file on whole scene, all other processes on whole bursts instead of only AOI**

* SAR2CUBE does topsar-split first, apply-orbit-file afterwards -> improves memory demand and processing time, results look exactly the same. while less memory is good, processing time win is capped by the fact that it needs to be run for each subswath then, so only makes things faster to a certain degree, especially if a couple bursts of one swath are used
* ESD? dual-pol?
* ESD needed fir interferometry, should be considered for coherence as well

## Trying to Execute diapTOB chains via python

* Not sure if diapOTB installed correctly or why it even exists since it has all(?) the same processes that are in OTB already. 
* the gitlab directory contains processing chains (see wiki) in `python_src` that can be executed together with the right config `.json` file in `./share/ex_config/`
* * ESD fails with error: `TilesAnalysisImageFilter(0x55bbf55d1bb0): Provided MaxShifts are not consistents. Check the input grid`
* try with `ESD_iter = 0`: works. was `2` originally. 
* the `coRegistration_S1IW.py` chain produces (when ESD is left out) coregistered, deramped tifs for ref and secondary.
* chain `diapOTB_S1IW.py` gives back orthorectified interferogram and (not orthorectified) coherence image
* coherence image (in `/filt`) can be georeferenced with the same command as its done for the interferogram at the bottom of the chain script
* afterwards I use `gdalwarp` to reference again since this automatic referencing is a mess.
* next: **compare SNAP and OTB coherence calculations**: measure time with `time python..`, do it on same area:
  * IW2, bursts 3-5 chosen, thats burst 2-4 in OTB counting
  * `pyro11.py` pyroSAR, with grouped workflow and apply-orbit-file only on the bursts, 10x3: real 5m21.896s
  * `diapOTB_S1IW.py` OTB processing chain, no ESD (it fails), 8x2, additionally produces interferogram: real 5m1.582s
  * results do not look the same, OTB result much more coherent but seems less quality, there is a striping effect, fields are often completely coherent (weird). Also has finer ground res (due to parameter `Spacingxy`)
  * trying to mess a bit with parameters: `SARCorrelationGridFilter(0x55e64e283600): GridSteps range mot a multiple of MLRan`
  * this warning pops up in the logging file, not sure if its important towards the whole coh thing: `func_utils.py :: INFO :: 2021-11-15 15:59:35 (WARNING): Encoding of file (/home/petra/Praktikum_VITO/S1A_IW_SLC__1SDV_20211014T165252_20211014T165319_040118_04C01F_7558.SAFE/measurement/s1a-iw2-slc-vv-20211014t165253-20211014t165318-040118-04c01f-005.tiff) is complex but will be read as a VectorImage of scalar type, with twice the number of bands.`
  * coherence improves when I change `"Filtered_Interferogram_mlran" : 10, "Filtered_Interferogram_mlazi" : 3` to 10x3, but is still faulty.
  * no other possibilities found to influence this process, so asked OTB forum.

## useful commands
* `export PROJ_LIB=/usr/share/proj`
* `source /home/petra/OTB-7.4.0-Linux64/otbenv.profile`
* `gdalwarp -overwrite -t_srs EPSG:32632 coherence_ortho.tif coherence_ortho_32632.tif`
