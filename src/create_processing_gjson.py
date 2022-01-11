#!/usr/bin/env python3

import sys
import sys, os
import pandas as pd
import geopandas as gpd
import datetime as dt
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