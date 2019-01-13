# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# This script compares the state from TLEs to the state propagated by SpOCK.
# The analysis starts at a start epoch (start_epoch) and ends at an end epoch (end_epoch). SpOCK propagates the sc from the TLE at spacectrack.org which epoch corresponds to this start epoch until the end epoch. The propagated state from start_epoch to end_epoch is then compared to the state derived from the TLEs at spacetrack for this same period (from start_epoch to end_epoch).
# Note: to derive the state from the TLEs and compare them with the propagated stated by SpOCK, you first need to call SGP4 to convert the elements from the TLEs into r, v ECI (this is because TLEs are mean elements generated by SPG4 so to convert them in r, v you need to use the same model that generated them (which is SGP4)). SGP4 is implemented in SpOCK via SPICE libraries so SpOCK does the conversion TLEs to r, v ECI at the epoch of the TLEs. In addition to giving r, v ECI from the TLEs, SpOCK also gives the osculating orbital elements (by converting r, v ECI into osculating elements). Therefore, r, v ECI and osculating elements corresponding to the TLEs can be compared to r, v ECI and osculating elements corresponding to the propagation by SpOCK. (I actually compated r, v ECI using SGP4 as implemented in SpOCK to using the actual SGP4 (fortran code) and got the exact same r, v ECI in both cases (using 721 for the gravitational constant mode in the SGP4 fortran code))
####
# ASSUMPTIONS:
# - the mass assumed for CYGNSS is 29 kg

import sys
sys.path.append("/Users/cbv/Google Drive/Work/PhD/Research/Code/spock/srcPython")
from norad_id_to_cygnss_name import *
from cygnss_name_to_norad_id import *
from orbit_average import *
from spock_main_input import *
import matplotlib.colors as colors
import matplotlib.cm as cmx
from cadre_read_last_tle import *
from get_prop_dir import *
import matplotlib.gridspec as gridspec
from read_input_file import *
from convert_tle_date_to_date import *
from matplotlib.colors import LogNorm
import pickle
from eci_to_lvlh import *

import fileinput
import time
from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt
import os
import subprocess
from get_name_mission import *
from find_in_read_input_order_variables import *

#plt.ion()


############ PARAMETERS TO SET ############
#load TLE sma pickle (set to 1) -> won't propagate TLEs with SpOCK to get sma at TLE epoch
load_tle_result = 1

# show spock propagation (set to 1)
spock_prop = 0


## path of the folder where you want to store the results (pickle, image, video)
path_folder_results = './'

## Parameters for the figure
height_fig = 11.  # the width is calculated as height_fig * 4/3.
fontsize_plot = 25
ratio_fig_size = 4./3

