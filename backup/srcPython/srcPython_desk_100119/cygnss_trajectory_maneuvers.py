# This script creates an animation of the CYGNSS spacing as a function of time between start_date and end_date. It downloads all TLEs in this time interval and computes the angle from the ascending node to the sc at each TLE epoch (= true anomaly + argument of perigee). The true anomaly and the argument of perigee are calculated from the TLEs by converting the TLEs elements into orbial elements. This is done by SGP4 at the initialization of SpOCK.
# To run this script:
# python cygnss_trajectory_maneuvers.py start_date end_date
# where start_date is the date where to start the animation.
# ASSUMPTIONS:
# - start_date and end_date must have the format YYYY-mm-dd (for example: 2017-03-26)
# - all dates have to be UTC
# - see section PARAMETERS TO SET
import sys
sys.path.append("/Users/cbv/Google Drive/Work/PhD/Research/Code/spock/srcPython")
import matplotlib
matplotlib.use("Agg") # without this line, when running this script from a cronjob we get an error "Unable to access the X Display, is $DISPLAY set properly?"

import matplotlib.gridspec as gridspec
import numpy as np
from struct import *
from matplotlib import pyplot as plt
from cygnss_read_spock_spec_bin import *
from mpl_toolkits.basemap import Basemap, shiftgrid
from datetime import datetime, timedelta
from collections import *
import os
from read_input_file import *
from read_output_file import *
import pickle
from spock_main_input import *
from convert_tle_date_to_date import *
#from cygnss_read_spock_spec import *

# PARAMETERS TO SET
#load TLE sma pickle (set to 1) -> won't propagate TLEs with SpOCK to get sma at TLE epoch
load_tle_result = 0

## path of the folder where you want to store the results (pickle, image, video)
path_folder_results = './'

## Parameters for the figure
height_fig = 11.  # the width is calculated as height_fig * 4/3.
fontsize_plot = 25
ratio_fig_size = 4./3
# end of PARAMETERS TO SET

# Run SpOCK to get the CYGNSS positions
earth_radius        = 6378.137; # mean equatorial radius (km)                                                                                                                                                                                                                               
start_epoch_str = sys.argv[1]
end_epoch_str =  sys.argv[2]

start_epoch = datetime.strptime(start_epoch_str, "%Y-%m-%d")
end_epoch = datetime.strptime(end_epoch_str, "%Y-%m-%d")

nb_day = (int)((end_epoch - start_epoch).total_seconds() / 3600. / 24)
phase_angle = np.zeros([8, nb_day])
sma = np.zeros([8, nb_day])
phase_angle_ref = np.zeros([8, nb_day])
label_arr_conversion = [3, 2, 7, 1, 0, 5, 6, 4]
isc_ref = 3
isc_ref_nb = label_arr_conversion[isc_ref-1]
nb_sc = 8
date = []
date_spock = []
dt_simu = 10.
order_gravity = 4
forces = 'drag moon_gravity sun_gravity solar_pressure'
for iday in range(nb_day):
    print iday, nb_day-1
    date_spock_day = []
    date_now = start_epoch + timedelta(days = iday)
    date_tle_str = datetime.strftime(date_now, "%Y-%m-%d")
    date.append(date_now)
    #if date_now >= datetime.strptime("2018-06-10", "%Y-%m-%d"):
        #os.system("cygnss_tle_web.py " +   date_tle_str)
    date_now_str = datetime.strftime(date_now, "%Y-%m-%dT00:00:00")
    date_start_str = datetime.strftime(date_now, "%Y-%m-%dT00:00:00")
    date_end_str = datetime.strftime(date_now, "%Y-%m-%dT00:00:01")
    main_input_filename = date_tle_str + '.txt'
    cygnss_tle_filename = 'cygnss_' + date_tle_str + '.txt'
    spock_main_input(
        main_input_filename,
        # for TIME section
        date_start_str,
        date_end_str,
        dt_simu,
        # for SPACECRAFT section
        8,
        '0',
        29.,
        'cygnss_geometry_2016_acco08.txt',
        # for ORBIT section
        cygnss_tle_filename,
        # for FORCES section
        order_gravity,
        forces,
        'static',
        # for OUTPUT section
        '~/cygnss/website/trajectory_maneuvers/out', 
        dt_simu, 
        # for ATTITUDE section
        "nadir",
        # for GROUNDS_STATIONS section
        "0",#"my_ground_stations.txt"
        # for SPICE section
        '/Users/cbv/cspice/data', 
        # for DENSITY_MOD section
        1
        )
