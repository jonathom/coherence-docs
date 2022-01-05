from pyroSAR import identify
import stsa
import pandas as pd
import geopandas as gpd
import sys, os
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
            
            
def create_gpd_for_scene(path: str = None, name: str = None, id: str = None, make_regular: bool = False):
    """Create a geopandas dataframe for a S1 scene.
    
    Metadata is read using pyroSAR. Creates the gpd using stsa.
    A gpd with all bursts is returned.
    
    :param path: Path to the scene
    :param name: ESA SAFE format product name of the scene
    :param id: 4-letter identifier of the scene
    :param make_regular: when true, additional bursts are deleted from the df
    """
    if name is None:
        name = path[path.rfind("/")+1:len(path)-4]
        
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

    return(stsa_geom)

# a quick test
# df = create_gpd_for_scene(path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/10/03/S1A_IW_SLC__1SDV_20211003T173237_20211003T173305_039958_04BAA1_14F6/S1A_IW_SLC__1SDV_20211003T173237_20211003T173305_039958_04BAA1_14F6.zip", make_regular = True)
    
def list_days(list_of_days, month_path):
    all_file_list = []
    for day in list_of_days:
        file_list = glob.glob(os.path.join(month_path, day) + "/*/*.zip")
        all_file_list.extend(file_list)
    return all_file_list