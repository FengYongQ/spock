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

# This script computes the distance between the spec of 2 SpOCK simulations. The distance is along-track (direction of motion) and cross-track (perdicular to motion). Motion = motion of satellites ~ motion of SPs
# It identifies spec with their PRN. If the two simu don't have a PRN in common the distance is set to -1e30
# To run:
# python cygnss_dist_spec_spock.py spock_input_filename1 spock_input_filename2
# ASSUMPTIONS:
# - see section "#PARAMETERS TO SET UP BEFORE RUNNING THIS SCRIPT"
# - the two simulations have the same epochs and output time step

import sys
sys.path.append("/Users/cbv/Google Drive/Work/PhD/Research/Code/spock/srcPython")
import numpy as np
from read_input_file import *
from cygnss_read_spock_spec_bin import *
from ecef_to_lvlh import *
import matplotlib.gridspec as gridspec
from matplotlib import pyplot as plt


# PARAMETERS TO SET UP BEFORE RUNNING THIS SCRIPT
cygfm = 1
# end of PARAMETERS TO SET UP BEFORE RUNNING THIS SCRIPT

cygfm_to_nb = [4,3,8,2,1,6,7,5] # ['41884', '41885', '41886', '41887', '41888', '41889', '41890', '41891']
isc =  cygfm_to_nb[cygfm-1] - 1

# Spec from simu 1
print 'Reading specular point locations of simu 1...'
input_filename1 = sys.argv[1]
var_in, var_in_order = read_input_file(input_filename1)
dt_output1 = var_in[find_in_read_input_order_variables(var_in_order, 'dt_output')]; 
output_file_path_list1 = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]; 
output_file_name_list1 = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')];
gps_name_list1 = var_in[find_in_read_input_order_variables(var_in_order, 'gps_name')];
spec_filename1 = output_file_path_list1[isc] + "specular_" + output_file_name_list1[isc]
data_spec1 = cygnss_read_spock_spec_bin(spec_filename1.replace('.txt','.bin'), gps_name_list1, dt_output1, 1) 
date1 = data_spec1[0]; lon1 = data_spec1[1]; lat1 = data_spec1[2]; gain1 = data_spec1[3]; prn1 = data_spec1[4]; normpower1 = data_spec1[5]; x_cyg1 = data_spec1[6]; y_cyg1 = data_spec1[7]; z_cyg1 = data_spec1[8]; x_gps1 = data_spec1[9]; y_gps1 = data_spec1[10]; z_gps1 = data_spec1[11];  x_spec1 = data_spec1[12]; y_spec1 = data_spec1[13]; z_spec1 = data_spec1[14]; nb_spec1 = data_spec1[15];  el_spec1 = data_spec1[16]; az_spec1 = data_spec1[17]; el_gps_from_cyg1 = data_spec1[18];  el_spec_not_int1 = data_spec1[19]; az_spec_not_int1 = data_spec1[20]; vx_cyg1 = data_spec1[21]; vy_cyg1 = data_spec1[22]; vz_cyg1 = data_spec1[23] 

# Spec from simu 2
print 'Reading specular point locations of simu 2...'
input_filename2 = sys.argv[2]
var_in, var_in_order = read_input_file(input_filename2)
dt_output2 = var_in[find_in_read_input_order_variables(var_in_order, 'dt_output')]; 
output_file_path_list2 = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]; 
output_file_name_list2 = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')];
gps_name_list2 = var_in[find_in_read_input_order_variables(var_in_order, 'gps_name')];
spec_filename2 = output_file_path_list2[isc] + "specular_" + output_file_name_list2[isc]
data_spec2 = cygnss_read_spock_spec_bin(spec_filename2.replace('.txt','.bin'), gps_name_list2, dt_output2, 1) 
date2 = data_spec2[0]; lon2 = data_spec2[1]; lat2 = data_spec2[2]; gain2 = data_spec2[3]; prn2 = data_spec2[4]; normpower2 = data_spec2[5]; x_cyg2 = data_spec2[6]; y_cyg2 = data_spec2[7]; z_cyg2 = data_spec2[8]; x_gps2 = data_spec2[9]; y_gps2 = data_spec2[10]; z_gps2 = data_spec2[11];  x_spec2 = data_spec2[12]; y_spec2 = data_spec2[13]; z_spec2 = data_spec2[14]; nb_spec2 = data_spec2[15];  el_spec2 = data_spec2[16]; az_spec2 = data_spec2[17]; el_gps_from_cyg2 = data_spec2[18];  el_spec_not_int2 = data_spec2[19]; az_spec_not_int2 = data_spec2[20]; vx_cyg2 = data_spec2[21]; vy_cyg2 = data_spec2[22]; vz_cyg2 = data_spec2[23]


