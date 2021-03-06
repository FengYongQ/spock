# find rho_control that min error in 18 hours (18 = interval (variable))
# move 3 hours aehad, find rho_control that min error in 18 hours (3 = step_move_save (variable))
# move 3 hours ahead, min error in 18 hours
# so on

# copy of 071318_spock_odtk_ensemble_new_iteration_on_rv.py on Sep 10 2018. Here we assume the r0/v0 has already been otimipized (in first part of script 071318_spock_odtk_ensemble_new_iteration_on_rv.py). A PID is then applied to minimize the along-track distance of SpOCK with respect to the osbervations
#  071318_spock_odtk_ensemble_new_iteration_on_rv.py was itself a of spock_odtk_ensemble_new_iteration_on_rv.py on 071318
# This script runs SpOCK with ensembles on the initial state (r, v ECI). The initial mean r,v is taken from GPS measurements. It's a similiar script ot ~/Google Drive/Work/PhD/Research/Code/cygnss/eclipse/ensemble_ini_state/spock_odtk_ensemble_dev.py but this one here uses GPS measuremnts while the other used Kyle Nave ODTK states.
# ASSUMPTIONS
# first run cygnss_convert_swri_att_to_spock.py to convert the GPS measurements into files readible by SpOCK (attitude)
#- see section "PARAMETERS TO SET UP BEFORE RUNNIG THIS SCRIPT"
#- run SpOCK with a 1s time step 
#- rho_mod_arr must be such that the coeff 1 is included



# PARAMETERS TO SET UP BEFORE RUNNIG THIS SCRIPT
plot_var = 'dist' # dist, ecc, argper
rho_more = 'pole' # equator, pole, mid -> where to add more rho (pole means the ighhes tlatitude of the orbit)
isbig = 0 # if runnign script from Big
ispleiades = 0 # if runnign script from Pleaides

no_prop = 1 # set this variable to 1 to prevent creating SpOCK main input files and propagating them
interval = 18.0 #18.0 # interval of time to compare the two trajectories (data and SpOCK). In hours
step_move_save = 3.0
step_drho = 0.1 # the rho control will vary by this amount to find the optimum rho over an interval
kplist = [1.] # list of proportional gains for PID
kdlist = [1.] # list of derivative gains for PID
kilist = [0.000] # list of integral gains for PID
plot_or_not = 1
inter_start_algo = 2.0
prefix_name = 'may18'
# end of PARAMETERS TO SET UP BEFORE RUNNIG THIS SCRIPT
if rho_more == 'equator':
    rho_phase = 0
elif rho_more == 'pole':
    rho_phase = 0.5
elif rho_more == 'mid':
    rho_phase = 0.25
else:
    print '***! rho_more needs to be equator, pole or mid. The program will stop. !***'; raise Exception
if isbig == 1 & ispleiades == 1:
    print "***! Choose to run on Pleiades or Big, but not both. The program will stop. !***"; raise Exception


import sys
import numpy as np

if isbig == 1:
    sys.path.append("/home/cbv/code/spock/srcPython")
    path_mpirun = '/usr/local/bin/mpirun'
    spice_path = '/raid4/cbv/cspice/data'
    nb_proc = 12
elif ispleiades == 1:
    sys.path.append("/home1/cbussy/Code/spock/srcPython")
    path_mpirun = 'mpiexec'
    spice_path = '/home1/cbussy/cspice/data'
    nb_proc = 0    

else:
    sys.path.append("/Users/cbv/Google Drive/Work/PhD/Research/Code/spock/srcPython")
    path_mpirun = 'mpirun'
    spice_path = '/Users/cbv/cspice/data'
    nb_proc = 4


import pickle
import os

from read_input_file import *
from read_output_file import *
from spock_main_input import *
#if ispleiades != 1:
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.gridspec as gridspec
if ((isbig != 1) & (ispleiades !=1)):
    #from convert_cygnss_obs_ecef_to_eci import *
    import ipdb
from eci_to_lvlh import *
#plt.ion()




# Read r/v of observations
# obs_rv_filename = 'HD_data/spock_FM5_20171216_eng_pvt_query-13527.txt'#'HD_data/spock_FM5_20171216_eng_pvt_query-13527.txt'#'HD_data/spock_FM5_20171216_eng_pvt_query-13527_1800tomorrow.txt' # 'HD_data/spock_FM5_20171216_eng_pvt_query-13527_2days.txt'
# obs_att_filename = 'HD_data/spock_FM5_20171216_eng_adcs_query-13528.txt' #HD_data/spock_FM5_20171216_eng_adcs_query-13528.txt'#'HD_data/spock_FM5_20171216_eng_adcs_query-13528_1800tomorrow.txt' # 'HD_data/spock_FM5_20171216_eng_adcs_query-13528_2days.txt''


obs_rv_filename = 'HD_data/high_drag_data_20180521/spock_FM5_20180521_eng_pvt_query-15601_15d.txt'#spock_FM5_20180521_eng_pvt_query-15601_4d.txt'#spock_FM5_20180521_eng_pvt_query-15601.txt'
obs_att_filename = 'HD_data/high_drag_data_20180521/spock_FM5_20180521_eng_adcs_query-15600_15d.txt'#spock_FM5_20180521_eng_adcs_query-15600_4d.txt'#spock_FM5_20180521_eng_adcs_query-15600.txt'

# #Convert ECEF file to ECI file
# if ((isbig == 1) | (ispleiades == 1)):
#     obs_rv_filename_eci = obs_rv_filename.replace('.txt','_eci.txt')
# else:
#     obs_rv_filename_eci = convert_cygnss_obs_ecef_to_eci(obs_rv_filename)
obs_rv_filename_eci = obs_rv_filename.replace('.txt','_eci.txt')


# Read observation ECI r/v 
obs_rv_file = open(obs_rv_filename_eci)
read_obs_rv_file = obs_rv_file.readlines()
nb_header = 0
while (read_obs_rv_file[nb_header].split()[0] != '#START'):
    nb_header = nb_header + 1
nb_header = nb_header + 1
nb_obs = len(read_obs_rv_file) - nb_header
date_obs = []
date_obs_str = []
r_obs = np.zeros([nb_obs, 3])
v_obs = np.zeros([nb_obs, 3])
ecc_obs = np.zeros([nb_obs])

earth_mu = 398600.4418 # km^3/s^2
orbit_period = 95 * 60. # in seconds
for iobs in range(nb_obs):
    date_obs_str.append( read_obs_rv_file[iobs + nb_header].split()[0] )
    date_obs.append( datetime.strptime(date_obs_str[-1], "%Y-%m-%dT%H:%M:%S" ) )
    r_obs[iobs, 0] = np.float( read_obs_rv_file[iobs + nb_header].split()[1] ) 
    r_obs[iobs, 1] = np.float( read_obs_rv_file[iobs + nb_header].split()[2] ) 
    r_obs[iobs, 2] = np.float( read_obs_rv_file[iobs + nb_header].split()[3] ) 
    v_obs[iobs, 0] = np.float( read_obs_rv_file[iobs + nb_header].split()[4] ) 
    v_obs[iobs, 1] = np.float( read_obs_rv_file[iobs + nb_header].split()[5] ) 
    v_obs[iobs, 2] = np.float( read_obs_rv_file[iobs + nb_header].split()[6] ) 

    mu_earth = 398600.4418; # km^3/s^2 
    rrss = np.linalg.norm(r_obs[iobs, :])
    vrss = np.linalg.norm(v_obs[iobs, :])
    rdotv = np.dot(r_obs[iobs, :], v_obs[iobs, :])
    tempv1 = v_obs[iobs, :] * rdotv
    
    coeff = vrss*vrss - (mu_earth/rrss);
    tempv2 = r_obs[iobs, :] * coeff
    e_vector = tempv2 - tempv1
    coeff = 1.0/mu_earth;
    e_vector = e_vector * coeff
    ecc_obs[iobs] = np.linalg.norm(e_vector)


# Run SpOCK: initial r/v is given by observations + ensemble with std given by x_sigma, y_sigma, etc
date_obs_start_str = date_obs_str[0]
date_obs_start= datetime.strptime(date_obs_start_str, "%Y-%m-%dT%H:%M:%S")
date_obs_end_str = date_obs_str[-1]
date_obs_end= datetime.strptime(date_obs_end_str, "%Y-%m-%dT%H:%M:%S")
interval_sec = interval * 3600.
nb_interval = 56#(int) ( ( date_obs_end - date_obs_start ).total_seconds()/ ( step_move_sec ) ) # !!!!!!!! (int) ( ( date_obs_end - date_obs_start ).total_seconds()/ ( interval_sec ) ) #!!!!!! should be (int) ( ( date_obs_end - date_obs_start ).total_seconds()/ ( interval_sec ) )


print 'nb of intervals:', nb_interval
nb_seconds_since_start = []
distance = []

date_start = date_obs_start
date_end = date_start + timedelta(seconds = interval_sec)
date_end_str = datetime.strftime(date_end, "%Y-%m-%dT%H:%M:%S")
date_start_str = datetime.strftime(date_start, "%Y-%m-%dT%H:%M:%S")

index_obs_interval_start = 0 # !!!!!!!!!!! to change

## SpOCK main input file:
dt  = 1
dt_output = 60 # !!!!!!!!!used to be 1
gravity_order = 20 # !!!!!!!!!! put 50 (or 20)

date_start = date_obs_start#datetime.strptime("2017-12-18T06:00:00", "%Y-%m-%dT%H:%M:%S")#date_obs_start
date_end = date_start + timedelta(seconds = interval_sec)
date_end_str = datetime.strftime(date_end, "%Y-%m-%dT%H:%M:%S")
date_start_str = datetime.strftime(date_start, "%Y-%m-%dT%H:%M:%S")

min_distance_pid = []
ipid_best = [] 
distance_pid = []
distance_lvlh_pid = []
nb_seconds_since_start_pid = []
nb_seconds_since_start_pid = []
date_datetime_round_sec_spock_pid_ok = []

