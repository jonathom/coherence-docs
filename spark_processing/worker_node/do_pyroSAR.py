def handle_gpd(gdf):
    import geopandas as gpd
    
    return len(gdf)

def do_pyroSAR(df):
    
    from pyroSAR.snap.auxil import parse_recipe, parse_node, gpt, groupbyWorkers
    from pyroSAR import identify
    import geopandas as gpd
    from os import mkdir, environ
    from os.path import isdir, isfile

    root = "/data/users/Public/jonathanbahlmann/spark_results/"

    continueOnFailAOF = False
    
    pwd = environ["PWD"]
    osvdir = pwd + "/./auxdata/Orbits/Sentinel-1"

    scene = df.iloc[0]["path"]
    id = identify(scene)
    match = id.getOSV(osvdir=osvdir, osvType='RES', returnMatch=True)
    match = id.getOSV(osvdir=osvdir, osvType='POE', returnMatch=True)
    
    ref_scene = df.iloc[0]["ref_path"]
    ref_id = identify(ref_scene)
    match = ref_id.getOSV(osvdir=osvdir, osvType='RES', returnMatch=True)
    match = ref_id.getOSV(osvdir=osvdir, osvType='POE', returnMatch=True)
    
    name = str(df.iloc[0]["id"]) + "_" + df.iloc[0]["ref_scene"] + "_" + str(int(df.iloc[0]["sce_min_burst"])) + "_" + str(int(df.iloc[0]["sce_max_burst"]))
    workflow_filename = "graph_" + name + ".xml"
    out_filename = name + "_Stack_deb"
    
    year = df.iloc[0]["start"][0:4]
    month = df.iloc[0]["start"][4:6]
    day = df.iloc[0]["start"][6:8]
    
    if not isdir(root + year):
        mkdir(root + year)
    if not isdir(root + year + "/" + month):
        mkdir(root + year + "/" + month)
    if not isdir(root + year + "/" + month + "/" + day):
        mkdir(root + year + "/" + month + "/" + day)
        
    output_dir = root + year + "/" + month + "/" + day + "/" + name
    if not isdir(output_dir):
        mkdir(root + year + "/" + month + "/" + day + "/" + name)
        
    output_dir = output_dir + "/"
    dim_file = output_dir + out_filename + ".dim"
        
    # test if processing was done already
    if isfile(dim_file):
        print("[MESSAGE]: ", dim_file, " exists. Skipping.")
        pass
    else:
        # each of these frames that I get here are similar to the pyroXX_workflow.py
        processing_dict = {"IW1": {"min_sce": None, "max_sce": None, "min_ref": None, "max_ref": None}, 
                           "IW2": {"min_sce": None, "max_sce": None, "min_ref": None, "max_ref": None}, 
                           "IW3": {"min_sce": None, "max_sce": None, "min_ref": None, "max_ref": None}}

        for i, row in df.iterrows():
            swath = row["subswath"]
            processing_dict[swath]["min_sce"] = int(row["sce_min_burst"])
            processing_dict[swath]["max_sce"] = int(row["sce_max_burst"])
            processing_dict[swath]["min_ref"] = int(row["ref_min_burst"])
            processing_dict[swath]["max_ref"] = int(row["ref_max_burst"])

        workflow = parse_recipe('blank')

        # reference
        read = parse_node("Read")
        read.parameters["file"] = df.iloc[0]["ref_path"]
        read.parameters["formatName"] = "SENTINEL-1"
        workflow.insert_node(read)

        # secondary
        read2 = parse_node("Read")
        read2.parameters["file"] = df.iloc[0]["path"]
        read2.parameters["formatName"] = "SENTINEL-1"
        workflow.insert_node(read2)

        merge_list = []

        # check IW1, empty?
        if processing_dict["IW1"]["max_sce"] is None or processing_dict["IW1"]["max_ref"] is None:
            print("[PROCESSING IW1]: No bursts needed from IW1")
        else:
            print("[PROCESSING IW1]: ", processing_dict["IW1"])
            # TopSAR Split
            split = parse_node("TOPSAR-Split")
            split.parameters["subswath"] = "IW1"
            split.parameters["selectedPolarisations"] = ["VV", "VH"]
            split.parameters["firstBurstIndex"] = processing_dict["IW1"]["min_ref"]
            split.parameters["lastBurstIndex"] = processing_dict["IW1"]["max_ref"]
            workflow.insert_node(split, before = read.id, resetSuccessorSource = False)

            # TopSAR Split 2
            split2 = parse_node("TOPSAR-Split")
            split2.parameters["subswath"] = "IW1"
            split2.parameters["selectedPolarisations"] = ["VV", "VH"]
            split2.parameters["firstBurstIndex"] = processing_dict["IW1"]["min_sce"]
            split2.parameters["lastBurstIndex"] = processing_dict["IW1"]["max_sce"]
            workflow.insert_node(split2, before = read2.id, resetSuccessorSource = False)

            # apply orbit file 1
            aof = parse_node("Apply-Orbit-File")
            aof.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
            aof.parameters["polyDegree"] = 3
            aof.parameters["continueOnFail"] = continueOnFailAOF
            workflow.insert_node(aof, before = split.id)

            # apply orbit file 2
            aof2 = parse_node("Apply-Orbit-File")
            aof2.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
            aof2.parameters["polyDegree"] = 3
            aof2.parameters["continueOnFail"] = continueOnFailAOF
            workflow.insert_node(aof2, before = split2.id)

            # Back-Geocoding
            geocode = parse_node("Back-Geocoding")
            geocode.parameters["demName"] = "SRTM 1Sec HGT"
            workflow.insert_node(geocode, before = [aof.id, aof2.id])

            # deburst
            deb = parse_node("TOPSAR-Deburst")
            workflow.insert_node(deb, before = geocode.id)

            merge_list.append(deb.id)
        # check IW2, empty?
        if processing_dict["IW2"]["max_sce"] is None or processing_dict["IW2"]["max_ref"] is None:
            print("[PROCESSING IW2]: No bursts needed from IW2")
        else:
            print("[PROCESSING IW2]: ", processing_dict["IW2"])
            # TopSAR Split
            split3 = parse_node("TOPSAR-Split")
            split3.parameters["subswath"] = "IW2"
            split3.parameters["selectedPolarisations"] = ["VV", "VH"]
            split3.parameters["firstBurstIndex"] = processing_dict["IW2"]["min_ref"]
            split3.parameters["lastBurstIndex"] = processing_dict["IW2"]["max_ref"]
            workflow.insert_node(split3, before = read.id, resetSuccessorSource = False)

            # TopSAR Split 2
            split4 = parse_node("TOPSAR-Split")
            split4.parameters["subswath"] = "IW2"
            split4.parameters["selectedPolarisations"] = ["VV", "VH"]
            split4.parameters["firstBurstIndex"] = processing_dict["IW2"]["min_sce"]
            split4.parameters["lastBurstIndex"] = processing_dict["IW2"]["max_sce"]
            workflow.insert_node(split4, before = read2.id, resetSuccessorSource = False)

            # apply orbit file 1
            aof3 = parse_node("Apply-Orbit-File")
            aof3.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
            aof3.parameters["polyDegree"] = 3
            aof3.parameters["continueOnFail"] = continueOnFailAOF
            workflow.insert_node(aof3, before = split3.id)

            # apply orbit file 2
            aof4 = parse_node("Apply-Orbit-File")
            aof4.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
            aof4.parameters["polyDegree"] = 3
            aof4.parameters["continueOnFail"] = continueOnFailAOF
            workflow.insert_node(aof4, before = split4.id)

            # Back-Geocoding
            geocode2 = parse_node("Back-Geocoding")
            geocode2.parameters["demName"] = "SRTM 1Sec HGT"
            workflow.insert_node(geocode2, before = [aof3.id, aof4.id])

            # deburst
            deb2 = parse_node("TOPSAR-Deburst")
            workflow.insert_node(deb2, before = geocode2.id)

            merge_list.append(deb2.id)
        # check IW3, empty?
        if processing_dict["IW3"]["max_sce"] is None or processing_dict["IW3"]["max_ref"] is None:
            print("[PROCESSING IW3]: No bursts needed from IW3")
        else:
            print("[PROCESSING IW3]: ", processing_dict["IW3"])
            # TopSAR Split
            split5 = parse_node("TOPSAR-Split")
            split5.parameters["subswath"] = "IW3"
            split5.parameters["selectedPolarisations"] = ["VV", "VH"]
            split5.parameters["firstBurstIndex"] = processing_dict["IW3"]["min_ref"]
            split5.parameters["lastBurstIndex"] = processing_dict["IW3"]["max_ref"]
            workflow.insert_node(split5, before = read.id, resetSuccessorSource = False)

            # TopSAR Split 2
            split6 = parse_node("TOPSAR-Split")
            split6.parameters["subswath"] = "IW3"
            split6.parameters["selectedPolarisations"] = ["VV", "VH"]
            split6.parameters["firstBurstIndex"] = processing_dict["IW3"]["min_sce"]
            split6.parameters["lastBurstIndex"] = processing_dict["IW3"]["max_sce"]
            workflow.insert_node(split6, before = read2.id, resetSuccessorSource = False)

            # apply orbit file 1
            aof5 = parse_node("Apply-Orbit-File")
            aof5.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
            aof5.parameters["polyDegree"] = 3
            aof5.parameters["continueOnFail"] = continueOnFailAOF
            workflow.insert_node(aof5, before = split5.id)

            # apply orbit file 2
            aof6 = parse_node("Apply-Orbit-File")
            aof6.parameters["orbitType"] = "Sentinel Restituted (Auto Download)"
            aof6.parameters["polyDegree"] = 3
            aof6.parameters["continueOnFail"] = continueOnFailAOF
            workflow.insert_node(aof6, before = split6.id)

            # Back-Geocoding
            geocode3 = parse_node("Back-Geocoding")
            geocode3.parameters["demName"] = "SRTM 1Sec HGT"
            workflow.insert_node(geocode3, before = [aof5.id, aof6.id])

            # deburst
            deb3 = parse_node("TOPSAR-Deburst")
            workflow.insert_node(deb3, before = geocode3.id)

            merge_list.append(deb3.id)
            
        if len(merge_list) > 1:
            merge = parse_node("TOPSAR-Merge")
            workflow.insert_node(merge, before = merge_list)
            
            write = parse_node("Write")
            write.parameters["file"] = output_dir + out_filename
            write.parameters["formatName"] = "BEAM-DIMAP"
            workflow.insert_node(write, before = merge.id)
            
        elif len(merge_list) == 1:
            write = parse_node("Write")
            write.parameters["file"] = output_dir + out_filename
            write.parameters["formatName"] = "BEAM-DIMAP"
            workflow.insert_node(write, before = merge_list[0])

        workflow.write(output_dir + workflow_filename)

        groups = groupbyWorkers(output_dir + workflow_filename, n=1)
        gpt(output_dir + workflow_filename, groups = groups, tmpdir = './', gpt_args = ['-Dsnap.userdir=.', '-J-Xmx5G'])

        return groups