# start and end of the simulation. The most recent TLE corresponding to start_epoch will be downloaded from spacetrack to initialize SpOCK.
start_epoch = '2017-01-01' # Please use format 'YYYY-MM-DD'
end_epoch = '2017-12-31' # Please use format 'YYYY-MM-DD'
sma_tle_at_tle_epoch_all = []
date_tle_from_tle_all = []
# which norad_id to consider
for i in range(8):
    norad_id_int = 41884 + i
    norad_id = str(norad_id_int) # has to be a string
    if load_tle_result != 1:
        # ############ ALGORITHM ############
        earth_mu     = 398600.4418; # gravitational parameter (km^3/s^2)
        earth_radius = 6378.137; # mean equatorial radius (km)
        # END OF SOME PRE STUFF
        cygnss_real_mass = 29.
        order_gravity = 10
        forces = "drag sun_gravity moon_gravity"
        density_mode = 'omniweb'
        spice_path = '/Users/cbv/cspice/data' #'/raid4/cbv/cspice/data'  # '/Users/cbv/cspice/data'
        root_save_fig_name = path_folder_results
        cygnss_geometry = 'cygnss_geometry_2016_acco08.txt'

        # TLE STATES
        # Download all TLEs from start_epoch to end_epoch (all TLEs are included in the same file)
        link = "https://www.space-track.org/basicspacedata/query/class/tle/NORAD_CAT_ID/" + norad_id + "/EPOCH/" + start_epoch + '--' + end_epoch +  "/format/tle/emptyresult/show/orderby/EPOCH%20asc/"
        os.system("wget  --post-data='identity=cbv@umich.edu&password=cygnssisawesome' --cookies=on --keep-session-cookies --save-cookies=cookies.txt 'https://www.space-track.org/ajaxauth/login' -olog")
        name_all_tle_from_initial_to_end_epoch = norad_id + '_from_' + start_epoch + '_to_' + end_epoch + ".txt"
        os.system("wget --limit-rate=100K --keep-session-cookies --load-cookies=cookies.txt " + link + " -O " + name_all_tle_from_initial_to_end_epoch)


        # We can't just use 2 body equations to convert mean motion to sma and then compare this sma to the sma in SpOCK. Indeed, SpOCK uses osculating elements but the TLEs uses Kozai mean elements: they can differ by several km. So using the wrong theory (2 body equations) to convert the TLEs would give us errors, we need to use SGP4 because SGP4's equations convert Kozai mean elements into r, v ECI. Then we convert r, v ECI into osculating elements. Recall: SGP4 is integrated in SpOCK (via SPICE libraries) -> at the initialization, SpOCK converts the TLEs into r, v ECI and then osculating elements. So we convert TLE into r,v then propgate over 1 orbit then take the orbit average of the same over this orbit
        ## For each TLE in name_all_tle_from_initial_to_end_epoch, run SpOCK for about two orbits
        all_tle_file = open( name_all_tle_from_initial_to_end_epoch)
        read_all_tle_file = all_tle_file.readlines()
        nb_tle = len(read_all_tle_file) / 2
        date_tle_from_tle = []
        iline = 0
        sma_average_tle = []
        date_average_tle_end_orbit = []
        date_average_tle_start_orbit = []
        x_axis_average_tle = []
        nb_orbit_tle = np.zeros([nb_tle]).astype(np.int)
        r_eci_tle_at_tle_epoch = np.zeros([nb_tle, 3])
        radius_tle_at_tle_epoch = np.zeros([nb_tle])
        v_eci_tle_at_tle_epoch = np.zeros([nb_tle, 3])
        alt_tle_at_tle_epoch = np.zeros([nb_tle])
        sma_tle_at_tle_epoch = np.zeros([nb_tle])
        ecc_tle_at_tle_epoch = np.zeros([nb_tle])

        for itle in range(nb_tle):
            print 'tle ', itle, nb_tle-1
            date_average_tle_end_orbit_run_str = []
            date_average_tle_start_orbit_run_str = []
            date_average_tle_end_orbit_run = []
            date_average_tle_start_orbit_run = []
            x_axis_average_tle_run = []
            dt_tle = 1 # we don't care about dt here because we only look at the initialization
            dt_tle_output = dt_tle
            date_tle_temp = read_all_tle_file[iline].split()[3]  
            date_start_temp = convert_tle_date_to_date(date_tle_temp)
            date_tle_from_tle.append(date_start_temp)
            date_start_tle = datetime.strftime(date_start_temp, "%Y-%m-%dt_tle%H:%M:%S.%f")
            date_start_spock = datetime.strftime(date_start_temp + timedelta(seconds = dt_tle), "%Y-%m-%dT%H:%M:%S.%f") # make sur ethe initial epoch starts at least one time step after TLE epoch
            ### Create a TLE file for SpOCK with only the current TLE
            tle_filename_one_sc_one_time = norad_id + "_" + date_start_tle.replace(".","_") + ".txt"
            tle_file_one_sc_one_time = open(tle_filename_one_sc_one_time, "w")
            print >> tle_file_one_sc_one_time, read_all_tle_file[iline].replace("\r", ""), read_all_tle_file[iline+1].replace("\r", "")
            tle_file_one_sc_one_time.close()
            ### Create main input file for SpOCK with this TLE
            main_input_filename = "TLE_" + norad_id + "_" + date_start_tle.replace(".","_") + ".txt"
            date_end_temp = date_start_temp + timedelta(seconds = dt_tle_output)  # !!!! assumption: orbit period is < 100 min
            date_end_spock = datetime.strftime(date_end_temp, "%Y-%m-%dT%H:%M:%S.%f")
            spock_main_input(
                main_input_filename,
                # for TIME section
                date_start_spock,
                date_end_spock,
                dt_tle,
                # for SPACECRAFT section
                1,
                '0',
                cygnss_real_mass,
                cygnss_geometry,
                # for ORBIT section
                tle_filename_one_sc_one_time,
                # for FORCES section
                4,#order_gravity,
                'none',#forces,
                density_mode,
                # for OUTPUT section
                        '~/cygnss/comparison_tle/out',
                dt_tle_output, 
                # for ATTITUDE section
                "nadir",
                # for GROUNDS_STATIONS section
                "0",#"my_ground_stations.txt"
                # for SPICE section
                spice_path, 
                # for DENSITY_MOD section
                1
            )

            ### Run SpOCK with this main input file
            #os.system("mpirun -np 1 spock " + main_input_filename)

            ### Read TLE output file (starts the with the prefix 'TLE_')
            #### Read main input filename to figure out the name of the output
            var_in, var_in_order = read_input_file( main_input_filename)
            output_file_path_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]; 
            output_file_name_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')];
            isc = 0 # here only one sc in main input file
            var_to_read = ["altitude", "sma", "radius", "eccentricity","latitude"]
            var_out, var_out_order = read_output_file( output_file_path_list[isc] + output_file_name_list[isc], var_to_read )

            date_tle = var_out[find_in_read_input_order_variables(var_out_order, 'date')]
            nb_steps_new = len(date_tle) # in case the sc reentered the atmosphere before the end of the run OR if bug in SpCOK before the end of run (still want to run this script)
            nb_sc = var_in[find_in_read_input_order_variables(var_in_order, 'nb_sc')];


            #sma at epoch of TLE (so from TLE_ output file)
            tle_out_name = output_file_path_list[0] + 'TLE_' + output_file_name_list[0]
            tle_out = open(tle_out_name, "r")
            read_tle_out = tle_out.readlines()
            n_header = 12
            r_eci_tle_at_tle_epoch[itle, 0] = read_tle_out[n_header].split()[2]; r_eci_tle_at_tle_epoch[itle, 1] = read_tle_out[n_header].split()[3]; r_eci_tle_at_tle_epoch[itle, 2] = read_tle_out[n_header].split()[4]; 
            radius_tle_at_tle_epoch[itle] = np.sqrt( r_eci_tle_at_tle_epoch[itle, 0]*r_eci_tle_at_tle_epoch[itle, 0] + r_eci_tle_at_tle_epoch[itle, 1]*r_eci_tle_at_tle_epoch[itle, 1] + r_eci_tle_at_tle_epoch[itle, 2]*r_eci_tle_at_tle_epoch[itle, 2] )
            v_eci_tle_at_tle_epoch[itle, 0] = read_tle_out[n_header].split()[5]; v_eci_tle_at_tle_epoch[itle, 1] = read_tle_out[n_header].split()[6]; v_eci_tle_at_tle_epoch[itle, 2] = read_tle_out[n_header].split()[7]; 
            alt_tle_at_tle_epoch[itle] = read_tle_out[n_header].split()[10]
            sma_tle_at_tle_epoch[itle] = read_tle_out[n_header].split()[11]
            ecc_tle_at_tle_epoch[itle] = read_tle_out[n_header].split()[13]

            tle_out.close()