#    if iday == nb_day -1:
    #if date_now >= datetime.strptime("2018-06-10", "%Y-%m-%d"):
        #os.system("mpirun -np 4 spock_dev " + main_input_filename)
    var_in, var_in_order = read_input_file(main_input_filename)
    output_file_path_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]; 
    output_file_name_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')]; 
    dt = var_in[find_in_read_input_order_variables(var_in_order, 'dt_output')];
    var_to_read = ["phase_angle"]
    for isc in range(8):
        var_out, var_out_order = read_output_file( output_file_path_list[isc] + output_file_name_list[isc], var_to_read )
        phase_angle[isc, iday] = var_out[find_in_read_input_order_variables(var_out_order, 'phase_angle')][0]
        sma[isc, iday] = open(output_file_path_list[isc] + 'TLE_' + output_file_name_list[isc]).readlines()[12].split()[11]
        date_spock_day.append( var_out[find_in_read_input_order_variables(var_out_order, 'date')][0] )
    for isc in range(8):
        absolute_angular_dist = np.abs( phase_angle[isc,iday] - phase_angle[isc_ref_nb,iday] )
        phase_angle_ref[isc, iday] = min( [absolute_angular_dist, 360 - absolute_angular_dist] )
    date_spock.append(date_spock_day)

# Predictions
nb_month_pred = 2
nb_day_pred = nb_month_pred * 30
date_end_str = datetime.strftime(date_now + timedelta(days = nb_day_pred), "%Y-%m-%dT%H:%M:%S")
## Nadir
main_input_filename = main_input_filename.replace(".txt","_pred.txt")
# order_gravity= 0
# dt_simu = 60
spock_main_input(
    main_input_filename,
    # for TIME section
    date_start_str,
    date_end_str,
    dt_simu,
    # for SPACECRAFT section
    8,
    '0',
    29.,
    'cygnss_geometry_2016_acco08.txt',
    # for ORBIT section
    cygnss_tle_filename,
    # for FORCES section
    order_gravity,
    forces,
    'dynamic',
    # for OUTPUT section
    '~/cygnss/website/trajectory_maneuvers/out', 
    dt_simu, 
    # for ATTITUDE section
    "nadir",
    # for GROUNDS_STATIONS section
    "0",#"my_ground_stations.txt"
    # for SPICE section
    '/Users/cbv/cspice/data', 
    # for DENSITY_MOD section
    1
    )
os.system("mpirun -np 4 spock_dev " + main_input_filename)
os.system("python state.py . " + main_input_filename + " save sma_average")
pickle_sma_average_nadir_prediction =  main_input_filename.replace(".txt","_sma_average.pickle")
sma_average_nadir_prediction = pickle.load( open( pickle_sma_average_nadir_prediction ) )
pickle_x_axis_average_nadir_prediction = main_input_filename.replace(".txt","_x_axis_average.pickle")
x_axis_average_nadir_prediction = pickle.load( open( pickle_x_axis_average_nadir_prediction ) ) # be careful, this is in number of seconds this the start date of 
# the SpOCK's simulation. So it is in number of seconds since today. But we want it to be in number of seconds since date_ini

## Highdrag
main_input_filename = main_input_filename.replace(".txt","_high_drag.txt")
spock_main_input(
    main_input_filename,
    # for TIME section
    date_start_str,
    date_end_str,
    dt_simu,
    # for SPACECRAFT section
    8,
    '0',
    29.,
    'cygnss_geometry_2016_acco08.txt',
    # for ORBIT section
    cygnss_tle_filename,
    # for FORCES section
    order_gravity,
    forces,
    'dynamic',
    # for OUTPUT section
    '~/cygnss/website/trajectory_maneuvers/out', 
    dt_simu, 
    # for ATTITUDE section
    "(82; 0; 0)(0; 0; 0)",
    # for GROUNDS_STATIONS section
    "0",#"my_ground_stations.txt"
    # for SPICE section
    '/Users/cbv/cspice/data', 
    # for DENSITY_MOD section
    1
    )
os.system("mpirun -np 4 spock_dev " + main_input_filename)
os.system("python state.py . " + main_input_filename + " save sma_average")
pickle_sma_average_highdrag_prediction =  main_input_filename.replace(".txt","_sma_average.pickle")
sma_average_highdrag_prediction = pickle.load( open( pickle_sma_average_highdrag_prediction ) )
pickle_x_axis_average_highdrag_prediction = main_input_filename.replace(".txt","_x_axis_average.pickle")
x_axis_average_highdrag_prediction = pickle.load( open( pickle_x_axis_average_highdrag_prediction ) ) # be careful, this is in number of seconds this the start date of 
# the SpOCK's simulation. So it is in number of seconds since today. But we want it to be in number of seconds since date_ini

## Convert x_axis_average_nadir_prediction and x_axis_average_high_drag_prediction so that they correspond to the number of seconds since date_ini
date_start = datetime.strptime(date_start_str, "%Y-%m-%dT%H:%M:%S")
for isc in range(nb_sc):
    nb_tle_times_two = len(x_axis_average_nadir_prediction[isc])
    for itle_times_two in range(nb_tle_times_two):
        x_axis_average_nadir_prediction[isc][itle_times_two] = x_axis_average_nadir_prediction[isc][itle_times_two] + ( date_start - date[0] ).total_seconds()
for isc in range(nb_sc):
    nb_tle_times_two = len(x_axis_average_highdrag_prediction[isc])
    for itle_times_two in range(nb_tle_times_two):
        x_axis_average_highdrag_prediction[isc][itle_times_two] = x_axis_average_highdrag_prediction[isc][itle_times_two] + ( date_start - date[0] ).total_seconds()

    
