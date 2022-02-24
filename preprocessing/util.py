from pyroSAR import identify
import stsa
import pandas as pd
import geopandas as gpd
import sys, os
from pathlib import Path
import datetime
import glob
from contextlib import contextmanager

@contextmanager
def suppress_stdout():
    """Suppress functions from writing output to stdout. 
    Especially stsa functions write unnecessary output.
    source http://thesmithfam.org/blog/2012/10/25/temporarily-suppress-console-output-in-python/
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout
            
            
def create_gpd_for_scene(path: str, name: str = None, id: str = None, make_regular: bool = False) -> gpd.GeoDataFrame:
    """Create a geopandas dataframe for a S1 scene.
    
    Metadata is read using pyroSAR. Creates the gpd using stsa.
    A gpd with all bursts is returned.
    
    :param path: Path to the scene
    :param name: ESA SAFE format product name of the scene
    :param id: 4-letter identifier of the scene
    :param make_regular: when true, additional bursts are deleted from the df
    """
    if name is None:
        name = Path(path).stem
        
    if id is None:
        id = name[len(name)-4:len(name)]        
    
    # use pyroSAR to extract metadata
    pyro = identify(path)

    # use stsa to create swath geometry
    stsa_geom = stsa.TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'])
    with suppress_stdout():
        stsa_geom.load_data(zip_path = path)
        stsa_geom._create_subswath_geometry()

    # add attributes to bursts
    stsa_geom = stsa_geom.df
    stsa_geom["id"] = id
    stsa_geom["name"] = name
    stsa_geom["path"] = path
    stsa_geom["sensor"] = pyro.sensor
    stsa_geom["polarizations"] = ','.join(str(e) for e in pyro.polarizations)
    stsa_geom["start"] = pyro.start
    stsa_geom["stop"] = pyro.stop
    stsa_geom["mode"] = pyro.acquisition_mode
    stsa_geom["product"] = pyro.product
    stsa_geom["orbit_direction"] = pyro.orbit
    stsa_geom["rel_orbit"] = pyro.orbitNumber_rel
    
    reg_burst_pattern = [1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,9]

    if make_regular:
        # leave out additional bursts, however missing bursts will not be replaced and flagged accordingly
        # this corrects only for max 1 extra burst..
        if pyro.orbit == "D":
            # allow a 10th burst, needed in vis inspection
            stsa_geom = stsa_geom.loc[stsa_geom["burst"] < 11]
        elif pyro.orbit == "A":
            liw1 = len(stsa_geom.loc[stsa_geom["subswath"] == "IW1"])
            if liw1 != 9:
                print("scene ", id, ", IW1, has ", liw1, " bursts.")  
            liw2 = len(stsa_geom.loc[stsa_geom["subswath"] == "IW2"])
            if liw2 != 9:
                print("scene ", id, ", IW2, has ", liw2, " bursts.")
            liw3 = len(stsa_geom.loc[stsa_geom["subswath"] == "IW3"])
            if liw3 != 9:
                print("scene ", id, ", IW3, has ", liw3, " bursts.")
            # TODO cut only from subswath where the extra bursts lie
        else:
            print("create_gpd_for_scene: incorrect orbit given.")
        
    # check whether the scene has a regular burst pattern (no missing, no additional bursts)
    if stsa_geom.loc[:,"burst"].to_list() == [1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,9]:
        stsa_geom["regular_burst_pattern"] = 1
    else:
        # print(path)
        # print(stsa_geom.loc[:,"burst"].to_list())
        stsa_geom["regular_burst_pattern"] = 0

    return stsa_geom

# a quick test
# df = create_gpd_for_scene(path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/10/03/S1A_IW_SLC__1SDV_20211003T173237_20211003T173305_039958_04BAA1_14F6/S1A_IW_SLC__1SDV_20211003T173237_20211003T173305_039958_04BAA1_14F6.zip", make_regular = True)


def search_for_reference(scene_gpd, ref_gpd, ref_sensor: str = "S1A", epsg: int = 32631) -> list:
    """This function searches for the set of eligible reference scenes for coregistration.
    
    If no scene is found, something is off.
    If one scene is found, it should be from the same sensor.
    If two scenes are found, it should be a different sensor.
    :param scene_gpd: gpd of scene to search a reference for
    :param ref_gpd: gpd with reference bursts
    :param ref_sensor: sensor of ref_gpd
    :param epsg: EPSG CRS to convert to for area calculation
    """
    epsg_str = 'epsg:' + str(epsg)
    
    scene_gpd = scene_gpd.dissolve("subswath", as_index = False)
    # scene_gpd.to_file("scene_gpd_check_" + str(scene_gpd.iloc[0]["id"]) + ".geojson", driver = "GeoJSON")
    scene_sensor = scene_gpd.iloc[0]["sensor"]
    rel_o = scene_gpd.iloc[0]["rel_orbit"]
    o_dir = scene_gpd.iloc[0]["orbit_direction"]
    # search in existing table for bursts of the same relative orbit and orbit direction
    ref_gpd_same_orbit = ref_gpd.loc[(ref_gpd["rel_orbit"] == rel_o) & (ref_gpd["orbit_direction"] == o_dir)]
    
    # if scenes from the same orbit are found
    if not ref_gpd_same_orbit.empty:
        ref_gpd_same_orbit = ref_gpd_same_orbit.dissolve(["id", "subswath"], as_index = False)
        
    # calculate intersection
    intersection = gpd.overlay(ref_gpd_same_orbit, scene_gpd, how = "intersection") # so id_1 is different each intersection
    
    if not intersection.empty:
        
        intersection["area"] = intersection.to_crs({'init': epsg_str}).area

        # intersection.to_file("intersection" + str(intersection.iloc[0]["id_2"]) + ".geojson", driver="GeoJSON")

    
        if scene_sensor == ref_sensor:
            # only one scene needs to be found, which is the one with biggest overlap
            area_max = intersection["area"].idxmax()
            # return id of that scene
            return [intersection.iloc[area_max]["id_1"]]
        else:
            # 
            print(intersection[["id_2", "subswath_2", "burst_2", "area", "id_1", "subswath_1", "burst_1"]])
            burst_size = 1800000000.0
            # filter intersection for geometries larger or equal to the size of a single burst
            intersection = intersection.loc[intersection["area"] > burst_size]
            # make set of id_1 column
            ids = set(intersection["id_1"].array)
            return list(ids)
            # 1.825593e+09 is in
            # 2.075e-09 is in, 1.569e-09 (full subswath side intersection) is out
            # 1.814e-09 is in, one burst, same sensor
            
    # when no intersection, return empty array
    else:
        return[]
    
    
def save_new_bursts(new_bursts, create_new_file: bool, filename,
                    old_gpd = None, save_as_scenes: bool = False, scenes_filename: str = None):
    """A function to save a gpd of bursts.
    
    Adding to a new file when create_new_file is True, saving to new file if not.
    :param new_bursts: gpd of bursts to be added, may be empty
    :param create_new_file: bool of whether to make a new file
    :param old_gpd: optional, gpd to add the new bursts to
    :param filename: filename of old or new file
    :param save_as_scenes: should the gpd be dissolved into scenes?
    :param scenes_filename: give filename for probable scenes file
    """
    
    # when new bursts are found
    if new_bursts:
        new_bursts_df = gpd.GeoDataFrame(pd.concat(new_bursts, ignore_index = True), crs=new_bursts[0].crs)

        # if a file exists, add to it and rewrite
        if not create_new_file:
            print(len(new_bursts_df), " bursts added.")
            new_bursts_df = old_gpd.append(new_bursts_df, sort = False)
        else:
            print(len(new_bursts_df), " bursts found.")

        # write bursts
        new_bursts_df.to_file(filename, driver = "GeoJSON")
        if save_as_scenes:
            # extract scenes and write
            new_bursts_df.dissolve(["id"], as_index = False).to_file(scenes_filename, driver = "GeoJSON")

    elif not new_bursts:
        print("nothing added")
    else:
        raise RuntimeError("save_new_bursts: new_bursts unclear.")

    print("[INFO]: Done looking for new scenes.")


def list_products_by_time(start, end, path: str = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/") -> list:
    """This function returns an array of paths of S1 SLC products. The search is right-closed,
    i.e. to get one day yone must enter day, day+1
    
    The search is temporal and oriented at the TERRASCOPE folder structure.
    :param start: start time of search in YYYY/mm/dd
    :param end: end of search in YYYY/mm/dd
    :param path: path of directory with the scenes
    """
    start_date = datetime.datetime.strptime(start, "%Y/%m/%d")
    end_date = datetime.datetime.strptime(end, "%Y/%m/%d")

    # Using pathlib.Path as well for more robust path handling and walking
    root = Path(path)
    start_dir = str(root / start_date.strftime("%Y/%m/%d"))
    end_dir = str(root / end_date.strftime("%Y/%m/%d"))

    list_of_products = []
    for year in range(start_date.year, end_date.year + 1):
        year_path = Path(path) / str(year)
        for day_dir in year_path.glob("[01][0123456789]/[0123][0123456789]"):
            if start_dir <= str(day_dir) < end_dir:
                list_of_products.extend(day_dir.glob("*/*.zip"))
        
    return list_of_products


def search_for_reference(scene_gpd, ref_gpd, ref_sensor: str = "S1A", epsg: int = 32631) -> dict:
    """This function searches for the set of eligible reference scenes for coregistration.
    
    If no scene is found, something is off.
    If one scene is found, it should be from the same sensor.
    If two scenes are found, it should be a different sensor.
    :param scene_gpd: gpd of scene to search a reference for
    :param ref_gpd: gpd with reference bursts
    :param ref_sensor: sensor of ref_gpd
    :param epsg: EPSG CRS to convert to for area calculation
    :return: A dict is returned that contains the found reference scenes IDs as keys, with an array of the applicable subswaths as values.
    """
    epsg_str = 'epsg:' + str(epsg)
    
    scene_gpd = scene_gpd.dissolve("subswath", as_index = False)
    # scene_gpd.to_file("scene_gpd_check_" + str(scene_gpd.iloc[0]["id"]) + ".geojson", driver = "GeoJSON")
    scene_sensor = scene_gpd.iloc[0]["sensor"]
    rel_o = scene_gpd.iloc[0]["rel_orbit"]
    o_dir = scene_gpd.iloc[0]["orbit_direction"]
    # search in existing table for bursts of the same relative orbit and orbit direction
    ref_gpd_same_orbit = ref_gpd.loc[(ref_gpd["rel_orbit"] == rel_o) & (ref_gpd["orbit_direction"] == o_dir)]
    
    # if scenes from the same orbit are found
    if not ref_gpd_same_orbit.empty:
        ref_gpd_same_orbit = ref_gpd_same_orbit.dissolve(["id", "subswath"], as_index = False)
        
        # calculate intersection
        intersection = gpd.overlay(ref_gpd_same_orbit, scene_gpd, how = "intersection") # so id_1 is different each intersection

        if not intersection.empty:

            intersection["area"] = intersection.to_crs({'init': epsg_str}).area

            # intersection.to_file("intersection" + str(intersection.iloc[0]["id_2"]) + ".geojson", driver="GeoJSON")

            # filter intersection for geometries larger or equal to the size of a single burst
            burst_size = 1800000000.0
            intersection = intersection.loc[intersection["area"] > burst_size]
            
            if not intersection.empty:

                if scene_sensor == ref_sensor:
                    #intersection.to_file("intersection.geojson", driver=  "GeoJSON")
                    #scene_gpd.to_file("scene_gpd.geojson", driver="GeoJSON")
                    # intersection should now contain only one specific id_1
                    # print(intersection[["id_2", "subswath_2", "burst_2", "area", "id_1", "subswath_1", "burst_1"]])
                    subs = set(intersection["subswath_1"].array)
                    return {intersection.iloc[0].loc["id_1"]: list(subs)}
                else:
                    # print(intersection[["id_2", "subswath_2", "burst_2", "area", "id_1", "subswath_1", "burst_1"]])            
                    # make set of id_1 column
                    ids = set(intersection["id_1"].array)
                    # search for each id for involved subswaths
                    subs_dict = {}
                    for id in ids:
                        subs = intersection.loc[intersection["id_1"] == id]["subswath_1"].array
                        # in intersection, burst info is lost..
                        subs_dict[id] = list(subs)
                    # print(subs_dict)
                    return subs_dict
                    # 1.825593e+09 is in
                    # 2.075e-09 is in, 1.569e-09 (full subswath side intersection) is out
                    # 1.814e-09 is in, one burst, same sensor
                    
            else:
                return {}
            
    # when no intersection, return empty dict
    else:
        return {}


def process_geojson(products, prod_file: str, ref_bursts_file: str, epsg_str: str = "epsg:32631"):

    if os.path.isfile(prod_file):
        prod_gpd = gpd.read_file(prod_file)
        print(prod_file, " contains ", len(prod_gpd.index), " bursts.")
        create_new_file = False
    else:
        print("prod_file not found")
        create_new_file = True

    ref_bursts = gpd.read_file(ref_bursts_file)

    new_bursts = []

    for path in products:
        # convert back to string
        abs_path = path.absolute()
        path = abs_path.as_posix()
        # make swath geometry and add basic info to df
        scene_bursts = create_gpd_for_scene(path)

        # search directly for ref scene
        ref_scene_dict = search_for_reference(scene_bursts, ref_bursts)

        # decide which bursts need to be processed!
        # iterate through subswaths of reference scenes
        if ref_scene_dict:
            # for each found reference scene
            for id in [*ref_scene_dict]:
                # for each subswath
                for subs in ref_scene_dict[id]:
                    # filter current scene and reference bursts for the current subswath
                    scene_bursts_subs = scene_bursts.loc[scene_bursts["subswath"] == subs]
                    ref_bursts_filtered = ref_bursts.loc[(ref_bursts["id"] == id) & (ref_bursts["subswath"] == subs)]
                    intersection = gpd.overlay(ref_bursts_filtered, scene_bursts_subs, how = "intersection")

                    # filter for those roughly big enough to represent a burst
                    intersection["area"] = intersection.to_crs({'init': epsg_str}).area
                    intersection = intersection.loc[intersection["area"] > 1000000000.0]

                    # define ranges
                    range_ref = [min(intersection["burst_1"]), max(intersection["burst_1"])]
                    range_sce = [min(intersection["burst_2"]), max(intersection["burst_2"])]
                    # print(intersection.iloc[0].loc["id_2"], "_", id, range_ref, range_sce)
                    ref_path = ref_bursts_filtered.dissolve(["id", "path"], as_index=False).iloc[0]["path"]

                    # add corresponding scene_bursts to new_bursts
                    rows = (scene_bursts["subswath"] == subs) & (scene_bursts["burst"] >= range_sce[0]) & (scene_bursts["burst"] <= range_sce[1])
                    
                    scene_bursts.loc[rows, "ref_scene"] = id
                    scene_bursts.loc[rows, "ref_min_burst"] = int(range_ref[0])
                    scene_bursts.loc[rows, "ref_max_burst"] = int(range_ref[1])
                    # write scene burst info as well
                    scene_bursts.loc[rows, "sce_min_burst"] = int(range_sce[0])
                    scene_bursts.loc[rows, "sce_max_burst"] = int(range_sce[1])
                    scene_bursts.loc[rows, "processing_status"] = 0
                    # also add path
                    scene_bursts.loc[rows, "ref_path"] = ref_path
                    
                    bursts_to_add = scene_bursts.loc[rows]

                    if create_new_file:
                        new_bursts.append(bursts_to_add)
                    else:
                        for burst in list(bursts_to_add.loc[:, "burst"]):
                            # test if burst in frame already
                            in_table = prod_gpd.loc[(prod_gpd["id"] == bursts_to_add.iloc[0].loc["id"]) & 
                                                    (prod_gpd["subswath"] == subs) & 
                                                    # convert to str, otherwise comparison is false
                                                    (prod_gpd["burst"] == str(burst))]                        
                            if in_table.empty:
                                new_bursts.append(bursts_to_add.loc[bursts_to_add["burst"] == burst])
                            else:
                                pass
        else:
            print("scene has no references")

    if create_new_file:
        save_new_bursts(new_bursts = new_bursts, create_new_file = create_new_file, 
                        filename = prod_file)
    else:
        save_new_bursts(new_bursts = new_bursts, create_new_file = create_new_file, 
                        filename = prod_file, old_gpd = prod_gpd)