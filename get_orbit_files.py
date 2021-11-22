from pyroSAR.S1 import OSV
import os

osvdir = "/home/petra/Praktikum_VITO/pyroSAR/osv_files"

with OSV(osvdir) as osv:
    files = osv.catch(sensor="S1B", osvtype="POE",
    start="20211001T000000", stop="20211031T000000") #define dates here
    osv.retrieve(files)

with OSV(osvdir) as osv:
    files = osv.catch(sensor="S1A", osvtype="POE",
    start="20211001T000000", stop="20211031T000000") #define dates here
    osv.retrieve(files)