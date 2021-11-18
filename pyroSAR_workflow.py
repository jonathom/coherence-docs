import logging
logging.basicConfig(level=logging.INFO)

import os
os.environ['PROJ_LIB'] = '/usr/share/proj'

import stsa

s1 = stsa.TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'])
s1.load_data(zip_path='/home/petra/Praktikum_VITO/S1A_IW_SLC__1SDV_20211014T165252_20211014T165319_040118_04C01F_7558.zip')
s1.to_shapefile('/home/petra/Praktikum_VITO/pyroSAR/try_stsa.shp')
s1.to_json('/home/petra/Praktikum_VITO/pyroSAR/try_stsa.geojson')

import geopandas as gpd

footprint = gpd.read_file("/home/petra/Praktikum_VITO/pyroSAR/try_stsa.shp")
aoi = gpd.read_file("/home/petra/Praktikum_VITO/pyroSAR/2swaths.shp")
inter = gpd.overlay(footprint, aoi, how = "intersection")

processing_dict = {"IW1": {"min": None, "max": None}, "IW2": {"min": None, "max": None}, "IW3": {"min": None, "max": None}}

for i, row in inter.iterrows():
    swath = row["subswath"]
    if processing_dict[swath]["min"] is None:
        processing_dict[swath]["min"] = row["burst"]
        processing_dict[swath]["max"] = row["burst"]
    elif row["burst"] < processing_dict[swath]["min"]:
        processing_dict[swath]["min"] = row["burst"]
    elif row["burst"] > processing_dict[swath]["max"]:
        processing_dict[swath]["max"] = row["burst"]
    else:
        pass

# overwrite for testing purposes
processing_dict = {"IW1": {"min": None, "max": None}, "IW2": {"min": 3, "max": 5}, "IW3": {"min": None, "max": None}}

from pyroSAR.snap.auxil import parse_recipe, parse_node
import logging
logging.basicConfig(level=logging.INFO)

workflow = parse_recipe('blank')

# reference
read = parse_node("Read")
read.parameters["file"] = "/home/petra/Praktikum_VITO/S1A_IW_SLC__1SDV_20211014T165252_20211014T165319_040118_04C01F_7558.zip"
read.parameters["formatName"] = "SENTINEL-1"
workflow.insert_node(read)

# secondary
read2 = parse_node("Read")
read2.parameters["file"] = "/home/petra/Praktikum_VITO/S1B_IW_SLC__1SDV_20211020T165211_20211020T165239_029222_037CCF_4397.zip"
read2.parameters["formatName"] = "SENTINEL-1"
workflow.insert_node(read2)

merge_list = []

# check IW1, empty?
if processing_dict["IW1"]["max"] is None:
    print("[PROCESSING IW1]: No bursts needed from IW1")
else:
    print("[PROCESSING IW1]: ", processing_dict["IW1"])
    # TopSAR Split
    split = parse_node("TOPSAR-Split")
    split.parameters["subswath"] = "IW1"
    split.parameters["selectedPolarisations"] = ["VV"]
    split.parameters["firstBurstIndex"] = processing_dict["IW1"]["min"]
    split.parameters["lastBurstIndex"] = processing_dict["IW1"]["max"]
    workflow.insert_node(split, before = read.id, resetSuccessorSource = False)

    # TopSAR Split 2
    split2 = parse_node("TOPSAR-Split")
    split2.parameters["subswath"] = "IW1"
    split2.parameters["selectedPolarisations"] = ["VV"]
    split2.parameters["firstBurstIndex"] = processing_dict["IW1"]["min"]
    split2.parameters["lastBurstIndex"] = processing_dict["IW1"]["max"]
    workflow.insert_node(split2, before = read2.id, resetSuccessorSource = False)

    # apply orbit file 1
    aof = parse_node("Apply-Orbit-File")
    aof.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
    aof.parameters["polyDegree"] = 3
    workflow.insert_node(aof, before = split.id)

    # apply orbit file 2
    aof2 = parse_node("Apply-Orbit-File")
    aof2.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
    aof2.parameters["polyDegree"] = 3
    workflow.insert_node(aof2, before = split2.id)

    # Back-Geocoding
    geocode = parse_node("Back-Geocoding")
    geocode.parameters["demName"] = "SRTM 1Sec HGT"
    workflow.insert_node(geocode, before = [aof.id, aof2.id])

    # coherence
    coh = parse_node("Coherence")
    coh.parameters["cohWinAz"] = 3
    coh.parameters["cohWinRg"] = 10
    coh.parameters["squarePixel"] = "true"
    coh.parameters["subtractFlatEarthPhase"] = "false"
    coh.parameters["srpPolynomialDegree"] = 5
    coh.parameters["srpNumberPoints"] = 501
    coh.parameters["orbitDegree"] = 3
    coh.parameters["subtractTopographicPhase"] = "false"
    workflow.insert_node(coh, before = geocode.id)

    # deburst
    deb = parse_node("TOPSAR-Deburst")
    workflow.insert_node(deb, before = coh.id)

    merge_list.append(deb.id)


