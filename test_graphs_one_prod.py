from pyroSAR.snap.auxil import parse_recipe, parse_node

firstBurstIndex = 5
lastBurstIndex = 6
subswath = "IW1"

workflow = parse_recipe('blank')

# reference
read = parse_node("Read")
read.parameters["file"] = "/VM_out/S1B_IW_SLC__1SDV_20211013T055004_20211013T055031_029113_037955_FC03.zip"
read.parameters["formatName"] = "SENTINEL-1"
workflow.insert_node(read)

# secondary
read2 = parse_node("Read")
read2.parameters["file"] = "/VM_out/S1A_IW_SLC__1SDV_20211019T055030_20211019T055057_040184_04C279_2606.zip"
read2.parameters["formatName"] = "SENTINEL-1"
workflow.insert_node(read2)

# TopSAR Split
split = parse_node("TOPSAR-Split")
split.parameters["subswath"] = subswath
split.parameters["selectedPolarisations"] = ["VV"]
split.parameters["firstBurstIndex"] = firstBurstIndex
split.parameters["lastBurstIndex"] = lastBurstIndex
workflow.insert_node(split, before = read.id, resetSuccessorSource = False)

# apply orbit file 1
aof = parse_node("Apply-Orbit-File")
aof.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
aof.parameters["polyDegree"] = 3
workflow.insert_node(aof, before = split.id)

write = parse_node("Write")
write.parameters["file"] = "/VM_out/SNAP_res/test_graphs_two_prod"
write.parameters["formatName"] = "BEAM-DIMAP"
workflow.insert_node(write, before = aof.id)

workflow.write("/home/petra/Praktikum_VITO/coherence-docs/test_graphs_two_prod.xml")