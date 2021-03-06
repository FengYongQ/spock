
# THis script plots the distance, amplitude, orbit average of runs amde with pid_algo_v2.py. The pickle were saved in pid_algo_v2.py
# inputs: pickle_root_list stores each pickle to load (one per run in pid_algo_v2.py) (the pickles are assumed ot be in ./pickle)
# (pickle_root =  prefix_name + '_' + rho_more in pid_algo_v2.py)
plot_swarm = 1
external = ['/Users/cbv/work/spockOut/density/swarm/nadir.txt']
#['/Users/cbv/work/spockOut/density/swarm/swarmB.txt', '/Users/cbv/work/spockOut/density/swarm/swarmB_omniweb_mod.txt', '/Users/cbv/work/spockOut/density/swarm/cyg_omniweb_mod.txt'] 
external_label = ['NRLMSIS00e along Swarm - actual F10.7/Ap', 'NRLMSIS00e along Swarm - corrected F10.7/Ap', 'NRLMSIS00e along CYGNSS - corrected F10.7/Ap']
external_color = ['limegreen', 'red', 'blue']
# ['/Users/cbv/work/spockOut/density/swarm/swarm_omniweb_mod.txt']
# ['/Users/cbv/work/spockOut/density/swarm/cyg_omniweb_mod.txt']# simulations that were run durectly with SpOCK (like a typical SpOCK's simulations). indicate here the name of the main input file. Can only use if toplot = 'rho'
pickle_root_list = ["swarmB_20170901_mass460_quaternion_pleiades_mid"]
# ["swarmB_20170901_mass310_mid",  "swarmB_20170901_mass460_quaternion_minus_theta_mid", "swarmB_20170901_mass460_quaternion_mid"]
# ["swarmB_20170901_mass310_mid"]
# ['FM03_20190415_interval12h_mid', 'FM03_20190415_mid', 'FM03_20190415_interval30h_mid']
# ['FM03_20190415_mid', 'distance_lvlh_nb_seconds_since_start_date_start_msis']# 'FM03_20190415_interval30h_mid']#['FM03_20190415_mid', 'distance_lvlh_nb_seconds_since_start_date_start_msis']
#['FM07_20170901_mid']#['FM08_20170901_no_storm_mid']#['FM8_20170901_omniweb_mid']
#['FM03_20180901_mid', 'FM03_20181016_mid', 'FM03_20181106_mid', 'FM03_20181218_mid', 'FM03_20190110_mid', 'FM03_20190217_mid']
# ['FM03_20190415_mid', 'FM03_20190409_mid']
# ['FM03_20190320_mid', 'FM03_20190415_mid', 'FM03_20190515_mid', 'FM03_20190610_mid', 'FM03_20190715_mid', 'FM03_20190818_mid']
#['FM1_20170817_mid']#['FM07_20170901_mid', 'FM8_20170901_omniweb_mid', 'FM8_20170901_no_storm_mid']# ['FM8_20170901_omniweb_mid', 'FM8_20170901_again_mid', 'FM8_20170901_no_storm_mid'] #['FM8_20170901_mid']
label_overwrite = ['SpOCK nadir', 'SpOCK quaternions', 'bad']#['12h', '18h', '30h']
#['SpOCK', 'NRLMSIS00e']#['18h', '30h']#['SpOCK - with storm', 'SpOCK - without storm']
#['FM07', 'FM08', 'FM08 no storm']#['Omniweb', 'SWPC', 'No storm']
#['FM4_20180112_fine_mid'] ['FM4_20180112_mid']
#["fm01_20170817_mid"] 
# ["fm4_mid", "test_mid", "2018jan12_mid", "nadir"]
#["rv0_error16m_mid", "test_mid"]
#["fastearth_sp10_mid", "fastearth_sp11_mid", "fastearth_sp12_mid", "fastearth_sp13_mid", "earth_sp13_mid", "gravMap_sp13_mid"]
#["grav50_mid", "sp11_mid", "sp12_mid", "sp13_mid", "sp14_mid", "sp15_mid", "sp16_mid", "sp20_mid"]
#['solpres05_mid']#['dt02_mid']#['noSolarPressure_mid']#['grav50_mid']#['dt02_mid']#['onlyDrag_mid']
#pickle_root_list = ['dec17_pole', 'dec17_mid', 'dec17_highamp_pole', 'dec17_equator']
#pickle_root_list = ['rhonosine_grav50_mid', 'rho0_grav50_solarzenith_mid','egm08_mid','grav80_mid', 'localtime70percent_mid']
#['rhonosine_grav50_mid', 'rho0_grav50_solarzenith_mid']#['egm08_mid']#['grav80_mid']#['rho0_grav50_solarzenith_mid']     #['dt0_1s_solarzenith_mid']#['grav50_solarzenith_mid']
#['localtime70percent_mid']#['localtime_pole', 'localtime_equator', 'localtime70percent_mid']
#['solarzenith_equator', 'solarzenith_pole', 'localtime70percent_mid']# ['localtime70percentAp2_mid']#

toplot = 'rho' # raw, amplitude, rho_control, rho
if 'distance_lvlh_nb_seconds_since_start_date_start_msis' in pickle_root_list:
    toplot = 'raw'
    
suffix_plot = '_temp'
color_arr = ['blue', 'red', 'black' ,'mediumorchid', 'dodgerblue', 'magenta', 'darkgreen', 'limegreen'] #['blue', 'red', 'green', 'black', 'magenta']
isbig = 0
ispleiades = 0
import sys
import numpy as np
from scipy import stats

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
    sys.path.append("/Users/cbv/work/spock/srcPython")
    path_mpirun = 'mpirun'
    spice_path = '/Users/cbv/cspice/data'
    nb_proc = 4


