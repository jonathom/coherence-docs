from terracatalogueclient import Catalogue
import datetime as dt

# processes only VV

# define name of result
name = "testRun_01"

catalogue = Catalogue()

bbox = {"west": 4.38, "south": 51.21, "east": 4.42, "north": 51.24}

# give one date, find closest acqusition before and after
event = dt.date(2021, 10, 15) # input

before = event - dt.timedelta(days = 6)
after = event + dt.timedelta(days = 14)

print("[CATALOGUE]: starting search for scenes...")

# first search
cat_before = catalogue.get_products(
	"urn:eop:VITO:CGS_S1_SLC_L1",
	start = before,
	end = event,
	bbox = bbox
)

prod_before = {"date": None, "id": None, "path": None, 
			"orbitDirection": None, "relativeOrbitNumber": None}

# find the product closest to event date, save direction and rel orbit
for p in cat_before:
	if prod_before["date"] is None:
		prod_before["date"] = p.beginningDateTime
		prod_before["id"]  = p.id
		path = p.data[0].href 
		iw_index = path.index("IW")
		prod_before["path"] = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]
		prod_before["orbitDirection"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["orbitDirection"]
		prod_before["relativeOrbitNumber"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["relativeOrbitNumber"]
	else:
		if p.beginningDateTime > prod_before["date"]:
			prod_before["date"] = p.beginningDateTime
			prod_before["id"] = p.id
			path = p.data[0].href 
			iw_index = path.index("IW")
			prod_before["path"] = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]
			prod_before["orbitDirection"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["orbitDirection"]
			prod_before["relativeOrbitNumber"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["relativeOrbitNumber"]
		else:
			pass

print("[CATALOGUE]: found first scene at: ", prod_before["path"])

# quary for second product given the direction and rel orbit
cat_after = catalogue.get_products(
	"urn:eop:VITO:CGS_S1_SLC_L1",
	start = event + dt.timedelta(days = 10),
	end = after,
	bbox = bbox,
	orbitDirection = prod_before["orbitDirection"],
	relativeOrbitNumber = prod_before["relativeOrbitNumber"]
)

prod_after = {"date": None, "id": None, "path": None}

# find the closest one to event date
for p in cat_after:		
	if prod_after["date"] is None:
		prod_after["date"] = p.beginningDateTime
		prod_after["id"]  = p.id
		path = p.data[0].href 
		iw_index = path.index("IW")
		prod_after["path"] = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]
	else:
		if p.beginningDateTime < prod_after["date"]:
			prod_after["date"] = p.beginningDateTime
			prod_after["id"] = p.id
			path = p.data[0].href
			iw_index = path.index("IW")
			prod_after["path"] = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]
		else:
			pass
			
print("[CATALOGUE]: found matching scene at: ", prod_after["path"])

# s1-tops-split-analyzer
import stsa
ana_split = stsa.TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'])
ana_split.load_data(zip_path = prod_before["path"])

# intersect subswaths and bursts with bbox
ana_split._create_subswath_geometry()
tops_split = ana_split.df.cx[bbox["west"]:bbox["east"], bbox["south"]:bbox["north"]]
print("[S1-TOPS-SPLIT]: found the following bursts: \n", tops_split)

# create a processing dictionary
processing_dict = {"IW1": {"min": None, "max": None}, "IW2": {"min": None, "max": None}, "IW3": {"min": None, "max": None}}

for i, row in tops_split.iterrows():
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

print("[S1-TOPS-SPLIT]: created processing dict: ", processing_dict)

from pyroSAR.snap.auxil import parse_recipe, parse_node
import logging
logging.basicConfig(level=logging.INFO)

workflow = parse_recipe('blank')

# reference
read = parse_node("Read")
read.parameters["file"] = prod_before["path"]
read.parameters["formatName"] = "SENTINEL-1"
workflow.insert_node(read)

# secondary
read2 = parse_node("Read")
read2.parameters["file"] = prod_after["path"]
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
    aof5.parameters["continueOnFail"] = "true"
    workflow.insert_node(aof5, before = split5.id)

    # apply orbit file 2
    aof6 = parse_node("Apply-Orbit-File")
    aof6.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
    aof6.parameters["polyDegree"] = 3
    aof5.parameters["continueOnFail"] = "true"
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
write.parameters["file"] = "/data/users/Public/jonathanbahlmann/SNAP_results/" + name
write.parameters["formatName"] = "GeoTIFF"
workflow.insert_node(write, before = tc.id)

workflow.write("/data/users/Public/jonathanbahlmann/SNAP_results/SNAP_workflow.xml")

from pyroSAR.snap.auxil import gpt
from pyroSAR.snap.auxil import groupbyWorkers

groups = groupbyWorkers('/data/users/Public/jonathanbahlmann/SNAP_results/SNAP_workflow.xml', n=1)
print(groups)

gpt('/data/users/Public/jonathanbahlmann/SNAP_results/SNAP_workflow.xml', groups = groups, outdir = "/data/users/Public/jonathanbahlmann/SNAP_results/" + name)