#             # sma over one orbit
#             alt_tle = var_out[find_in_read_input_order_variables(var_out_order, 'altitude')]
#             sma_tle = var_out[find_in_read_input_order_variables(var_out_order, 'sma')]
#             lat_tle = var_out[find_in_read_input_order_variables(var_out_order, 'latitude')]
#             radius_tle = var_out[find_in_read_input_order_variables(var_out_order, 'radius')]
#             ecc_tle = var_out[find_in_read_input_order_variables(var_out_order, 'eccentricity')]
#             # Orbit average
#             sma_orbit_averaged, time_averaged, index_time_averaged = orbit_average(sma_tle, lat_tle, date_tle )
#             sma_average_tle.append( sma_orbit_averaged ) # each sc might not have the same orbital period so the length of the array might not be the same between each sc
#             date_average_tle_start_orbit_run_str.append( np.array(time_averaged)[:,0] ) # take the date at the start of the bin
#             date_average_tle_end_orbit_run_str.append( np.array(time_averaged)[:,2] ) # take the date at the end of the bin
#             nb_orbit_tle[itle] = len(time_averaged)
#             for iorbit in range(nb_orbit_tle[itle]):
#                 date_average_tle_start_orbit_temp = date_average_tle_start_orbit_run_str[-1][iorbit]
#                 date_average_tle_start_orbit_run.append( datetime.strptime( date_average_tle_start_orbit_temp, "%Y/%m/%d %H:%M:%S.%f" ) )
#                 date_average_tle_end_orbit_temp = date_average_tle_end_orbit_run_str[-1][iorbit]
#                 date_average_tle_end_orbit_run.append( datetime.strptime( date_average_tle_end_orbit_temp, "%Y/%m/%d %H:%M:%S.%f" ) )
#                 nb_seconds_between_start_orbit_and_date_start = ( date_average_tle_start_orbit_run[-1] - date_tle_from_tle[0] ).total_seconds()
#                 x_axis_average_tle_run.append( nb_seconds_between_start_orbit_and_date_start )

#             date_average_tle_end_orbit.append(date_average_tle_end_orbit_run)
#             date_average_tle_start_orbit.append(date_average_tle_start_orbit_run)
#             x_axis_average_tle.append(x_axis_average_tle_run)


            ### move to next tle
            iline = iline + 2


#         x_axis_average_tle = np.array(x_axis_average_tle)
#         sma_average_tle = np.array(sma_average_tle)
        pickle.dump( date_tle_from_tle, open( '/Users/cbv/cygnss/comparison_tle/date_tle_from_tle_' + norad_id + ".pickle", "w" ) )
        pickle.dump( sma_tle_at_tle_epoch, open( '/Users/cbv/cygnss/comparison_tle/sma_tle_at_tle_epoch_' + norad_id + ".pickle", "w" ) )

    else:
        date_tle_from_tle = pickle.load(open( '/Users/cbv/cygnss/comparison_tle/date_tle_from_tle_' + norad_id + ".pickle","r"))
        sma_tle_at_tle_epoch = pickle.load(open( '/Users/cbv/cygnss/comparison_tle/sma_tle_at_tle_epoch_' + norad_id + ".pickle","r"))
        date_tle_from_tle_all.append(date_tle_from_tle)
        sma_tle_at_tle_epoch_all.append(sma_tle_at_tle_epoch)