# Distance between spec of simu 1 and spec of simu 2
n = np.min([len(date1), len(date2)]) # sometimes the two array could differ because the last time step is omitted in the specular point output file
if date1[:n] != date2[:n]:
    print "***! The two simulations must have the same epochs and output time steps. The program will stop. !***"; raise Exception
distance = np.zeros([n, nb_spec2, 2]) - 1e30
min_along = 10000
max_along = -10000
min_cross = 10000
max_cross = -10000
for i in range(n):
    r1_cyg = np.array([x_cyg1[i][0], y_cyg1[i][0], z_cyg1[i][0]])
    v1_cyg = np.array([vx_cyg1[i][0], vy_cyg1[i][0], vz_cyg1[i][0]])
    for ispec2 in range(nb_spec2):
        prn2_here = prn2[i][ispec2]
        r2 = np.array([x_spec2[i][ispec2], y_spec2[i][ispec2], z_spec2[i][ispec2]])
        if prn2_here in prn1[i]:
            ispec1 = prn1[i].index(prn2_here) 
            r1 = np.array([x_spec1[i][ispec1], y_spec1[i][ispec1], z_spec1[i][ispec1]])
            rdiff = r2 - r1

            rdiff_lvlh = ecef_to_lvlh(r1_cyg, v1_cyg, rdiff) 
            distance[i, ispec2, :] = rdiff_lvlh[:2]*1000 # km to m
            if i < n :
                if distance[i, ispec2, 0] < min_along:
                    min_along = distance[i, ispec2, 0]
                if distance[i, ispec2, 0] > max_along:
                    max_along = distance[i, ispec2, 0]
                if distance[i, ispec2, 1] < min_cross:
                    min_cross = distance[i, ispec2, 1]
                if distance[i, ispec2, 1] > max_cross:
                    max_cross = distance[i, ispec2, 1]

nb_diff_prn = len(np.where(distance[:, :, 0] == -1e30)[0])
percentage_diff_prn = nb_diff_prn * 100. / (n * nb_spec2)

# Plot along-track distance
height_fig = 11.  # the width is calculated as height_fig * 4/3.                                                                             
fontsize_plot = 25      
ratio_fig_size = 4./3
fig_title = ''
y_label = 'Along-track distance (m)'
x_label = 'Time (hours)'
fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'normal',)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                                                                      
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax = fig.add_subplot(gs[0, 0])
ax.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                       
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                           

ax.plot(np.arange(0,n)/ 3600., distance[:,0,0], color = 'b', linewidth = 2) # time step of spec file is 1 second so n is the number of seconds
ax.plot(np.arange(0,n)/ 3600., distance[:,1,0], color = 'r', linewidth = 2)
ax.plot(np.arange(0,n)/ 3600., distance[:,2,0], color = 'k', linewidth = 2)
ax.plot(np.arange(0,n)/ 3600., distance[:,3,0], color = 'm', linewidth = 2)
ax.text(0.98, 0.02, '# diff PRN: '+ str(nb_diff_prn) + ' (' + format(percentage_diff_prn, ".2f")+ '%)', transform = ax.transAxes, fontsize = fontsize_plot, horizontalalignment = 'right', verticalalignment = 'bottom')
ax.set_ylim([min_along, max_along])
ax.margins(0,0)
fig_save_name = 'alongtrack_distance_spec_' + input_filename1.replace(".txt","") + '_to_' + input_filename2.replace(".txt","")  + '.pdf'
fig.savefig(fig_save_name, facecolor=fig  .get_facecolor(), edgecolor='none', bbox_inches='tight')