import pickle
import os

from read_input_file import *
from read_output_file import *
from orbit_average import *
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
from find_in_read_input_order_variables import *


#FIGURES ###################

height_fig = 11
ratio_fig_size = 4./3
fontsize_plot = 25



######
fig_title = ''#'Distance between SpOCK and data for different density coefficient conditions' 
x_label = 'Time (days)' #'Real time'#'Time (days)' 

fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'normal',)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax = fig.add_subplot(gs[0, 0])


ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='normal') ## make the labels of the ticks in bold


pickle_root_concatenate = ''
nb_pickle = len(pickle_root_list)
date_start_all = datetime.strptime('2900-01-01', "%Y-%m-%d")
date_pickle = []
for ipickle in range(nb_pickle): # determine the oldest start date of all simulations
    pickle_root = 'pickle/' + pickle_root_list[ipickle]
    if pickle_root_list[ipickle] == 'distance_lvlh_nb_seconds_since_start_date_start_msis':
        [dist_lvlh_msis, sec_msis, date_start_msis] = pickle.load(open(pickle_root + ".pickle"))
    else:

        [duration_simu, nb_interval, nb_seconds_since_start_pid_concatenate_arr, distance_lvlh_pid_concantenate_arr, nb_seconds_since_start_pid_average_concatenate_arr, \
                     distance_lvlh_pid_average_concantenate_arr, nb_seconds_since_start_pid_average_mid_concatenate_arr, \
                     distance_lvlh_pid_average_mid_concantenate_arr, distance_lvlh_pid_amplitude_mid_concantenate_arr, ecc_average_mid_concantenate_arr, \
                     ecc_obs_average_mid_concantenate_arr, localtime_spock_ok_pid_concatenate, phase_spock_ok_pid_concatenate_arr, argper_average_mid_concantenate_arr, \
                         index_period_spock_concatenate_arr, argper_spock_ok_pid_concatenate_arr,\
                     ecc_ave_conc,ecc_obs_ave_conc,localtime_per,longitude_per,latitude_per,nb_seconds_ave_conc_arr, rho_control, nb_seconds_interval, date_start_save, rho_ave_conc, rho_msis_ave_conc]= pickle.load(open(pickle_root + ".pickle"))

    if date_start_save < date_start_all:
        date_start_all = date_start_save

seconds_pickle = []
density_pickle = []
for ipickle in range(nb_pickle): # now make the plots
    pickle_root = 'pickle/' + pickle_root_list[ipickle]

    if pickle_root_list[ipickle] == 'distance_lvlh_nb_seconds_since_start_date_start_msis':
        [dist_lvlh_msis, sec_msis, date_start_msis] = pickle.load(open(pickle_root + ".pickle"))
    else:
        [duration_simu, nb_interval, nb_seconds_since_start_pid_concatenate_arr, distance_lvlh_pid_concantenate_arr, nb_seconds_since_start_pid_average_concatenate_arr, \
                 distance_lvlh_pid_average_concantenate_arr, nb_seconds_since_start_pid_average_mid_concatenate_arr, \
                 distance_lvlh_pid_average_mid_concantenate_arr, distance_lvlh_pid_amplitude_mid_concantenate_arr, ecc_average_mid_concantenate_arr, \
                 ecc_obs_average_mid_concantenate_arr, localtime_spock_ok_pid_concatenate, phase_spock_ok_pid_concatenate_arr, argper_average_mid_concantenate_arr, \
                     index_period_spock_concatenate_arr, argper_spock_ok_pid_concatenate_arr,\
                 ecc_ave_conc,ecc_obs_ave_conc,localtime_per,longitude_per,latitude_per,nb_seconds_ave_conc_arr, rho_control, nb_seconds_interval, date_start_save, rho_ave_conc, rho_msis_ave_conc]= pickle.load(open(pickle_root + ".pickle"))

    delta_date = date_start_save - date_start_all # !!!!!! added these three lines on 09-24-2019
    delta_date_sec = delta_date.total_seconds() #0# delta_date.total_seconds()
    nb_seconds_interval_corr = np.array(nb_seconds_interval) + delta_date_sec
    date_pickle.append(date_start_save)
    seconds_pickle.append(delta_date_sec)
    # if ipickle == 1:
    #     raise Exception
#     [duration_simu, nb_interval, nb_seconds_since_start_pid_concatenate_arr, distance_lvlh_pid_concantenate_arr, nb_seconds_since_start_pid_average_concatenate_arr, \
#          distance_lvlh_pid_average_concantenate_arr, nb_seconds_since_start_pid_average_mid_concatenate_arr, distance_lvlh_pid_average_mid_concantenate_arr,\
#          distance_lvlh_pid_amplitude_mid_concantenate_arr, ecc_average_mid_concantenate_arr, ecc_obs_average_mid_concantenate_arr] = pickle.load(open(pickle_root + ".pickle"))
    
    label_temp = pickle_root_list[ipickle].replace("localtime_", "")
#     if 'equator' in pickle_root_list[ipickle]:
#         label = 'zenith'#'midnight'#'perigee'
#     elif 'pole' in pickle_root_list[ipickle]:
#         label = 'nadir' #'noon'
#     elif 'highamp_pole' in pickle_root_list[ipickle]:
#         label = 'highamp_apogee'
#     elif 'mid' in pickle_root_list[ipickle]:
#         label = '210 deg local time'
    label = pickle_root_list[ipickle]                                                                                                                                           
    if pickle_root_list[ipickle] == 'grav50_mid':
        label = 'Cr = 1.0'
    else:
        if len(label_overwrite) > 0:
            if label_overwrite[0] != '':
                label = label_overwrite[ipickle]
            else:
                label  = pickle_root_list[ipickle].replace('_mid', '').replace('FM03_', '')
        else:
            label  = pickle_root_list[ipickle].replace('_mid', '').replace('FM03_', '')


    if ipickle == 0:
        nb_interval_previous = nb_interval
