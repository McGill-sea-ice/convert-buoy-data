# convert-buoy-data
Code to convert binary Iridium SBD files from SIMBA instruments into human-readable format.  
This code works for  
    *SAMS Enterprise Snow and Ice Mass Balance Apparatus (SIMBA)*  
    *User Manual (Software Version 8.09)*  
    *Revision 004*  
Adjustments are necessary in case your instrument is not a SIMBA or has a different software version.

# Documentation and usage

## Preparations

### conda environment
The python code in `decode_convert.py` requires certain modules included in `environment.yml`. We thus create a [conda](https://anaconda.org/channels/anaconda/packages/conda/overview) environment with those modules that we can later load to run the code. `conda env create -f environment.yml` will create the required environment.

### `get-buoy-data`
`convert-buoy-data` works with SBD files that have been downloaded using [get-buoy-data](https://github.com/McGill-sea-ice/get-buoy-data). If you get your SBD data in another way, make sure to set up the directory structure and naming conventions as in [get-buoy-data](https://github.com/McGill-sea-ice/get-buoy-data) to make sure that `convert-buoy-data` functions properly.

## Usage
Adjust the [IMEI number](https://github.com/McGill-sea-ice/convert-buoy-data/blob/d2f99a84be392626501b7cbbc089aa8ada7cfb35/decode_convert.py#L9) and [paths](https://github.com/McGill-sea-ice/convert-buoy-data/blob/d2f99a84be392626501b7cbbc089aa8ada7cfb35/decode_convert.py#L10-L11) in `decode_convert.py`. Load the conda environment created during the preparations. When run, `decode_convert.py` will check the specified folder for SBD files and call [`convertT2nc`](https://github.com/McGill-sea-ice/convert-buoy-data/blob/d2f99a84be392626501b7cbbc089aa8ada7cfb35/decode.py#L122). This function is defined in [`decode.py`](https://github.com/McGill-sea-ice/convert-buoy-data/blob/main/decode.py), together with [`unpack_simba_v8_09_sbd`](https://github.com/McGill-sea-ice/convert-buoy-data/blob/d2f99a84be392626501b7cbbc089aa8ada7cfb35/decode.py#L9). `unpack_simba_v8_09_sbd` performs the actual decoding of the SBD data and this function is highly specific to the type of instrument and even software version of the particular SIMBA instrument. Adjustments are necessary for different instruments/versions. `convertT2nc` specifically extracts the temperature data and saves it to a [netcdf file](https://www.unidata.ucar.edu/software/netcdf) but this usage is very specific to the variables you want to extract from the SBD files. The more important part of `convertT2nc` is that it also converts all SBD messages into human-readable [json files](https://www.json.org/json-en.html) that get saved alongside the original SBD files in their directory.
After `decode_convert.py` is run for the first time, it will create a file `last_access` that saves the last time the script checked the specified folder for new SBD files. The next time `decode_convert.py` is run, it will only convert data newer than the timestamp saved in `last_access`.

### Automation
The file `decode_convert.sh` contains bash code that handles loading the correct conda environment and executing `decode_convert.py`. Note that `source /opt/anaconda3/etc/profile.d/conda.sh` is necessary due to the way the conda environments are set up on the machine that this code was developped on but almost certainly needs to be adjusted or removed depending on your local machine.  
An example of how use [cron](https://en.wikipedia.org/wiki/Cron) to automatically run `decode_convert.sh` every day to check for new sbd files and convert them if necessary is shown in `to_crontab`. Including this in your crontab will create a log file `decode_convert.log`. Don't forget to adjust paths and directories.
