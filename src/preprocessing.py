#!/usr/bin/env python3

import sys
import sys, os
import pandas as pd
import geopandas as gpd
import datetime as dt
from util import list_days

if __name__ == "__main__":

    try:
        start = sys.argv[1] # start date of processing
        end = sys.argv[2] # dt.datetime.strptime(sys.argv[2], "%d/%m/%Y") # end date of processing
        export_path = sys.argv[3] # directory to write output to
        progress_file = sys.argv[4] # file that contains the processing progress
        ref_bursts_file = sys.argv[5] # file containing the reference bursts
        print(start)
    except IndexError:
        print("[ERROR]: There should be the following input: start (YYYY/mm/dd), end (YYYY/mm/dd), export_path, progress_file, ref_bursts_file")
        sys.exit(1)
        
    prod_list = list_products_by_time(start, end)
        
# step 1: list terrascope S1 products between start and end dates

def list_products_by_time(start, end, path: str = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/"):
    """This function returns an array of paths of S1 SLC products.
    
    The search is temporal and oriented at the TERRASCOPE folder structure.
    :param start: start time of search in YYYY/mm/dd
    :param end: end of search in YYYY/mm/dd
    :param path: path of directory with the scenes
    """
    s_month = int(start[5:7])
    e_month = int(end[5:7])
    s_day = int(start[8:])
    e_day = int(end[8:])

    start_folder = path + start[0:7] # year and month, no /
    end_folder = path + end[0:7]

    # if only in one month
    if s_month == e_month:
        start_folder_days = os.listdir(start_folder)[s_day-1:e_day] # list days, from start day : end day
        list_of_products = list_days(list_of_days = start_folder_days, month_path = start_folder)
    # no in between month
    elif s_month + 1 == e_month:
        start_folder_days = os.listdir(start_folder)[s_day-1:] # list days, from start day
        # print(start_folder , "\n" , s_day , "\n" , s_day-1 , "\n" , os.listdir(start_folder) , "\n" , start_folder_days)
        end_folder_days = os.listdir(end_folder)[:e_day]
        list_of_products = list_days(start_folder_days, start_folder) + list_days(end_folder_days, end_folder)
    # with month in between
    elif s_month +1 < e_month:
        start_folder_days = os.listdir(start_folder)[s_day-1:]
        end_folder_days = os.listdir(end_folder)[:e_day]
        list_of_products = list_days(start_folder_days, start_folder) + list_days(end_folder_days, end_folder)

        for i in range(s_month+1,e_month):
            if i < 10:
                month = "0" + str(i)
            elif i >= 10:
                month = str(i)

            month_path = os.path.join(path, start[0:5], month)
            month_days_list = os.listdir(month_path)
            month_prod_list = list_days(month_days_list, month_path)
            list_of_products.extend(month_prod_list)
        
    return list_of_products

# step 2: make a gpd of these scenes / add them to an existing gpd + check if they have been processed