nb_seconds_since_start = np.arange(0, nb_day * 24 * 3600, 24 * 3600)
nb_seconds_in_simu = nb_seconds_since_start[-1]
nb_day_with_pred = nb_day + nb_day_pred
nb_seconds_since_start_pred = np.arange(0, nb_day_with_pred * 24 * 3600, 24 * 3600)
nb_seconds_in_simu_pred = nb_seconds_since_start_pred[-1]

dsma =  sma[isc, -1] - sma_average_nadir_prediction[isc][0]
sma = sma - dsma

satColors = ['black', 'blue', 'red', 'mediumorchid', 'dodgerblue', 'magenta', 'darkgreen', 'limegreen'] #['lime', 'blue', 'indigo', 'purple', 'dodgerblue', 'steelblue', 'seagreen', 'limegreen']
label_arr = ['FM05', 'FM04', 'FM02', 'FM01', 'FM08', 'FM06', 'FM07', 'FM03']


# with PREDICTIONS
ratio_fig_size = 4./3
height_fig = 11
width_fig = height_fig * ratio_fig_size 
fontsize_plot = 22
fig_title = ''
fig = plt.figure(num=None, figsize=(width_fig, height_fig), dpi=80, facecolor='w', edgecolor='k')
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                                                                      
gs = gridspec.GridSpec(1, 1)
# SMA
y_label = 'Semi-major axis - $R_E$ (km)'
x_label = 'Real time'
ax = plt.subplot(gs[0, 0])#fig.add_subplot(gs[0, 2])
ax.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                       
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                           
sma_min = 1e6
for isc_temp in range(nb_sc):
    isc = label_arr_conversion[isc_temp]        
    ax.plot(nb_seconds_since_start, sma[isc, :]-earth_radius, linewidth = 2, color = satColors[isc], label = label_arr[isc])
    #ax.scatter(x_axis_average_nadir_prediction[isc], np.array(sma_average_nadir_prediction[isc])-earth_radius,  color = satColors[isc], label = label_arr[isc],s = 0.1, marker = 'o')
    N = 20
    running_ave_sma = np.convolve( np.array(sma_average_nadir_prediction[isc])-earth_radius, np.ones((N,))/N, mode='valid')
    ax.plot(x_axis_average_nadir_prediction[isc][:-N+1], running_ave_sma, linewidth = 2, color = satColors[isc], label = label_arr[isc]) #[1:] ebcause the first value of running_ave_sma is messed up
    #ax.plot(x_axis_average_nadir_prediction[isc], np.array(sma_average_nadir_prediction[isc])-earth_radius, linewidth = 0.1, color = satColors[isc], label = label_arr[isc])
    running_ave_sma = np.convolve( np.array(sma_average_highdrag_prediction[isc])-earth_radius, np.ones((N,))/N, mode='valid')
    ax.plot(x_axis_average_highdrag_prediction[isc][:-N+1], running_ave_sma, linewidth = 2, color = satColors[isc], label = label_arr[isc]) #[1:] ebcause the first value of running_ave_sma is messed up
    if np.min(np.array(sma_average_highdrag_prediction[isc])) < sma_min:
        sma_min = np.min(np.array(sma_average_highdrag_prediction[isc]))
ax.text((nb_seconds_since_start[-1] + nb_seconds_since_start[0])/2.,  sma.max()-earth_radius - (sma.max() - sma_min)/ 100., 'Historical TLEs' , verticalalignment = 'top', horizontalalignment = 'center', fontsize = fontsize_plot, weight = 'normal')
ax.text((x_axis_average_highdrag_prediction[isc][-1] + x_axis_average_highdrag_prediction[isc][0])/2.,  sma.max()-earth_radius - (sma.max() - sma_min)/ 100., "SpOCK's\npredictions" , verticalalignment = 'top', horizontalalignment = 'center', fontsize = fontsize_plot, weight = 'normal')
ax.plot([x_axis_average_highdrag_prediction[isc][0], x_axis_average_highdrag_prediction[isc][0]], [0, 1e6], linewidth = 2, linestyle = 'dashed' , color = 'k')
ax.text(x_axis_average_highdrag_prediction[isc][0],   sma.max()-earth_radius - (sma.max() - sma_min)/ 5., date_start_str[:10] , verticalalignment = 'top', horizontalalignment = 'right', fontsize = fontsize_plot, weight = 'normal', rotation= 90, color = 'black')
nb_ticks_xlabel = 8
dt_xlabel =  nb_seconds_in_simu_pred / nb_ticks_xlabel # dt for ticks on x axis (in seconds)
start_xaxis_label = 0
date_ref = date[0]
xticks = np.arange(start_xaxis_label, start_xaxis_label+nb_seconds_in_simu_pred+1, dt_xlabel)
date_list_str = []
date_list = [date_ref + timedelta(seconds=x-xticks[0]) for x in xticks]
for i in range(len(xticks)):
    if dt_xlabel >= 3*24*3600:
        date_list_str.append( str(date_list[i])[5:10] )
    else:
        date_list_str.append( str(date_list[i])[5:10] + "\n" + str(date_list[i])[11:16] )
