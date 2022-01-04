from terracatalogueclient import Catalogue
import datetime as dt
import glob
import pandas as pd
import geopandas as gpd
import sys, os

from util import suppress_stdout, create_gpd_for_scene

def create_reference_scene_json(start, end, aoi_file: str = None, bursts_file: str = None):
    """Create a GeoJSON that contains a set of Sentinel 1 reference scenes that are needed as common coregister-references.
    
    This function employs some tests to make sure every individual scene is only covered once. 
    However the file coming out of this should be checked one in a while.
    
    :param start: The start time of the search
    :param end: The end time of the search
    :param aoi_file: AOI file to limit the search
    :param bursts_file: existing .geojson file with reference scenes
    """
    
    # input checks
    timediff = start - end
    if not timediff == dt.timedelta(-12):
        print("[CAUTION]: For full coverage, a 12 day timedelta is needed.")
    
    if os.path.isfile(aoi_file):
        aoi = gpd.read_file(aoi_file)
    else:
        print("[ERROR]: no aoi_file given")
        return
    
    ref_inter_bursts_file = bursts_file
    if os.path.isfile(ref_inter_bursts_file):
        ref_inter_bursts = gpd.read_file(ref_inter_bursts_file)
        create_new_file = False
    else:
        print("ref_inter_bursts_file not found")
        create_new_file = True

    print("starting search for scenes...")

    catalogue = Catalogue()

    cat = catalogue.get_products(
        "urn:eop:VITO:CGS_S1_SLC_L1",
        start = start,
        end = end
        # , geometry =  WKT string or shapely geom
    )

    s1a = []

    for p in cat:
        path = p.data[0].href 
        iw_index = path.index("IW")
        vm_path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]

        # make swath geometry and add basic info to df
        ana_split = create_gpd_for_scene(vm_path, make_regular = True)

        # append to list based on satellite
        if ana_split["sensor"].iloc[0] == "S1A":

            # AOI INTERSECTION
            # create boolean of which bursts intersect with aoi and which dont
            intersects = ana_split.intersects(aoi.iloc[0]["geometry"])
            # keep only those bursts that intersect with aoi
            intersecting_bursts = ana_split[intersects]

            if not intersecting_bursts.empty:

                # CHECK IF EXISTS
                rel_o = intersecting_bursts.iloc[0]["rel_orbit"]
                o_dir = intersecting_bursts.iloc[0]["orbit_direction"]

                # if a file already exists
                if not create_new_file:
                    # search in existing table for bursts of the same relative orbit and orbit direction
                    check = ref_inter_bursts.loc[(ref_inter_bursts["rel_orbit"] == rel_o) & (ref_inter_bursts["orbit_direction"] == o_dir)]
                    # if some are found:
                    if not check.empty:
                        # intersect with the new bursts
                        intersec = gpd.overlay(intersecting_bursts, check, how = "intersection") # .to_file("intersection_test_" + ana_split.iloc[0]["id"] + ".geojson", driver = "GeoJSON")
                        intersec["area"] = intersec.to_crs({'init': 'epsg:32631'}).area
                        # calculate the overall intersecting area
                        intersec_area = intersec["area"].sum()
                    else:
                        # if none are found, intersecting area is 0
                        intersec_area = 0

                    # calculate area of new bursts
                    new_scene_area = intersecting_bursts.to_crs({'init': 'epsg:32631'}).area.sum()
                    # calculate ratio between the two areas
                    ratio = intersec_area / new_scene_area

                # otherwise add all, of course
                else:
                    ratio = 0

                if ratio < 0.9:
                    s1a.append(intersecting_bursts)

    if s1a:
        s1a_df = gpd.GeoDataFrame(pd.concat(s1a, ignore_index = True), crs=s1a[0].crs)

        # if a file exists, add to it and rewrite
        if not create_new_file:
            print(len(s1a_df), " bursts added.")
            s1a_df = ref_inter_bursts.append(s1a_df, sort = False)
        else:
            print(len(s1a_df), " bursts found.")

        # create empty dictionairy for the mapping ID - frame number
        relative_frames = {}
        # initiate column
        s1a_df["rel_frame"] = 0
        # init frame number
        fnr = int(1)

        # TODO heard that iterrows() is slow, not sure how I could improve here
        for index, row in s1a_df.iterrows():
            if row["id"] in relative_frames:
                s1a_df.at[index, "rel_frame"] = relative_frames[row["id"]]
            else:
                s1a_df.at[index, "rel_frame"] = fnr
                relative_frames[row["id"]] = fnr
                fnr += 1

        # write bursts
        s1a_df.to_file("reference_bursts.geojson", driver = "GeoJSON")
        # extract scenes and write
        s1a_df.dissolve(["id"], as_index = False).to_file("reference_scenes.geojson", driver = "GeoJSON")

    elif not s1a:
        print("nothing added")
    else:
        print("error")

    # gpd.overlay(aoi, s1a_df, how = "intersection").to_file("test2.geojson", driver = "GeoJSON")

    print("end")
    return



# input time frame in which reference scenes should be defined
# this should be no longer than 12 days! after 12 days, orbits of a single satellite repeat and ambiguities arise
# My use case was to collect the base scenes from 1.10 - 12.10.2021, and to add some scenes over france from oct 2020 later on
start = dt.date(2020, 10, 1)
end = dt.date(2020, 10, 13)
bursts_file = "/home/jonathanbahlmann/Public/coherence-docs/src/reference_bursts.geojson"
aoi_file = "/home/jonathanbahlmann/Public/coherence-docs/aoi/belgium_france.geojson"

# usage
# create_reference_scene_json(start = start, end = end, aoi_file = aoi_file, bursts_file = bursts_file)