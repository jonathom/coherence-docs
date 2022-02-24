#!/usr/bin/env python3

import sys, os
import pandas as pd
import geopandas as gpd
import datetime as dt
from util import *

# call via create_processing_gjson.py "2021/09/05" "2021/09/07"
# or by    create_processing_gjson.py "2021/09/05" "2021/09/07" "reference_bursts.geojson" "processing.geojson"

def main(start, end, ref_bursts_file="reference_bursts.geojson", prod_file="processing.geojson"):
    # step 1: list terrascope S1 products between start and end dates
    products = list_products_by_time(start, end)
    # step 2: make a gpd of these scenes / add them to an existing gpd + check if they have been processed
    process_geojson(products=products, prod_file=prod_file, ref_bursts_file=ref_bursts_file)


if __name__ == "__main__":
    main(*sys.argv[1:])