#     if nb_interval != nb_interval_previous:
#         print "***! The number of interval of all runs has to be the same. The program will stop. !***"; raise Exception;

    if toplot == 'raw':
        if pickle_root_list[ipickle] == 'distance_lvlh_nb_seconds_since_start_date_start_msis':
            ax.plot(sec_msis/3600., dist_lvlh_msis * 1000., linewidth = 2, color = 'limegreen', label = 'NRLMSIS00e')
        else:
            ax.plot(nb_seconds_since_start_pid_average_concatenate_arr[::2]/3600., distance_lvlh_pid_average_concantenate_arr[::2] * 1000., linewidth = 2, color = color_arr[ipickle], label = label)
        #ax.plot(nb_seconds_since_start_pid_concatenate_arr/3600., distance_lvlh_pid_concantenate_arr * 1000., linewidth = 2,color = 'b', alpha = 0.3)
        #ax.plot(nb_seconds_since_start_pid_average_concatenate_arr/3600., distance_lvlh_pid_average_concantenate_arr * 1000., linewidth = 2, color = 'magenta', linestyle = 'dashed')

        #OLD
    #     ax.plot(nb_seconds_since_start_pid_average_mid_concatenate_arr/3600., distance_lvlh_pid_average_mid_concantenate_arr * 1000., linewidth = 2, color = 'magenta')
    #     ax.plot(nb_seconds_since_start_pid_average_mid_concatenate_arr/3600., ( distance_lvlh_pid_amplitude_mid_concantenate_arr + distance_lvlh_pid_average_mid_concantenate_arr )* 1000., linewidth = 2, color = 'red')
    #     ax.scatter(nb_seconds_since_start_pid_average_mid_concatenate_arr/3600., ( distance_lvlh_pid_amplitude_mid_concantenate_arr + distance_lvlh_pid_average_mid_concantenate_arr )* 1000., s= 500, marker = '.', color = 'red')
    elif toplot == 'amplitude':
        
        ax.plot(nb_seconds_since_start_pid_average_mid_concatenate_arr/3600., ( distance_lvlh_pid_amplitude_mid_concantenate_arr )* 1000., linewidth = 2, color = color_arr[ipickle], label = label)

    elif toplot == 'rho_control':
        #ax.scatter(nb_seconds_interval_corr/3600., rho_control, linewidth = 2, color = 'k')#, color = color_arr[ipickle])
        if ipickle == 0:
            ax.plot([[0] + [i for i in nb_seconds_interval_corr/3600.]][0], np.zeros([len(nb_seconds_interval_corr)+1]) + 1, linewidth = 2, color = 'limegreen', label = 'NRLMSIS00e')#, linestyle = 'dashed')
        #     ax.text(0.01,0.51,'NRLMSIS00e', fontsize = fontsize_plot, transform = ax.transAxes, horizontalalignment = 'left')
        ax.plot(nb_seconds_interval_corr/3600., rho_control+1, linewidth = 2, color = color_arr[ipickle], label = label)
    elif toplot == 'rho':
        density_pickle.append(rho_ave_conc)
        ax.plot(nb_seconds_ave_conc_arr[:-1]/3600., rho_ave_conc, linewidth = 2, color = color_arr[ipickle], label = label)
        ax.scatter(nb_seconds_ave_conc_arr[:-1]/3600., rho_ave_conc, linewidth = 2, color = color_arr[ipickle])
        # if ipickle == (nb_pickle - 1):
        #     ax.plot(nb_seconds_ave_conc_arr[:-1]/3600., rho_msis_ave_conc, linewidth = 2, color = 'limegreen', label = 'NRLMSIS00e - actual F10.7/Ap')
        #     ax.scatter(nb_seconds_ave_conc_arr[:-1]/3600., rho_msis_ave_conc, linewidth = 2, color = 'limegreen')

        
    if ipickle == 0:
        pickle_root_concatenate = pickle_root_list[ipickle]
    else:
        pickle_root_concatenate = pickle_root_concatenate + '_+_' +  pickle_root_list[ipickle]


    date_ref = date_start_save
    nb_ticks_xlabel = 10
    xticks_temp = nb_seconds_interval_corr/3600.
    nticks_temp = len(xticks_temp)
    xticks = []
    # for itick in range(nticks_temp):
    #     if np.mod(itick, nticks_temp / nb_ticks_xlabel ) == 0:
    #         xticks.append(xticks_temp[itick])

    # External density
    if ipickle == 0:
        if ((len(external) != 0) & (toplot == 'rho')):
            next = len(external)
            for iext in range(next):
                filename_ext = external[iext]
                dir_ext = '/'.join( filename_ext.split('/')[:-1]) + '/'
                var_in, var_in_order = read_input_file(filename_ext)
                isc = 0
                output_file_path_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]
                output_file_name_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')];                
                var_to_read = ['density', 'latitude']
                var_out, var_out_order = read_output_file( dir_ext + output_file_path_list[isc] + output_file_name_list[isc], var_to_read )
                density = var_out[find_in_read_input_order_variables(var_out_order, 'density')]
                latitude = var_out[find_in_read_input_order_variables(var_out_order, 'latitude')]
                date_ext = var_out[find_in_read_input_order_variables(var_out_order, 'date')]
                date_average_start_orbit_list = []
                date_average_end_orbit_list = []
                x_axis_average = []
                density_average, time_averaged, index_time_averaged = orbit_average(density, latitude, date_ext )
                date_average_start_orbit_list.append( np.array(time_averaged)[:,0] ) # take the date at the start of the bin
                date_average_end_orbit_list.append( np.array(time_averaged)[:,2] ) # take the date at the end of the bin
                norbit = len(time_averaged)
                for iorbit in range(norbit):
                    date_average_start_orbit = date_average_start_orbit_list[-1][iorbit]
                    date_average_start_orbit = datetime.strptime( date_average_start_orbit, "%Y/%m/%d %H:%M:%S.%f" )
                    nb_seconds_between_start_orbit_and_date_start = ( date_average_start_orbit - date_ref ).total_seconds()
                    x_axis_average.append( nb_seconds_between_start_orbit_and_date_start )
                x_axis_average = np.array(x_axis_average)
                ax.plot(x_axis_average/3600., density_average, linewidth = 2, color = external_color[iext], label = external_label[iext])
                ax.scatter(x_axis_average/3600., density_average, linewidth = 2, color = external_color[iext])
    # end of external density        

    # Add swarm density form pickle created on Big by code/swarm/read_swarm_rho.py
    if plot_swarm == 1:
        [sec_swarm, density_swarm, date_ref_swarm] = pickle.load(open('pickle/swarm.pickle'))
        delta_sec_swarm = (date_ref_swarm - date_ref).total_seconds()
        ax.plot((sec_swarm  + delta_sec_swarm)/3600., density_swarm, linewidth = 2, color = 'black', label = 'Swarm accelerometer')

    
    # end of add swarm density form pickle created on Big by code/swarm/read_swarm_rho.py
    
    dt = 24 # in hour
    date_arr = np.array([date_ref + timedelta(hours=i) for i in np.arange(0,nb_seconds_interval_corr[-1]/3600.,dt)])
    nticks = len(date_arr)
    for itick in range(nticks):
        xticks.append((date_arr[itick] - date_ref).total_seconds()/3600)

    xticks = []
    for itick in range(0,9*24+1,24):
        xticks.append(itick)
    # for itick in range(0,7*24*3600+1, 23*3600 + 52 * 60):
    #         xticks.append(np.float(itick) / 3600)

    date_list_str = []
    date_list = [date_ref + timedelta(hours=x) for x in xticks]
    for i in range(len(xticks)):
        #date_list_str.append( str(date_list[i])[5:10])# + "\n" + str(date_list[i])[11:16] )
        #date_list_str.append( format((xticks[i]/24.), ".1f"))
        date_list_str.append( format((xticks[i]/24.), ".0f"))

    # # for yearlong study
    # if ipickle == (nb_pickle - 1):
    #     xticks = np.array(seconds_pickle)/3600.
    #     nticks = len(xticks)
    #     date_list_str = []
    #     for itick in range(nticks):
    #         date_list_str.append(str(date_pickle[itick])[5:10])
    #     ax.xaxis.set_ticks(xticks)
    #     ax.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot, rotation='vertical')            
    # # end of for yearlong study    

    # Uncomment two lines below if not yearlong study
    ax.xaxis.set_ticks(xticks)
    ax.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')

