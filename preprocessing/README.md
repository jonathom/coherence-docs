# Preprocessing Documentation

## Step 1: Create a Set of Reference Scenes

To be able to calculate coherence on the fly, we first need to coregister all products (of the same relative orbit, frame) to common reference (old: master) scenes. The problem is to define a set of scenes that cover the AOI, but to avoid duplicates. The scenes can only be from one satellite, to not mess with area coverage. This means data from the chosen satellite can always be coregistered to a single master, and data from the other satellite(s) will always be coregistered to two reference scenes, because S1A and S1B have a half scene offset over Belgium. 

I asked around a bit and coregistration should still work fine for scenes with up to a 10 year time gap. For a rolling system it makes sense to choose the reference scenes as recent as possible to be ready for many years to come. In this case, I chose the first 12 days of October 2021 and Sentinel 1A (which makes even more sense after the unfortunate failure of S1B in December).

* A single S1 satellite repeats tracks after 12 days. A 12 day search window therefore guarantees full coverage over the AOI
* The burst patterns are sometimes irregular (some subswaths contain more bursts than the usual 9). I don't know why this happens but it seems that the whole area is covered by the regular 9 bursts either case. Currently, descending orbits are just cut at burst 9, while ascending orbits can not be corrected that easily. It would be conceivable to search for "regular" scenes once an irregular one is found.
* There are currently no tests for this function. The result is the basis for any preprocessing and should therefore be looked at before preprocessing is started.

The function `create_reference_scene_json()` in `reference_frames.py` takes a timeframe, an AOI file and an optional already existing reference file to create 2 geojson files, one with bursts (the result) and one with aggregated scenes (only needed for visualization purposes). The function checks whether there already exist reference scenes for new scenes, so it can be run multiple times. That is useful because the Terrascope Sentinel 1 SLC collection is quite diverse geographically, and a single 12-day period might not contain references for all scenes that you want to process. Have a look at the geojsons in `/relative_frames_examples` to check some example output. The function input timeframe should not exceed 12 days, because the function does not do ambiguity checks inside a single run.

* In the final `reference_bursts.geojson`, only those *bursts* that intersect with the AOI are contained (in opposition to containing *full scenes*)
* bursts that lie in the middle of a subswath but do not intersect the AOI are left out. Out of practicality, only continuous subswaths should be processed (via min-max constraint probably)

The result of this step is the `reference_bursts.geojson`, which will serve as a lookup table to find reference scenes for scenes that should be processed.

**Step 1 is to execute `create_reference_frames.py` with a proper timeframe (currently hardcoded) and an AOI `geojson` file. It will create or add to `reference_bursts.geojson` which will contain a collection of bursts that covers the AOI (consider Terrascope availability).**

## Step 2: Organize Bursts to Process

Now that we have gathered reference scenes, it is time to round up a set of scenes we actually want to process.

### 2.1 List products in a given time range

`list_products_by_time` in `preprocessing.py`

### 2.2 make gpd / integrate into gpd of processed bursts

The `processing.geojson` file is produced here. It contains all bursts that are fed to it via the `list_products_by_time` function (only once). For *each burst* it contains the `id` and the range of bursts (`min`, `max`) of the scene and its reference scene. It is not necessary to relate every scene burst to the exact reference burst because the processing is gonna be subswath - wise anyway.

* `process_geojson()` function to handle the `processing.geojson` file, via `create_processing_gjson.py`
* e.g. call `python create_processing_gjson.py "2021/07/06" "2021/07/10"`
* `processing.geojson` is created containing bursts and their reference scenes and those scenes relevant swaths
* the `processing_status` attribute is not in use yet

**Step 2 is to execute `python create_processing_gjson.py "2021/07/06" "2021/07/10"`. It will create or add to `processing.geojson` with a list of bursts that shall be processed.** Use any dates you like within one year, maybe steer clear of Oct 2021 because it contains the reference scenes and that case is not handled yet.

## Step 3: Orchestrate Preprocessing via pyroSAR

* processing will be done in docker containers via spark
* one coreg process per reference_scene over all applicable subswaths (to be able to use `SNAP merge` to make one subscene again)

Next step: **`/spark_processing`**