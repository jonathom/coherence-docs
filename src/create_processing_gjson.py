#!/usr/bin/env python3

# It seems like a lot of these imports are unused
import sys, os
import pandas as pd
import geopandas as gpd
import datetime as dt

# In general, avoid doing "import *", it makes it harder to track where functions/classes are coming from

# Also, it's risky to use the very generic "util" as module name for your own imports:
# very high risk to collide with something complete different but with the same name.
# Quick solution: rename "util.py" to something less generic (e.g. prefix it short project name)
# More elaborate solution: make the whole project an installable package, so that submodules can be imported in a more standard way
from util import *

# call via create_processing_gjson.py "2021/09/05" "2021/09/07"
# or by    create_processing_gjson.py "2021/09/05" "2021/09/07" "reference_bursts.geojson" "processing.geojson"

if __name__ == "__main__":


    try:
        start = sys.argv[1] # start date of processing
        end = sys.argv[2] # dt.datetime.strptime(sys.argv[2], "%d/%m/%Y") # end date of processing
    except IndexError:
        print("[ERROR]: There should be the following input: start (YYYY/mm/dd), end (YYYY/mm/dd), export_path, progress_file, ref_bursts_file")
        sys.exit(1)
    try:
        ref_bursts_file = sys.argv[3] # file containing the reference bursts
    except IndexError:
        ref_bursts_file = "reference_bursts.geojson"
    try:
        prod_file = sys.argv[4]
    except IndexError:
        prod_file = "processing.geojson"

    # step 1: list terrascope S1 products between start and end dates
    products = list_products_by_time(start, end)
    # step 2: make a gpd of these scenes / add them to an existing gpd + check if they have been processed
    process_geojson(products = products, prod_file = prod_file, ref_bursts_file = ref_bursts_file)


# Just a tip: see https://www.stefaanlippens.net/simple-cli-argument-handling-in-python/
# for quick and compact command line handling.
# In this case the whole script could just be something like:

def main(start, end, ref_bursts_file="reference_bursts.geojson", prod_file="processing.geojson"):
    # step 1: list terrascope S1 products between start and end dates
    products = list_products_by_time(start, end)
    # step 2: make a gpd of these scenes / add them to an existing gpd + check if they have been processed
    process_geojson(products=products, prod_file=prod_file, ref_bursts_file=ref_bursts_file)


if __name__ == "__main__":
    main(*sys.argv[1:])
