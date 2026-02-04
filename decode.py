# Function to decode the hex from the payload into temperatures
import struct
from datetime import datetime
import numpy as np
import os
import xarray as xr
import json

def unpack_simba_v8_09_sbd(msg):
    '''Convert the binary content of `msg` based on the definitions
    in the user manual: 
    SAMS Enterprise Snow and Ice Mass Balance Apparatus (SIMBA)
    User Manual (Software Version 8.09)
    Revision 004

    Parameters
    ----------
    msg : str
        Contents of a binary `.sbd` file from a SIMBA with software
        version 8.09

    Returns
    -------
    out : dict
        Dictionary with all fields converted to human readable
        format. See the above mentioned user manual for details
        on the fields.
    '''
    # First 32 entries are contents of the header. We check how long the
    # rest of the message is to define arrays later on
    l = len(msg[32::])
    out = {}
    # common header
    out["SampleNum"] = struct.unpack(">H", msg[0:2])[0]
    out["Packages_No"] = struct.unpack(">B", msg[2:3])[0]
    out["Packages_Tot"] = struct.unpack(">B", msg[3:4])[0]
    out["Mess_type"] = struct.unpack(">B", msg[4:5])[0]
    out["RTC_Time"] = datetime.fromtimestamp(struct.unpack(">I", msg[5:9])[0])
    out["Pckt_Len"] = struct.unpack(">H", msg[9:11])[0]
    out["Tot_Records"] = struct.unpack(">H", msg[11:13])[0]
    out["Version"] = struct.unpack(">H", msg[13:15])[0]
    out["Head_Spare2"] = struct.unpack(">B", msg[15:16])[0] # should be 0
    # depending on Mess_type, define next fields
    if out["Mess_type"] == 10:
        out["Record_Size"] = struct.unpack(">H", msg[16:18])[0]
        out["Records"] = struct.unpack(">H", msg[18:20])[0]
        out["Chain_ID"] = struct.unpack(">H", msg[20:22])[0] # should be 534
        out["Sensor_Sep"] = struct.unpack(">H", msg[22:24])[0]
        out["TempSpare1"] = struct.unpack(">H", msg[24:26])[0] # should be 0
        out["TempSpare2"] = struct.unpack(">H", msg[26:28])[0] # should be 0
        out["TempSpare3"] = struct.unpack(">H", msg[28:30])[0] # should be 0
        out["TempSpare4"] = struct.unpack(">H", msg[30:32])[0] # should be 0
        out["Temp"] = np.array([struct.unpack(">" + "h", msg[N:N+2])[0] for N in np.arange(32, l+32, 2)]) / 16
    elif out["Mess_type"] in [11, 12, 13, 14]:
        out["Record_Size"] = struct.unpack(">H", msg[16:18])[0]
        out["Records"] = struct.unpack(">H", msg[18:20])[0]
        out["ChainD_ID"] = struct.unpack(">H", msg[20:22])[0] # should be 534
        out["SensorD_Sep"] = struct.unpack(">H", msg[22:24])[0]
        out["ElapsedT_ID"] = struct.unpack(">H", msg[24:26])[0] 
        out["SpareD"] = struct.unpack(">H", msg[26:28])[0] # should be 0
        out["Heater_Volts"] = struct.unpack(">H", msg[28:30])[0]
        out["SpareD2"] = struct.unpack(">H", msg[30:32])[0] # should be 0
        out["Delta"] = np.array([struct.unpack(">" + "b", msg[N:N+1])[0] for N in np.arange(32, l+32, 1)]) / 16
    elif out["Mess_type"] == 21:
        out["Record_Size"] = struct.unpack(">H", msg[16:18])[0]
        out["Records"] = struct.unpack(">H", msg[18:20])[0]
        out["GPSSpare1"] = struct.unpack(">H", msg[20:22])[0] # should be 534
        out["GPSSpare2"] = struct.unpack(">H", msg[22:24])[0]
        out["GPSSpare3"] = struct.unpack(">H", msg[24:26])[0] 
        out["GPSSpare4"] = struct.unpack(">H", msg[26:28])[0] # should be 0
        out["GPSSpare5"] = struct.unpack(">H", msg[28:30])[0]
        out["GPSSpare6"] = struct.unpack(">H", msg[30:32])[0] # should be 0
        c = 0
        for R in np.arange(32, 32 * out["Records"], 42):
            out["GPS" + str(c)] = {}
            out["GPS" + str(c)]["GPS_Time"] = datetime.fromtimestamp(struct.unpack(">I", msg[R:R+4])[0])
            out["GPS" + str(c)]["Lat"] = struct.unpack(">i", msg[R+4:R+8])[0]
            out["GPS" + str(c)]["Long"] = struct.unpack(">i", msg[R+8:R+12])[0]
            out["GPS" + str(c)]["BaroTemp"] = struct.unpack(">h", msg[R+12:R+14])[0] / 16
            out["GPS" + str(c)]["Pressure"] = struct.unpack(">H", msg[R+14:R+16])[0]
            out["GPS" + str(c)]["Mag_X"] = struct.unpack(">h", msg[R+16:R+18])[0]
            out["GPS" + str(c)]["Mag_Y"] = struct.unpack(">h", msg[R+18:R+20])[0]
            out["GPS" + str(c)]["Mag_Z"] = struct.unpack(">h", msg[R+20:R+22])[0]
            out["GPS" + str(c)]["Acc_X"] = struct.unpack(">h", msg[R+22:R+24])[0]
            out["GPS" + str(c)]["Acc_Y"] = struct.unpack(">h", msg[R+24:R+26])[0]
            out["GPS" + str(c)]["Acc_Z"] = struct.unpack(">h", msg[R+26:R+28])[0]
            out["GPS" + str(c)]["Tilt"] = struct.unpack(">H", msg[R+28:R+30])[0]
            out["GPS" + str(c)]["Heading"] = struct.unpack(">H", msg[R+30:R+32])[0]
            out["GPS" + str(c)]["GPSSerialNo"] = struct.unpack(">H", msg[R+32:R+34])[0]
            c += 1
    elif out["Mess_type"] == 31:
        out["Record_Size"] = struct.unpack(">H", msg[16:18])[0] # should be 132
        out["Records"] = struct.unpack(">H", msg[18:20])[0] # should be 1
        out["Last_Change"] = datetime.fromtimestamp(struct.unpack(">I", msg[20:24])[0])
        out["StSpare0"] = struct.unpack(">H", msg[24:26])[0] # should be 0
        out["StSpare1"] = struct.unpack(">H", msg[26:28])[0] # should be 0
        out["StSpare2"] = struct.unpack(">H", msg[28:30])[0] # should be 0
        out["StSpare3"] = struct.unpack(">H", msg[30:32])[0] # should be 0
        out["STATUS_SKIP"] = struct.unpack(">H", msg[32:34])[0]
        out["SAMPLE_PERIOD"] = struct.unpack(">H", msg[34:36])[0]
        out["TEMP_SKIP"] = struct.unpack(">H", msg[36:38])[0]
        out["GPS_SKIP"] = struct.unpack(">H", msg[38:40])[0]
        out["HEAT_SKIP"] = struct.unpack(">H", msg[40:42])[0]
        out["GPS_MESS"] = struct.unpack(">H", msg[42:44])[0]
        out["IRIDIUM_SKIP"] = struct.unpack(">H", msg[44:46])[0]
        for i in range(1, 9):
            out["HST_" + str(i)] = struct.unpack(">H", msg[46+((i-1)*2):48+((i-1)*2)])[0]
        out["SET_CLK"] = struct.unpack(">H", msg[62:64])[0]
        out["WD"] = struct.unpack(">H", msg[64:66])[0]
        out["HEAT_THRES"] = struct.unpack(">H", msg[66:68])[0]
        out["SSPARE1"] = struct.unpack(">H", msg[68:70])[0] # should be 0
        for i in range(0, 8):
            out["ADC_" + str(i)] = struct.unpack(">H", msg[70+(i*2):72+(i*2)])[0]
        for i in range(2, 9):
            out["SSPARE" + str(i)] = struct.unpack(">H", msg[86+((i-2)*2):88+((i-2)*2)])[0] # should be 0
        for i in range(0, 63):
            out["ERR_" + str(i)] = struct.unpack(">B", msg[100+i:101+i])[0]
    else:
        print("Message type " + str(out["Mess_type"]) + " not recognized!")
    return out