nkp = len(kplist); nkd = len(kdlist); nki = len(kilist); 
nk = (int)( 2. / step_drho ) + 1# this is the maximum of iteration to find the optim rho (since rho_control vaies from -1 to 1 with a step step_drho

last_r0_pid = np.zeros([nk])
last_r1_pid = np.zeros([nk])
last_r2_pid = np.zeros([nk])
last_v0_pid = np.zeros([nk])
last_v1_pid = np.zeros([nk])
last_v2_pid = np.zeros([nk])
index_obs_kept = []
date_obs_pid_ok = []
pid_center = 1 # factor to apply to each pid_mod_arr[ipid]
pid_center_list = []
klist = np.zeros([nk,3])
for ikp in range(nkp):
    kp = kplist[ikp]
    for ikd in range(nkd):
        kd = kdlist[ikd]
        for iki in range(nki):
            ki = kilist[iki]
            klist[ikp*nkd*nki + ikd*nki + iki, 0] = kp
            klist[ikp*nkd*nki + ikd*nki + iki, 1] = kd
            klist[ikp*nkd*nki + ikd*nki + iki, 2] = ki


rho_control = np.zeros([nb_interval]) -0.#-0.5 # -.5 cause first should starts at -0.5
step_derivative = 3 # how may indices to go bakward to compute slope
curr_input = -1
index_period_spock_all_inter = []
index_period_mid_spock_all_inter = []
nb_total_index_spock = 0
distance_lvlh_pid_orbit_average_interval_all_inter = []
distance_lvlh_pid_orbit_amplitude_interval_all_inter = []
distance_lvlh_pid_orbit_mid_average_interval_all_inter = []
distance_lvlh_pid_orbit_mid_amplitude_interval_all_inter = []

ecc_orbit_average_interval_all_inter = []
ecc_obs_orbit_average_interval_all_inter = []
ecc_obs_same_spock_all_inter = []
ecc_spock_ok_pid_all_inter = []
argper_orbit_average_interval_all_inter = []
argper_obs_orbit_average_interval_all_inter = []
argper_obs_same_spock_all_inter = []
argper_spock_ok_pid_all_inter = []

duration_simu = (nb_interval - inter_start_algo) * step_move_save + inter_start_algo * interval # first inter_start_algo are interval hour long, then rest of the intervals are step_move_save hour long
index_period_spock_step_move = np.zeros([nb_interval]) # index in orbit average variables of the end of each interval
index_step_move_save = []
for iinter in range(nb_interval):#!!!!! shoul be nb_interval):
    if iinter < inter_start_algo:
        step_move = interval-0.1 # shoule be = interval
    else:
        step_move = step_move_save
    step_move_sec = step_move * 3600.
    variation_slope_previous_rho = 1e30
    last_error_previous_rho = 1e30
    distance_lvlh_pid_orbit_average_interval_sub = []
    distance_lvlh_pid_orbit_amplitude_interval_sub = []
    distance_lvlh_pid_orbit_mid_average_interval_sub = []
    distance_lvlh_pid_orbit_mid_amplitude_interval_sub = []

    ecc_orbit_average_interval_sub = []
    ecc_obs_orbit_average_interval_sub = []
    argper_orbit_average_interval_sub = []
    argper_obs_orbit_average_interval_sub = []

    nb_seconds_since_start_pid_inter = []
    index_obs_kept_inter = []
    distance_pid_interval = []
    distance_lvlh_pid_interval = []
    print ''
    print ''
    print 'NEW INTERVAL', iinter, nb_interval-1,
    if iinter == 0:
        # This calcualted in first aprt of 071318_spock_odtk_ensemble_new_iteration_on_rv
#         # with spock_FM5_20171216_eng_pvt_query...
#         r0 = '-2.54076587561000e+03'#
#         r1 = '-5.06266991514000e+03'#
#         r2 = '-3.95089081204000e+03'#
#         v0 = '6.76840081300000e+00'#'
#         v1 = '-3.44599707500000e+00'#
#         v2 = '4.16872280000000e-02'#'
#         # with spock_FM5_20180521_eng_pvt_query...
        r0 = '5.10860462753000e+03'
        r1 = '3.05387469849000e+03'
        r2 = '-3.52007146222000e+03'
        v0 = '-2.67948375200000e+00'
        v1 = '6.80476316700000e+00'
        v2 = '2.01646612700000e+00'
        
        # observations:
#         r0 = '5.10860318107304e+03'
#         r1 = '3.05386257583597e+03' 
#         r2 = '-3.52007809557189e+03' 
#         v0 = '-2.67948999739825e+00' 
#         v1 = '6.80476356644363e+00'
#         v2 = '2.01648680191435e+00'



    else:
        r0 = format(last_r0, '.14e')
        r1 = format(last_r1, '.14e')
        r2 = format(last_r2, '.14e')
        v0 = format(last_v0, '.14e')
        v1 = format(last_v1, '.14e')
        v2 = format(last_v2, '.14e')

    print 'Initial state:', r0, r1, r2, v0, v1, v2
    print ''

    drho = 0 # first iteration eblow: keep the same rho_control as the previous interval
    irho = -1
    error_change_sign = 0
    while ( ( error_change_sign == 0 ) & ( np.abs(rho_control[iinter-1] + drho) < 1 ) ):
        irho = irho + 1
        # if iinter == 6: # !!!!!!!!!!! REMOVE
        #     rho_control[iinter-1]  = -0.4

        if iinter >= inter_start_algo:

            rho_control[iinter] = rho_control[iinter-1] + drho
            rho_control_spock = ['msis_lat_depend', 1 + rho_control[iinter], 0.*(1 + rho_control[iinter]), rho_phase] #1 + rho_control[iinter]
        else:# don't apply the PID for the first 3 intervals (36 horus) and take rho_control = 0
            rho_control[iinter] = -0.5#-0.46# -0.5 # !!!!!!uncomment
            rho_control_spock = 1 + rho_control[iinter] # not latitude dependent -> equivalent to ['msis_lat_depend', 1 + rho_control, 0, 0]
            error_change_sign = 1 #no iteration for this interval
        # !!!!!!! remove block
        print 'irho ' + str(irho) + ' | rho_control ' + str(rho_control[iinter])

        # # rho_control can't be below -1 otherwises the density si negative. 
        # if rho_control[iinter] <= -1:
        #     rho_control[iinter] = -0.99

        main_input_filename = prefix_name + '_' + rho_more + '_interval' + format(interval, ".1f").replace(".","_") + "_iinter" + str(iinter)  + '_irho' + str(irho) + '.txt'
        if no_prop != 1:

            spock_main_input( # need to be in spokc/srcPython to run this script   
                main_input_filename,
                # for TIME section
                   date_start_str, # first interval: same as during the r/v optimization. subsequent intervals: last date of previous interval
                date_end_str,
                dt,
                # for SPACECRAFT section
                        1,
                '0',
                29,
                "cygnss_geometry_2016_acco09.txt", #"cygnss_geometry_2016_smaller_solar_radiation_coeff.txt", #"cygnss_geometry_2016.txt",#"cygnss_geometry_2016_acco09.txt",
                # for ORBIT section
                    ['state_eci','(' + r0 + '; ' + r1 + '; ' + r2 + ') (' + v0 + '; ' + v1 + '; ' + v2 + ')' ],
                # for FORCES section
                gravity_order, # !!!!!!!!!!! put back 20
                "drag solar_pressure sun_gravity moon_gravity", # !!!!!!!!!!!!! put back to "drag sun_gravity moon_gravity"
                'swpc',
                # for OUTPUT section
                        "out",
                dt_output, 
                # for ATTITUDE section
                obs_att_filename,
                # for GROUND_STATIONS section
                        "0",
                # for SPICE section
                        spice_path,
                # FOR #DENSITY_MOD section
                rho_control_spock
            )

            #Run SpOCK

            #if iinter >= inter_start_algo:
            if iinter >= 1800:
            #if ((iinter > 0) | ((iinter== 0) & (irho >=2))):
                if ispleiades != 1:
                    os.system(path_mpirun + ' -np 1 spock_dev ' + main_input_filename)
                else:
                    os.system(path_mpirun + ' /home1/cbussy/spock ' + main_input_filename)

        #save position and velocity
        #os.system("python state_dev.py ./ " + main_input_filename + " save position velocity")


        # Read the position and velocity predicted by SpOCK
        isc = 0
        var_in, var_in_order = read_input_file(main_input_filename)

        output_file_path_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]; 
        output_file_name_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')]; 
        var_to_read = ["position", "velocity", "eccentricity", "argument_perigee"]
        var_out, var_out_order = read_output_file( output_file_path_list[isc] + output_file_name_list[isc], var_to_read )
        date_spock = np.array(var_out[find_in_read_input_order_variables(var_out_order, 'date')])
        date_datetime_round_sec_spock = np.array(var_out[find_in_read_input_order_variables(var_out_order, 'date_datetime_round_sec')])
        r_spock = var_out[find_in_read_input_order_variables(var_out_order, 'position')]
        v_spock = var_out[find_in_read_input_order_variables(var_out_order, 'velocity')]
        ecc_spock = var_out[find_in_read_input_order_variables(var_out_order, 'eccentricity')]
        argper_spock = var_out[find_in_read_input_order_variables(var_out_order, 'argument_perigee')]
        n_spock = len(date_spock)

        if irho == 0:
            index_spock_same_date_as_obs_pid = []
            #if iinter == 0: # for the next interval, start date_obs[iobs] at the last observation of the previous interval
            iobs = np.where(np.array(date_obs) == date_start)[0][0]
            #ipdb.set_trace()
            print 'iobs', iobs
            while iobs < nb_obs:
                if date_obs[iobs] > date_datetime_round_sec_spock[-1]:
                    break
                else:
                    if len(index_spock_same_date_as_obs_pid) == 0:
                        first_obs = iobs
                    if len(np.where(date_datetime_round_sec_spock == date_obs[iobs])[0]) != 0:#can be = 0 if an observation is missing at that time
                        index_spock_same_date_as_obs_pid.append(np.where(date_datetime_round_sec_spock == date_obs[iobs])[0][0])
                        nb_seconds_since_start_pid_inter.append( ( date_obs[iobs] - date_obs[0] ).total_seconds() )
                        index_obs_kept_inter.append(iobs)
                        iobs = iobs + 60
                    else: # find next obs
                        while len(np.where(date_datetime_round_sec_spock == date_obs[iobs])[0]) == 0:
                            iobs = iobs + 1
                        index_spock_same_date_as_obs_pid.append(np.where(date_datetime_round_sec_spock == date_obs[iobs])[0][0])
                        nb_seconds_since_start_pid_inter.append( ( date_obs[iobs] - date_obs[0] ).total_seconds() )
                        index_obs_kept_inter.append(iobs)
                        iobs = iobs + 60

                        
            nb_seconds_since_start_pid.append(nb_seconds_since_start_pid_inter)
            index_obs_kept.append(index_obs_kept_inter)
            n = len(index_spock_same_date_as_obs_pid) #!!!!!!!!!! j-index_interval[iinter]
            date_datetime_round_sec_spock_pid_ok.append(date_datetime_round_sec_spock[index_spock_same_date_as_obs_pid])
            date_obs_pid_ok.append(np.array(date_obs)[index_obs_kept[-1]])

        # Compare SpOCK and data
        date_datetime_round_sec_spock_ok_pid = date_datetime_round_sec_spock[index_spock_same_date_as_obs_pid]
        r_spock_ok_pid = np.zeros([n, 3])
        r_spock_ok_pid[:, 0] = r_spock[index_spock_same_date_as_obs_pid, 0]
        r_spock_ok_pid[:, 1] = r_spock[index_spock_same_date_as_obs_pid, 1]
        r_spock_ok_pid[:, 2] = r_spock[index_spock_same_date_as_obs_pid, 2]
        v_spock_ok_pid = np.zeros([n, 3])
        v_spock_ok_pid[:, 0] = v_spock[index_spock_same_date_as_obs_pid, 0]
        v_spock_ok_pid[:, 1] = v_spock[index_spock_same_date_as_obs_pid, 1]
        v_spock_ok_pid[:, 2] = v_spock[index_spock_same_date_as_obs_pid, 2]
        ecc_spock_ok_pid = np.zeros([n])
        ecc_spock_ok_pid = ecc_spock[index_spock_same_date_as_obs_pid]
        argper_spock_ok_pid = np.zeros([n])
        argper_spock_ok_pid = argper_spock[index_spock_same_date_as_obs_pid]

        #if pid_mod_arr[irho] == 1:
        if irho == 0:
            #ipdb.set_trace()
            index_step_move = np.where(date_datetime_round_sec_spock_ok_pid == (date_start + timedelta(seconds = step_move_sec)))[0][0]
            index_step_move_save.append(index_step_move)
        last_r0_pid[irho] = r_spock_ok_pid[index_step_move, 0]
        last_r1_pid[irho] = r_spock_ok_pid[index_step_move, 1]
        last_r2_pid[irho] = r_spock_ok_pid[index_step_move, 2]
        last_v0_pid[irho] = v_spock_ok_pid[index_step_move, 0]
        last_v1_pid[irho] = v_spock_ok_pid[index_step_move, 1]
        last_v2_pid[irho] = v_spock_ok_pid[index_step_move, 2]
        print 'interval', iinter
        #print 'Final state', format(last_r0_pid[irho],".14e"),format(last_r1_pid[irho],".14e"),format(last_r2_pid[irho],".14e"), format(last_v0_pid[irho],".14e"),format(last_v1_pid[irho],".14e"),format(last_v2_pid[irho],".14e")
            


        distance_lvlh_pid_sub = []
        # distance represents the along-track distance from observation to SpOCK. > 0 means SpOCK is trailing, < 0 means SpOCK is leading
        nb_seconds_since_start_interval = 0
        iperiod_find = 0
        if irho == 0:
            index_period_spock_temp = []
            ecc_obs_same_spock_all_inter.append( ecc_obs[index_obs_kept[-1]] )
        for i in range(n):
            distance_here = r_obs[index_obs_kept[-1]][i, :] - r_spock_ok_pid[i, :]
            distance_lvlh_pid_sub.append( eci_to_lvlh(r_spock_ok_pid[i, :], v_spock_ok_pid[i, :], distance_here)[0] ) #[0]: along-track
            # "if" below used to calculate orbit average error
            if irho == 0:
                nb_seconds_since_start_interval = ( date_datetime_round_sec_spock_pid_ok[-1][i] - date_datetime_round_sec_spock_pid_ok[-1][0] ).total_seconds()
                if nb_seconds_since_start_interval >= orbit_period * iperiod_find:
                    iperiod_find = iperiod_find + 1
                    index_period_spock_temp.append(i)
                    if irho == 0:
                        if ((nb_seconds_since_start_interval >= step_move_sec) & (index_period_spock_step_move[iinter] == 0 )): # don't go twice in here so second condition
                            index_period_spock_step_move[iinter] =  len(index_period_spock_temp) - 1
        
        distance_lvlh_pid_interval.append( distance_lvlh_pid_sub )
        # calculate orbit average error
        if irho == 0:
            nb_period_this_inter = iperiod_find
            index_period_spock = np.zeros([2*(nb_period_this_inter-1)])
            index_period_mid_spock = np.zeros([(nb_period_this_inter-1)])
            nb_total_index_spock = nb_total_index_spock + len(r_spock_ok_pid)
        distance_lvlh_pid_orbit_average_interval = np.zeros([2*(nb_period_this_inter-1)])
        distance_lvlh_pid_orbit_amplitude_interval = np.zeros([2*(nb_period_this_inter-1)])
        distance_lvlh_pid_orbit_mid_average_interval = np.zeros([(nb_period_this_inter-1)])
        distance_lvlh_pid_orbit_mid_amplitude_interval = np.zeros([(nb_period_this_inter-1)])

        ecc_orbit_average_interval = np.zeros([2*(nb_period_this_inter-1)])
        ecc_obs_orbit_average_interval = np.zeros([2*(nb_period_this_inter-1)])
        argper_orbit_average_interval = np.zeros([2*(nb_period_this_inter-1)])

        for iperiod in range(nb_period_this_inter-1):
            iorbit_start = index_period_spock_temp[iperiod]
            iorbit_stop = index_period_spock_temp[iperiod+1]
            distance_lvlh_pid_orbit_average_interval[2*iperiod] = np.mean( distance_lvlh_pid_sub[iorbit_start:iorbit_stop] ) 
            distance_lvlh_pid_orbit_average_interval[2*iperiod+1] = np.mean( distance_lvlh_pid_sub[iorbit_start:iorbit_stop] ) 
            distance_lvlh_pid_orbit_amplitude_interval[2*iperiod] = np.max( distance_lvlh_pid_sub[iorbit_start:iorbit_stop] )  - np.mean( distance_lvlh_pid_sub[iorbit_start:iorbit_stop] ) 
            distance_lvlh_pid_orbit_amplitude_interval[2*iperiod+1] = np.max( distance_lvlh_pid_sub[iorbit_start:iorbit_stop] )  - np.mean( distance_lvlh_pid_sub[iorbit_start:iorbit_stop] ) 

            distance_lvlh_pid_orbit_mid_average_interval[iperiod] = np.mean( distance_lvlh_pid_sub[iorbit_start:iorbit_stop] ) 
            distance_lvlh_pid_orbit_mid_amplitude_interval[iperiod] = np.max( distance_lvlh_pid_sub[iorbit_start:iorbit_stop] )  - np.mean( distance_lvlh_pid_sub[iorbit_start:iorbit_stop] ) 


            ecc_orbit_average_interval[2*iperiod] = np.mean( ecc_spock_ok_pid[iorbit_start:iorbit_stop] ) 
            ecc_orbit_average_interval[2*iperiod+1] = np.mean( ecc_spock_ok_pid[iorbit_start:iorbit_stop] ) 
            ecc_obs_orbit_average_interval[2*iperiod] = np.mean( ecc_obs_same_spock_all_inter[-1][iorbit_start:iorbit_stop] ) 
            ecc_obs_orbit_average_interval[2*iperiod+1] = np.mean( ecc_obs_same_spock_all_inter[-1][iorbit_start:iorbit_stop] ) 

            argper_orbit_average_interval[2*iperiod] = np.mean( argper_spock_ok_pid[iorbit_start:iorbit_stop] ) 
            argper_orbit_average_interval[2*iperiod+1] = np.mean( argper_spock_ok_pid[iorbit_start:iorbit_stop] ) 

            index_period_spock[2*iperiod] = index_period_spock_temp[iperiod]
            index_period_spock[2*iperiod+1] = index_period_spock_temp[iperiod+1]

            index_period_mid_spock[iperiod] = ( index_period_spock_temp[iperiod+1] + index_period_spock_temp[iperiod] ) / 2
        #ipdb.set_trace()    
            #print 'ZZZZZZZZZZZZZZZZZZZZZZZZ', distance_lvlh_pid_orbit_average_interval_sub
        distance_lvlh_pid_orbit_average_interval_sub.append(distance_lvlh_pid_orbit_average_interval)
        distance_lvlh_pid_orbit_amplitude_interval_sub.append(distance_lvlh_pid_orbit_amplitude_interval)
        distance_lvlh_pid_orbit_mid_average_interval_sub.append(distance_lvlh_pid_orbit_mid_average_interval)
        distance_lvlh_pid_orbit_mid_amplitude_interval_sub.append(distance_lvlh_pid_orbit_mid_amplitude_interval)

        ecc_orbit_average_interval_sub.append(ecc_orbit_average_interval)
        ecc_obs_orbit_average_interval_sub.append(ecc_obs_orbit_average_interval)
        argper_orbit_average_interval_sub.append(argper_orbit_average_interval)

        #print 'YYYYYYYYYYYYYYYYYYYYYYY', distance_lvlh_pid_orbit_average_interval
        #print 'XXXXXXXXXXXXXXXXXXXXX', distance_lvlh_pid_orbit_average_interval_sub
        # if irho == 1:
        #     raise Exception
        slope_orbit_average_error_inter_start_to_end = distance_lvlh_pid_orbit_average_interval[-1] - distance_lvlh_pid_orbit_average_interval[0]
        last_error = distance_lvlh_pid_orbit_average_interval[-1]
        variation_slope = np.abs(slope_orbit_average_error_inter_start_to_end)

        sign_slope = np.sign(slope_orbit_average_error_inter_start_to_end)
        if irho == 0: # the first iteration tells which direction to go, ie if we need to add or remove density
            sign_step_drho = sign_slope
            index_period_spock_all_inter.append(list(index_period_spock))#+nb_total_index_spock))
            index_period_mid_spock_all_inter.append(list(index_period_mid_spock))#+nb_total_index_spock))
        #if ( (sign_slope != sign_step_drho) | (iinter <= 1)): # in this case (first condition), it means that we've added (or removed) too much density and inverted the trend so we found the optimum rho. So we'll move to the next inter. iinter<=2 is here becasue for the first 3 intervals ndistance_lvlh_pid_oro iteratio
        sign_last_error_previous_rho = np.sign(last_error_previous_rho)
        if (irho == 0):
            sign_last_error_previous_rho = np.sign(last_error)
        if ( (np.sign(last_error) != sign_last_error_previous_rho) | (iinter < inter_start_algo) | ( np.abs(rho_control[iinter-1] + drho + step_drho) >= 1 ) | ( np.abs(rho_control[iinter-1] + drho - step_drho) >=1  ) ): # in this case (first condition), it means that we've added (or removed) too much density and inverted the trend so we found the optimum rho. So we'll move to the next inter. iinter<=2 is here becasue for the first 3 intervals ndistance_lvlh_pid_oro iteratio
            error_change_sign = 1
            
            # start and end dates of next interval
            date_start = date_start + timedelta(seconds = step_move_sec)
            date_start_str = datetime.strftime(date_start, "%Y-%m-%dT%H:%M:%S")
            date_end_str = datetime.strftime(date_start + timedelta(seconds = interval_sec), "%Y-%m-%dT%H:%M:%S")

            # initials tate of next interval is final state of current inter with optim rho
            if iinter < inter_start_algo:
                iii = 0
            else:
                iii = 1 # except for the fist inter_start_algo-1 intervals, there was at least 2 iterations. the last one is to throw awau because variation_slope > variation_slope_previous_rho
                rho_control[iinter] = previous_rho_control #rho_control[iinter] -  step_drho * sign_step_drho
            last_r0 = last_r0_pid[irho-iii] # the last irho is to trhow away
            last_r1 = last_r1_pid[irho-iii]
            last_r2 = last_r2_pid[irho-iii]
            last_v0 = last_v0_pid[irho-iii]
            last_v1 = last_v1_pid[irho-iii]
            last_v2 = last_v2_pid[irho-iii]

            distance_lvlh_pid_orbit_average_interval_all_inter.append(distance_lvlh_pid_orbit_average_interval_sub)
            distance_lvlh_pid_orbit_amplitude_interval_all_inter.append(distance_lvlh_pid_orbit_amplitude_interval_sub)

            distance_lvlh_pid_orbit_mid_average_interval_all_inter.append(distance_lvlh_pid_orbit_mid_average_interval_sub)
            distance_lvlh_pid_orbit_mid_amplitude_interval_all_inter.append(distance_lvlh_pid_orbit_mid_amplitude_interval_sub)

            ecc_orbit_average_interval_all_inter.append(ecc_orbit_average_interval_sub)
            ecc_obs_orbit_average_interval_all_inter.append(ecc_obs_orbit_average_interval_sub)
            ecc_spock_ok_pid_all_inter.append(ecc_spock_ok_pid)

            argper_orbit_average_interval_all_inter.append(argper_orbit_average_interval_sub)
            argper_spock_ok_pid_all_inter.append(argper_spock_ok_pid)



            print 'last_error' , last_error, last_error_previous_rho, rho_control[iinter]
            print 'OPTIMUM RHO CONTROL', rho_control[:iinter+1] 
        else:
            print 'last_error' , last_error, last_error_previous_rho, rho_control[iinter]
            previous_rho_control = rho_control[iinter] 
            last_error_previous_rho = last_error
            if last_error > 0:
                drho = drho + step_drho 
            else:
                drho = drho - step_drho 
            #print 'orbit average error', distance_lvlh_pid_orbit_average_interval