ax.xaxis.set_ticks(xticks)
ax.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')

ax.set_ylim([sma_min-earth_radius, sma.max()-earth_radius])
ax.set_xlim([0, nb_seconds_since_start_pred[-1]])
gs.update(left = 0, right=1, top = 1,bottom = 0., wspace = 0.14, hspace = 0)
fig_save_name = 'pred.pdf'
fig.savefig(fig_save_name, facecolor=fig  .get_facecolor(), edgecolor='none', bbox_inches='tight')





#Read file of maneuverse  (high drag and Sun pointed)
filename_man = '/Users/cbv/cygnss/comparison_tle/maneuvers_with_year.txt'
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
        man_start = datetime.strptime(man_start, '%y%d%m') #280717
        man_end = datetime.strptime(man_end, '%y%d%m') #280717
        nb_seconds_first_tle_to_start_highdrag_isc.append((man_start - date[0]).total_seconds())
        nb_seconds_first_tle_to_end_highdrag_isc.append((man_end - date[0]).total_seconds())
        highdrag_sc.append([man_start, man_end])
        iline = iline + 1
    iline = iline + 1 # skip line called 'sunpointed'
    while len(read_file_man[iline].rstrip()) != 0: # reached next sc if this is false. otherwise fill sunpointed dates
        man_start = read_file_man[iline].rstrip().split('-')[0]
        man_end = read_file_man[iline].rstrip().split('-')[1]
        man_start = datetime.strptime(man_start, '%y%d%m') #280717
        man_end = datetime.strptime(man_end, '%y%d%m') #280717
        sunpointed_sc.append([man_start, man_end])
        nb_seconds_first_tle_to_start_sunpointed_isc.append((man_start - date[0]).total_seconds())
        nb_seconds_first_tle_to_end_sunpointed_isc.append((man_end - date[0]).total_seconds())
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






