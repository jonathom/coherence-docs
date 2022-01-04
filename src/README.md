# Preprocessing Documentation

## Step 1: Create a Set of Reference Scenes

To be able to calculate coherence on the fly, we first need to coregister all products (of the same relative orbit, frame) to a common reference (old: master) scene. The problem is to define a set of scenes that cover the AOI, but to avoid duplicates.

* A single S1 satellite repeats tracks after 12 days. A 12 day search window therefore guarantees full coverage.
* The burst patterns are sometimes irregular (some subswaths contain more bursts than the usual 9). For descending orbits this can be easily cut. For ascending orbits this problem can not be corrected so easily and should be kept in mind. It would be conceivable to search for "regular" scenes once a irregular one is found..

