#!/bin/bash
# to be run each day, checking for new sbd data,
# converting it from binary and saving to netcdf
echo "---------- decode_convert.sh -----------"
echo " "
date

# load conda environment
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate /opt/anaconda3/envs/buoy-data

# run python script to decode and convert data
python3 /storage/common/buoy-data/convert-buoy-data/decode_convert_300534065720080/decode_convert.py
