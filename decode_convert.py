import glob
import os
import time
import numpy as np
from decode import unpack_simba_v8_09_sbd, convertT2nc

# defining the IMEI of the instrument
# to create directories and filenames
imei = "300340657110080"
datapath = "/storage/common/buoy-data/get-buoy-data/" + imei + "/"
path = "/storage/common/buoy-data/convert-buoy-data/"
# last_access stores the time this script was last run
last_access_path = path + "last_access"
ncdatapath = path + imei + ".nc"
# check if the file last_access exists, if not last_access=0
# and all files the from the instrument with the IMEI will be processed 
if os.path.isfile(last_access_path):
    with open(last_access_path, "rb") as f:
        last_access = float(f.read())
    f.close()
else:
    last_access = 0
# store time of this access
access_time = time.time()
# get all filenames that correspond to the IMEI provided
filelist = sorted(glob.glob(datapath + "*" + imei + "*.sbd"))
# get times of last modification of each of those files
times = [os.path.getmtime(filelist[i]) for i in range(0, len(filelist))]
# only keep filenames in the list that have been create/modified
# after the last_access
openlist = np.array(filelist)[np.array(times)>last_access]
ncname = ncdatapath
# print a statement if no files are in that list
# otherwise run the decoding script
if len(openlist)==0:
    print("No data found to be added to " + str(ncname))
else:
    print("Processing " + str(len(openlist)) + " new files")
    ds = convertT2nc(openlist, ncname)
# write the time of this access to a file
with open(last_access_path, "w") as f:
    f.write(str(access_time))
f.close()