start_xaxis_label = 0
date_ref =  date[0]
ratio_fig_size = 4./3
height_fig = 16
width_fig = height_fig * ratio_fig_size 
fontsize_plot = 22
fig_title = ''
iday_count = -1
for iday in range(nb_day):#nb_day): # !!!!!!!!!!!
    print iday, nb_day-1
    iday_count = iday_count + 1
    fig = plt.figure(num=None, figsize=(width_fig, height_fig), dpi=80, facecolor='w', edgecolor='k')
    plt.rc('font', weight='normal') ## make the labels of the ticks in bold                                                                      
    gs = gridspec.GridSpec(2, 2)

    ax = plt.subplot(gs[0, 0:2])#fig.add_subplot(gs[0, 0])
    [i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                       
    plt.rc('font', weight='normal') ## make the labels of the ticks in bold                           
    phi_array=np.arange(0,6.28,0.01)
    r = 1.
    ax.plot( r*np.cos(phi_array), r*np.sin(phi_array), 'k--', linewidth = 2 )
    ax.set_xlim([-r*1.08, r*1.08])
    ax.set_ylim([-r*1.08, r*1.08])
    ax.axis('off')
    for isc_temp in range(8):
        isc = label_arr_conversion[isc_temp]
        x1 = r*1.0*np.cos((phase_angle[isc, iday] - phase_angle[isc_ref_nb,iday])*np.pi/180)                                  
        y1 = r*1.0*np.sin((phase_angle[isc,iday] - phase_angle[isc_ref_nb,iday])*np.pi/180)                                                              
        ax.scatter( [x1], [y1], marker = 'o', label = label_arr[isc] + ' (' +  format(phase_angle_ref[isc, iday], ".0f") + u'\N{DEGREE SIGN}' + ')', s = 200, color= satColors[isc],linewidth = 4, zorder = 5)        
        nb_man = len(nb_seconds_first_tle_to_start_highdrag[isc_temp])
        one_hd = 0
        for iman in range(nb_man):
            if ((nb_seconds_since_start[iday] >= nb_seconds_first_tle_to_start_highdrag[isc_temp][iman]) & (nb_seconds_since_start[iday] <= nb_seconds_first_tle_to_end_highdrag[isc_temp][iman] )):
                ax.text(x1*0.85, y1*0.85, 'HD', fontsize = fontsize_plot, horizontalalignment = 'center', verticalalignment = 'center')
                ax.plot( [x1*0.85], [y1*0.85], marker = 'o', linewidth = 4, zorder = 5, ms=40, mec= satColors[isc], mfc='none', mew=2)
                one_hd = 1
        if one_hd == 0: # in the file with maneuvers, there are a few times that are classified as SP and HD. In these cases, only indicate HD (not HD and SP)
            nb_man = len(nb_seconds_first_tle_to_start_sunpointed[isc_temp])
            for iman in range(nb_man):
                if ((nb_seconds_since_start[iday] >= nb_seconds_first_tle_to_start_sunpointed[isc_temp][iman]) & (nb_seconds_since_start[iday] <= nb_seconds_first_tle_to_end_sunpointed[isc_temp][iman] )):
                    ax.text(x1*0.85, y1*0.85, 'SP', fontsize = fontsize_plot, horizontalalignment = 'center', verticalalignment = 'center')
                    ax.plot( [x1*0.85], [y1*0.85], marker = 'o', linewidth = 4, zorder = 5, ms=40, mec= satColors[isc], mfc='none', mew=2)
    
    legend = ax.legend(loc='center right', bbox_to_anchor=(0.9, 0.5), numpoints = 1,  title="", fontsize = fontsize_plot,handlelength=0, handletextpad=0)
    for isc_temp in range(len(legend.get_texts())):
        isc = label_arr_conversion[isc_temp]
        legend.get_texts()[isc_temp].set_color(satColors[isc]) # set the label the same color as the plot
        legend.legendHandles[isc_temp].set_visible(False) # hide the line in the label
    ax.axis('equal')
    ax.text(0.1, 0.5, datetime.strftime(date[iday], "%B %-d, %Y"), horizontalalignment ='left', verticalalignment = 'center', transform=ax.transAxes, fontsize = fontsize_plot)
    ax.set_ylim([-1.04, 1.04])
    ax.margins(0,0)

    # Phase angle
    y_label = 'Angular separation wrt. FM03 ' + u'(\N{DEGREE SIGN})'
    x_label = 'Real time'
    ax2 = plt.subplot(gs[1, 0])#fig.add_subplot(gs[0, 1])
    ax2.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
    ax2.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                       
    ax2.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    plt.rc('font', weight='normal') ## make the labels of the ticks in bold                           
    for isc_temp in range(nb_sc):
        isc = label_arr_conversion[isc_temp]
        if isc != isc_ref_nb:
            ax2.plot(nb_seconds_since_start[:iday+1], phase_angle_ref[isc, :iday+1], linewidth = 2, color = satColors[isc], label = label_arr[isc])

    nb_ticks_xlabel = 8
    dt_xlabel =  nb_seconds_in_simu / nb_ticks_xlabel # dt for ticks on x axis (in seconds)
    xticks = np.arange(start_xaxis_label, start_xaxis_label+nb_seconds_in_simu+1, dt_xlabel)
    date_list_str = []
    date_list = [date_ref + timedelta(seconds=x-xticks[0]) for x in xticks]
    for i in range(len(xticks)):
        if dt_xlabel >= 3*24*3600:
            date_list_str.append( str(date_list[i])[5:10] )
        else:
            date_list_str.append( str(date_list[i])[5:10] + "\n" + str(date_list[i])[11:16] )
    ax2.xaxis.set_ticks(xticks)
    ax2.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')
    ax2.set_ylim([0, 180])
    ax2.set_xlim([0, nb_seconds_since_start[-1]])

    # SMA
    y_label = 'Semi-major axis - $R_E$ (km)'
    x_label = 'Real time'
    ax3 = plt.subplot(gs[1, 1])#fig.add_subplot(gs[0, 2])
    ax3.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
    ax3.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                       
    ax3.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    plt.rc('font', weight='normal') ## make the labels of the ticks in bold                           
    for isc_temp in range(nb_sc):
        isc = label_arr_conversion[isc_temp]        
        ax3.plot(nb_seconds_since_start[:iday+1], sma[isc, :iday+1]-earth_radius, linewidth = 2, color = satColors[isc], label = label_arr[isc])

    nb_ticks_xlabel = 8
    dt_xlabel =  nb_seconds_in_simu / nb_ticks_xlabel # dt for ticks on x axis (in seconds)
    xticks = np.arange(start_xaxis_label, start_xaxis_label+nb_seconds_in_simu+1, dt_xlabel)
    date_list_str = []
    date_list = [date_ref + timedelta(seconds=x-xticks[0]) for x in xticks]
    for i in range(len(xticks)):
        if dt_xlabel >= 3*24*3600:
            date_list_str.append( str(date_list[i])[5:10] )
        else:
            date_list_str.append( str(date_list[i])[5:10] + "\n" + str(date_list[i])[11:16] )
    ax3.xaxis.set_ticks(xticks)
    ax3.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')

    ax3.set_ylim([sma.min()-earth_radius, sma.max()-earth_radius])
    ax3.set_xlim([0, nb_seconds_since_start[-1]])
    gs.update(left = 0, right=1, top = 1,bottom = 0., wspace = 0.14, hspace = 0)
    fig_save_name = 'animation/' +str(iday_count) + '.png'
    fig.savefig(fig_save_name, facecolor=fig  .get_facecolor(), edgecolor='none', bbox_inches='tight')


os.system('ffmpeg -y -r 10 -i animation/%d.png -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -vcodec libx264 -pix_fmt yuv420p animation/ani_trajectory_maneuvers.mp4')# + start_epoch_str + '_TO_' + end_epoch_str + '.mp4')
os.system('mv ' + fig_save_name + ' ani_trajectory_maneuvers.png')
#os.system('rm -f animation/*.png')
os.system('mv  ani_trajectory_maneuvers.png animation/ani_trajectory_maneuvers.png')








raise Exception

height_fig = 11.  # the width is calculated as height_fig * 4/3.                                                                             
fontsize_plot = 25      
ratio_fig_size = 4./3
fig_title = ''#Accuracy VS RCG
y_label = 'Angular separation ' + u'(\N{DEGREE SIGN})'
x_label = 'Real time'

fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'normal',)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                                                                      
gs = gridspec.GridSpec(2, 1, width_ratios=[1],
                          height_ratios=[ 0.1,1])