# ax.plot([0, duration_simu], [0,0], linestyle = 'dashed', linewidth = 2, color = 'black')
#ax.set_xlim([0, 198.]); #ax.set_ylim([-20, 20])
# ax.text(duration_simu/2., -200, 'SpOCK in front -> need rho_control < 0', horizontalalignment = 'center', verticalalignment = 'bottom', fontsize = fontsize_plot, weight = 'normal')
# ax.text(duration_simu/2., 1200, 'SpOCK behind -> need rho_control > 0', horizontalalignment = 'center', verticalalignment = 'top', fontsize = fontsize_plot, weight = 'normal')
ax.margins(0,0)
legend = ax.legend(loc='upper left', bbox_to_anchor=(0, 1), numpoints = 1,  title="", fontsize = fontsize_plot)


if toplot == 'amplitude':
    fig_save_name = 'fig/all_amplitude_' + pickle_root_concatenate + '_nbinter' + str(nb_interval) + suffix_plot + ".pdf"
    y_label = 'Amplitude ocillations (m)'
if toplot == 'rho_control':
    fig_save_name = 'fig/all_rho_control_' + pickle_root_concatenate + '_nbinter' + str(nb_interval) + suffix_plot + ".pdf"
    y_label = '$\mu$'#'rho_contro''
    ax.set_ylim([0, 2])
    ax.set_xlim([0, ax.get_xlim()[1]])
if toplot == 'rho':
    y_label = 'Density (kg/m$^3$)'
    fig_save_name = 'fig/all_rho_' + pickle_root_concatenate + '_nbinter' + str(nb_interval) + suffix_plot + ".pdf"
    if len(external) > 0:
        fig_save_name = 'fig/all_rho_control_' + pickle_root_concatenate + '_nbinter' + str(nb_interval) + suffix_plot + "_with_external_" + external[0].split('/')[-1].replace(".txt", ".pdf")
    if plot_swarm == 1:
        fig_save_name = fig_save_name.replace('.pdf', '_with_swarm.pdf')

if toplot == 'raw':
    fig_save_name = 'fig/all_raw_' + pickle_root_concatenate + '_nbinter' + str(nb_interval) + suffix_plot + ".pdf"
    y_label = 'Distance (m)'
    ax.set_ylim([-50, 50])
    #ax.set_ylim([-7000, 500])
    #ax.set_xlim([0, 6*24])
    #ax.set_ylim([-200, 1200])
    #ax.text(0.5,0.98,label.title(),fontsize = fontsize_plot, weight = 'normal', color = 'k', transform = ax.transAxes, horizontalalignment = 'center', verticalalignment = 'top')
ax.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