if spock_prop == 1:
    # # SPOCK PROPAGATION
    # # Download the most recent TLE corresponding to start_epoch to initialize SpOCK
    link = "https://www.space-track.org/basicspacedata/query/class/tle/NORAD_CAT_ID/" + norad_id + "/EPOCH/%3E" + start_epoch +  "/format/tle/emptyresult/show/orderby/EPOCH%20asc/limit/1"
    #os.system("wget  --post-data='identity=cbv@umich.edu&password=cygnssisawesome' --cookies=on --keep-session-cookies --save-cookies=cookies.txt 'https://www.space-track.org/ajaxauth/login' -olog")
    name_tle = norad_id + '_on_' + start_epoch + ".txt"
    #os.system("wget --limit-rate=100K --keep-session-cookies --load-cookies=cookies.txt " + link + " -O " + name_tle)

    # # Run SpOCK: run nb_run_spock runs, each run corresponding to a different mass (this is equivalent to modeling a different Cd)
    cd_array = np.array([2.4])#np.arange(2.6,4.4,0.8)
    cd_geo_file = 2.4 # all the cd in the geomtry file must be equal to cd_geo_file
    cygnss_real_mass_times_cd_geo_file = cygnss_real_mass * cd_geo_file
    mass_array = cygnss_real_mass_times_cd_geo_file / cd_array
    nb_run_spock = (int)(len(cd_array))
    sma_average_spock = []
    nb_orbit_spock = np.zeros([nb_run_spock]).astype(np.int)
    date_average_spock_end_orbit = []
    date_average_spock_start_orbit = []
    x_axis_average_spock = []
    for irun in range(nb_run_spock):
        date_average_spock_end_orbit_run_str = []
        date_average_spock_start_orbit_run_str = []
        date_average_spock_end_orbit_run = []
        date_average_spock_start_orbit_run = []
        x_axis_average_spock_run = []
        ## Create main input file for SpOCK with this TLE
        main_input_filename = name_tle.replace(".txt", "") + "_cd_" + str(cd_array[irun]).replace(".","_") + ".txt"
        ### look at TLE epoch start: SpOCK needs to start earlier than the TLE epoch
        tle_file = open(name_tle)
        read_tle_file = tle_file.readlines()
        tle_epoch_temp = ( read_tle_file[0].split()[3] ) # TLE epoch -> initial epoch of SpOCK
        tle_epoch = convert_tle_date_to_date(tle_epoch_temp)
        ### Set up the start epoch for the propagation with SpOCK
        dt_spock = 10 # dt that will be used to run SpOCK
        dt_spock_output = dt_spock
        date_start_spock = datetime.strftime(tle_epoch + timedelta(seconds = dt_spock), "%Y-%m-%dT%H:%M:%S.%f") # ned to add dt to tle epoch to make sure that SpOCK starts earlier than the TLE epoch
        date_end_spock = end_epoch + "T00:00:00"
        ### Creates main input file to run SpOCK
        mass = mass_array[irun]
        spock_main_input(
            main_input_filename,
            # for TIME section
            date_start_spock,
            date_end_spock,
            dt_spock,
            # for SPACECRAFT section
            1,
            '0',
            mass,
            cygnss_geometry,
            # for ORBIT section
            name_tle,
            # for FORCES section
            order_gravity,
            forces,
            density_mode,
            # for OUTPUT section
            'out',
            dt_spock_output, # the last time step is the only we care about here and is always printed
            # for ATTITUDE section
            "(82;0; 0) (0;0;0)",
            # for GROUNDS_STATIONS section
            "0",#"my_ground_stations.txt"
            # for SPICE section
            spice_path, 
            # for DENSITY_MOD section
            1
            )


            ############
            ### Run SpOCK with this main input file
        os.system("mpirun -np 1 spock " + main_input_filename)
    #    raise Exception
        ## Read propagated state
        var_in, var_in_order = read_input_file( main_input_filename)
        output_file_path_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]; 
        output_file_name_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')]; 
        isc = 0 # here only one sc in main input file
        var_to_read = ["altitude", "sma", "radius", "eccentricity","latitude"]
        var_out, var_out_order = read_output_file( output_file_path_list[isc] + output_file_name_list[isc], var_to_read )
        if irun  == 0:
            date_spock = var_out[find_in_read_input_order_variables(var_out_order, 'date')]
            nb_steps_new = len(date_spock) # in case the sc reentered the atmosphere before the end of the run OR if bug in SpCOK before the end of run (still want to run this script)
            nb_sc = var_in[find_in_read_input_order_variables(var_in_order, 'nb_sc')]; 
            alt_spock = np.zeros([nb_run_spock, nb_steps_new]); sma_spock = np.zeros([nb_run_spock, nb_steps_new]); radius_spock = np.zeros([nb_run_spock, nb_steps_new]); ecc_spock = np.zeros([nb_run_spock, nb_steps_new]); lat_spock = np.zeros([nb_run_spock, nb_steps_new])

        alt_spock[irun, :] = var_out[find_in_read_input_order_variables(var_out_order, 'altitude')]
        sma_spock[irun, :] = var_out[find_in_read_input_order_variables(var_out_order, 'sma')]
        lat_spock[irun, :] = var_out[find_in_read_input_order_variables(var_out_order, 'latitude')]
        radius_spock[irun, :] = var_out[find_in_read_input_order_variables(var_out_order, 'radius')]
        ecc_spock[irun, :] = var_out[find_in_read_input_order_variables(var_out_order, 'eccentricity')]
        # Orbit average
        sma_orbit_averaged, time_averaged, index_time_averaged = orbit_average(sma_spock[irun, :nb_steps_new], lat_spock[isc, :nb_steps_new], date_spock )
        sma_average_spock.append( sma_orbit_averaged ) # each sc might not have the same orbital period so the length of the array might not be the same between each sc
        date_average_spock_start_orbit_run_str.append( np.array(time_averaged)[:,0] ) # take the date at the start of the bin
        date_average_spock_end_orbit_run_str.append( np.array(time_averaged)[:,2] ) # take the date at the end of the bin

        nb_orbit_spock[irun] = len(time_averaged)
        for iorbit in range(nb_orbit_spock[irun]):
            date_average_spock_start_orbit_temp = date_average_spock_start_orbit_run_str[-1][iorbit]
            date_average_spock_start_orbit_run.append( datetime.strptime( date_average_spock_start_orbit_temp, "%Y/%m/%d %H:%M:%S.%f" ) )
            date_average_spock_end_orbit_temp = date_average_spock_end_orbit_run_str[-1][iorbit]
            date_average_spock_end_orbit_run.append( datetime.strptime( date_average_spock_end_orbit_temp, "%Y/%m/%d %H:%M:%S.%f" ) )
            nb_seconds_between_start_orbit_and_date_start = ( date_average_spock_start_orbit_run[-1] - date_tle_from_tle[0] ).total_seconds() # with respect to first tle date
            x_axis_average_spock_run.append( nb_seconds_between_start_orbit_and_date_start )

        date_average_spock_end_orbit.append(date_average_spock_end_orbit_run)
        date_average_spock_start_orbit.append(date_average_spock_start_orbit_run)
        x_axis_average_spock.append(x_axis_average_spock_run)
    sma_average_spock = np.array(sma_average_spock)
    x_axis_average_spock = np.array(x_axis_average_spock)
    date_average_spock_end_orbit = np.array(date_average_spock_end_orbit)
    date_average_spock_start_orbit = np.array(date_average_spock_start_orbit)