#                  gridspec_kw={"height_ratios":[1, 0.05]})
ax = fig.add_subplot(gs[1, 0])
ax.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                       
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                           
for isc_temp in range(nb_sc):
    isc = label_arr_conversion[isc_temp]
    ax.plot(nb_seconds_since_start, phase_angle_ref[isc, :], linewidth = 2, color = satColors[isc], label = label_arr[isc])


# x axis label is in real time
            ## all output files of one simulation have the same number of steps, and start at the same date
nb_ticks_xlabel = 8
dt_xlabel =  nb_seconds_in_simu / nb_ticks_xlabel # dt for ticks on x axis (in seconds)
xticks = np.arange(start_xaxis_label, start_xaxis_label+nb_seconds_in_simu+1, dt_xlabel)
date_list_str = []
date_list = [date_ref + timedelta(seconds=x-xticks[0]) for x in xticks]
for i in range(len(xticks)):
    if dt_xlabel >= 3*24*3600:
        date_list_str.append( str(date_list[i])[5:10] )
    else:
        date_list_str.append( str(date_list[i])[5:10] + "\n" + str(date_list[i])[11:16] )
ax.xaxis.set_ticks(xticks)
ax.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')
 
ax.margins(0,0)
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="", fontsize = fontsize_plot,handlelength=0, handletextpad=0)
for isc_temp in range(len(legend.get_texts())):
    isc = label_arr_conversion[isc_temp]
    legend.get_texts()[isc_temp].set_color(satColors[isc]) # set the label the same color as the plot
    legend.legendHandles[isc_temp].set_visible(False) # hide the line in the label

fig_save_name = 'phase_angle_' + start_epoch_str + '_TO_' + end_epoch_str + '.pdf'
fig.savefig(fig_save_name, facecolor=fig  .get_facecolor(), edgecolor='none', bbox_inches='tight')







# # start and end of the simulation. The most recent TLE corresponding to start_epoch will be downloaded from spacetrack to initialize SpOCK.
# sma_tle_at_tle_epoch_all = []
# date_tle_from_tle_all = []
# true_ano_tle_at_tle_epoch_all = []
# arg_per_tle_at_tle_epoch_all = []
# phase_angle_tle_at_tle_epoch_all = []
# # which norad_id to consider
# for i in range(8):
#     norad_id_int = 41884 + i
#     norad_id = str(norad_id_int) # has to be a string
#     if load_tle_result != 1:
#         # ############ ALGORITHM ############
#         earth_mu     = 398600.4418; # gravitational parameter (km^3/s^2)
#         earth_radius = 6378.137; # mean equatorial radius (km)
#         cygnss_real_mass = 29.
#         order_gravity = 10
#         forces = "drag sun_gravity moon_gravity"
#         density_mode = 'static'
#         spice_path = '/Users/cbv/cspice/data' #'/raid4/cbv/cspice/data'  # '/Users/cbv/cspice/data'
#         root_save_fig_name = path_folder_results
#         cygnss_geometry = 'cygnss_geometry_2016_acco08.txt'

#         # TLE STATES
#         # Download all TLEs from start_epoch to end_epoch (all TLEs are included in the same file)
#         link = "https://www.space-track.org/basicspacedata/query/class/tle/NORAD_CAT_ID/" + norad_id + "/EPOCH/" + start_epoch + '--' + end_epoch +  "/format/tle/emptyresult/show/orderby/EPOCH%20asc/"
#         #os.system("wget  --post-data='identity=cbv@umich.edu&password=cygnssisawesome' --cookies=on --keep-session-cookies --save-cookies=cookies.txt 'https://www.space-track.org/ajaxauth/login' -olog")
#         name_all_tle_from_initial_to_end_epoch = norad_id + '_from_' + start_epoch + '_to_' + end_epoch + ".txt"
#         #os.system("wget --limit-rate=100K --keep-session-cookies --load-cookies=cookies.txt " + link + " -O " + name_all_tle_from_initial_to_end_epoch)