def convertT2nc(filelist, outname):
    '''Convert decoded temperature data from SIMBA instrument to an xarray 
    dataset and store it in a netCDF file.

    Parameters
    ----------
    filelist : list
        List of filnames to be opened and added to the the dataset if they
        contain temperature date.
    outname : str
        Name of the netCDF file to be written to disk.

    Returns
    -------
    temp_nc : xarray.Dataset
        Xarray dataset containing the temperature data. The same dataset is
        also written to disk in `outname`.
    '''
    ncname = outname
    temp_nc = False
    # loop over all files in filelist
    for filename in filelist:
        # Open filename
        with open(filename, "rb") as f:
            t = f.read()
        f.close()
        # Unpack and decode the binary data
        msg = unpack_simba_v8_09_sbd(t)
        msg_json = msg.copy()
        msg_json["RTC_Time"] = str(msg["RTC_Time"])
        if msg["Mess_type"] == 10:
            msg_json["Temp"] = list(msg["Temp"])
        elif msg["Mess_type"] in [11, 12, 13, 14]:
            msg_json["Delta"] = list(msg["Delta"])
        elif msg["Mess_type"] == 21:
            c = 0
            for R in np.arange(32, 32 * msg["Records"], 42):
                msg_json["GPS" + str(c)]["GPS_Time"] = str(msg["GPS" + str(c)]["GPS_Time"])
                c += 1
        elif msg["Mess_type"] == 31:
            msg_json["Last_Change"] = str(msg["Last_Change"])
        with open(filename.replace("sbd", "json"), "w", encoding='utf-8') as fj:
            json.dump(msg_json, fj, ensure_ascii=False, indent=4)
        fj.close()
        # Only messages of `Mess_type` = 10 contain temperature data, so we skip
        # all other message types.
        if msg["Mess_type"] == 10:
            # If a netcdf file with `ncname` already exists, the new temperature
            # data will be appended to that file.
            # Otherwise, a new netcdf file will be created.
            if os.path.isfile(ncname):
                temp_nc = xr.open_dataset(ncname)
                # Data of the same sample are transmitted in different messages
                # if too big. We check if the sample number of the the current
                # data already exists in the dataset. If yes, the content of this
                # message needs to be combined with the already existing data with
                # the same sample number.
                if (msg["SampleNum"] == temp_nc["SampleNum"]).any():
                    # get the temperature data of the same sample number
                    loc1 = int(abs(temp_nc.temp.where(temp_nc.SampleNum == msg["SampleNum"]).sum("pos")).argmax().values)
                    temp1 = temp_nc.temp.isel(time=loc1).dropna("pos").values
                    # Check if current message is above (`Packages_No`=1) or 
                    # below (`Packages_No`=2) the existing data with same sample number
                    # and combine the data accordingly.
                    if msg["Packages_No"] == 1:
                        temp_combined = np.hstack([msg["Temp"], temp1.squeeze()])
                    elif msg["Packages_No"] == 2:
                        temp_combined = np.hstack([temp1.squeeze(), msg["Temp"]])
                    # Write data into a xarray dataset and merge with the already
                    # existing dataset
                    temp = xr.Dataset(
                            data_vars={"temp": (["pos"], temp_combined)},
                            coords={"time": msg["RTC_Time"], "pos": temp_nc.pos}
                            ).expand_dims("time")
                    temp_nc = xr.merge([temp_nc, temp], compat="no_conflicts", join="left")
                else:
                    # No data with same sample number exists, we create a new entry
                    # and it up with NaNs below or above the temperature data, depending 
                    # on `Pacakges_No`.
                    if msg["Packages_No"] == 1:
                        temp = xr.Dataset(
                            data_vars={"temp": (["pos"], np.hstack((msg["Temp"], np.ones(msg["Tot_Records"] - msg["Records"]) * np.nan)))},
                            coords={"time": msg["RTC_Time"], "pos": temp_nc.pos}
                            )
                        temp["SampleNum"] = msg["SampleNum"]
                    elif msg["Packages_No"] == 2:
                        temp = xr.Dataset(
                            data_vars={"temp": (["pos"], np.hstack((np.ones(msg["Tot_Records"] - msg["Records"]) * np.nan, msg["Temp"])))},
                            coords={"time": msg["RTC_Time"], "pos": temp_nc.pos}
                            )
                        temp["SampleNum"] = msg["SampleNum"]
                    # concatenate this new data entry with the existing dataset
                    temp_nc = xr.concat([temp_nc, temp], dim="time").sortby("time")
                # write dataset to disk
                temp_nc.to_netcdf(ncname)
            else:
                # No netcdf file with name `ncname` exists, so we create one.
                # Depending on the value of `Sensor_Sep` we define the vertical
                # resolution of the data in cm.
                if msg["Sensor_Sep"] == 0:
                    dz = 2
                elif  msg["Sensor_Sep"] == 1:
                    dz = 4
                else:
                    print("Unrecognized value of Sensor_Sep, should be 0 or 1")
                # create a new xarray Dataset with a vertical coordinate
                temp_nc = xr.Dataset(coords={"pos": np.arange(0, msg["Tot_Records"]*dz, dz)})
                temp_nc["pos"].attrs["long_name"] = "centimeters_from_start_of_chain"
                temp_nc["pos"].attrs["units"] = "cm"
                # Create the first data entry and fill up with NaNs where there is no
                # temperature data (depends on `Packages_No`). Also add a time
                # dimension.
                if msg["Packages_No"] == 1:
                    temp = xr.DataArray(
                        data=np.hstack((msg["Temp"], np.ones(msg["Tot_Records"] - msg["Records"]) * np.nan)),
                        dims=["pos"],
                        coords={"time": msg["RTC_Time"], "pos": temp_nc.pos}
                        )
                elif msg["Packages_No"] == 2:
                    temp = xr.DataArray(
                        data=np.hstack((np.ones(msg["Tot_Records"] - msg["Records"]) * np.nan, msg["Temp"])),
                        dims=["pos"],
                        coords={"time": msg["RTC_Time"], "pos": temp_nc.pos}
                        )
                # Add the first data entry to the dataset that was created before
                temp_nc = xr.merge([temp_nc, temp.rename("temp")]).expand_dims("time")
                temp_nc["SampleNum"] = ("time", [msg["SampleNum"],])
                # Write to disk
                temp_nc.to_netcdf(ncname)
        else:
            pass # not a temperature file
    if temp_nc:
        return temp_nc
    else:
        return