#             # # ################### FIGURE: distance for each rho_control of current interval. These figures will be overwritten by the next interval
#             height_fig = 11
#             ratio_fig_size = 4./3
#             fontsize_plot = 20

#             ######
#             fig_title = ''#'Distance between SpOCK and data for different density coefficient' #'Distance with respect to pid = 0.7'#'Distance between SpOCK and data for different density coefficient'
#             y_label = 'Distance (m)'
#             x_label = 'Time (hours)' 

#             fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
#             fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
#             plt.rc('font', weight='bold') ## make the labels of the ticks in bold
#             gs = gridspec.GridSpec(1, 1)
#             gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
#             ax = fig.add_subplot(gs[0, 0])

#             ax.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
#             ax.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

#             [i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure
#             ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
#             plt.rc('font', weight='bold') ## make the labels of the ticks in bold


#             # Previous intervals
#             for iinter_loop in range(iinter):
#                 ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])/3600., np.array(distance_lvlh_pid[iinter_loop][-1])*1000, linewidth = 2, color = 'b')
#                 ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_spock_all_inter[iinter_loop]).astype(int)]/3600., np.array(distance_lvlh_pid_orbit_average_interval_all_inter[iinter_loop][-1])*1000, linewidth = 2, color = 'magenta')
#                     # ax.plot(np.array(nb_seconds_since_start_pid[-1])[index_period_spock_all_inter[-1]][:-1]/3600, distance_lvlh_pid_orbit_average_interval)
#                     # ax.plot(np.array(nb_seconds_since_start_pid[1]) / 3600, distance_lvlh_pid_sub)

#                 ax.plot([np.array(nb_seconds_since_start_pid[iinter_loop][0])/3600., np.array(nb_seconds_since_start_pid[iinter_loop][0])/3600.], [-200, np.array(distance_lvlh_pid[iinter_loop][-1][0])*1000], linewidth = 2, color = 'r', linestyle = 'dashed')
#                 ax.plot([0,duration_simu], [0,0], linewidth = 2, linestyle = 'dashed', color = 'b')
#                 ax.text(np.array(nb_seconds_since_start_pid[iinter_loop][0])/3600., np.array(distance_lvlh_pid[iinter_loop][-1][0])*1000, format(rho_control[iinter_loop], ".2f"), horizontalalignment = 'left', fontsize = fontsize_plot, weight = 'bold', color = 'r', verticalalignment = 'center', label = 'rho_control')

#             # Current interval: all irho so far
#             for irho_here in range(len(distance_lvlh_pid_orbit_average_interval_sub)):
#                 ax.plot(np.array(nb_seconds_since_start_pid[-1])[np.array(index_period_spock_all_inter[-1]).astype(int)]/3600., np.array(distance_lvlh_pid_orbit_average_interval_sub[irho_here])*1000, linewidth = 2, color = 'magenta')
#                 #print irho_here, np.array(distance_lvlh_pid_orbit_average_interval_sub[irho_here])[-1]*1000
#             ax.text(duration_simu/2., -200, 'SpOCK in front -> need rho_control < 0', horizontalalignment = 'center', verticalalignment = 'bottom', fontsize = fontsize_plot, weight = 'bold')
#             ax.text(duration_simu/2., 1200, 'SpOCK behind -> need rho_control > 0', horizontalalignment = 'center', verticalalignment = 'top', fontsize = fontsize_plot, weight = 'bold')

#             ax.set_xlim([0, duration_simu]); ax.set_ylim([-200, 1200])
#             ax.margins(0,0)