#         # We can't just use 2 body equations to convert mean motion to sma and then compare this sma to the sma in SpOCK. Indeed, SpOCK uses osculating elements but the TLEs uses Kozai mean elements: they can differ by several km. So using the wrong theory (2 body equations) to convert the TLEs would give us errors, we need to use SGP4 because SGP4's equations convert Kozai mean elements into r, v ECI. Then we convert r, v ECI into osculating elements. Recall: SGP4 is integrated in SpOCK (via SPICE libraries) -> at the initialization, SpOCK converts the TLEs into r, v ECI and then osculating elements. So we convert TLE into r,v then propgate over 1 orbit then take the orbit average of the same over this orbit
#         ## For each TLE in name_all_tle_from_initial_to_end_epoch, run SpOCK for about two orbits
#         all_tle_file = open( name_all_tle_from_initial_to_end_epoch)
#         read_all_tle_file = all_tle_file.readlines()
#         nb_tle = len(read_all_tle_file) / 2
#         date_tle_from_tle = []
#         iline = 0
#         sma_average_tle = []
#         date_average_tle_end_orbit = []
#         date_average_tle_start_orbit = []
#         x_axis_average_tle = []
#         nb_orbit_tle = np.zeros([nb_tle]).astype(np.int)
#         r_eci_tle_at_tle_epoch = np.zeros([nb_tle, 3])
#         radius_tle_at_tle_epoch = np.zeros([nb_tle])
#         v_eci_tle_at_tle_epoch = np.zeros([nb_tle, 3])
#         alt_tle_at_tle_epoch = np.zeros([nb_tle])
#         sma_tle_at_tle_epoch = np.zeros([nb_tle])
#         ecc_tle_at_tle_epoch = np.zeros([nb_tle])
#         true_ano_tle_at_tle_epoch = np.zeros([nb_tle])
#         arg_per_tle_at_tle_epoch = np.zeros([nb_tle])
#         phase_angle_tle_at_tle_epoch = np.zeros([nb_tle])
#         for itle in range(nb_tle):
#             print 'tle ', itle, nb_tle-1
#             date_average_tle_end_orbit_run_str = []
#             date_average_tle_start_orbit_run_str = []
#             date_average_tle_end_orbit_run = []
#             date_average_tle_start_orbit_run = []
#             x_axis_average_tle_run = []
#             dt_tle = 1 # we don't care about dt here because we only look at the initialization
#             dt_tle_output = dt_tle
#             date_tle_temp = read_all_tle_file[iline].split()[3]  
#             date_start_temp = convert_tle_date_to_date(date_tle_temp)
#             date_tle_from_tle.append(date_start_temp)
#             date_start_tle = datetime.strftime(date_start_temp, "%Y-%m-%dt_tle%H:%M:%S.%f")
#             date_start_spock = datetime.strftime(date_start_temp + timedelta(seconds = dt_tle), "%Y-%m-%dT%H:%M:%S.%f") # make sur ethe initial epoch starts at least one time step after TLE epoch
#             ### Create a TLE file for SpOCK with only the current TLE
#             tle_filename_one_sc_one_time = norad_id + "_" + date_start_tle.replace(".","_") + ".txt"
#             tle_file_one_sc_one_time = open(tle_filename_one_sc_one_time, "w")
#             print >> tle_file_one_sc_one_time, read_all_tle_file[iline].replace("\r", ""), read_all_tle_file[iline+1].replace("\r", "")
#             tle_file_one_sc_one_time.close()
#             ### Create main input file for SpOCK with this TLE
#             main_input_filename = "TLE_" + norad_id + "_" + date_start_tle.replace(".","_") + ".txt"
#             date_end_temp = date_start_temp + timedelta(seconds = dt_tle_output)  # !!!! assumption: orbit period is < 100 min
#             date_end_spock = datetime.strftime(date_end_temp, "%Y-%m-%dT%H:%M:%S.%f")
#             spock_main_input(
#                 main_input_filename,
#                 # for TIME section
#                 date_start_spock,
#                 date_end_spock,
#                 dt_tle,
#                 # for SPACECRAFT section
#                 1,
#                 '0',
#                 cygnss_real_mass,
#                 cygnss_geometry,
#                 # for ORBIT section
#                 tle_filename_one_sc_one_time,
#                 # for FORCES section
#                 4,#order_gravity,
#                 'none',#forces,
#                 density_mode,
#                 # for OUTPUT section
#                 '~/cygnss/comparison_tle/out', # simulations were run for anoter analysis previously. The outputs were written in this folder
#                 dt_tle_output, 
#                 # for ATTITUDE section
#                 "nadir",
#                 # for GROUNDS_STATIONS section
#                 "0",#"my_ground_stations.txt"
#                 # for SPICE section
#                 spice_path, 
#                 # for DENSITY_MOD section
#                 1
#             )

#             ### Run SpOCK with this main input file
#             #os.system("mpirun -np 1 spock " + main_input_filename)

#             ### Read TLE output file (starts the with the prefix 'TLE_')
#             #### Read main input filename to figure out the name of the output
#             var_in, var_in_order = read_input_file( main_input_filename)
#             output_file_path_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]; 
#             output_file_name_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')];
#             isc = 0 # here only one sc in main input file
#             var_to_read = ["altitude", "sma", "radius", "eccentricity","latitude"]
#             var_out, var_out_order = read_output_file( output_file_path_list[isc] + output_file_name_list[isc], var_to_read )

#             date_tle = var_out[find_in_read_input_order_variables(var_out_order, 'date')]
#             nb_steps_new = len(date_tle) # in case the sc reentered the atmosphere before the end of the run OR if bug in SpCOK before the end of run (still want to run this script)
#             nb_sc = var_in[find_in_read_input_order_variables(var_in_order, 'nb_sc')];


