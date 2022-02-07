def processing_geojson_as_array(bursts_to_process):
    
    import geopandas as gpd
    # load bursts we want to process
    # bursts_to_process = gpd.read_file("/data/users/Public/jonathanbahlmann/coherence-docs/src/processing.geojson")
    # go per scene to process, dissolve to extract ids
    combinations = bursts_to_process.dissolve(["id", "subswath", "ref_scene"], as_index = False)
    return [v for k, v in combinations.loc[:,["id", "ref_scene", "subswath", "sce_min_burst", "sce_max_burst", "ref_min_burst", "ref_max_burst", "processing_status", "path", "ref_path"]].groupby(['id', "ref_scene"])]