#             fig_save_name = 'fig/optim_nbinter' + str(nb_interval) + "_iinter"+ str(iinter) +  "_rhocontrol" + format(rho_control[iinter], ".1f").replace(".","") + ".pdf"
#             fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

                
    distance_lvlh_pid.append( distance_lvlh_pid_interval )
    # if iinter == 3:
    #     raise Exception
    print '-->\n-->'

    #if iinter == 0:
    ################### FIGURES ###################
    height_fig = 11
    ratio_fig_size = 4./3
    fontsize_plot = 20

    ######
    fig_title = ''#'Distance between SpOCK and data for different density coefficient' #'Distance with respect to pid = 0.7'#'Distance between SpOCK and data for different density coefficient'
    x_label = 'Time (hours)' 

    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
    fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    gs = gridspec.GridSpec(1, 1)
    gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
    ax = fig.add_subplot(gs[0, 0])


    ax.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

    [i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure
    ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
        


    for iinter_loop in range(iinter+1):
        if iinter_loop < inter_start_algo:
            iii = -1
            if plot_var == 'dist':
                #index_period_spock_step_move[iinter_loop] = -0.5 # *2 gives the last index, which is what we want for the first inter_start_algo because they last interval hours
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[:index_step_move_save[iinter_loop]+1]/3600., np.array(distance_lvlh_pid[iinter_loop][iii])[:index_step_move_save[iinter_loop]+1]*1000, linewidth = 2, color = 'b', alpha = 0.3)
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_spock_all_inter[iinter_loop]).astype(int)]/3600., np.array(distance_lvlh_pid_orbit_average_interval_all_inter[iinter_loop][iii])*1000, linewidth = 4, color = 'magenta') #-2 becaue the last one is to throw away
            elif plot_var == 'ecc':
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[:index_step_move_save[iinter_loop]+1]/3600., ecc_obs_same_spock_all_inter[iinter_loop][:index_step_move_save[iinter_loop]+1], linewidth = 2, color = 'r', alpha = 0.3)
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_spock_all_inter[iinter_loop]).astype(int)]/3600., np.array(ecc_obs_orbit_average_interval_all_inter[iinter_loop][iii]), linewidth = 4, color = 'r') #-2 becaue the last one is to throw away
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[:index_step_move_save[iinter_loop]+1]/3600., ecc_spock_ok_pid_all_inter[iinter_loop][:index_step_move_save[iinter_loop]+1], linewidth = 2, color = 'b', alpha = 0.3)
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_spock_all_inter[iinter_loop]).astype(int)]/3600., np.array(ecc_orbit_average_interval_all_inter[iinter_loop][iii]), linewidth = 4, color = 'b') #-2 becaue the last one is to throw away
            elif plot_var == 'argper':
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[:index_step_move_save[iinter_loop]+1]/3600., argper_spock_ok_pid_all_inter[iinter_loop][:index_step_move_save[iinter_loop]+1], linewidth = 2, color = 'b', alpha = 0.3)
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_spock_all_inter[iinter_loop]).astype(int)]/3600., np.array(argper_orbit_average_interval_all_inter[iinter_loop][iii]), linewidth = 4, color = 'b') #-2 becaue the last one is to throw away
        else:
            iii = -2
            if plot_var == 'dist':
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[:index_step_move_save[iinter_loop]+1]/3600., np.array(distance_lvlh_pid[iinter_loop][iii])[:index_step_move_save[iinter_loop]+1]*1000, linewidth = 2, color = 'b', alpha = 0.3)
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_spock_all_inter[iinter_loop]).astype(int)[:(int)(2*index_period_spock_step_move[iinter_loop])]]/3600., np.array(distance_lvlh_pid_orbit_average_interval_all_inter[iinter_loop][iii])[:(int)(2*index_period_spock_step_move[iinter_loop])]*1000, linewidth = 4, color = 'magenta') #-2 becaue the last one is to throw away
            elif plot_var == 'ecc':
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[:index_step_move_save[iinter_loop]+1]/3600., ecc_obs_same_spock_all_inter[iinter_loop][:index_step_move_save[iinter_loop]+1], linewidth = 2, color = 'r', alpha = 0.3)
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_spock_all_inter[iinter_loop]).astype(int)]/3600., np.array(ecc_obs_orbit_average_interval_all_inter[iinter_loop][iii]), linewidth = 4, color = 'r') #-2 becaue the last one is to throw away
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[:index_step_move_save[iinter_loop]+1]/3600., ecc_spock_ok_pid_all_inter[iinter_loop][:index_step_move_save[iinter_loop]+1], linewidth = 2, color = 'b', alpha = 0.3)
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_spock_all_inter[iinter_loop]).astype(int)]/3600., np.array(ecc_orbit_average_interval_all_inter[iinter_loop][iii]), linewidth = 4, color = 'b') #-2 becaue the last one is to throw away
            elif plot_var == 'argper':
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[:index_step_move_save[iinter_loop]+1]/3600., argper_spock_ok_pid_all_inter[iinter_loop][:index_step_move_save[iinter_loop]+1], linewidth = 2, color = 'b', alpha = 0.3)
                ax.plot(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_spock_all_inter[iinter_loop]).astype(int)]/3600., np.array(argper_orbit_average_interval_all_inter[iinter_loop][iii]), linewidth = 4, color = 'b') #-2 becaue the last one is to throw away


    ax.margins(0,0)
    if plot_var == 'dist':
        ax.plot([0, duration_simu], [0,0], linestyle = 'dashed', linewidth = 2, color = 'black')
        ax.set_xlim([0, duration_simu]); ax.set_ylim([-200, 1200]) 
        ax.text(duration_simu/2., -200, 'SpOCK in front -> need rho_control < 0', horizontalalignment = 'center', verticalalignment = 'bottom', fontsize = fontsize_plot, weight = 'bold')
        ax.text(duration_simu/2., 1200, 'SpOCK behind -> need rho_control > 0', horizontalalignment = 'center', verticalalignment = 'top', fontsize = fontsize_plot, weight = 'bold')
        fig_save_name = 'fig/' + prefix_name + '_' + rho_more + '_nbinter' + str(nb_interval) + "_iinter"+ str(iinter) +  "_rhocontrol" + format(rho_control[iinter], ".1f").replace(".","") + ".pdf"
        y_label = 'Distance (m)'
    elif plot_var == 'ecc':
        fig_save_name = 'fig/' + prefix_name + '_' +rho_more + 'nbinter' + str(nb_interval) + "_iinter"+ str(iinter) +  "_rhocontrol" + format(rho_control[iinter], ".1f").replace(".","") + "_eccentricity.pdf"
        y_label = 'Eccentricity'
    elif plot_var == 'argper':
        y_label = 'Argument of perigee ' + u'(\N{DEGREE SIGN})'
        fig_save_name = 'fig/' + prefix_name + '_' + rho_more + 'nbinter' + str(nb_interval) + "_iinter"+ str(iinter) +  "_rhocontrol" + format(rho_control[iinter], ".1f").replace(".","") + "_argument_perigee.pdf"

    ax.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  
#     if iinter == 10:
#         ipdb.set_trace()

raise Exception

distance_lvlh_pid_concantenate = []
nb_seconds_since_start_pid_concatenate = []

# 2 identical values per orbt (occurring at start and end of orbit)
distance_lvlh_pid_average_concantenate = []
nb_seconds_since_start_pid_average_concatenate = []

# 1 value per orbit (occurring at center of orbit)
distance_lvlh_pid_average_mid_concantenate = []
nb_seconds_since_start_pid_average_mid_concatenate = []
distance_lvlh_pid_amplitude_mid_concantenate = []
nb_seconds_since_start_pid_amplitude_mid_concatenate = []

for iinter_loop in range(nb_interval):
    if iinter_loop < inter_start_algo:
        iii = -1
        # start and end of orbit
        distance_lvlh_pid_average_concantenate = distance_lvlh_pid_average_concantenate + list(np.array(distance_lvlh_pid_orbit_average_interval_all_inter[iinter_loop][iii]))
        nb_seconds_since_start_pid_average_concatenate = nb_seconds_since_start_pid_average_concatenate + list(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_spock_all_inter[iinter_loop]).astype(int)])
        # center of orbit
        distance_lvlh_pid_average_mid_concantenate = distance_lvlh_pid_average_mid_concantenate + list(np.array(distance_lvlh_pid_orbit_mid_average_interval_all_inter[iinter_loop][iii]))
        distance_lvlh_pid_amplitude_mid_concantenate = distance_lvlh_pid_amplitude_mid_concantenate + list(np.array(distance_lvlh_pid_orbit_mid_amplitude_interval_all_inter[iinter_loop][iii]))
        nb_seconds_since_start_pid_average_mid_concatenate = nb_seconds_since_start_pid_average_mid_concatenate + list(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_mid_spock_all_inter[iinter_loop]).astype(int)])

    else: 
        iii = -2
        # start and end of orbit
        distance_lvlh_pid_average_concantenate = distance_lvlh_pid_average_concantenate + list(np.array(distance_lvlh_pid_orbit_average_interval_all_inter[iinter_loop][iii])[:(int)(2*index_period_spock_step_move[iinter_loop])])
        nb_seconds_since_start_pid_average_concatenate = nb_seconds_since_start_pid_average_concatenate + list(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_spock_all_inter[iinter_loop]).astype(int)[:(int)(2*index_period_spock_step_move[iinter_loop])]])
        # center of orbit     
        distance_lvlh_pid_average_mid_concantenate = distance_lvlh_pid_average_mid_concantenate + list(np.array(distance_lvlh_pid_orbit_mid_average_interval_all_inter[iinter_loop][iii])[:(int)(2*index_period_spock_step_move[iinter_loop])])
        distance_lvlh_pid_amplitude_mid_concantenate = distance_lvlh_pid_amplitude_mid_concantenate + list(np.array(distance_lvlh_pid_orbit_mid_amplitude_interval_all_inter[iinter_loop][iii])[:(int)(2*index_period_spock_step_move[iinter_loop])])
        nb_seconds_since_start_pid_average_mid_concatenate = nb_seconds_since_start_pid_average_mid_concatenate + list(np.array(nb_seconds_since_start_pid[iinter_loop])[np.array(index_period_mid_spock_all_inter[iinter_loop]).astype(int)[:(int)(2*index_period_spock_step_move[iinter_loop])]])

    distance_lvlh_pid_concantenate = distance_lvlh_pid_concantenate +  list(np.array(distance_lvlh_pid[iinter_loop][iii])[:index_step_move_save[iinter_loop]+1])
    nb_seconds_since_start_pid_concatenate = nb_seconds_since_start_pid_concatenate + list(np.array(nb_seconds_since_start_pid[iinter_loop])[:index_step_move_save[iinter_loop]+1])


nb_seconds_since_start_pid_concatenate_arr = np.array(nb_seconds_since_start_pid_concatenate)
distance_lvlh_pid_concantenate_arr = np.array(distance_lvlh_pid_concantenate)

nb_seconds_since_start_pid_average_concatenate_arr = np.array(nb_seconds_since_start_pid_average_concatenate)
distance_lvlh_pid_average_concantenate_arr = np.array(distance_lvlh_pid_average_concantenate)

nb_seconds_since_start_pid_average_mid_concatenate_arr = np.array(nb_seconds_since_start_pid_average_mid_concatenate)
distance_lvlh_pid_average_mid_concantenate_arr = np.array(distance_lvlh_pid_average_mid_concantenate)
distance_lvlh_pid_amplitude_mid_concantenate_arr = np.array(distance_lvlh_pid_amplitude_mid_concantenate)

pickle_root = 'pickle/' + prefix_name + '_' + rho_more
pickle.dump([duration_simu, nb_interval, nb_seconds_since_start_pid_concatenate_arr, distance_lvlh_pid_concantenate_arr, nb_seconds_since_start_pid_average_concatenate_arr, \
                 distance_lvlh_pid_average_concantenate_arr, nb_seconds_since_start_pid_average_mid_concatenate_arr, \
                 distance_lvlh_pid_average_mid_concantenate_arr, distance_lvlh_pid_amplitude_mid_concantenate_arr], open(pickle_root + ".pickle", "w"))



raise Exception