#             #sma at epoch of TLE (so from TLE_ output file)
#             tle_out_name = output_file_path_list[0] + 'TLE_' + output_file_name_list[0]
#             tle_out = open(tle_out_name, "r")
#             read_tle_out = tle_out.readlines()
#             n_header = 12
#             r_eci_tle_at_tle_epoch[itle, 0] = read_tle_out[n_header].split()[2]; r_eci_tle_at_tle_epoch[itle, 1] = read_tle_out[n_header].split()[3]; r_eci_tle_at_tle_epoch[itle, 2] = read_tle_out[n_header].split()[4]; 
#             radius_tle_at_tle_epoch[itle] = np.sqrt( r_eci_tle_at_tle_epoch[itle, 0]*r_eci_tle_at_tle_epoch[itle, 0] + r_eci_tle_at_tle_epoch[itle, 1]*r_eci_tle_at_tle_epoch[itle, 1] + r_eci_tle_at_tle_epoch[itle, 2]*r_eci_tle_at_tle_epoch[itle, 2] )
#             v_eci_tle_at_tle_epoch[itle, 0] = read_tle_out[n_header].split()[5]; v_eci_tle_at_tle_epoch[itle, 1] = read_tle_out[n_header].split()[6]; v_eci_tle_at_tle_epoch[itle, 2] = read_tle_out[n_header].split()[7]; 
#             alt_tle_at_tle_epoch[itle] = read_tle_out[n_header].split()[10]
#             sma_tle_at_tle_epoch[itle] = read_tle_out[n_header].split()[11]
#             ecc_tle_at_tle_epoch[itle] = read_tle_out[n_header].split()[13]

#             true_ano_tle_at_tle_epoch[itle] = read_tle_out[n_header].split()[14]
#             arg_per_tle_at_tle_epoch[itle] = read_tle_out[n_header].split()[16]

#             phase_angle_tle_at_tle_epoch[itle] = np.float(np.mod(true_ano_tle_at_tle_epoch[itle] + arg_per_tle_at_tle_epoch[itle], 360))
#             tle_out.close()


#             ### move to next tle
#             iline = iline + 2


# #         x_axis_average_tle = np.array(x_axis_average_tle)
# #         sma_average_tle = np.array(sma_average_tle)
#         pickle.dump( date_tle_from_tle, open( '/Users/cbv/cygnss/website/trajectory_maneuvers/date_tle_from_tle_' + norad_id + ".pickle", "w" ) )
#         pickle.dump( sma_tle_at_tle_epoch, open( '/Users/cbv/cygnss/website/trajectory_maneuvers/sma_tle_at_tle_epoch_' + norad_id + ".pickle", "w" ) )
#         pickle.dump( true_ano_tle_at_tle_epoch, open( '/Users/cbv/cygnss/website/trajectory_maneuvers/sma_tle_at_tle_epoch_' + norad_id + ".pickle", "w" ) )
#         pickle.dump( arg_per_tle_at_tle_epoch, open( '/Users/cbv/cygnss/website/trajectory_maneuvers/sma_tle_at_tle_epoch_' + norad_id + ".pickle", "w" ) )
#         pickle.dump( phase_angle_tle_at_tle_epoch, open( '/Users/cbv/cygnss/website/trajectory_maneuvers/sma_tle_at_tle_epoch_' + norad_id + ".pickle", "w" ) )

#         date_tle_from_tle_all.append(date_tle_from_tle)
#         sma_tle_at_tle_epoch_all.append(sma_tle_at_tle_epoch)
#         true_ano_tle_at_tle_epoch_all.append(true_ano_tle_at_tle_epoch)
#         arg_per_tle_at_tle_epoch_all.append(arg_per_tle_at_tle_epoch)
#         phase_angle_tle_at_tle_epoch_all.append(phase_angle_tle_at_tle_epoch)


#     else:
#         date_tle_from_tle = pickle.load(open( '/Users/cbv/cygnss/website/trajectory_maneuvers/date_tle_from_tle_' + norad_id + ".pickle","r"))
#         sma_tle_at_tle_epoch = pickle.load(open( '/Users/cbv/cygnss/website/trajectory_maneuvers/sma_tle_at_tle_epoch_' + norad_id + ".pickle","r"))
#         true_ano_tle_at_tle_epoch = pickle.load(open( '/Users/cbv/cygnss/website/trajectory_maneuvers/true_ano_tle_at_tle_epoch_' + norad_id + ".pickle","r"))
#         arg_per_tle_at_tle_epoch = pickle.load(open( '/Users/cbv/cygnss/website/trajectory_maneuvers/arg_per_tle_at_tle_epoch_' + norad_id + ".pickle","r"))
#         phase_angle_tle_at_tle_epoch = pickle.load(open( '/Users/cbv/cygnss/website/trajectory_maneuvers/phase_angle_tle_at_tle_epoch_' + norad_id + ".pickle","r"))
#         date_tle_from_tle_all.append(date_tle_from_tle)
#         true_ano_tle_at_tle_epoch_all.append(true_ano_tle_at_tle_epoch)
#         arg_per_tle_at_tle_epoch_all.append(arg_per_tle_at_tle_epoch)
#         phase_angle_tle_at_tle_epoch_all.append(phase_angle_tle_at_tle_epoch)
#         sma_tle_at_tle_epoch_all.append(sma_tle_at_tle_epoch)
