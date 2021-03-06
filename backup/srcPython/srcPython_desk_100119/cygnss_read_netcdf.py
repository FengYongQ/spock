# This script reads a given netcdf file filename and return information on the satellite and SPs
# inputs: 
# - filename: name of netcdf file to read
# outputs:
# - lat_cyg, lon_cyg: latitude and longitude of cyg
# - lat_sp, lon_sp: latitude and longitude of sp
# - fom_sp, prn_sp: figure of merit (0-15) and prn of sp


# Assumptions:
# - see section PARAMETERS TO SET UP BEFORE RUNNING THIS SCRIPT
import ipdb
import matplotlib
from datetime import datetime, timedelta
import numpy as np
import os
import sys
sys.path.append("/Users/cbv/Google Drive/Work/PhD/Research/Code/spock/srcPython")

from os import listdir
from read_input_file import *
from read_output_file import *
from cygnss_read_spock_spec import *
from cygnss_read_spock_spec_bin import *
from netCDF4 import Dataset
import numpy.ma as ma
from mpl_toolkits.basemap import Basemap, shiftgrid
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.gridspec as gridspec
from matplotlib.colors import LogNorm
from matplotlib import pyplot as plt
#from ecef2eci import *
#from eci_to_lvlh import *
from ecef_to_lvlh import *
import pickle
from cygnss_name_to_norad_id import *
import os.path