# Plot cross-track distance
height_fig = 11.  # the width is calculated as height_fig * 4/3.                                                                             
fontsize_plot = 25      
ratio_fig_size = 4./3
fig_title = ''
y_label = 'Cross-track distance (m)'
x_label = 'Time (hours)'
fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'normal',)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                                                                      
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax = fig.add_subplot(gs[0, 0])
ax.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                       
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                           

ax.plot(np.arange(0,n)/ 3600., distance[:,0,1], color = 'b', linewidth = 2)
ax.plot(np.arange(0,n)/ 3600., distance[:,1,1], color = 'r', linewidth = 2)
ax.plot(np.arange(0,n)/ 3600., distance[:,2,1], color = 'k', linewidth = 2)
ax.plot(np.arange(0,n)/ 3600., distance[:,3,1], color = 'm', linewidth = 2)
ax.text(0.98, 0.02, '# diff PRN: '+ str(nb_diff_prn) + ' (' + format(percentage_diff_prn, ".2f")+ '%)', transform = ax.transAxes, fontsize = fontsize_plot, horizontalalignment = 'right', verticalalignment = 'bottom')
ax.set_ylim([min_cross, max_cross])
ax.margins(0,0)
fig_save_name = 'crosstrack_distance_spec_' + input_filename1.replace(".txt","") + '_to_' + input_filename2.replace(".txt","")  + '.pdf'
fig.savefig(fig_save_name, facecolor=fig  .get_facecolor(), edgecolor='none', bbox_inches='tight')





# run cygnss_dist_spec_spock.py spock_spec_start_2018-03-24T00_00_00_end_2018-03-27T23_59_59_10s_order8.txt spock_spec_start_2018-03-24T00_00_00_end_2018-03-27T23_59_59_1s.txt

# run cygnss_dist_spec_spock.py spock_spec_start_2018-03-27T00_00_00_end_2018-03-30T23_59_59_10s_order8.txt spock_spec_start_2018-03-27T00_00_00_end_2018-03-30T23_59_59_1s.txt

# run cygnss_dist_spec_spock.py spock_spec_start_2018-03-30T00_00_00_end_2018-04-02T23_59_59_10s_order8.txt spock_spec_start_2018-03-30T00_00_00_end_2018-04-02T23_59_59_1s.txt

#mrun -np 4 spock_dev spock_spec_start_2018-03-24T00_00_00_end_2018-03-27T23_59_59_10s_order8.txt; mrun -np 4 spec_dev spock_spec_start_2018-03-24T00_00_00_end_2018-03-27T23_59_59_10s_order8.txt -lon=0 -rot=0 -min;mrun -np 4 spock_dev spock_spec_start_2018-03-27T00_00_00_end_2018-03-30T23_59_59_10s_order8.txt; mrun -np 4 spec_dev spock_spec_start_2018-03-27T00_00_00_end_2018-03-30T23_59_59_10s_order8.txt -lon=0 -rot=0 -min;mrun -np 4 spock_dev spock_spec_start_2018-03-30T00_00_00_end_2018-04-02T23_59_59_10s_order8.txt; mrun -np 4 spec_dev spock_spec_start_2018-03-30T00_00_00_end_2018-04-02T23_59_59_10s_order8.txt -lon=0 -rot=0 -min


#time mrun -np 4 spock_dev spock_spec_start_2018-03-24T00_00_00_end_2018-03-27T23_59_59_10s_order8.txt; time mrun -np 4 spec_dev spock_spec_start_2018-03-24T00_00_00_end_2018-03-27T23_59_59_10s_order8.txt -lon=0 -rot=0 -min; time mrun -np 4 spock_dev spock_spec_start_2018-03-27T00_00_00_end_2018-03-30T23_59_59_10s_order8.txt; time mrun -np 4 spec_dev spock_spec_start_2018-03-27T00_00_00_end_2018-03-30T23_59_59_10s_order8.txt -lon=0 -rot=0 -min;time mrun -np 4 spock_dev spock_spec_start_2018-03-30T00_00_00_end_2018-04-02T23_59_59_10s_order8.txt; time mrun -np 4 spec_dev spock_spec_start_2018-03-30T00_00_00_end_2018-04-02T23_59_59_10s_order8.txt -lon=0 -rot=0 -min