distance_lvlh_pid_concantenate = []
nb_seconds_since_start_pid_concatenate = []
for irho in range(nk):
    distance_lvlh_pid_concantenate_irho = []
    for iinter in range(nb_interval):
        distance_lvlh_pid_concantenate_irho = distance_lvlh_pid_concantenate_irho + distance_lvlh_pid[iinter][irho]
        if irho == 0:
            nb_seconds_since_start_pid_concatenate = nb_seconds_since_start_pid_concatenate + nb_seconds_since_start_pid[iinter]
    distance_lvlh_pid_concantenate.append(distance_lvlh_pid_concantenate_irho )



distance_min_concatenate = []
for iinter in range(nb_interval):
    distance_min_concatenate = distance_min_concatenate + distance_lvlh_pid[iinter][ipid_best[iinter]] 
distance_min_concatenate = np.array(distance_min_concatenate)



main_input_filename_root =  date_obs_start_str.replace(":","_") + '_' + date_obs_end_str.replace(":","_") + '_interval' + format(interval, ".1f").replace(".","_")+ '.txt'
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxx
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxx
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxx
# raise Exception
# pickle.dump(nb_seconds_since_start_pid, open('pickle/nb_seconds_since_start_pid'+ '.pickle', 'w'))
# pickle.dump(nk, open('pickle/nk'+ '.pickle', 'w'))
# pickle.dump(distance_lvlh_pid, open('pickle/distance_lvlh_pid'+ '.pickle', 'w'))
# pickle.dump(pid_mod_arr, open('pickle/pid_mod_arr'+ '.pickle', 'w'))
# pickle.dump(date_datetime_round_sec_spock_pid_ok, open('pickle/date_datetime_round_sec_spock_pid_ok'+ '.pickle', 'w'))
# pickle.dump(main_input_filename_root, open('pickle/main_input_filename_root'+ '.pickle', 'w'))
# pickle.dump(distance_lvlh_pid_concantenate, open('pickle/distance_lvlh_pid_concantenate'+ '.pickle', 'w'))
# pickle.dump(nb_seconds_since_start_pid_concatenate, open('pickle/nb_seconds_since_start_pid_concatenate'+ '.pickle', 'w'))

# nb_seconds_since_start_pid = pickle.load(open('pickle/nb_seconds_since_start_pid' + '.pickle'))
# nk = pickle.load(open('pickle/nk' + '.pickle'))
# distance_lvlh_pid = pickle.load(open('pickle/distance_lvlh_pid' + '.pickle'))
# pid_mod_arr = pickle.load(open('pickle/pid_mod_arr' + '.pickle'))
# date_datetime_round_sec_spock_pid_ok = pickle.load(open('pickle/date_datetime_round_sec_spock_pid_ok' + '.pickle'))
# main_input_filename_root = pickle.load(open('pickle/main_input_filename_root' + '.pickle'))
# distance_lvlh_pid_concantenate = pickle.load(open('pickle/distance_lvlh_pid_concantenate' + '.pickle'))
# nb_seconds_since_start_pid_concatenate = pickle.load(open('pickle/nb_seconds_since_start_pid_concatenate' + '.pickle'))

# raise Exception






################### FIGURES ###################
height_fig = 11
ratio_fig_size = 4./3
fontsize_plot = 20

######
fig_title = ''#'Distance between SpOCK and data for different density coefficient' #'Distance with respect to pid = 0.7'#'Distance between SpOCK and data for different density coefficient'
y_label = 'Distance (m)'
x_label = 'Time (hours)' 

fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax = fig.add_subplot(gs[0, 0])

ax.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
ax.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='bold') ## make the labels of the ticks in bold

x_axis = np.array(nb_seconds_since_start_pid_concatenate)
if nk > 1:
    alpha_arr = np.arange(0.2,1+0.2/nk,(1-0.2)/(nk-1))
else: 
    alpha_arr = [1]
min_y = 1.e30
max_y = -1.e30

for iinter in range(nb_interval):
    for ik in range(nk):
        if alpha_arr[ik] >1:
            alpha_arr[ik] = 1
        ax.plot(np.array(nb_seconds_since_start_pid[iinter])/3600., np.array(distance_lvlh_pid[iinter][ik])*1000, linewidth = 2, color = 'b', alpha = alpha_arr[ik])
        ax.plot([np.array(nb_seconds_since_start_pid[iinter][0])/3600., np.array(nb_seconds_since_start_pid[iinter][0])/3600.],[-1e30, np.array(distance_lvlh_pid[iinter][ik][0])*1000], linewidth = 2, linestyle = 'dashed', color = 'red')

        if np.min(np.array(distance_lvlh_pid[iinter][ik])*1000) < min_y:
            min_y = np.min(np.array(distance_lvlh_pid[iinter][ik])*1000)
        if np.max(np.array(distance_lvlh_pid[iinter][ik])*1000) > max_y:
            max_y = np.max(np.array(distance_lvlh_pid[iinter][ik])*1000)        
        print ik

delta_y_text = (max_y - min_y) / 20.
for iinter in range(nb_interval): # can't couple that with previous loop because need to figure out min_y and max_y firs
    for ik in range(nk):
        # rho_control
        ax.text(np.array(nb_seconds_since_start_pid[iinter][0])/3600., np.array(distance_lvlh_pid[iinter][ik][0])*1000, format(rho_control[iinter], ".2f"), horizontalalignment = 'left', fontsize = fontsize_plot, weight = 'bold', color = 'r', alpha = alpha_arr[ik], verticalalignment = 'center', label = 'rho_control')

        # err
        ax.text(np.array(nb_seconds_since_start_pid[iinter][-1])/3600., np.array(distance_lvlh_pid[iinter][ik][-1])*1000 - delta_y_text, format(err[iinter]*1000, ".2f"), horizontalalignment = 'right', fontsize = fontsize_plot, weight = 'bold', color = 'b', alpha = alpha_arr[ik], verticalalignment = 'center', label = 'error')
        # derr/dr
        ax.text(np.array(nb_seconds_since_start_pid[iinter][-1])/3600., np.array(distance_lvlh_pid[iinter][ik][-1])*1000 - 2*delta_y_text/1.2, format(derrdt[iinter]*1000, ".2f"), horizontalalignment = 'right', fontsize = fontsize_plot, weight = 'bold', color = 'magenta', alpha = alpha_arr[ik], verticalalignment = 'center', label = 'derror/dt')
        # interr
        ax.text(np.array(nb_seconds_since_start_pid[iinter][-1])/3600., np.array(distance_lvlh_pid[iinter][ik][-1])*1000 - 3*delta_y_text/1.2, format(interr[iinter]*1000, ".2f"), horizontalalignment = 'right', fontsize = fontsize_plot, weight = 'bold', color = 'grey', alpha = alpha_arr[ik], verticalalignment = 'center', label = 'interror')


ax.plot([np.array(nb_seconds_since_start_pid[0][0])/3600., np.array(nb_seconds_since_start_pid[nb_interval-1][-1])/3600.],[0, 0], linewidth = 2, linestyle = 'dashed', color = 'blue')
ax.plot(x_axis/3600., distance_min_concatenate*1000, linewidth = 2, color = 'r')
ax.text(x_axis[-1]/3600., max_y/2., 'SpOCK\nbehind', horizontalalignment = 'left', fontsize = fontsize_plot, weight = 'bold',verticalalignment = 'center')
ax.text(x_axis[-1]/3600., min_y/2., 'SpOCK\nin front', horizontalalignment = 'left', fontsize = fontsize_plot, weight = 'bold',verticalalignment = 'center')
# # x axis label is in real time
# nb_seconds_in_simu = nb_seconds_since_start_pid_concatenate[-1] - nb_seconds_since_start_pid_concatenate[0]
# start_xaxis_label = nb_seconds_since_start_pid_concatenate[0]
# date_ref = date_datetime_round_sec_spock_pid_ok[0][0]
# nb_ticks_xlabel = 10
# dt_xlabel =  nb_seconds_in_simu / nb_ticks_xlabel # dt for ticks on x axis (in seconds)
# xticks = np.arange(start_xaxis_label, start_xaxis_label+nb_seconds_in_simu+1, dt_xlabel)
# date_list_str = []
# date_list = [date_ref + timedelta(seconds=x-xticks[0]) for x in xticks]
# for i in range(len(xticks)):
#     if dt_xlabel > nb_ticks_xlabel*24*3600:
#         date_list_str.append( str(date_list[i])[5:10] )
#     else:
#         date_list_str.append( str(date_list[i])[5:10] + "\n" + str(date_list[i])[11:16] )
#         ax.xaxis.set_ticks(xticks)
#         ax.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')
ax.margins(0,0); ax.set_ylim([min_y, max_y])
#        ax.set_xlim([ax.get_xlim()[0], most_recent_tle_among_all_sc])

legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="", fontsize = fontsize_plot)
fig_save_name = 'fig/distance_optimum_pid_to_obs_' + main_input_filename_root.replace(".txt", ".pdf")
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

os.system("rsync -av " + fig_save_name + " cbv@srbwks2014-0008.engin.umich.edu:")



raise Exception




################### FIGURES ###################
height_fig = 11
ratio_fig_size = 4./3
fontsize_plot = 20

######
fig_title = ''#'Distance_Lvlh between SpOCK and data for different density coefficient' #'Distance_Lvlh with respect to pid = 0.7'#'Distance_Lvlh between SpOCK and data for different density coefficient'
y_label = 'Distance_Lvlh (m)'
x_label = 'Real time'

fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax = fig.add_subplot(gs[0, 0])

ax.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
ax.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='bold') ## make the labels of the ticks in bold

x_axis = nb_seconds_since_start_pid_concatenate
if nk > 1:
    alpha_arr = np.arange(0.2,1+0.2/nk,(1-0.2)/(nk-1))
else: 
    alpha_arr = [1]

