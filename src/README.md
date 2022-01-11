# Preprocessing Documentation

## Step 1: Create a Set of Reference Scenes

To be able to calculate coherence on the fly, we first need to coregister all products (of the same relative orbit, frame) to a common reference (old: master) scene. The problem is to define a set of scenes that cover the AOI, but to avoid duplicates.

* A single S1 satellite repeats tracks after 12 days. A 12 day search window therefore guarantees full coverage.
* The burst patterns are sometimes irregular (some subswaths contain more bursts than the usual 9). Currently, descending orbits are just cut at burst 9, while ascending orbits can not be corrected that easily. It would be conceivable to search for "regular" scenes once an irregular one is found.
* There are currently no tests for this function. The result is the basis for any preprocessing and should therefore be looked at before preprocessing is started.

The function `create_reference_scene_json()` in `reference_frames.py` takes a timeframe, an AOI file and an optional already existing reference file to create 2 geojson files, one with bursts and one with aggregated scenes. The function checks whether there already exist reference scenes for new scenes, so it can be run multiple times. The timeframe can not exceed 12 days, because the function does not do ambiguity checks inside a single run.

* In the final `.geojson`, only those bursts that intersect with the AOI are contained (in opposition to containing full scenes)
* bursts that lie in the middle of a subswath but do not intersect the AOI are left out. Out of practicality, only continuous subswaths should be processed (via min-max constraint probably)
* Of course the `.geojson` does not contain any SAR data and can only serve as a guide to which scenes should be processed and with which respective reference scenes that should be done.

**Step 1 is to execute `create_reference_frames.py` with a proper timeframe (currently hardcoded) and an AOI `geojson` file. It will create or add to `reference_bursts.geojson` which will contain a collection of bursts that covers the AOI (consider Terrascope availability).**

## Step 2: Organize Bursts to Process

### 2.1 List products in a given time range

`list_products_by_time` in `preprocessing.py`

* known bug: if months contain a day or more with no acquisitions, the date handling is shifted by one day. This is however not super important rn.
* can not handle year changes
* is only designed to be able to get *one day* of data, or like *five days* or *a month* if it works better for testing purposes.

### 2.2 make gpd / integrate into gpd of processed bursts

The `processing.geojson` file is produced here. It contains all bursts that are fed to it via the `list_products_by_time` function (only once). For each burst it contains the reference scene `id` and the range of bursts (`min`, `max`) of the reference scene for that subswath. It is not necessary to relate every scene burst to the exact reference burst because the processing is gonna be subswath - wise anyway.

* `process_geojson()` function to handle the `processing.geojson` file, via `create_processing_gjson.py`
* e.g. call `python create_processing_gjson.py "2021/07/06" "2021/07/10"`
* processing.geojson is created containing bursts and their reference scenes and those scenes relevant swaths

**Step 2 is to execute `python create_processing_gjson.py "2021/07/06" "2021/07/10"` (with any dates you like within one year, maybe steer clear of Oct 2021). It will create or add to `processing.geojson` with a list of bursts that shall be processed.**

## Step 3: Orchestrate Preprocessing via pyroSAR

* processing will be done in docker containers
* how to orchestrate? might make sense to do 1 container = 1 coregistration
* one coreg process per reference_scene over all applicable subswaths (to be able to use SNAP merge to make one subscene again)
* questions then: where to control docker from? how to register and wait for jobs? 
* make docker container that can be launched with exactly one job