# Compare SpOCK and Swarm (correlation and nrms error)
swarm_end_date = date_ref_swarm + timedelta(seconds = sec_swarm[-1])
swarm_end_seconds_since_date_ref = (swarm_end_date - date_ref).total_seconds()
swarm_time = sec_swarm  + delta_sec_swarm# np.arange(delta_sec_swarm, swarm_end_seconds_since_date_ref,)
spock_time = nb_seconds_ave_conc_arr[:-1]
istart_swarm_spock = np.where(swarm_time >= spock_time[0])[0][0]
iend_swarm_spock = np.where(swarm_time <= spock_time[-1])[0][-1]
swarm_inter_spock_time = swarm_time[istart_swarm_spock:iend_swarm_spock+1] # this is the time interval to interpolate SpOCK on
istart_spock_swarm = np.where(spock_time >= swarm_time[0])[0][0]
iend_spock_swarm = np.where(spock_time <= swarm_time[-1])[0][-1]
spock_inter_swarm_time = spock_time[istart_spock_swarm:iend_spock_swarm+1]
nspock_inter_swarm = len(spock_inter_swarm_time)
dens_spock_inter = []
for ispock in range(nspock_inter_swarm-1):
    itime_spock = spock_inter_swarm_time[ispock]
    itime_spock_next = spock_inter_swarm_time[ispock+1]
    iinter_start = np.where(swarm_inter_spock_time >= itime_spock)[0][0]
    iinter_end = np.where(swarm_inter_spock_time < itime_spock_next)[0][-1]
    ainter = (rho_ave_conc[ispock+1] - rho_ave_conc[ispock]) / (itime_spock_next - itime_spock)
    binter = rho_ave_conc[ispock] - ainter * itime_spock
    for itime_inter in swarm_inter_spock_time[iinter_start:iinter_end+1]:
        dens_spock_inter.append( ainter * itime_inter + binter )
        #print itime_spock, itime_inter, itime_spock_next 
dens_spock_inter = np.array(dens_spock_inter)
dens_swarm_inter = density_swarm[istart_swarm_spock:iend_swarm_spock+1]
nrms_error_swarm_spock = np.sqrt(np.mean((dens_spock_inter - dens_swarm_inter)**2)/np.mean(dens_swarm_inter**2))
print 'Correlation Swarm SpOCK', stats.pearsonr(dens_swarm_inter, dens_spock_inter)
print 'NRMS error Swarm SpOCK', nrms_error_swarm_spock


# Compare MSIS and Swarm (correlation and nrms error)
external_time = x_axis_average
istart_swarm_external = np.where(swarm_time >= external_time[0])[0][0]
iend_swarm_external = np.where(swarm_time <= external_time[-1])[0][-1]
swarm_inter_external_time = swarm_time[istart_swarm_external:iend_swarm_external+1] # this is the time interval to interpolate SpOCK on
istart_external_swarm = np.where(external_time >= swarm_time[0])[0][0]
iend_external_swarm = np.where(external_time <= swarm_time[-1])[0][-1]
external_inter_swarm_time = external_time[istart_external_swarm:iend_external_swarm+1]
nexternal_inter_swarm = len(external_inter_swarm_time)
dens_external_inter = []
for iexternal in range(nexternal_inter_swarm-1):
    itime_external = external_inter_swarm_time[iexternal]
    itime_external_next = external_inter_swarm_time[iexternal+1]
    iinter_start = np.where(swarm_inter_external_time >= itime_external)[0][0]
    iinter_end = np.where(swarm_inter_external_time < itime_external_next)[0][-1]
    ainter = (density_average[iexternal+1] - density_average[iexternal]) / (itime_external_next - itime_external)
    binter = density_average[iexternal] - ainter * itime_external
    for itime_inter in swarm_inter_external_time[iinter_start:iinter_end+1]:
        dens_external_inter.append( ainter * itime_inter + binter )
        #print itime_external, itime_inter, itime_external_next 
dens_external_inter = np.array(dens_external_inter)
dens_swarm_inter = density_swarm[istart_swarm_external:iend_swarm_external+1]
nrms_error_swarm_external = np.sqrt(np.mean((dens_external_inter - dens_swarm_inter)**2)/np.mean(dens_swarm_inter**2))
print '\nCorrelation Swarm MSIS', stats.pearsonr(dens_swarm_inter, dens_external_inter)
print 'NRMS error Swarm MSIS', nrms_error_swarm_external



# ax.plot(swarm_inter_spock_time/3600., dens_spock_inter, color = 'r')
# ax.plot(swarm_inter_external_time/3600., dens_external_inter)
# fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  


raise Exception


fig_title = ''#local time of perigee vs delta eccentricity
x_label = 'Difference in eccentricity' 

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


pickle_root_concatenate = ''
nb_pickle = len(pickle_root_list)
ipickle = 0
pickle_root = 'pickle/' + pickle_root_list[ipickle]


[duration_simu, nb_interval, nb_seconds_since_start_pid_concatenate_arr, distance_lvlh_pid_concantenate_arr, nb_seconds_since_start_pid_average_concatenate_arr, \
             distance_lvlh_pid_average_concantenate_arr, nb_seconds_since_start_pid_average_mid_concatenate_arr, \
             distance_lvlh_pid_average_mid_concantenate_arr, distance_lvlh_pid_amplitude_mid_concantenate_arr, ecc_average_mid_concantenate_arr, \
             ecc_obs_average_mid_concantenate_arr, localtime_spock_ok_pid_concatenate, phase_spock_ok_pid_concatenate_arr, argper_average_mid_concantenate_arr, \
     index_period_spock_concatenate_arr, argper_spock_ok_pid_concatenate_arr,\
                 ecc_ave_conc,ecc_obs_ave_conc,localtime_per,longitude_per,latitude_per,nb_seconds_ave_conc_arr]= pickle.load(open(pickle_root + ".pickle"))


