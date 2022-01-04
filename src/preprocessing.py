#!/usr/bin/env python3

import sys
import sys, os
import pandas as pd
import geopandas as gpd
import datetime as dt

if __name__ == "__main__":

    try:
        start = dt.datetime.strptime(sys.argv[1], "%d/%m/%Y") # start date of processing
        end = dt.datetime.strptime(sys.argv[2], "%d/%m/%Y") # end date of processing
        export_path = sys.argv[3] # directory to write output to
        progress_file = sys.argv[4] # file that contains the processing progress
        ref_bursts_file = sys.argv[5] # file containing the reference bursts
        print(start)
    except IndexError:
        print("[ERROR]: There should be the following input: start (dd/mm/YYYY), end (dd/mm/YYYY), export_path, progress_file, ref_bursts_file")
        sys.exit(1)
        
# step 1: list terrascope S1 products between start and end dates

# build paths for the days in that period

product_list = 