# put all sc reference to sc with oldest tle
nb_sc = 8
oldest_tle = date_tle_from_tle_all[0][0]
for isc in range(1,nb_sc):
    if date_tle_from_tle_all[isc][0] < oldest_tle:
        oldest_tle = date_tle_from_tle_all[isc][0]

nb_seconds_oldest_tle_to_this_tle = []
for isc in range(nb_sc):
    nb_tle_now = len(date_tle_from_tle_all[isc])
    nb_seconds_oldest_tle_to_this_tle_sc = []
    for itle in range(nb_tle_now):
        nb_seconds_oldest_tle_to_this_tle_sc.append( ( date_tle_from_tle_all[isc][itle] - oldest_tle ).total_seconds() )
    nb_seconds_oldest_tle_to_this_tle.append( nb_seconds_oldest_tle_to_this_tle_sc )

most_recent_tle = date_tle_from_tle_all[0][-1] 
for isc in range(1,nb_sc):
    if date_tle_from_tle_all[isc][-1] > most_recent_tle:
        most_recent_tle = date_tle_from_tle_all[isc][-1]


#Read file of maneuverse  (high drag and Sun pointed)
filename_man = '/Users/cbv/cygnss/comparison_tle/maneuvers.txt'
file_man = open(filename_man)
read_file_man = file_man.readlines()
nb_line_man = len(read_file_man)
highdrag = []
sunpointed = []
sc_name = []
nb_highdrag = np.zeros([nb_sc]).astype(np.int)
nb_sunpointed = np.zeros([nb_sc]).astype(np.int)
nb_seconds_first_tle_to_start_highdrag = []
nb_seconds_first_tle_to_end_highdrag = []
nb_seconds_first_tle_to_start_sunpointed = []
nb_seconds_first_tle_to_end_sunpointed = []
iline = 0
for isc in range(nb_sc):
    highdrag_sc = []
    sunpointed_sc = []
    nb_seconds_first_tle_to_start_highdrag_isc = []
    nb_seconds_first_tle_to_end_highdrag_isc = []
    nb_seconds_first_tle_to_start_sunpointed_isc = []
    nb_seconds_first_tle_to_end_sunpointed_isc = []
    while read_file_man[iline][0] != '#':
        iline = iline + 1
    sc_name.append(read_file_man[iline][1:].rstrip())
    iline = iline + 2 # skip line called 'highdrag'
    while read_file_man[iline].rstrip() != 'sunpointed':  # reached sunpointd is this is false. otherwise fill highdrag dates
        man_start = read_file_man[iline].rstrip().split('-')[0]
        man_end = read_file_man[iline].rstrip().split('-')[1]
        man_start = datetime.strptime(man_start + '17', '%d%m%y') #280717
        man_end = datetime.strptime(man_end + '17', '%d%m%y') #280717
        nb_seconds_first_tle_to_start_highdrag_isc.append((man_start - oldest_tle).total_seconds())
        nb_seconds_first_tle_to_end_highdrag_isc.append((man_end - oldest_tle).total_seconds())
        highdrag_sc.append([man_start, man_end])
        iline = iline + 1
    iline = iline + 1 # skip line called 'sunpointed'
    while len(read_file_man[iline].rstrip()) != 0: # reached next sc if this is false. otherwise fill sunpointed dates
        man_start = read_file_man[iline].rstrip().split('-')[0]
        man_end = read_file_man[iline].rstrip().split('-')[1]
        man_start = datetime.strptime(man_start + '17', '%d%m%y') #280717
        man_end = datetime.strptime(man_end + '17', '%d%m%y') #280717
        sunpointed_sc.append([man_start, man_end])
        nb_seconds_first_tle_to_start_sunpointed_isc.append((man_start - oldest_tle).total_seconds())
        nb_seconds_first_tle_to_end_sunpointed_isc.append((man_end - oldest_tle).total_seconds())
        iline = iline + 1
        if iline == len(read_file_man):
            break
    highdrag.append(highdrag_sc)
    sunpointed.append(sunpointed_sc)
    nb_seconds_first_tle_to_start_highdrag.append(nb_seconds_first_tle_to_start_highdrag_isc)
    nb_seconds_first_tle_to_end_highdrag.append(nb_seconds_first_tle_to_end_highdrag_isc)
    nb_seconds_first_tle_to_start_sunpointed.append(nb_seconds_first_tle_to_start_sunpointed_isc)
    nb_seconds_first_tle_to_end_sunpointed.append(nb_seconds_first_tle_to_end_sunpointed_isc)

    nb_highdrag[isc] = len(highdrag_sc)
    nb_sunpointed[isc] = len(sunpointed_sc)

