# Preprocessing Documentation

## Step 1: Create a Set of Reference Scenes

To be able to calculate coherence on the fly, we first need to coregister all products (of the same relative orbit, frame) to a common reference (old: master) scene. The problem is to define a set of scenes that cover the AOI, but to avoid duplicates.

* A single S1 satellite repeats tracks after 12 days. A 12 day search window therefore guarantees full coverage.
* The burst patterns are sometimes irregular (some subswaths contain more bursts than the usual 9). Currently, descending orbits are just cut at burst 9, while ascending orbits can not be corrected that easily. It would be conceivable to search for "regular" scenes once an irregular one is found..

The function `create_reference_scene_json()` in `reference_frames.py` takes a timeframe and an AOI file to create a geojson containing reference scenes.
