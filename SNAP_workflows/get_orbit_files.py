# download orbit files manually if some sort of orbit file error occurs
# osvdir needs to be changed to the local place for osv files, should be similar
from pyroSAR.S1 import OSV
import os

osvdir = "/home/jonathanbahlmann/Public/coherence-docs/.snap/auxdata/Orbits/Sentinel-1"

with OSV(osvdir) as osv:
    files = osv.catch(sensor="S1B", osvtype="POE",
    start="20211001T000000", stop="20211031T000000") #define dates here
    osv.retrieve(files)

with OSV(osvdir) as osv:
    files = osv.catch(sensor="S1A", osvtype="POE",
    start="20211001T000000", stop="20211031T000000") #define dates here
    osv.retrieve(files)