# check IW2, empty?
if processing_dict["IW2"]["max"] is None:
    print("[PROCESSING IW2]: No bursts needed from IW2")
else:
    print("[PROCESSING IW2]: ", processing_dict["IW2"])
    # TopSAR Split
    split3 = parse_node("TOPSAR-Split")
    split3.parameters["subswath"] = "IW2"
    split3.parameters["selectedPolarisations"] = ["VV"]
    split3.parameters["firstBurstIndex"] = processing_dict["IW2"]["min"]
    split3.parameters["lastBurstIndex"] = processing_dict["IW2"]["max"]
    workflow.insert_node(split3, before = read.id, resetSuccessorSource = False)

    # TopSAR Split 2
    split4 = parse_node("TOPSAR-Split")
    split4.parameters["subswath"] = "IW2"
    split4.parameters["selectedPolarisations"] = ["VV"]
    split4.parameters["firstBurstIndex"] = processing_dict["IW2"]["min"]
    split4.parameters["lastBurstIndex"] = processing_dict["IW2"]["max"]
    workflow.insert_node(split4, before = read2.id, resetSuccessorSource = False)

    # apply orbit file 1
    aof3 = parse_node("Apply-Orbit-File")
    aof3.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
    aof3.parameters["polyDegree"] = 3
    workflow.insert_node(aof3, before = split3.id)

    # apply orbit file 2
    aof4 = parse_node("Apply-Orbit-File")
    aof4.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
    aof4.parameters["polyDegree"] = 3
    workflow.insert_node(aof4, before = split4.id)

    # Back-Geocoding
    geocode2 = parse_node("Back-Geocoding")
    geocode2.parameters["demName"] = "SRTM 1Sec HGT"
    workflow.insert_node(geocode2, before = [aof3.id, aof4.id])

    # coherence
    coh2 = parse_node("Coherence")
    coh2.parameters["cohWinAz"] = 3
    coh2.parameters["cohWinRg"] = 10
    coh2.parameters["squarePixel"] = "true"
    coh2.parameters["subtractFlatEarthPhase"] = "false"
    coh2.parameters["srpPolynomialDegree"] = 5
    coh2.parameters["srpNumberPoints"] = 501
    coh2.parameters["orbitDegree"] = 3
    coh2.parameters["subtractTopographicPhase"] = "false"
    workflow.insert_node(coh2, before = geocode2.id)

    # deburst
    deb2 = parse_node("TOPSAR-Deburst")
    workflow.insert_node(deb2, before = coh2.id)

    merge_list.append(deb2.id)


# check IW3, empty?
if processing_dict["IW3"]["max"] is None:
    print("[PROCESSING IW3]: No bursts needed from IW3")
