import sys
sys.path.append("/Users/cbv/Google Drive/Work/PhD/Research/Code/spock/srcPython")
from cadre_read_last_tle import *
from get_prop_dir import *
import matplotlib.gridspec as gridspec
from read_input_file import *
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
plt.ion()
plt.isinteractive()

############ PARAMETERS TO SET ############
## Save or not the plots
save_results = 1

## Show or not the plots
show_plots = 1

## path of the folder where you want to store the results (pickle, image, video)
path_folder_results = './'#path_folder_results = '/raid3/Armada/Charles/python/' #get_prop_dir(2) + 'output/python_propagator/'

## If the second spacecraft was propagated from the same main input file in SpOCK as the first spacecraft
same_spock_input_file = 1

############ ALGORITHM ############
# Read input file sat1
input_filename_sat1 =    sys.argv[1]

input_variables, order_input_variables = read_input_file(input_filename_sat1)
sat1_to_plot_path = input_variables[find_in_read_input_order_variables(order_input_variables, 'output_file_path_list')][0]; sat1_to_plot = input_variables[find_in_read_input_order_variables(order_input_variables, 'output_file_name_list')][0];
dt_sat1 = input_variables[find_in_read_input_order_variables(order_input_variables, 'dt_output')]; nb_steps_sat1 = input_variables[find_in_read_input_order_variables(order_input_variables, 'nb_steps')];

name_mission = ''

root_save_fig_name = path_folder_results + name_mission + '/result/image/' + sat1_to_plot.replace(".txt","_")

# Read output file sat1
r_eci_sat1 = np.zeros([nb_steps_sat1])
var_to_read = ["position"]
var_out, var_out_order = read_output_file( sat1_to_plot_path + sat1_to_plot, var_to_read )
r_eci_sat1 = var_out[find_in_read_input_order_variables(var_out_order, 'position')]
date_start = datetime.strptime(var_out[find_in_read_input_order_variables(var_out_order, 'date')][0], "%Y/%m/%d %H:%M:%S.%f")
date1 = var_out[find_in_read_input_order_variables(var_out_order, 'date')]
# Read input file sat2
if same_spock_input_file == 1:
    sat2_to_plot_path = input_variables[find_in_read_input_order_variables(order_input_variables, 'output_file_path_list')][1]; sat2_to_plot = input_variables[find_in_read_input_order_variables(order_input_variables, 'output_file_name_list')][1];
    dt_sat2 = input_variables[find_in_read_input_order_variables(order_input_variables, 'dt_output')]; nb_steps_sat2 = input_variables[find_in_read_input_order_variables(order_input_variables, 'nb_steps')];
else:
    input_filename_sat2 =    sys.argv[2] 
    input_variables, order_input_variables = read_input_file(input_filename_sat2)
    sat2_to_plot_path = input_variables[find_in_read_input_order_variables(order_input_variables, 'output_file_path_list')][0]; sat2_to_plot = input_variables[find_in_read_input_order_variables(order_input_variables, 'output_file_name_list')][0];
    dt_sat2 = input_variables[find_in_read_input_order_variables(order_input_variables, 'dt_output')]; nb_steps_sat2 = input_variables[find_in_read_input_order_variables(order_input_variables, 'nb_steps')];


# Read output file sat2
r_eci_sat2 = np.zeros([nb_steps_sat2])
var_to_read = ["position"]
var_out, var_out_order = read_output_file( sat2_to_plot_path + sat2_to_plot, var_to_read )
r_eci_sat2 = var_out[find_in_read_input_order_variables(var_out_order, 'position')]

nb_steps_sat1 = r_eci_sat1.shape[0]
nb_steps_sat2 = r_eci_sat2.shape[0]
if nb_steps_sat2 != nb_steps_sat1:
    print "***! Error: the number of time steps in both sumations is different. The program will stop. !***"
    raise Exception




# Distance between both sc
dist_between_sat1_and_sat2 = np.zeros([nb_steps_sat2])
for i in range(nb_steps_sat2):
    dist_between_sat1_and_sat2[i] = np.linalg.norm( r_eci_sat2[i,:] - r_eci_sat1[i,:] )
print min(dist_between_sat1_and_sat2)

# Plot
dt = dt_sat1
nb_steps = nb_steps_sat1
## Set up plot parameters 
height_fig = 9.  # the width is calculated as height_fig * 4/3.
fontsize_plot = 20 
hour_time_step_xticks = 24. # time step of ticks when plotting a function as a function of time
step_plot = dt / 3600. # step in hours to plot

## Make plots
ratio_fig_size = 4./3
if ( step_plot < dt / 3600. ):
    step_plot = dt / 3600.
step_plot_in_index = (int) (step_plot * 3600. / dt)
nb_steps_adjusted = (int) ( nb_steps * dt / 3600 / step_plot) 
x_axis = np.arange(0, nb_steps, step_plot_in_index)
#x_axis = np.arange(0, 2*24*360)# !!!!!!!!!!! remove
### Distance between spacecraft 1 and 2
fig_title = ''#'Distance between spacecraft 1 and 2'
y_label = 'Distance (km)'
x_label = 'Real time'
y_axis = dist_between_sat1_and_sat2 
factor_on_y = 1
### Plot with these parameters
fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 0.973,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
plt.rc('font', weight='bold') ## make the labels of the ticks in bold
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.94, top = 0.93,bottom = 0.12, hspace = 0.01)
ax = fig.add_subplot(gs[0, 0])

ax.plot(x_axis[:-1], y_axis[0:nb_steps:step_plot_in_index][:-1] * factor_on_y, linewidth = 2, color = 'k')#ax.plot(x_axis, y_axis[0:nb_steps:step_plot_in_index] * factor_on_y, linewidth = 2, color = 'k')
ax.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
ax.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='bold') ## make the labels of the ticks in bold

hour_time_step_xticks_converted_in_index_adjusted = hour_time_step_xticks / step_plot
xticks = np.arange(0, nb_steps_adjusted, hour_time_step_xticks_converted_in_index_adjusted)
date_list_str = []
nb_hours_simu = nb_steps * dt/ 3600.
date_list = [date_start + timedelta(hours=x) for x in np.arange(0, nb_hours_simu+1, hour_time_step_xticks)]
for i in range(len(xticks)):
    if hour_time_step_xticks < 12:
        if i == 0:
            date_list_str.append("h+" + str(int(xticks[i] * step_plot)))
        else:
            date_list_str.append("+" + str(int(xticks[i] * step_plot)))
    else:
        date_list_str.append( str(date_list[i])[5:10] + "\n(day + " + str(int(xticks[i] * step_plot / 24.)) + ")")
ax.xaxis.set_ticks(xticks)
ax.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')
ax.margins(0,0)

if save_results == 1:
    fig_save_name = fig_title.replace(" ","_").lower()
    fig_save_name = fig_save_name + 'distance_between_sat1_and_sat2.pdf'
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  
    #os.system("rsync -av " + fig_save_name +" srbwks2014-0008.engin.umich.edu:./" + name_mission)

if show_plots == 1:
    plt.show(); plt.show()