for iinter in range(nb_interval):
    for ik in range(nk):
        if alpha_arr[ik] >1:
            alpha_arr[ik] = 1
        ax.plot(nb_seconds_since_start_pid[iinter], np.array(distance_lvlh_pid[iinter][ik])*1000, linewidth = 2, color = 'b', alpha = alpha_arr[ik])
        #ax.plot(x_axis, (np.array(distance_lvlh_pid[iinter][ik]) - np.array(distance_lvlh_pid[iinter][0]))*1000, linewidth = 2, color = 'b', alpha = alpha_arr[ik])
        #ax.text(x_axis[-1], (np.array(distance_lvlh_pid[iinter][ik]) - np.array(distance_lvlh_pid[iinter][0]))[-1]*1000, format(pid_mod_arr[ik], ".1f"), horizontalalignment = 'left', fontsize = fontsize_plot, weight = 'bold', color = 'b', alpha = alpha_arr[ik], verticalalignment = 'center')
        #ax.text(x_axis[-1], distance_lvlh_min_concatenate[ik][-1]*1000, format(pid_mod_arr[ik], ".1f"), horizontalalignment = 'left', fontsize = fontsize_plot, weight = 'bold', color = 'b', alpha = alpha_arr[ik], verticalalignment = 'center')
        #ax.text(x_axis[-1], distance_lvlh_pid[iinter][ik][-1], str(pid_mod_arr[ik]), horizontalalignment = 'left', fontsize = fontsize_plot, weight = 'bold', color = 'b', alpha = alpha_arr[ik], verticalalignment = 'center')
        print ik
ax.plot(x_axis, distance_lvlh_min_concatenate*1000, linewidth = 2, color = 'r')
# x axis label is in real time
nb_seconds_in_simu = nb_seconds_since_start_pid_concatenate[-1] - nb_seconds_since_start_pid_concatenate[0]
start_xaxis_label = nb_seconds_since_start_pid_concatenate[0]
date_ref = date_datetime_round_sec_spock_pid_ok[0][0]
nb_ticks_xlabel = 10
dt_xlabel =  nb_seconds_in_simu / nb_ticks_xlabel # dt for ticks on x axis (in seconds)
xticks = np.arange(start_xaxis_label, start_xaxis_label+nb_seconds_in_simu+1, dt_xlabel)
date_list_str = []
date_list = [date_ref + timedelta(seconds=x-xticks[0]) for x in xticks]
for i in range(len(xticks)):
    if dt_xlabel > nb_ticks_xlabel*24*3600:
        date_list_str.append( str(date_list[i])[5:10] )
    else:
        date_list_str.append( str(date_list[i])[5:10] + "\n" + str(date_list[i])[11:16] )
        ax.xaxis.set_ticks(xticks)
        ax.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')
        ax.margins(0,0); ax.set_xlim([min(xticks), max(xticks)])
#        ax.set_xlim([ax.get_xlim()[0], most_recent_tle_among_all_sc])

legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="", fontsize = fontsize_plot)
#legend.get_title().set_fontsize(str(fontsize_plot))


fig_save_name = 'distance_lvlh_optimum_pid_to_obs_' + main_input_filename_root.replace("txt", "pdf")
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  




#######
fig_title = ''#'Distance between SpOCK and data for different density coefficient' #'Distance with respect to pid = 0.7'#'Distance between SpOCK and data for different density coefficient'
y_label = 'Distance (m)'
x_label = 'Real time'

fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax = fig.add_subplot(gs[0, 0])

ax.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
ax.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='bold') ## make the labels of the ticks in bold

x_axis = nb_seconds_since_start_pid_concatenate
if nk > 1:
    alpha_arr = np.arange(0.2,1+0.2/nk,(1-0.2)/(nk-1))
else: 
    alpha_arr = [1]
for ik in range(nk):
    if alpha_arr[ik] >1:
        alpha_arr[ik] = 1

    ax.plot(x_axis, np.array(distance_lvlh_pid_concantenate[ik])*1000, linewidth = 2, color = 'b', alpha = alpha_arr[ik])
    #ax.plot(x_axis, (np.array(distance_lvlh_pid[iinter][ik]) - np.array(distance_lvlh_pid[iinter][0]))*1000, linewidth = 2, color = 'b', alpha = alpha_arr[ik])
    #ax.text(x_axis[-1], (np.array(distance_lvlh_pid[iinter][ik]) - np.array(distance_lvlh_pid[iinter][0]))[-1]*1000, format(pid_mod_arr[ik], ".1f"), horizontalalignment = 'left', fontsize = fontsize_plot, weight = 'bold', color = 'b', alpha = alpha_arr[ik], verticalalignment = 'center')
    ax.text(x_axis[-1], distance_lvlh_pid_concantenate[ik][-1]*1000, format(pid_mod_arr[ik], ".1f"), horizontalalignment = 'left', fontsize = fontsize_plot, weight = 'bold', color = 'b', alpha = alpha_arr[ik], verticalalignment = 'center')
    #ax.text(x_axis[-1], distance_lvlh_pid  [iinter][ik][-1], str(pid_mod_arr[ik]), horizontalalignment = 'left', fontsize = fontsize_plot, weight = 'bold', color = 'b', alpha = alpha_arr[ik], verticalalignment = 'center')
    print ik                                           
# x axis label is in real time
nb_seconds_in_simu = nb_seconds_since_start_pid_concatenate[-1] - nb_seconds_since_start_pid_concatenate[0]
start_xaxis_label = nb_seconds_since_start_pid_concatenate[0]
date_ref = date_datetime_round_sec_spock_pid_ok[0][0]
nb_ticks_xlabel = 10
dt_xlabel =  nb_seconds_in_simu / nb_ticks_xlabel # dt for ticks on x axis (in seconds)
xticks = np.arange(start_xaxis_label, start_xaxis_label+nb_seconds_in_simu+1, dt_xlabel)
date_list_str = []
date_list = [date_ref + timedelta(seconds=x-xticks[0]) for x in xticks]
for i in range(len(xticks)):
    if dt_xlabel > nb_ticks_xlabel*24*3600:
        date_list_str.append( str(date_list[i])[5:10] )
    else:
        date_list_str.append( str(date_list[i])[5:10] + "\n" + str(date_list[i])[11:16] )
        ax.xaxis.set_ticks(xticks)
        ax.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')
        ax.margins(0,0); ax.set_xlim([min(xticks), max(xticks)])
#        ax.set_xlim([ax.get_xlim()[0], most_recent_tle_among_all_sc])

legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="", fontsize = fontsize_plot)
#legend.get_title().set_fontsize(str(fontsize_plot))


fig_save_name = 'pid_distance_ens_to_observations_' + main_input_filename_root.replace("txt", "pdf")
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  





# Distance between SpOCK ensembles and ODTK
height_fig = 11
ratio_fig_size = 4./3
fontsize_plot = 20

fig_title = 'Distance between SpOCK ensembles and ODTK'
y_label = 'Distance (m)'
x_label = 'Real time'

fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 0.96,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold                                                                                                                                       
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax = fig.add_subplot(gs[0, 0])

ax.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
ax.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                                                                                          
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold                                                                                                                                       
x_axis = nb_seconds_since_start


for it in range(nb_it):
    if it == 0:
        for iens in range(nb_ensemble_ini_state_corrected):
            if iens == 0:
                ax.plot(x_axis, np.array(distance[it][iens])*1000, linewidth = 2, color = 'b', alpha = 0.15, label= 'SpOCK ensemble')
            else:
                ax.plot(x_axis, np.array(distance[it][iens])*1000, linewidth = 2, color = 'b', alpha = 0.15)
            # distance of SpOCK reference sc to ODT
        ax.plot(x_axis, np.array(distance_ref)*1000, linewidth = 4, color = 'r', label = 'SpOCK from raw observations')

    # min mean distance
    ax.plot(x_axis, np.array(distance[it][(int)(which_ens_min_dist[it])])*1000, linewidth = 5, color = 'b', label = 'Iteration ' + str(it))




# x axis label is in real time
nb_seconds_in_simu = nb_seconds_since_start[-1] - nb_seconds_since_start[0]
start_xaxis_label = nb_seconds_since_start[0]
date_ref = date_obs[0]
nb_ticks_xlabel = 10
dt_xlabel =  nb_seconds_in_simu / nb_ticks_xlabel # dt for ticks on x axis (in seconds)
xticks = np.arange(start_xaxis_label, start_xaxis_label+nb_seconds_in_simu+1, dt_xlabel)
date_list_str = []
date_list = [date_ref + timedelta(seconds=x-xticks[0]) for x in xticks]
for i in range(len(xticks)):
    if dt_xlabel > nb_ticks_xlabel*24*3600:
        date_list_str.append( str(date_list[i])[5:10] )
    else:
        date_list_str.append( str(date_list[i])[5:10] + "\n" + str(date_list[i])[11:16] )
        ax.xaxis.set_ticks(xticks)
        ax.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')
        ax.margins(0,0); ax.set_xlim([min(xticks), max(xticks)])
#        ax.set_xlim([ax.get_xlim()[0], most_recent_tle_among_all_sc])

legend = ax.legend(loc='upper left', numpoints = 1,  title="", fontsize = fontsize_plot)
#legend.get_title().set_fontsize(str(fontsize_plot))


fig_save_name = 'rv_distance_ens_to_observations_' + main_input_filename_root.replace("txt", "pdf")
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  










# Distribution x eci
bin_width = sigma_x/5. # in m
fig_title = 'X ECI distribution at initial time (bin size ' + str(bin_width) + ' m, ' + str(nb_ensemble_ini_state_corrected) + ' ensembles)'
y_label = '# ensembles in bin'
x_label = 'X (km)'

fig_x = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

fig_x.suptitle(fig_title, y = 0.958,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax_x = fig_x.add_subplot(gs[0, 0])

ax_x.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
ax_x.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax_x.spines.itervalues()] # change the width of the frame of the figure
ax_x.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
bin_width = bin_width / 1000. # m to km

index_obs_start = 0#index_interval[itime_start]
index_in_spock_ok = 0
index_in_obs = index_obs_start + index_in_spock_ok


bins_arr = np.arange(min(r_spock_ok[index_in_spock_ok, :, 0]), max(r_spock_ok[index_in_spock_ok, :, 0]) + bin_width, bin_width)
n, bins, patches = ax_x.hist(r_spock_ok[index_in_spock_ok, :, 0], bins_arr,  histtype='stepfilled', alpha = 1, color = 'cornflowerblue',label = 'SpOCK ensembles\nstd dev: ' + format(np.std(r_spock_ok[index_in_spock_ok, :, 0])*1000, ".2f") + ' m') 
# Add Observations position
ax_x.plot([r_obs[index_in_obs, 0], r_obs[index_in_obs, 0]],[0,np.nanmax(n)], linewidth = 6, color = 'b', label = 'Observations', linestyle = 'dotted')