if 'equator' in pickle_root_list[ipickle]:
    label = 'midnight'#'zenith'#'midnight'#'perigee'
elif 'pole' in pickle_root_list[ipickle]:
    label = 'noon#''nadir' #'noon'
elif 'highamp_pole' in pickle_root_list[ipickle]:
    label = 'highamp_apogee'
elif 'mid' in pickle_root_list[ipickle]:
    label = 'mid'#'210 deg local time'



if ipickle == 0:
    nb_interval_previous = nb_interval
if nb_interval != nb_interval_previous:
    print "***! The number of interval of all runs has to be the same. The program will stop. !***"; raise Exception;

x_axis = ecc_ave_conc-ecc_obs_ave_conc
y_axis = localtime_per
ax.set_ylim([np.min(y_axis), np.max(y_axis)])
ax.set_xlim([np.min(x_axis), np.max(x_axis)])
ax.set_ylabel('Local time of perigee', weight = 'bold', fontsize  = fontsize_plot)
#fig_save_name = 'fig/delta_eccentricity_vs_amplitude' + pickle_root_concatenate + '_nbinter' + str(nb_interval) + ".pdf"
fig_save_name = 'fig/localtime_per_vs_delta_ecc' + pickle_root_concatenate + '_nbinter' + str(nb_interval) + ".pdf"
y_label = 'Eccentricity' #'Eccentricity'#'Difference in eccentricity'

ax.scatter(x_axis, y_axis , linewidth = 2, color = color_arr[ipickle], label = label)

fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

raise Exception

fig_title = ''#eccentriciy or delta ecc vs  amplitutde oscilaltion 
x_label = 'Amplitude oscillations (m)' 

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


pickle_root_concatenate = ''
nb_pickle = len(pickle_root_list)
ipickle = 0
pickle_root = 'pickle/' + pickle_root_list[ipickle]


[duration_simu, nb_interval, nb_seconds_since_start_pid_concatenate_arr, distance_lvlh_pid_concantenate_arr, nb_seconds_since_start_pid_average_concatenate_arr, \
             distance_lvlh_pid_average_concantenate_arr, nb_seconds_since_start_pid_average_mid_concatenate_arr, \
             distance_lvlh_pid_average_mid_concantenate_arr, distance_lvlh_pid_amplitude_mid_concantenate_arr, ecc_average_mid_concantenate_arr, \
             ecc_obs_average_mid_concantenate_arr, localtime_spock_ok_pid_concatenate, phase_spock_ok_pid_concatenate_arr, argper_average_mid_concantenate_arr, \
                 index_period_spock_concatenate_arr, argper_spock_ok_pid_concatenate_arr,\
                 ecc_ave_conc,ecc_obs_ave_conc,localtime_per,longitude_per,latitude_per,nb_seconds_ave_conc_arr]= pickle.load(open(pickle_root + ".pickle"))


if 'equator' in pickle_root_list[ipickle]:
    label = 'midnight'#'zenith'#'midnight'#'perigee'
elif 'pole' in pickle_root_list[ipickle]:
    label = 'noon#''nadir' #'noon'
elif 'highamp_pole' in pickle_root_list[ipickle]:
    label = 'highamp_apogee'
elif 'mid' in pickle_root_list[ipickle]:
    label = 'mid'#'210 deg local time'



if ipickle == 0:
    nb_interval_previous = nb_interval
if nb_interval != nb_interval_previous:
    print "***! The number of interval of all runs has to be the same. The program will stop. !***"; raise Exception;

x_axis = ( distance_lvlh_pid_amplitude_mid_concantenate_arr )* 1000.
y_axis = ecc_average_mid_concantenate_arr - ecc_obs_average_mid_concantenate_arr#ecc_average_mid_concantenate_arr
ax.set_ylim([np.min(y_axis), np.max(y_axis)])
ax.set_ylabel('Difference in eccentricity', weight = 'bold', fontsize  = fontsize_plot)
#fig_save_name = 'fig/delta_eccentricity_vs_amplitude' + pickle_root_concatenate + '_nbinter' + str(nb_interval) + ".pdf"
fig_save_name = 'fig/delta_eccentricity_vs_amplitude' + pickle_root_concatenate + '_nbinter' + str(nb_interval) + ".pdf"
y_label = 'Eccentricity' #'Eccentricity'#'Difference in eccentricity'

ax.scatter(x_axis, y_axis , linewidth = 2, color = color_arr[ipickle], label = label)

fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  


raise Exception
fig_title = ''#eccentriciy and  amplitutde oscilaltion vs time
x_label = 'Time (days)'#'Amplitude oscillations (m)' 

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


pickle_root_concatenate = ''
nb_pickle = len(pickle_root_list)
ipickle = 0
pickle_root = 'pickle/' + pickle_root_list[ipickle]


[duration_simu, nb_interval, nb_seconds_since_start_pid_concatenate_arr, distance_lvlh_pid_concantenate_arr, nb_seconds_since_start_pid_average_concatenate_arr, \
             distance_lvlh_pid_average_concantenate_arr, nb_seconds_since_start_pid_average_mid_concatenate_arr, \
             distance_lvlh_pid_average_mid_concantenate_arr, distance_lvlh_pid_amplitude_mid_concantenate_arr, ecc_average_mid_concantenate_arr, \
             ecc_obs_average_mid_concantenate_arr, localtime_spock_ok_pid_concatenate, phase_spock_ok_pid_concatenate_arr, argper_average_mid_concantenate_arr, \
                 index_period_spock_concatenate_arr, argper_spock_ok_pid_concatenate_arr,\
                 ecc_ave_conc,ecc_obs_ave_conc,localtime_per,longitude_per,latitude_per,nb_seconds_ave_conc_arr]= pickle.load(open(pickle_root + ".pickle"))