else:
    print("[PROCESSING IW3]: ", processing_dict["IW3"])
    # TopSAR Split
    split5 = parse_node("TOPSAR-Split")
    split5.parameters["subswath"] = "IW3"
    split5.parameters["selectedPolarisations"] = ["VV"]
    split5.parameters["firstBurstIndex"] = processing_dict["IW3"]["min"]
    split5.parameters["lastBurstIndex"] = processing_dict["IW3"]["max"]
    workflow.insert_node(split5, before = read.id, resetSuccessorSource = False)

    # TopSAR Split 2
    split6 = parse_node("TOPSAR-Split")
    split6.parameters["subswath"] = "IW3"
    split6.parameters["selectedPolarisations"] = ["VV"]
    split6.parameters["firstBurstIndex"] = processing_dict["IW3"]["min"]
    split6.parameters["lastBurstIndex"] = processing_dict["IW3"]["max"]
    workflow.insert_node(split6, before = read2.id, resetSuccessorSource = False)

    # apply orbit file 1
    aof5 = parse_node("Apply-Orbit-File")
    aof5.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
    aof5.parameters["polyDegree"] = 3
    workflow.insert_node(aof5, before = split5.id)

    # apply orbit file 2
    aof6 = parse_node("Apply-Orbit-File")
    aof6.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
    aof6.parameters["polyDegree"] = 3
    workflow.insert_node(aof6, before = split6.id)

    # Back-Geocoding
    geocode3 = parse_node("Back-Geocoding")
    geocode3.parameters["demName"] = "SRTM 1Sec HGT"
    workflow.insert_node(geocode3, before = [aof5.id, aof6.id])

    # coherence
    coh3 = parse_node("Coherence")
    coh3.parameters["cohWinAz"] = 3
    coh3.parameters["cohWinRg"] = 10
    coh3.parameters["squarePixel"] = "true"
    coh3.parameters["subtractFlatEarthPhase"] = "false"
    coh3.parameters["srpPolynomialDegree"] = 5
    coh3.parameters["srpNumberPoints"] = 501
    coh3.parameters["orbitDegree"] = 3
    coh3.parameters["subtractTopographicPhase"] = "false"
    workflow.insert_node(coh3, before = geocode3.id)

    # deburst
    deb3 = parse_node("TOPSAR-Deburst")
    workflow.insert_node(deb3, before = coh3.id)

    merge_list.append(deb3.id)


if len(merge_list) > 1:
    merge = parse_node("TOPSAR-Merge")
    workflow.insert_node(merge, before = merge_list)

    # terrain correction
    tc = parse_node("Terrain-Correction")
    tc.parameters["demName"] = "SRTM 1Sec HGT"
    tc.parameters["pixelSpacingInMeter"] = 20
    tc.parameters["mapProjection"] = "AUTO:42001"
    tc.parameters["outputComplex"] = "false"
    workflow.insert_node(tc, before = merge.id)

elif len(merge_list) == 1:
    # terrain correction
    tc = parse_node("Terrain-Correction")
    tc.parameters["demName"] = "SRTM 1Sec HGT"
    tc.parameters["pixelSpacingInMeter"] = 20
    tc.parameters["mapProjection"] = "AUTO:42001"
    tc.parameters["outputComplex"] = "false"
    # if only one deburst node is registered, then its name is "TOPSAR-Deburst"
    workflow.insert_node(tc, before = "TOPSAR-Deburst")

write = parse_node("Write")
write.parameters["file"] = "/home/petra/Praktikum_VITO/pyroSAR/pyro11_4GBRAM"
write.parameters["formatName"] = "GeoTIFF"
workflow.insert_node(write, before = tc.id)

workflow.write("/home/petra/Praktikum_VITO/pyroSAR/pyro11_workflow.xml")

from pyroSAR.snap.auxil import gpt

from pyroSAR.snap.auxil import groupbyWorkers

groups = groupbyWorkers('/home/petra/Praktikum_VITO/pyroSAR/pyro11_workflow.xml', n=1)
print(groups)

gpt('/home/petra/Praktikum_VITO/pyroSAR/pyro11_workflow.xml', groups = groups, outdir = "/home/petra/Praktikum_VITO/pyroSAR/pyro11_4GBRAM")

# 17.02 - 17.09 = 7min, grouped, apply orbit fle below 4gb of ram, back-geocoding above, about 10gb