legend = ax_x.legend(loc='top right', numpoints = 1,  title="", fontsize = fontsize_plot)

fig_save_name = 'x_eci_' + main_input_filename.replace(".txt", "_test.pdf")
fig_x.savefig(fig_save_name, facecolor=fig_x.get_facecolor(), edgecolor='none', bbox_inches='tight')  


# Distribution y eci
bin_width = sigma_y/5. # in m
fig_title = 'Y ECI distribution at initial time (bin size ' + str(bin_width) + ' m, ' + str(nb_ensemble_ini_state_corrected) + ' ensembles)'
y_label = '# ensembles in bin'
x_label = 'Y (km)'

fig_y = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

fig_y.suptitle(fig_title, y = 0.958,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax_y = fig_y.add_subplot(gs[0, 0])

ax_y.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
ax_y.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax_y.spines.itervalues()] # change the width of the frame of the figure
ax_y.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
bin_width = bin_width / 1000. # m to km

index_obs_start = 0 # index_interval[itime_start]
index_in_spock_ok = 0
index_in_obs = index_obs_start + index_in_spock_ok


bins_arr = np.arange(min(r_spock_ok[index_in_spock_ok, :, 1]), max(r_spock_ok[index_in_spock_ok, :, 1]) + bin_width, bin_width)
n, bins, patches = ax_y.hist(r_spock_ok[index_in_spock_ok, :, 1], bins_arr,  histtype='stepfilled', alpha = 1, color = 'cornflowerblue',label = 'SpOCK ensembles\nstd dev: ' + format(np.std(r_spock_ok[index_in_spock_ok, :, 1])*1000, ".2f") + ' m') 
# Add Observations position
ax_y.plot([r_obs[index_in_obs, 1], r_obs[index_in_obs, 1]],[0,np.nanmax(n)], linewidth = 6, color = 'b', label = 'Observations', linestyle = 'dotted')

legend = ax_y.legend(loc='top right', numpoints = 1,  title="", fontsize = fontsize_plot)

fig_save_name = 'y_eci_' + main_input_filename.replace(".txt", "_test.pdf")
fig_y.savefig(fig_save_name, facecolor=fig_y.get_facecolor(), edgecolor='none', bbox_inches='tight')  


# Distribution z eci
bin_width = sigma_z/5. # in m
fig_title = 'Z ECI distribution at initial time (bin size ' + str(bin_width) + ' m, ' + str(nb_ensemble_ini_state_corrected) + ' ensembles)'
y_label = '# ensembles in bin'
x_label = 'Z (km)'

fig_z = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

fig_z.suptitle(fig_title, y = 0.958,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax_z = fig_z.add_subplot(gs[0, 0])

ax_z.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
ax_z.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax_z.spines.itervalues()] # change the width of the frame of the figure
ax_z.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
bin_width = bin_width / 1000. # m to km

index_obs_start = 0 # index_interval[itime_start]
index_in_spock_ok = 0
index_in_obs = index_obs_start + index_in_spock_ok


bins_arr = np.arange(min(r_spock_ok[index_in_spock_ok, :, 2]), max(r_spock_ok[index_in_spock_ok, :, 2]) + bin_width, bin_width)
n, bins, patches = ax_z.hist(r_spock_ok[index_in_spock_ok, :, 2], bins_arr,  histtype='stepfilled', alpha = 1, color = 'cornflowerblue',label = 'SpOCK ensembles\nstd dev: ' + format(np.std(r_spock_ok[index_in_spock_ok, :, 2])*1000, ".2f") + ' m') 
# Add Observations position
ax_z.plot([r_obs[index_in_obs, 2], r_obs[index_in_obs, 2]],[0,np.nanmax(n)], linewidth = 6, color = 'b', label = 'Observations', linestyle = 'dotted')

legend = ax_z.legend(loc='top right', numpoints = 1,  title="", fontsize = fontsize_plot)

fig_save_name = 'z_eci_' + main_input_filename.replace(".txt", "_test.pdf")
fig_z.savefig(fig_save_name, facecolor=fig_z.get_facecolor(), edgecolor='none', bbox_inches='tight')  



# Distribution vx eci
bin_width = sigma_vx/5. # in m
fig_vtitle = 'Vx ECI distribution at initial time (bin size ' + str(bin_width) + ' m, ' + str(nb_ensemble_ini_state_corrected) + ' ensembles)'
y_label = '# ensembles in bin'
x_label = 'X (km)'

fig_vx = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

fig_vx.suptitle(fig_vtitle, y = 0.958,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax_vx = fig_vx.add_subplot(gs[0, 0])

ax_vx.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
ax_vx.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax_vx.spines.itervalues()] # change the width of the frame of the figure
ax_vx.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
bin_width = bin_width / 1000. # m to km

index_obs_start = 0 # index_interval[itime_start]
index_in_spock_ok = 0
index_in_obs = index_obs_start + index_in_spock_ok


bins_arr = np.arange(min(v_spock_ok[index_in_spock_ok, :, 0]), max(v_spock_ok[index_in_spock_ok, :, 0]) + bin_width, bin_width)
n, bins, patches = ax_vx.hist(v_spock_ok[index_in_spock_ok, :, 0], bins_arr,  histtype='stepfilled', alpha = 1, color = 'cornflowerblue',label = 'SpOCK ensembles\nstd dev: ' + format(np.std(v_spock_ok[index_in_spock_ok, :, 0])*1000, ".2f") + ' m/s') 
# Add Observations position
ax_vx.plot([v_obs[index_in_obs, 0], v_obs[index_in_obs, 0]],[0,np.nanmax(n)], linewidth = 6, color = 'b', label = 'Observations', linestyle = 'dotted')

legend = ax_vx.legend(loc='top right', numpoints = 1,  title="", fontsize = fontsize_plot)

fig_vsave_name = 'vx_eci_' + main_input_filename.replace(".txt", "_test.pdf")
fig_vx.savefig(fig_vsave_name, facecolor=fig_vx.get_facecolor(), edgecolor='none', bbox_inches='tight')  


# Distribution vy eci
bin_width = sigma_vy/5. # in m
fig_vtitle = 'Vy ECI distribution at initial time (bin size ' + str(bin_width) + ' m, ' + str(nb_ensemble_ini_state_corrected) + ' ensembles)'
y_label = '# ensembles in bin'
x_label = 'Y (km)'

fig_vy = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

fig_vy.suptitle(fig_vtitle, y = 0.958,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax_vy = fig_vy.add_subplot(gs[0, 0])

ax_vy.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
ax_vy.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax_vy.spines.itervalues()] # change the width of the frame of the figure
ax_vy.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
bin_width = bin_width / 1000. # m to km

index_obs_start = 0 # index_interval[itime_start]
index_in_spock_ok = 0
index_in_obs = index_obs_start + index_in_spock_ok


bins_arr = np.arange(min(v_spock_ok[index_in_spock_ok, :, 1]), max(v_spock_ok[index_in_spock_ok, :, 1]) + bin_width, bin_width)
n, bins, patches = ax_vy.hist(v_spock_ok[index_in_spock_ok, :, 1], bins_arr,  histtype='stepfilled', alpha = 1, color = 'cornflowerblue',label = 'SpOCK ensembles\nstd dev: ' + format(np.std(v_spock_ok[index_in_spock_ok, :, 1])*1000, ".2f") + ' m/s') 
# Add Observations position
ax_vy.plot([v_obs[index_in_obs, 1], v_obs[index_in_obs, 1]],[0,np.nanmax(n)], linewidth = 6, color = 'b', label = 'Observations', linestyle = 'dotted')

legend = ax_vy.legend(loc='top right', numpoints = 1,  title="", fontsize = fontsize_plot)

fig_vsave_name = 'vy_eci_' + main_input_filename.replace(".txt", "_test.pdf")
fig_vy.savefig(fig_vsave_name, facecolor=fig_vy.get_facecolor(), edgecolor='none', bbox_inches='tight')  


# Distribution vz eci
bin_width = sigma_vz/5. # in m
fig_vtitle = 'Vz ECI distribution at initial time (bin size ' + str(bin_width) + ' m, ' + str(nb_ensemble_ini_state_corrected) + ' ensembles)'
y_label = '# ensembles in bin'
x_label = 'Z (km)'

fig_vz = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

fig_vz.suptitle(fig_vtitle, y = 0.958,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax_vz = fig_vz.add_subplot(gs[0, 0])

ax_vz.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
ax_vz.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax_vz.spines.itervalues()] # change the width of the frame of the figure
ax_vz.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
bin_width = bin_width / 1000. # m to km

index_obs_start = 0 # index_interval[itime_start]
index_in_spock_ok = 0
index_in_obs = index_obs_start + index_in_spock_ok


bins_arr = np.arange(min(v_spock_ok[index_in_spock_ok, :, 2]), max(v_spock_ok[index_in_spock_ok, :, 2]) + bin_width, bin_width)
n, bins, patches = ax_vz.hist(v_spock_ok[index_in_spock_ok, :, 2], bins_arr,  histtype='stepfilled', alpha = 1, color = 'cornflowerblue',label = 'SpOCK ensembles\nstd dev: ' + format(np.std(v_spock_ok[index_in_spock_ok, :, 2])*1000, ".2f") + ' m/s') 
# Add Observations position
ax_vz.plot([v_obs[index_in_obs, 2], v_obs[index_in_obs, 2]],[0,np.nanmax(n)], linewidth = 6, color = 'b', label = 'Observations', linestyle = 'dotted')

legend = ax_vz.legend(loc='top right', numpoints = 1,  title="", fontsize = fontsize_plot)

fig_vsave_name = 'vz_eci_' + main_input_filename.replace(".txt", "_test.pdf")
fig_vz.savefig(fig_vsave_name, facecolor=fig_vz.get_facecolor(), edgecolor='none', bbox_inches='tight')  