file_man.close()
nb_seconds_first_tle_to_start_highdrag = np.array(nb_seconds_first_tle_to_start_highdrag)
nb_seconds_first_tle_to_end_highdrag = np.array(nb_seconds_first_tle_to_end_highdrag)
nb_seconds_first_tle_to_start_sunpointed = np.array(nb_seconds_first_tle_to_start_sunpointed)
nb_seconds_first_tle_to_end_sunpointed = np.array(nb_seconds_first_tle_to_end_sunpointed)


## Parameters for the figure
height_fig = 12.5  # the width is calculated as height_fig * 4/3.
fontsize_plot = 25
width_fig = 11*4./3
### For plots, generate disctinct colors
if spock_prop == 1:
    NCURVES = nb_run_spock
    np.random.seed(101)
    curves = [np.random.random(20) for i in range(NCURVES)]
    values = range(NCURVES)
    jet = cm = plt.get_cmap('jet') 
    cNorm  = colors.Normalize(vmin=0, vmax=values[-1])
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
    print 'AAAAAAAAA'
### or choose among color_arr
color_arr = ['b', 'r','k','g', 'm', 'gold', 'cyan', 'darkgray',  'lawngreen', 'green', 'chocolate','cornflowerblue','fuchsia']

fig_title = ''#'SMA from TLE as a function of time'
y_label = 'SMA (km)'
x_label = 'Real time'
fig_sma_average = plt.figure(num=None, figsize=(width_fig, height_fig), dpi=80, facecolor='w', edgecolor='k')

fig_sma_average.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'normal',)
plt.rc('font', weight='normal') ## make the labels of the ticks in normal
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax_sma_average = fig_sma_average.add_subplot(gs[0, 0])

ax_sma_average.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
ax_sma_average.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax_sma_average.spines.itervalues()] # change the width of the frame of the figure
ax_sma_average.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='normal') ## make the labels of the ticks in normal


if spock_prop == 1:
    for irun in range(nb_run_spock):
        colorVal = scalarMap.to_rgba(irun)
        ax_sma_average.plot(x_axis_average_spock[irun, :], sma_average_spock[irun, :], linewidth = 2, color = colorVal)


#ax_sma_average.scatter(x_axis_average_tle[:,0], sma_average_tle[:,0], linewidth = 2, color = 'b') # [:, 0]: 0 because we look only at the first orbit average of the TLE (since we want to show the sma average corresponding ot the TLE so take the orbit right after the TLE epoch)
#ax_sma_average.plot(x_axis_average_tle[:,0], sma_average_tle[:,0], linewidth = 2, color = 'b') # [:, 0]: 0 because we look only at the first orbit average of the TLE (since we want to show the sma average corresponding ot the TLE so take the orbit right after the TLE epoch)

#ax_sma_average.scatter(x_axis_average_tle[:,0], sma_tle_at_tle_epoch, linewidth = 2, color = 'r') # [:, 0]: 0 because we look only at the first orbit average of the TLE (since we want to show the sma average corresponding ot the TLE so take the orbit right after the TLE epoch)
max_sma_tle = 0
min_sma_tle = 100000000
norad_id_arr = []
for ifm in range(1,nb_sc+1):
    cygnss_name = 'FM0' + str(ifm)
    norad_id_arr.append((int)(cygnss_name_to_norad_id(cygnss_name)) - 41884)

