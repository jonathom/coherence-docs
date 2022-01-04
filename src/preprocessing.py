#!/usr/bin/env python3

import sys
import sys, os
import pandas as pd
import geopandas as gpd

if __name__ == "__main__":

    try:
        start = sys.argv[1] # start date of processing
        end = sys.argv[2] # end date of processing
        export_path = sys.argv[3] # directory to write output to
        progress_file = sys.argv[4] # file that contains the processing progress
        ref_bursts_file = sys.argv[5] # file containing the reference bursts
        
    except IndexError:
        print("[ERROR]: There should be the following input: start, end, export_path, progress_file, ref_bursts_file")
        sys.exit(1)