def cygnss_read_netcdf(filename):
    #filename = '/Users/cbv/cygnss/netcdf/2018/270/cyg02.ddmi.s20180927-000000-e20180927-235959.l1.power-brcs.a21.d21.nc'

    time_gain_0 = []
    x_spec = []
    y_spec = []
    z_spec = []
    lat_spec = [] 
    quality_flags = [] 
    lon_spec = [] 

    x_cyg = []
    y_cyg = []
    z_cyg = []

    lat_cyg = []
    lon_cyg = []

    pitch_cyg = []
    roll_cyg = []
    yaw_cyg = []

    x_gps = []
    y_gps = []
    z_gps = []

    vx_cyg = []
    vy_cyg = []
    vz_cyg = []


    gain = []
    az_spec = []
    el_spec = []
    az_orbit_spec = []
    el_orbit_spec = []

    fom = []
    index = []
    gps = []
    rx_to_sp_range = []
    tx_to_sp_range = []
    rcg = []
    date_flight = []
    date_flight_rounded = []
    index_in_spock_date_same = [] 
    index_in_spock_not_interpolated_date_same = []
    nb_seconds_since_initial_epoch_spock = []

    fh = Dataset(filename, mode='r')
    # nc_attrs = fh.ncattrs()
    # nc_dims = [dim for dim in fh.dimensions]  # list of nc dimensions
    # nc_vars = [var for var in fh.variables]  # list of nc variables

    x_spec_temp = fh.variables['sp_pos_x'][:] # X component of the specular point position in the ECEF coordinate system, in meters, at ddm_timestamp_utc, as calculated on the ground.
    y_spec_temp = fh.variables['sp_pos_y'][:]
    z_spec_temp = fh.variables['sp_pos_z'][:]

    lat_spec_temp = fh.variables['sp_lat'][:]
    lon_spec_temp = fh.variables['sp_lon'][:]

    x_cyg_temp = fh.variables['sc_pos_x'][:]
    y_cyg_temp = fh.variables['sc_pos_y'][:]
    z_cyg_temp= fh.variables['sc_pos_z'][:]

    lat_cyg_temp = fh.variables['sc_lat'][:]
    lon_cyg_temp = fh.variables['sc_lon'][:]

    pitch_cyg_temp = fh.variables['sc_pitch'][:] # Spacecraft pitch angle relative to the orbit frame, in radians at ddm_timestamp_utc
    roll_cyg_temp = fh.variables['sc_roll'][:]
    yaw_cyg_temp = fh.variables['sc_yaw'][:]

    x_gps_temp = fh.variables['tx_pos_x'][:]
    y_gps_temp = fh.variables['tx_pos_y'][:]
    z_gps_temp= fh.variables['tx_pos_z'][:]

    quality_flags_temp = fh.variables['quality_flags'][:]


    gain_temp = fh.variables['sp_rx_gain'][:] # The receive antenna gain in the direction of the specular point, in dBi, at ddm_timestamp_utc
    az_spec_temp = fh.variables['sp_az_body'][:] # Let line A be the line that extends from the spacecraft to the specular point, at ddm_timestamp_utc. Let line B be the projection of line A onto the spacecraft body frame XY plane. sp_az_body is the angle between the spacecraft body frame +X axis and line B, in degrees, at ddm_timestamp_utc. See UM Doc. 148-0336, CYGNSS Science Data Processing Coordinate Systems Definitions.
    el_spec_temp = fh.variables['sp_theta_body'][:] # The angle between the spacecraft body frame +Z axis and the line extending from the spacecraft to the specular point, in degrees, at ddm_timestamp_utc. See UM Doc. 148-0336, CYGNSS Science Data Processing Coordinate Systems Definitions.

    az_orbit_spec_temp = fh.variables['sp_az_orbit'][:] # Let line A be the line that extends from the spacecraft to the specular point at ddm_timestamp_utc. Let line B be the projection of line A onto the orbit frame XY plane. sp_az_orbit is the angle between the orbit frame +X axis (the velocity vector) and line B, in degrees, at ddm_timestamp_utc. See UM Doc. 148-0336, CYGNSS Science Data Processing Coordinate Systems D
    el_orbit_spec_temp = fh.variables['sp_theta_orbit'][:] # The angle between the orbit frame +Z axis and the line extending from the spacecraft to the specular point, in degrees, at ddm_timestamp_utc. See UM Doc. 148-0336, CYGNSS Science Data Processing Coordinate Systems Definitions.

    fom_temp = fh.variables['prn_fig_of_merit'][:] # The RCG Figure of Merit (FOM) for the DDM. Ranges from 0 through 15.The DDMI selects the four strongest specular points (SP) for DDM production. It ranks the strength of SPs using an antenna RCG map. The map converts the position of the SP in antenna azimuth and declination angles to an RCG FOM. 0 represents the least FOM value. 15 represents the greatest FOM value.

    gps_temp = fh.variables['prn_code'][:] # The PRN code of the GPS signal associated with the DDM. Ranges from 0 to 32. 0 = reflectometry channel idle. 1 through 32 = GPS PRN codes.
    vx_cyg_temp = fh.variables['sc_vel_x'][:]
    vy_cyg_temp = fh.variables['sc_vel_y'][:]
    vz_cyg_temp= fh.variables['sc_vel_z'][:]

    rx_to_sp_range_temp = np.double(fh.variables['rx_to_sp_range'][:])
    tx_to_sp_range_temp = np.double(fh.variables['tx_to_sp_range'][:])

    time_flight = fh.variables['ddm_timestamp_utc'][:]
    time_coverage_start = fh.getncattr(fh.ncattrs()[fh.ncattrs().index('time_coverage_start')])
    time_coverage_start_datetime = datetime.strptime(time_coverage_start[:-4], "%Y-%m-%dT%H:%M:%S.%f") 
    #fh.close()
    nb_time_flight_temp = len(x_cyg_temp)
    date_flight_t = []
    date_flight_rounded_temp = []
    time_remove_list = []
    itime = -1
    prog = 0
    while itime < nb_time_flight_temp-1:
        if itime*100./(nb_time_flight_temp-1) > prog:
            print str(prog)+'%'
            prog = prog + 10
        itime = itime + 1

        time_remove = 0
        date_flight_temp_date = time_coverage_start_datetime + timedelta(microseconds = round(time_flight[itime]*10**6))

        date_flight_temp = datetime.strftime(date_flight_temp_date, "%Y-%m-%dT%H:%M:%S.%f" )
        if ( date_flight_temp.split('.')[1][0] == '9' ): # round to next second
            date_flight_temp_date = datetime.strptime(date_flight_temp, "%Y-%m-%dT%H:%M:%S.%f")
            date_flight_date = date_flight_temp_date + timedelta(seconds = 1)
            date_flight_date_rounded_temp = datetime.strftime(date_flight_date, "%Y-%m-%dT%H:%M:%S.%f").split('.')[0]
            date_flight_date_rounded = datetime.strptime(date_flight_date_rounded_temp, "%Y-%m-%dT%H:%M:%S")
            date_flight_str_rounded = date_flight_date_rounded_temp
        elif ( date_flight_temp.split('.')[1][0] == '0' ): # round to next second
            date_flight_date_rounded = datetime.strptime(date_flight_temp.split('.')[0], "%Y-%m-%dT%H:%M:%S" )
            date_flight_str_rounded = date_flight_temp.split('.')[0]
        else: #if time can't be rounded by less than 100 ms
            time_remove = 1


        if ( time_remove == 1 ): # remove time if can't be rounded by ess than 100 ms 
            time_remove_list.append(itime)
        else:
            if type(x_spec_temp) == ma.core.MaskedArray:
                x_spec.append(x_spec_temp.data[itime]/1000.)
            else:
                x_spec.append(x_spec_temp[itime]/1000.)
            if type(y_spec_temp) == ma.core.MaskedArray:
                y_spec.append(y_spec_temp.data[itime]/1000.)
            else:
                y_spec.append(y_spec_temp[itime]/1000.)
            if type(z_spec_temp) == ma.core.MaskedArray:
                z_spec.append(z_spec_temp.data[itime]/1000.)
            else:
                z_spec.append(z_spec_temp[itime]/1000.)
            if type(gain_temp) == ma.core.MaskedArray:
                gain.append(gain_temp.data[itime])
            else:
                gain.append(gain_temp[itime])
            if type(az_spec_temp) == ma.core.MaskedArray:
                az_spec.append(az_spec_temp.data[itime])
            else:
                az_spec.append(az_spec_temp[itime])

            if type(el_spec_temp) == ma.core.MaskedArray:
                el_spec.append(el_spec_temp.data[itime])
            else:
                el_spec.append(el_spec_temp[itime])

            if type(az_orbit_spec_temp) == ma.core.MaskedArray:
                az_orbit_spec.append(az_orbit_spec_temp.data[itime])
            else:
                az_orbit_spec.append(az_orbit_spec_temp[itime])

            if type(el_orbit_spec_temp) == ma.core.MaskedArray:
                el_orbit_spec.append(el_orbit_spec_temp.data[itime])
            else:
                el_orbit_spec.append(el_orbit_spec_temp[itime])

            if type(fom_temp) == ma.core.MaskedArray:
                fom.append(fom_temp.data[itime])
            else:
                fom.append(fom_temp[itime])

            if type(gps_temp) == ma.core.MaskedArray:
                gps.append(gps_temp.data[itime])
            else:
                gps.append(gps_temp[itime])

            if type(rx_to_sp_range_temp) == ma.core.MaskedArray:
                rx_to_sp_range.append(rx_to_sp_range_temp.data[itime])
            else:
                rx_to_sp_range.append(rx_to_sp_range_temp[itime])
            if type(tx_to_sp_range_temp) == ma.core.MaskedArray:
                tx_to_sp_range.append(tx_to_sp_range_temp.data[itime])
            else:
                tx_to_sp_range.append(tx_to_sp_range_temp[itime])


            if type(lon_cyg_temp) == ma.core.MaskedArray:
                lon_cyg.append(lon_cyg_temp.data[itime])
            else:
                lon_cyg.append(lon_cyg_temp[itime])

            if type(lat_cyg_temp) == ma.core.MaskedArray:
                lat_cyg.append(lat_cyg_temp.data[itime])
            else:
                lat_cyg.append(lat_cyg_temp[itime])

            if type(lat_spec_temp) == ma.core.MaskedArray:
                lat_spec.append(lat_spec_temp.data[itime])
            else:
                lat_spec.append(lat_spec_temp[itime])
            if type(quality_flags_temp) == ma.core.MaskedArray:
                quality_flags.append(quality_flags_temp.data[itime])
            else:
                quality_flags.append(quality_flags_temp[itime])

            if type(lon_spec_temp) == ma.core.MaskedArray:
                lon_spec.append(lon_spec_temp.data[itime])
            else:
                lon_spec.append(lon_spec_temp[itime])

        date_flight_rounded.append(date_flight_str_rounded)


    return date_flight_rounded, lon_cyg, lat_cyg, lon_spec, lat_spec, fom, gps