isc_count = -1
for isc in norad_id_arr:#range(nb_sc):
    isc_count = isc_count + 1
    norad_id_int = 41884 + isc
    norad_id = str(norad_id_int) # has to be a string
    fm_id = norad_id_to_cygnss_name(norad_id)
    index_fm = np.where(np.array(sc_name) == fm_id)[0][0]
    ax_sma_average.plot(nb_seconds_oldest_tle_to_this_tle[isc], sma_tle_at_tle_epoch_all[isc], linewidth = 2, color = color_arr[isc_count], label = fm_id)# + ' (' + str(nb_highdrag[index_fm]) + ' HD)')
    nb_tle_now = len(date_tle_from_tle_all[isc])
    for iman in range(nb_highdrag[index_fm]):
        index_tle_start_man = np.where(np.array(nb_seconds_oldest_tle_to_this_tle[isc]) > nb_seconds_first_tle_to_start_highdrag[index_fm][iman])[0][0]
        ax_sma_average.scatter(nb_seconds_oldest_tle_to_this_tle[isc][index_tle_start_man], sma_tle_at_tle_epoch_all[isc][index_tle_start_man],marker = '.', color = 'b',s = 300)
        if len(np.where(np.array(nb_seconds_oldest_tle_to_this_tle[isc]) > nb_seconds_first_tle_to_end_highdrag[index_fm][iman])[0]) > 0: # = 0 is the highdrag maneuver is more recent than the most recent TLE
            index_tle_end_man = np.where(np.array(nb_seconds_oldest_tle_to_this_tle[isc]) > nb_seconds_first_tle_to_end_highdrag[index_fm][iman])[0][0]
            ax_sma_average.scatter(nb_seconds_oldest_tle_to_this_tle[isc][index_tle_end_man], sma_tle_at_tle_epoch_all[isc][index_tle_end_man],marker = '.', color = 'r', s = 300)

            
    for iman in range(nb_sunpointed[index_fm]):
        index_tle_start_man = np.where(np.array(nb_seconds_oldest_tle_to_this_tle[isc]) > nb_seconds_first_tle_to_start_sunpointed[index_fm][iman])[0][0]
        ax_sma_average.scatter(nb_seconds_oldest_tle_to_this_tle[isc][index_tle_start_man], sma_tle_at_tle_epoch_all[isc][index_tle_start_man],marker = '|', color = 'b',s = 200)
        if len(np.where(np.array(nb_seconds_oldest_tle_to_this_tle[isc]) > nb_seconds_first_tle_to_end_sunpointed[index_fm][iman])[0]) > 0: # = 0 is the sunpointed maneuver is more recent than the most recent TLE
            index_tle_end_man = np.where(np.array(nb_seconds_oldest_tle_to_this_tle[isc]) > nb_seconds_first_tle_to_end_sunpointed[index_fm][iman])[0][0]
            ax_sma_average.scatter(nb_seconds_oldest_tle_to_this_tle[isc][index_tle_end_man], sma_tle_at_tle_epoch_all[isc][index_tle_end_man],marker = '|', color = 'r', s = 200)

            


    if np.max(sma_tle_at_tle_epoch_all[isc]) > max_sma_tle:
        max_sma_tle = np.max(sma_tle_at_tle_epoch_all[isc])
    if np.min(sma_tle_at_tle_epoch_all[isc]) < min_sma_tle:
        min_sma_tle = np.min(sma_tle_at_tle_epoch_all[isc])

# # add the high drag and sunpointed maneuvers
# isc = 0
# ##highdrag
# for iman in range(nb_highdrag[isc]):   
#     #start man
#     ax_sma_average.plot([nb_seconds_first_tle_to_start_highdrag[isc, iman], nb_seconds_first_tle_to_start_highdrag[isc, iman]], [0, 10000], color = color_arr[iman], linewidth = 1)
#     ax_sma_average.plot([nb_seconds_first_tle_to_end_highdrag[isc, iman], nb_seconds_first_tle_to_end_highdrag[isc, iman]], [0, 10000], color = color_arr[iman], linewidth = 1)

# # ##sunpointed
# # for iman in range(nb_sunpointed[isc]):   
# #     #start man
# #     ax_sma_average.plot([nb_seconds_first_tle_to_start_sunpointed[isc, iman], nb_seconds_first_tle_to_start_sunpointed[isc, iman]], [0, 10000], color = color_arr[iman], linewidth = 1, linestyle = 'dashed')
# #     ax_sma_average.plot([nb_seconds_first_tle_to_end_sunpointed[isc, iman], nb_seconds_first_tle_to_end_sunpointed[isc, iman]], [0, 10000], color = color_arr[iman], linewidth = 1, linestyle = 'dashed')
## space weather
# storm on sep 08 2017
date_storm_start = '2017-09-04T00:00:00'
date_storm_end = '2017-09-09T00:00:00'
date_storm_start = datetime.strptime(date_storm_start, "%Y-%m-%dT%H:%M:%S")
date_storm_end = datetime.strptime(date_storm_end, "%Y-%m-%dT%H:%M:%S")
nb_seconds_first_tle_to_start_storm =  (date_storm_start - oldest_tle).total_seconds()
nb_seconds_first_tle_to_end_storm =  (date_storm_end - oldest_tle).total_seconds()
ax_sma_average.plot([nb_seconds_first_tle_to_start_storm,nb_seconds_first_tle_to_start_storm], [min_sma_tle, max_sma_tle], color = 'grey', alpha = 0.05)
ax_sma_average.plot([nb_seconds_first_tle_to_end_storm,nb_seconds_first_tle_to_end_storm], [min_sma_tle, max_sma_tle], color = 'grey', alpha = 0.05)