if 'equator' in pickle_root_list[ipickle]:
    label = 'midnight'#'zenith'#'midnight'#'perigee'
elif 'pole' in pickle_root_list[ipickle]:
    label = 'noon#''nadir' #'noon'
elif 'highamp_pole' in pickle_root_list[ipickle]:
    label = 'highamp_apogee'
elif 'mid' in pickle_root_list[ipickle]:
    label = 'mid'#'210 deg local time'



if ipickle == 0:
    nb_interval_previous = nb_interval
if nb_interval != nb_interval_previous:
    print "***! The number of interval of all runs has to be the same. The program will stop. !***"; raise Exception;

x_axis = nb_seconds_since_start_pid_average_mid_concatenate_arr/3600.#( distance_lvlh_pid_amplitude_mid_concantenate_arr )* 1000.
y_axis = ecc_average_mid_concantenate_arr# - ecc_obs_average_mid_concantenate_arr#ecc_average_mid_concantenate_arr
#y_axis = -y_axis*() + y_axis[0] + ( distance_lvlh_pid_amplitude_mid_concantenate_arr[0] )* 1000.
ax.set_ylim([np.min(y_axis), np.max(y_axis)])
ax.tick_params('y', colors='blue')

ax.set_ylabel('Eccentricity', weight = 'bold', fontsize  = fontsize_plot, color = 'blue')
#ax.plot(nb_seconds_since_start_pid_average_mid_concatenate_arr/3600., ecc_average_mid_concantenate_arr - ecc_obs_average_mid_concantenate_arr, linewidth = 2, color = color_arr[ipickle], label = label)
fig_save_name = 'fig/eccentricity_and_amplitude' + pickle_root_concatenate + '_nbinter' + str(nb_interval) + ".pdf"
y_label = 'Eccentricity' #'Eccentricity'#'Difference in eccentricity'

#ax.scatter(x_axis, y_axis , linewidth = 2, color = color_arr[ipickle], label = label)

ax.plot(x_axis, y_axis , linewidth = 2, color = 'blue')
ax.margins(0,0)
ax2 = ax.twinx()
ax2.set_ylabel('Amplitude of oscillations (m)', weight = 'bold', fontsize  = fontsize_plot, color = 'red')

[i.set_linewidth(2) for i in ax2.spines.itervalues()] # change the width of the frame of the figure
ax2.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
ax2.tick_params('y', colors='red')

y_axis_dist = ( distance_lvlh_pid_amplitude_mid_concantenate_arr )* 1000. 
ax2.plot(x_axis, y_axis_dist , linewidth = 2, color = 'red')

# pickle_root_concatenate = pickle_root_list[ipickle]

ax2.set_ylim([np.min(y_axis_dist), np.max(y_axis_dist)])
ax2.set_xlim([np.min(x_axis), np.max(x_axis)])
#ax.margins(0,0)

# ax.plot([0, duration_simu], [0,0], linestyle = 'dashed', linewidth = 2, color = 'black')
# ax.set_xlim([0, duration_simu]); #ax.set_ylim([-20, 20]) 
# ax.text(duration_simu/2., -200, 'SpOCK in front -> need rho_control < 0', horizontalalignment = 'center', verticalalignment = 'bottom', fontsize = fontsize_plot, weight = 'bold')
# ax.text(duration_simu/2., 1200, 'SpOCK behind -> need rho_control > 0', horizontalalignment = 'center', verticalalignment = 'top', fontsize = fontsize_plot, weight = 'bold')
ax2.margins(0,0)
#legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="", fontsize = fontsize_plot)


ax.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

raise Exception


######
fig_title = ''#Difference in eccentricy SpOCK - observations
x_label = 'Time (days)' 

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


pickle_root_concatenate = ''
nb_pickle = len(pickle_root_list)
for ipickle in range(nb_pickle):
    pickle_root = 'pickle/' + pickle_root_list[ipickle]

    [duration_simu, nb_interval, nb_seconds_since_start_pid_concatenate_arr, distance_lvlh_pid_concantenate_arr, nb_seconds_since_start_pid_average_concatenate_arr, \
                 distance_lvlh_pid_average_concantenate_arr, nb_seconds_since_start_pid_average_mid_concatenate_arr, \
                 distance_lvlh_pid_average_mid_concantenate_arr, distance_lvlh_pid_amplitude_mid_concantenate_arr, ecc_average_mid_concantenate_arr, \
                 ecc_obs_average_mid_concantenate_arr, localtime_spock_ok_pid_concatenate, phase_spock_ok_pid_concatenate_arr, argper_average_mid_concantenate_arr, \
                     index_period_spock_concatenate_arr, argper_spock_ok_pid_concatenate_arr,\
                 ecc_ave_conc,ecc_obs_ave_conc,localtime_per,longitude_per,latitude_per,nb_seconds_ave_conc_arr]= pickle.load(open(pickle_root + ".pickle")) 
    
    # label_temp = pickle_root_list[ipickle].replace("localtime_", "")
    # if 'equator' in pickle_root_list[ipickle]:
    #     label = 'zenith'#'midnight'#'perigee'
    # elif 'pole' in pickle_root_list[ipickle]:
    #     label = 'nadir' #'noon' 
    # elif 'highamp_pole' in pickle_root_list[ipickle]:
    #     label = 'highamp_apogee'
    # elif 'mid' in pickle_root_list[ipickle]:
    #     label = '210 deg local time' 

    if pickle_root_list[ipickle] == 'grav50_mid':
        label = 'Cr = 1.0'
    else:
        label_temp = pickle_root_list[ipickle].replace('_mid', '')
        label = 'Cd = ' + label_temp[0] + '.' + label_temp[1]        

    if ipickle == 0:
        nb_interval_previous = nb_interval
    if nb_interval != nb_interval_previous:
        print "***! The number of interval of all runs has to be the same. The program will stop. !***"; raise Exception;

    #ax.plot(nb_seconds_since_start_pid_average_mid_concatenate_arr/3600., ecc_average_mid_concantenate_arr - ecc_obs_average_mid_concantenate_arr, linewidth = 2, color = color_arr[ipickle], label = label)
    ax.plot(nb_seconds_ave_conc_arr[:-1]/3600., ecc_ave_conc-ecc_obs_ave_conc, linewidth = 2, color = color_arr[ipickle], label = label)

