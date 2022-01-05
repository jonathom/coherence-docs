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

**Step 1 is to execute `create_reference_scene_json()` with a proper timeframe and an AOI `geojson` file.**

## Step 2: Orchestrate Preprocessing Worklfow

**2.1 List products in a given time range**

`list_products_by_time` in `preprocessing.py`

* known bug: if months contain a day or more with no acquisitions, the date handling is shifted by one day. This is however not super important rn.
* can not handle year changes
* is only designed to be able to get *one day* of data, or like *five days* or *a month* if it works better for testing purposes.

**2.2 make gpd / integrate into gpd of processed bursts**