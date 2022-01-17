from terracatalogueclient import Catalogue
import datetime as dt
import glob
import pandas as pd
import geopandas as gpd
import sys, os

from util import suppress_stdout, create_gpd_for_scene, save_new_bursts

def create_reference_scene_json(start, end, aoi_file: str, ref_bursts_file: str = ""):
    """Create a GeoJSON that contains a set of Sentinel 1 reference scenes that are needed as common coregister-references.
    
    This function employs some tests to make sure every individual scene is only covered once. 
    However the file coming out of this should be checked one in a while.
    
    :param start: The start time of the search
    :param end: The end time of the search
    :param aoi_file: AOI geojson file to limit the scenes
    :param ref_bursts_file: existing .geojson file with reference scenes
    """
    
    # input checks
    if not start - end == dt.timedelta(days = 12):
        print("[CAUTION]: For full coverage, a 12 day timedelta is recommended. Timedelta: ", start-end)
    elif (start - end) > dt.timedelta(days = 12):
        # This is a pattern to avoid: `print("error") + return None`, this will cause a lot of problems down the road.
        # just throw an exception
        raise ValueError("the 'timedetla > 12' case is not covered here")

    # Same here: throw an exception instead. You can even use `assert`, which saves you an `if`.
    # Moreover: gpd.read_file is probably going to complain anyway, so you don't have to do the checking in the first place
    assert os.path.isfile(aoi_file)
    aoi = gpd.read_file(aoi_file)

    if os.path.isfile(ref_bursts_file):
        ref_bursts = gpd.read_file(ref_bursts_file)
        create_new_file = False
    else:
        print("ref_bursts_file not found")
        create_new_file = True

    print("starting search for scenes...")

    catalogue = Catalogue()

    cat = catalogue.get_products(
        "urn:eop:VITO:CGS_S1_SLC_L1",
        start = start,
        end = end
        # , geometry =  WKT string or shapely geom
    )

    new_bursts = []

    for p in cat:
        # construct the path from the hyperlink
        path = p.data[0].href 
        iw_index = path.index("IW")
        vm_path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]

        # make swath geometry and add basic info to df
        scene_bursts = create_gpd_for_scene(vm_path, make_regular = True)

        # append to list based on satellite
        if scene_bursts["sensor"].iloc[0] == "S1A":

            # AOI INTERSECTION
            # create boolean of which bursts intersect with aoi and which dont
            intersects = scene_bursts.intersects(aoi.iloc[0]["geometry"])
            # keep only those bursts that intersect with aoi
            intersecting_bursts = scene_bursts[intersects]

            if not intersecting_bursts.empty:

                # if a file already exists
                if not create_new_file:

                    # CHECK IF EXISTS ALREADY
                    rel_o = intersecting_bursts.iloc[0]["rel_orbit"]
                    o_dir = intersecting_bursts.iloc[0]["orbit_direction"]
                    # search in existing table for bursts of the same relative orbit and orbit direction
                    check = ref_bursts.loc[(ref_bursts["rel_orbit"] == rel_o) & (ref_bursts["orbit_direction"] == o_dir)]
                    # if some are found:
                    if not check.empty:
                        # intersect with the new bursts
                        intersec = gpd.overlay(intersecting_bursts, check, how = "intersection") # .to_file("intersection_test_" + scene_bursts.iloc[0]["id"] + ".geojson", driver = "GeoJSON")
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

                # If the overlap is bigger, the scenes are already in the dataset
                if ratio < 0.9:
                    new_bursts.append(intersecting_bursts)

    # when new bursts are found
    if not create_new_file:
        save_new_bursts(new_bursts = new_bursts, create_new_file = create_new_file, old_gpd = ref_bursts,
                        filename = "reference_bursts.geojson", save_as_scenes = True, 
                        scenes_filename = "reference_scenes.geojson")
    else:
        save_new_bursts(new_bursts = new_bursts, create_new_file = create_new_file,
                        filename = "reference_bursts.geojson", save_as_scenes = True, 
                        scenes_filename = "reference_scenes.geojson")
    return


# a relative frame number is given, not yet sure how useful that is
# create empty dictionairy for the mapping ID - frame number
# relative_frames = {}
# initiate column
# new_bursts_df["rel_frame"] = 0
# init frame number
# fnr = int(1)

# TODO heard that iterrows() is slow, not sure how I could improve here
# for index, row in new_bursts_df.iterrows():
#     if row["id"] in relative_frames:
#         new_bursts_df.at[index, "rel_frame"] = relative_frames[row["id"]]
#     else:
#         new_bursts_df.at[index, "rel_frame"] = fnr
#         relative_frames[row["id"]] = fnr
#         fnr += 1

# input time frame in which reference scenes should be defined
# this should be no longer than 12 days! after 12 days, orbits of a single satellite repeat and ambiguities arise
# My use case was to collect the base scenes from 1.10 - 12.10.2021, and to add some scenes over france from oct 2020 later on

# Avoid putting these settings at the top level of the file, at least put them under `if __name__ == "__main__":`

start = dt.date(2021, 10, 1)
end = dt.date(2021, 10, 13)
ref_bursts_file = "/home/jonathanbahlmann/Public/coherence-docs/src/reference_bursts.geojson"
aoi_file = "/home/jonathanbahlmann/Public/coherence-docs/aoi/belgium_france.geojson"

# usage
create_reference_scene_json(start = start, end = end, aoi_file = aoi_file, ref_bursts_file = ref_bursts_file)