#     ax.plot(nb_seconds_since_start_pid_average_mid_concatenate_arr/3600., ecc_average_mid_concantenate_arr , linewidth = 2, color = color_arr[ipickle], label = label)
#     if ipickle == 0: # observations same for each run
#         ax.plot(nb_seconds_since_start_pid_average_mid_concatenate_arr/3600., ecc_obs_average_mid_concantenate_arr, linewidth = 2, color = 'black', label = 'Observations')

    if ipickle == 0:
        pickle_root_concatenate = pickle_root_list[ipickle]
    else:
        pickle_root_concatenate = pickle_root_concatenate + '_+_' +  pickle_root_list[ipickle]
ax.margins(0,0)

# ax.plot([0, duration_simu], [0,0], linestyle = 'dashed', linewidth = 2, color = 'black')
# ax.set_xlim([0, duration_simu]); #ax.set_ylim([-20, 20]) 
# ax.text(duration_simu/2., -200, 'SpOCK in front -> need rho_control < 0', horizontalalignment = 'center', verticalalignment = 'bottom', fontsize = fontsize_plot, weight = 'bold')
# ax.text(duration_simu/2., 1200, 'SpOCK behind -> need rho_control > 0', horizontalalignment = 'center', verticalalignment = 'top', fontsize = fontsize_plot, weight = 'bold')
ax.margins(0,0)
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="", fontsize = fontsize_plot)

fig_save_name = 'fig/all_delta_eccentricity_' + pickle_root_concatenate + '_nbinter' + str(nb_interval) + "again.pdf"
y_label = 'Difference in eccentricity' #'Eccentricity'#'Difference in eccentricity'

ax.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  



raise Exception
# FTT
plt.close('all')
fig,ax = plt.subplots()
signal = distance_lvlh_pid_amplitude_mid_concantenate_arr*1000
# dt_sample about 95 minutes. actually not always the same (sometimes differ by 10 minutes or a couple of minutes)
dt_sample = nb_seconds_since_start_pid_average_mid_concatenate_arr[-1] - nb_seconds_since_start_pid_average_mid_concatenate_arr[-2] 
n = len(signal)
sp = np.fft.fft(signal)
freq = np.fft.fftfreq(n, dt_sample)
freq_pos_index = np.where(freq > 0)[0]
freq_pos_ok = freq[freq_pos_index]
sp_pos = sp[freq_pos_index]
sp_pos_abs = abs(sp_pos) # sp_pos is  a complex number, only the norm is relevant
ax.plot(signal)

fig,axfft = plt.subplots()
axfft.plot(1/freq_pos_ok/3600., sp_pos_abs) # sp.real





#plt.close('all')
fig,ax = plt.subplots()
signal = distance_lvlh_pid_amplitude_mid_concantenate_arr*1000
# dt_sample about 95 minutes. actually not always the same (sometimes differ by 10 minutes or a couple of minutes)
dt_sample = 1#nb_seconds_since_start_pid_average_mid_concatenate_arr[-1] - nb_seconds_since_start_pid_average_mid_concatenate_arr[-2] 
n = len(signal)
sp = np.fft.fft(signal)
freq = np.fft.fftfreq(n, dt_sample)
freq_pos_index = np.where(freq > 0)[0]
freq_pos = freq[freq_pos_index]
sp_pos = sp[freq_pos_index]
sp_pos_abs = abs(sp_pos) # sp_pos is  a complex number, only the norm is relevant
ax.plot(signal)

fig,axfft = plt.subplots()
#axfft.plot(1/freq_pos/3600., sp_pos_abs) # sp.real
axfft.plot(nb_seconds_since_start_pid_average_mid_concatenate_arr[(1/freq_pos).astype(int)-1]/3600., sp_pos_abs) # sp.real




raise Exception

plt.close('all')
t = np.arange(0, 6*np.pi, 0.1)
signal = np.sin(t)
sp = np.fft.fft(signal)
freq = np.fft.fftfreq(t.shape[-1])#, 0.1)
plt.plot(signal)

fig,ax = plt.subplots()
ax.plot(freq, abs(sp)) # sp.real



Fs = 150.0;  # sampling rate
Ts = 1.0/Fs; # sampling interval
t = np.arange(0,1,Ts) # time vector

ff = 5;   # frequency of the signal
y = np.sin(2*np.pi*ff*t)

n = len(y) # length of the signal
k = np.arange(n)
T = n/Fs
frq = k/T # two sides frequency range
frq = frq[range(n/2)] # one side frequency range

Y = np.fft.fft(y)/n # fft computing and normalization
Y = Y[range(n/2)]

fig, ax = plt.subplots(2, 1)
ax[0].plot(t,y)
ax[0].set_xlabel('Time')
ax[0].set_ylabel('Amplitude')
ax[1].plot(frq,abs(Y),'r') # plotting the spectrum
ax[1].set_xlabel('Freq (Hz)')
ax[1].set_ylabel('|Y(freq)|')