ax_sma_average.axvspan(nb_seconds_first_tle_to_start_storm, nb_seconds_first_tle_to_end_storm,  color='grey', alpha = 0.05)
ax_sma_average.text((nb_seconds_first_tle_to_start_storm+nb_seconds_first_tle_to_end_storm)/2, max_sma_tle, 'geom. storm', fontsize = 20, rotation =  90, horizontalalignment = 'center', verticalalignment = 'top')

nb_seconds_in_simu =  ( most_recent_tle - oldest_tle ).total_seconds()
date_ref = oldest_tle
nb_ticks_xlabel = 7
dt_xlabel =  nb_seconds_in_simu / nb_ticks_xlabel # dt for ticks on x axis (in seconds)
xticks = np.arange(0, nb_seconds_in_simu+1, dt_xlabel); 
date_list_str = []
date_list = [date_ref + timedelta(seconds=x-xticks[0]) for x in xticks]
for i in range(len(xticks)):
    if dt_xlabel >= 3*24*3600:
        date_list_str.append( str(date_list[i])[5:10] )
    else:
        date_list_str.append( str(date_list[i])[5:10] + "\n" + str(date_list[i])[11:16] )
        ax_sma_average.xaxis.set_ticks(xticks)
        ax_sma_average.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')
        ax_sma_average.margins(0,0); ax_sma_average.set_xlim([min(xticks), max(xticks)])
#        ax_sma_average.set_xlim([ax_sma_average.get_xlim()[0], most_recent_tle_among_all_sc])


#,transform = ax.transAxes
#ax_sma_average.text(0.05,0.05,''

ax_sma_average.xaxis.set_ticks(xticks)
ax_sma_average.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')
ax_sma_average.margins(0,0); ax_sma_average.set_xlim([min(xticks)-1*24*3600, max(xticks)])
ax_sma_average.set_ylim([min_sma_tle, max_sma_tle])


ax_sma_average.scatter(0.1,0.11, transform = ax_sma_average.transAxes,marker = '.', color = 'b', s = 300 )
ax_sma_average.scatter(0.2,0.11, transform = ax_sma_average.transAxes,marker = '.', color = 'r', s = 300 )
ax_sma_average.text(0.03,0.11, 'HD', color = 'k', fontsize = fontsize_plot, transform = ax_sma_average.transAxes, horizontalalignment = 'center', verticalalignment = 'center')
#ax_sma_average.text(0.2,0.19, 'HD', color = 'r', fontsize = fontsize_plot, transform = ax_sma_average.transAxes, horizontalalignment = 'center', verticalalignment = 'top')

ax_sma_average.scatter(0.1,0.05, transform = ax_sma_average.transAxes,marker = '|', color = 'b', s = 200 )
ax_sma_average.scatter(0.2,0.05, transform = ax_sma_average.transAxes,marker = '|', color = 'r', s = 200 )
ax_sma_average.text(0.03,0.05, 'SP', color = 'k', fontsize = fontsize_plot, transform = ax_sma_average.transAxes, horizontalalignment = 'center', verticalalignment = 'center')

ax_sma_average.text(0.1,0.03, 'start', color = 'b', fontsize = fontsize_plot, transform = ax_sma_average.transAxes, horizontalalignment = 'center', verticalalignment = 'top')
ax_sma_average.text(0.2,0.03, 'end', color = 'r', fontsize = fontsize_plot, transform = ax_sma_average.transAxes, horizontalalignment = 'center', verticalalignment = 'top')

#ax_sma_average.text(0.2,0.09, 'SP', color = 'r', fontsize = fontsize_plot, transform = ax_sma_average.transAxes, horizontalalignment = 'center', verticalalignment = 'top')

#ax_sma_average.scatter(nb_seconds_oldest_tle_to_this_tle[isc][index_tle_end_man], sma_tle_at_tle_epoch_all[isc][index_tle_end_man],marker = '.', color = 'r', s = 300)

legend = ax_sma_average.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), numpoints = 1,  title="", fontsize = fontsize_plot, ncol=4)
legend.get_title().set_fontsize(str(fontsize_plot))


fig_save_name = 'history_sma_with_hd_maneuvers'
fig_save_name = fig_save_name + '.pdf'
fig_sma_average.set_figheight(height_fig)
fig_sma_average.savefig(fig_save_name, facecolor=fig_sma_average.get_facecolor(), edgecolor='none', bbox_inches='tight')  



