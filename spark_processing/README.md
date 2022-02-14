# Spark Processing
Preprocess S1 data in docker containers via spark. All bursts (except single bursts) in `/src/processing.geojson` are processed. Steps taken are: split, apply orbit file, back-geocoding, merge, deburst.

Known issue: **Apply Orbit File is "turned off"** at the moment via the `ContinueOnFail` option set to `True`. For more exact results this needs to be resolved. There are some scripts in this repository that show how to download the orbit files via PyroSAR, since SNAP seems to fail to do so.