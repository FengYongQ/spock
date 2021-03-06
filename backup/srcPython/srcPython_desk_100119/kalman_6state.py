# The only difference with kalman.py is that this script the output of KF with a state of 6 elements whereas kalman.py does it for a 9 elts state.
from datetime import datetime, timedelta
import matplotlib.gridspec as gridspec
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import sys
from read_input_file import *
from read_output_file import *


# How to run this script:
# python kalman.py arg
# arg can be:
# - 3d then plot 3d orbit
# - r then plot position on three graphs on same page
# - v then plot speed on three graphs on same page
# - ad
# - rho
# - Pdiag
# - dX
# - y
# - drag_sigma

# Assumptions:
# - the time in the measurement file must be the same as in the kalman file

# Read measurement file
## Read SpOCK main input file to figure out the name of the measurement file
input_filename = sys.argv[1]
var_in, var_in_order = read_input_file(input_filename)
filename_kalman_meas = var_in[find_in_read_input_order_variables(var_in_order, 'filename_kalman_meas')];

# "spock/true/true1/noise_true1.txt" #"/Users/cbv/kalman/cbv/spock/netcdf/output/cyg07.ddmi.s20170609-000000-e20170609-235959.l1.power-brcs.sand004.txt"
file_meas = open(filename_kalman_meas)
read_file_meas = file_meas.readlines()
nb_header = 0
while (read_file_meas[nb_header].split()[0] != '#START'):
    nb_header = nb_header + 1
nb_header = nb_header + 1
n_meas = len(read_file_meas) - nb_header
r_meas = np.zeros([n_meas,3])
v_meas = np.zeros([n_meas,3])
date_meas = []
for itime in range(n_meas):
    date_meas.append(read_file_meas[itime+nb_header].split()[0])
    r_meas[itime,0] = read_file_meas[itime+nb_header].split()[1]
    r_meas[itime,1] = read_file_meas[itime+nb_header].split()[2]
    r_meas[itime,2] = read_file_meas[itime+nb_header].split()[3]
    v_meas[itime,0] = read_file_meas[itime+nb_header].split()[4]
    v_meas[itime,1] = read_file_meas[itime+nb_header].split()[5]
    v_meas[itime,2] = read_file_meas[itime+nb_header].split()[6]

file_meas.close()

# Read Kalman file

#### Read SpOCK main input file to figure out stuff to then read the output
output_file_path_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]; 
output_file_name_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')]; 


## Read kalman filter output file
isc = 0 # !!!!!!! all sc
filename_kalm = output_file_path_list[isc] + "kalman_" + output_file_name_list[isc]
file_kalm = open(filename_kalm)
read_file_kalm = file_kalm.readlines()
nb_header = 0
# while (read_file_kalm[nb_header].split()[0] != '#START'):
#     nb_header = nb_header + 1
# nb_header = nb_header + 1
n_kalm = len(read_file_kalm) - nb_header
r_kalm = np.zeros([n_kalm,3])
v_kalm = np.zeros([n_kalm,3])
Pdiag = np.zeros([n_kalm,6])
dX = np.zeros([n_kalm,6])
y = np.zeros([n_kalm,3])
sy = np.zeros([n_kalm,3])
y_pf = np.zeros([n_kalm,3])

date_kalm = []
date = []
nb_seconds_since_start = []
for itime in range(n_kalm):
    date_kalm.append(read_file_kalm[itime+nb_header].split()[0])
    date.append(datetime.strptime( date_kalm[-1], "%Y-%m-%dT%H:%M:%S.%f" ))
    nb_seconds_since_start.append( (date[-1] - date[0]).total_seconds() )
    r_kalm[itime,0] = read_file_kalm[itime+nb_header].split()[1]
    r_kalm[itime,1] = read_file_kalm[itime+nb_header].split()[2]
    r_kalm[itime,2] = read_file_kalm[itime+nb_header].split()[3]
    v_kalm[itime,0] = read_file_kalm[itime+nb_header].split()[4]
    v_kalm[itime,1] = read_file_kalm[itime+nb_header].split()[5]
    v_kalm[itime,2] = read_file_kalm[itime+nb_header].split()[6]
    Pdiag[itime,0] = read_file_kalm[itime+nb_header].split()[7]
    Pdiag[itime,1] = read_file_kalm[itime+nb_header].split()[8]
    Pdiag[itime,2] = read_file_kalm[itime+nb_header].split()[9]
    Pdiag[itime,3] = read_file_kalm[itime+nb_header].split()[10]
    Pdiag[itime,4] = read_file_kalm[itime+nb_header].split()[11]
    Pdiag[itime,5] = read_file_kalm[itime+nb_header].split()[12]
    dX[itime,0] = read_file_kalm[itime+nb_header].split()[13]
    dX[itime,1] = read_file_kalm[itime+nb_header].split()[14]
    dX[itime,2] = read_file_kalm[itime+nb_header].split()[15]
    dX[itime,3] = read_file_kalm[itime+nb_header].split()[16]
    dX[itime,4] = read_file_kalm[itime+nb_header].split()[17]
    dX[itime,5] = read_file_kalm[itime+nb_header].split()[18]
    y[itime,0] = read_file_kalm[itime+nb_header].split()[19]
    y[itime,1] = read_file_kalm[itime+nb_header].split()[20]
    y[itime,2] = read_file_kalm[itime+nb_header].split()[21]
    sy[itime,0] = read_file_kalm[itime+nb_header].split()[22]
    sy[itime,1] = read_file_kalm[itime+nb_header].split()[23]
    sy[itime,2] = read_file_kalm[itime+nb_header].split()[24]
    y_pf[itime,0] = read_file_kalm[itime+nb_header].split()[25]
    y_pf[itime,1] = read_file_kalm[itime+nb_header].split()[26]
    y_pf[itime,2] = read_file_kalm[itime+nb_header].split()[27]


file_kalm.close()

# test if times are the same in measurement and kalman file
if date_kalm != date_meas:
    print "Times in the measurement file are different from times in the Kalman file. This is ok but not to run this script. The program will stop."; raise Exception

# Time axis (in hours if more than 3 hours, otherwise in minutes)
nb_seconds_since_start = np.array(nb_seconds_since_start)
if ( date[-1] - date[0] ).total_seconds() > 3*3600:
    x_unit = "hour"
    x_axis = nb_seconds_since_start/3600.
else:
    x_unit = "min"
    x_axis = nb_seconds_since_start/60.

# What to plot
plot_3d = 0
plot_r = 0
plot_v = 0
plot_Pdiag = 0
plot_dX = 0
plot_y = 0
if '3d' in sys.argv:
    plot_3d = 1
if 'r' in sys.argv:
    plot_r = 1
if 'v' in sys.argv:
    plot_v = 1
if 'Pdiag' in sys.argv:
    plot_Pdiag = 1
if 'dX' in sys.argv:
    plot_dX = 1
if 'y' in sys.argv:
    plot_y = 1
compare_out = ""
for i in range(2,len(sys.argv)):
    if '.txt' in sys.argv[i]:
        compare_out = sys.argv[i]

    
## Parameters for the figure
height_fig = 11.  # the width is calculated as height_fig * 4/3.
fontsize_plot = 20 
ratio_fig_size = 4./3

# Plot 3d orbits
if plot_3d == 1:
    plt.ioff()
    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
    fig_title = '3D orbits'
    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

    fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    gs = gridspec.GridSpec(1, 1)
    gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.1)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold

    ax = fig.gca(projection='3d')
    ax.plot(r_kalm[:,0], r_kalm[:,1], r_kalm[:,2], label='Kalman', color = 'r', linewidth = 4)
    ax.scatter(r_meas[:,0], r_meas[:,1], r_meas[:,2], label='Measurement', color = 'b', linewidth = 6)
    x_label = "X (km)"
    y_label = "Y (km)"
    z_label = "Z (km)"
    ax.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot, labelpad = 35)
    ax.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot, labelpad = 35)
    ax.set_zlabel(z_label, weight = 'bold', fontsize  = fontsize_plot, labelpad = 35)
    [i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure
    ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)

    legend = ax.legend(loc = 'center', bbox_to_anchor=(0.5, 1),  fontsize = fontsize_plot)
    fig.savefig(output_file_name_list[isc].replace(".txt", "") + "_3d.pdf")
    plt.show()

# Plot position
if plot_r == 1:
    ## Magnitude of difference (not difference of magnitude)
    mag_of_r_diff = np.zeros([n_kalm])
    for itime in range(n_kalm):
        mag_of_r_diff[itime] = np.linalg.norm( r_meas[itime,:] - r_kalm[itime,:] )
    fig_title = 'Magnitude of difference position meas - kalm'
    if x_unit == "hour":
        x_label = 'Time (hr)'
    else:
        x_label = 'Time (min)'
    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

    fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    gs = gridspec.GridSpec(1, 1)
    gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.1, wspace = 0.35)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    
    ## X
    y_label = 'Magnitude of delta r (km)'
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    ax1.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax1.spines.itervalues()] # change the width of the frame of the figure
    ax1.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax1.plot(x_axis, mag_of_r_diff, linewidth = 2,label='', color = 'k')
    ax1.margins(0,0)


    fig_save_name = output_file_name_list[isc].replace(".txt", "") + '_r_mag.pdf'
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

    ## All components
    fig_title = ''
    if x_unit == "hour":
        x_label = 'Time (hr)'
    else:
        x_label = 'Time (min)'
    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

    fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    gs = gridspec.GridSpec(3, 2)
    gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.1, wspace = 0.35)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    
    ## X
    y_label = 'X (km)'
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_title('Meas (b), Kalm (r)', weight = 'bold', fontsize = fontsize_plot)
    ax1.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax1.spines.itervalues()] # change the width of the frame of the figure
    ax1.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax1.xaxis.set_ticklabels("")
    ax1.plot(x_axis, r_meas[:,0], linewidth = 2,label='Measurement', color = 'b')
    ax1.plot(x_axis, r_kalm[:,0], linewidth = 2,label='Kalman', color = 'r')
    #legend = ax1.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax1.margins(0,0)

    ## dX
    y_label = 'dX (km)'
    ax4 = fig.add_subplot(gs[0, 1])
    ax4.set_title('Meas - Kalm', weight = 'bold', fontsize = fontsize_plot)
    ax4.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax4.spines.itervalues()] # change the width of the frame of the figure
    ax4.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax4.xaxis.set_ticklabels("")
    ax4.plot(x_axis, r_meas[:,0] - r_kalm[:,0], linewidth = 2,label='', color = 'k')
    legend = ax4.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax4.margins(0,0)
    
    ## Y
    y_label = 'Y (km)'
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax2.spines.itervalues()] # change the width of the frame of the figure
    ax2.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax2.xaxis.set_ticklabels("")
    ax2.plot(x_axis, r_meas[:,1], linewidth = 2,label='Measurement', color = 'b')
    ax2.plot(x_axis, r_kalm[:,1], linewidth = 2,label='Kalman', color = 'r')
    ax2.margins(0,0)

    ## dY
    y_label = 'dY (km)'
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax5.spines.itervalues()] # change the width of the frame of the figure
    ax5.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax5.xaxis.set_ticklabels("")
    ax5.plot(x_axis, r_meas[:,1] - r_kalm[:,1], linewidth = 2,label='', color = 'k')
    legend = ax5.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax5.margins(0,0)


    ## X
    y_label = 'Z (km)'
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    ax3.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax3.spines.itervalues()] # change the width of the frame of the figure
    ax3.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
    ax3.plot(x_axis, r_meas[:,2], linewidth = 2,label='Measurement', color = 'b')
    ax3.plot(x_axis, r_kalm[:,2], linewidth = 2,label='Kalman', color = 'r')
    ax3.margins(0,0)    

    ## dZ
    y_label = 'dZ (km)'
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    ax6.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax6.spines.itervalues()] # change the width of the frame of the figure
    ax6.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax6.plot(x_axis, r_meas[:,2] - r_kalm[:,2], linewidth = 2,label='', color = 'k')
    legend = ax6.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax6.margins(0,0)


    fig_save_name = output_file_name_list[isc].replace(".txt", "") + '_r.pdf'
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

# Plot velocity
if plot_v == 1:
    ## Magnitude of difference (not difference of magnitude)
    mag_of_v_diff = np.zeros([n_kalm])
    for itime in range(n_kalm):
        mag_of_v_diff[itime] = np.linalg.norm( v_meas[itime,:] - v_kalm[itime,:] )
    fig_title = 'Magnitude of difference velocity meas - kalm'
    if x_unit == "hour":
        x_label = 'Time (hr)'
    else:
        x_label = 'Time (min)'
    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

    fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    gs = gridspec.GridSpec(1, 1)
    gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.1, wspace = 0.35)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    
    ## X
    y_label = 'Magnitude of delta v (km/s)'
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    ax1.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax1.spines.itervalues()] # change the width of the frame of the figure
    ax1.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax1.plot(x_axis, mag_of_v_diff, linewidth = 2,label='', color = 'k')
    ax1.margins(0,0)


    fig_save_name = output_file_name_list[isc].replace(".txt", "") + '_v_mag.pdf'
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

    ## All components

    fig_title = ''
    if x_unit == "hour":
        x_label = 'Time (hr)'
    else:
        x_label = 'Time (min)'
    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

    fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    gs = gridspec.GridSpec(3, 2)
    gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.1, wspace = 0.35)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    
    ## X
    y_label = 'Vx (km/s)'
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_title('Meas (b), Kalm (r)', weight = 'bold', fontsize = fontsize_plot)
    ax1.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax1.spines.itervalues()] # change the width of the frame of the figure
    ax1.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax1.xaxis.set_ticklabels("")
    ax1.plot(x_axis, v_meas[:,0], linewidth = 2,label='Measurement', color = 'b')
    ax1.plot(x_axis, v_kalm[:,0], linewidth = 2,label='Kalman', color = 'r')
    #legend = ax1.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax1.margins(0,0)

    ## dX
    y_label = 'dVx (km/s)'
    ax4 = fig.add_subplot(gs[0, 1])
    ax4.set_title('Meas - Kalm', weight = 'bold', fontsize = fontsize_plot)
    ax4.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax4.spines.itervalues()] # change the width of the frame of the figure
    ax4.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax4.xaxis.set_ticklabels("")
    ax4.plot(x_axis, v_meas[:,0] - v_kalm[:,0], linewidth = 2,label='', color = 'k')
    legend = ax4.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax4.margins(0,0)
    
    ## Y
    y_label = 'Vy (km/s)'
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax2.spines.itervalues()] # change the width of the frame of the figure
    ax2.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax2.xaxis.set_ticklabels("")
    ax2.plot(x_axis, v_meas[:,1], linewidth = 2,label='Measurement', color = 'b')
    ax2.plot(x_axis, v_kalm[:,1], linewidth = 2,label='Kalman', color = 'r')
    ax2.margins(0,0)

    ## dY
    y_label = 'dVy (km/s)'
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax5.spines.itervalues()] # change the width of the frame of the figure
    ax5.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax5.xaxis.set_ticklabels("")
    ax5.plot(x_axis, v_meas[:,1] - v_kalm[:,1], linewidth = 2,label='', color = 'k')
    legend = ax5.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax5.margins(0,0)


    ## X
    y_label = 'Vz (km/s)'
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    ax3.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax3.spines.itervalues()] # change the width of the frame of the figure
    ax3.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
    ax3.plot(x_axis, v_meas[:,2], linewidth = 2,label='Measurement', color = 'b')
    ax3.plot(x_axis, v_kalm[:,2], linewidth = 2,label='Kalman', color = 'r')
    ax3.margins(0,0)    

    ## dZ
    y_label = 'dVz (km/s)'
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    ax6.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax6.spines.itervalues()] # change the width of the frame of the figure
    ax6.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax6.plot(x_axis, v_meas[:,2] - v_kalm[:,2], linewidth = 2,label='', color = 'k')
    legend = ax6.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax6.margins(0,0)


    fig_save_name = output_file_name_list[isc].replace(".txt", "") + '_v.pdf'
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  
# Plot Pdiag
if plot_Pdiag == 1:
    fig_title = ''
    if x_unit == "hour":
        x_label = 'Time (hr)'
    else:
        x_label = 'Time (min)'

    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

    fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    gs = gridspec.GridSpec(3, 1)
    gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.27)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    
    ## Position uncertainty
    y_label = 'sigma position (km)'
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_title('Position uncertainty', fontsize = fontsize_plot, weight = 'bold')
    ax1.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax1.spines.itervalues()] # change the width of the frame of the figure
    ax1.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax1.xaxis.set_ticklabels("")
    ax1.plot(x_axis, Pdiag[:,0], linewidth = 2,label='X', color = 'b')
    ax1.plot(x_axis, Pdiag[:,1], linewidth = 2,label='Y', color = 'r')
    ax1.plot(x_axis, Pdiag[:,2], linewidth = 2,label='Z', color = 'k')
    legend = ax1.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax1.margins(0,0)

    ## Velocity uncertainty
    y_label = 'sigma velocity (km/s)'
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_title('Velocity uncertainty', fontsize = fontsize_plot, weight = 'bold')
    ax2.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax2.spines.itervalues()] # change the width of the frame of the figure
    ax2.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax2.xaxis.set_ticklabels("")
    ax2.plot(x_axis, Pdiag[:,3], linewidth = 2,label='Vx', color = 'b')
    ax2.plot(x_axis, Pdiag[:,4], linewidth = 2,label='Vy', color = 'r')
    ax2.plot(x_axis, Pdiag[:,5], linewidth = 2,label='Vz', color = 'k')
    legend = ax2.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax2.margins(0,0)

    ## ? uncertainty
    y_label = '?'
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.set_title('? uncertainty', fontsize = fontsize_plot, weight = 'bold')
    ax3.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    ax3.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax3.spines.itervalues()] # change the width of the frame of the figure
    ax3.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax3.plot(x_axis, Pdiag[:,6], linewidth = 2,label='?', color = 'b')
    ax3.margins(0,0)    

    fig_save_name = output_file_name_list[isc].replace(".txt", "") + '_Pdiag.pdf'
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  


# Plot dX
if plot_dX == 1:
    fig_title = ''
    if x_unit == "hour":
        x_label = 'Time (hr)'
    else:
        x_label = 'Time (min)'

    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

    fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    gs = gridspec.GridSpec(3, 1)
    gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.27)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    
    ## Position 
    y_label = 'dr (km)'
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_title('Position', fontsize = fontsize_plot, weight = 'bold')
    ax1.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax1.spines.itervalues()] # change the width of the frame of the figure
    ax1.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax1.xaxis.set_ticklabels("")
    ax1.plot(x_axis, dX[:,0], linewidth = 2,label='dX', color = 'b')
    ax1.plot(x_axis, dX[:,1], linewidth = 2,label='dY', color = 'r')
    ax1.plot(x_axis, dX[:,2], linewidth = 2,label='dZ', color = 'k')
    legend = ax1.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax1.margins(0,0)

    ## Velocity 
    y_label = 'dv (km/s)'
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_title('Velocity', fontsize = fontsize_plot, weight = 'bold')
    ax2.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax2.spines.itervalues()] # change the width of the frame of the figure
    ax2.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax2.xaxis.set_ticklabels("")
    ax2.plot(x_axis, dX[:,3], linewidth = 2,label='dVx', color = 'b')
    ax2.plot(x_axis, dX[:,4], linewidth = 2,label='dVy', color = 'r')
    ax2.plot(x_axis, dX[:,5], linewidth = 2,label='dVz', color = 'k')
    legend = ax2.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax2.margins(0,0)

    fig_save_name = output_file_name_list[isc].replace(".txt", "") + '_dX.pdf'
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  


# Plot y, sy, y_pf
if plot_y == 1:
    fig_title = ''
    if x_unit == "hour":
        x_label = 'Time (hr)'
    else:
        x_label = 'Time (min)'

    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

    fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    gs = gridspec.GridSpec(3, 1)
    gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.27)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    
    ## Position uncertainty
    y_label = 'y (km)'
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_title('y', fontsize = fontsize_plot, weight = 'bold')
    ax1.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax1.spines.itervalues()] # change the width of the frame of the figure
    ax1.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax1.xaxis.set_ticklabels("")
    ax1.plot(x_axis, y[:,0], linewidth = 2,label='Y[0]', color = 'b')
    ax1.plot(x_axis, y[:,1], linewidth = 2,label='Y[1]', color = 'r')
    ax1.plot(x_axis, y[:,2], linewidth = 2,label='Y[2]', color = 'k')

    legend = ax1.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax1.margins(0,0)

    ## Velocity uncertainty
    y_label = 'sy (?)'
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_title('sy', fontsize = fontsize_plot, weight = 'bold')
    ax2.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax2.spines.itervalues()] # change the width of the frame of the figure
    ax2.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax2.xaxis.set_ticklabels("")
    ax2.plot(x_axis, sy[:,0], linewidth = 2,label='sy[0]', color = 'b')
    ax2.plot(x_axis, sy[:,1], linewidth = 2,label='sy[1]', color = 'r')
    ax2.plot(x_axis, sy[:,2], linewidth = 2,label='sz[2]', color = 'k')
    legend = ax2.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax2.margins(0,0)

    ## Velocity uncertainty
    y_label = 'y_pf (km)'
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.set_title('y_pf', fontsize = fontsize_plot, weight = 'bold')
    ax3.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    ax3.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax3.spines.itervalues()] # change the width of the frame of the figure
    ax3.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax3.plot(x_axis, y_pf[:,0], linewidth = 2,label='y_pf[0]', color = 'b')
    ax3.plot(x_axis, y_pf[:,1], linewidth = 2,label='y_pf[1]', color = 'r')
    ax3.plot(x_axis, y_pf[:,2], linewidth = 2,label='y_pf[2]', color = 'k')
    legend = ax3.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax3.margins(0,0)
    
    fig_save_name = output_file_name_list[isc].replace(".txt", "") + '_y_sy_ypf.pdf'
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  




if compare_out != "":
    var_in, var_in_order = read_input_file(compare_out)
    output_file_path_list_comp = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]; 
    output_file_name_list_comp = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')];
    var_to_read = ["position","velocity"]
    var_out, var_out_order = read_output_file( output_file_path_list_comp[isc] + output_file_name_list_comp[isc], var_to_read )
    r_comp = var_out[find_in_read_input_order_variables(var_out_order, 'position')]
    v_comp = var_out[find_in_read_input_order_variables(var_out_order, 'velocity')]
    
    if x_unit == "hour":
        x_label = 'Time (hr)'
    else:
        x_label = 'Time (min)'
    fig_title = ''
    # fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

    # fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    # plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    # gs = gridspec.GridSpec(3, 1)
    # gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.1, wspace = 0.35)
    # plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    
    # ## X
    # y_label = 'X (m)'
    # ax1 = fig.add_subplot(gs[0, 0])
    # ax1.set_title('Position - Kalman (b), True (r)', weight = 'bold', fontsize = fontsize_plot)
    # ax1.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    # [i.set_linewidth(2) for i in ax1.spines.itervalues()] # change the width of the frame of the figure
    # ax1.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    # ax1.xaxis.set_ticklabels("")
    # ax1.scatter(x_axis, ( r_kalm[:,0] - r_comp[:,0] ) * 1000, linewidth = 2,label='Kalman', color = 'b')
    # ax1.plot(x_axis, ( r_comp[:,0] - r_comp[:,0] ) * 1000, linewidth = 4,label='True', color = 'r')
    # #legend = ax1.legend(loc = 'upper right',  fontsize = fontsize_plot)
    # ax1.margins(0,0)

    # ## Y
    # y_label = 'Y (m)'
    # ax2 = fig.add_subplot(gs[1, 0])
    # ax2.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    # [i.set_linewidth(2) for i in ax2.spines.itervalues()] # change the width of the frame of the figure
    # ax2.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    # ax2.xaxis.set_ticklabels("")
    # ax2.scatter(x_axis, ( r_kalm[:,1] - r_comp[:,1] ) * 1000, linewidth = 2,label='Kalman', color = 'b')
    # ax2.plot(x_axis, ( r_comp[:,1] - r_comp[:,1] ) * 1000, linewidth = 4,label='True', color = 'r')
    # ax2.margins(0,0)

    # ## X
    # y_label = 'Z (m)'
    # ax3 = fig.add_subplot(gs[2, 0])
    # ax3.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    # ax3.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)
    # [i.set_linewidth(2) for i in ax3.spines.itervalues()] # change the width of the frame of the figure
    # ax3.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
    # ax3.scatter(x_axis, ( r_kalm[:,2] - r_comp[:,2] ) * 1000, linewidth = 2,label='Kalman', color = 'b')
    # ax3.plot(x_axis, ( r_comp[:,2] - r_comp[:,2] ) * 1000, linewidth = 4,label='True', color = 'r')
    # ax3.margins(0,0)    

    # fig_save_name = output_file_name_list[isc].replace(".txt", "") + '_true_vs_kalm_r.pdf'
    # fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

    
    # if x_unit == "hour":
    #     x_label = 'Time (hr)'
    # else:
    #     x_label = 'Time (min)'
    # fig_title = ''
    # fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

    # fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    # plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    # gs = gridspec.GridSpec(3, 1)
    # gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.1, wspace = 0.35)
    # plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    
    # ## X
    # y_label = 'Vx (m/s)'
    # ax1 = fig.add_subplot(gs[0, 0])
    # ax1.set_title('Velocity - Kalman (b), True (r)', weight = 'bold', fontsize = fontsize_plot)
    # ax1.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    # [i.set_linewidth(2) for i in ax1.spines.itervalues()] # change the width of the frame of the figure
    # ax1.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    # ax1.xaxis.set_ticklabels("")
    # ax1.scatter(x_axis, (v_kalm[:,0] - v_comp[:,0])*1000., linewidth = 2,label='Kalman', color = 'b')
    # ax1.plot(x_axis, (v_comp[:,0] - v_comp[:,0])*1000., linewidth = 4,label='True', color = 'r')
    # #legend = ax1.legend(loc = 'upper right',  fontsize = fontsize_plot)
    # ax1.margins(0,0)

    # ## Y
    # y_label = 'Vy (m/s)'
    # ax2 = fig.add_subplot(gs[1, 0])
    # ax2.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    # [i.set_linewidth(2) for i in ax2.spines.itervalues()] # change the width of the frame of the figure
    # ax2.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    # ax2.xaxis.set_ticklabels("")
    # ax2.scatter(x_axis, (v_kalm[:,1] - v_comp[:,1])*1000., linewidth = 2,label='Kalman', color = 'b')
    # ax2.plot(x_axis, (v_comp[:,1] - v_comp[:,1])*1000., linewidth = 4,label='True', color = 'r')
    # ax2.margins(0,0)

    # ## X
    # y_label = 'Vz (m/s)'
    # ax3 = fig.add_subplot(gs[2, 0])
    # ax3.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    # ax3.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)
    # [i.set_linewidth(2) for i in ax3.spines.itervalues()] # change the width of the frame of the figure
    # ax3.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
    # ax3.scatter(x_axis, (v_kalm[:,2] - v_comp[:,2])*1000., linewidth = 2,label='Kalman', color = 'b')
    # ax3.plot(x_axis, (v_comp[:,2] - v_comp[:,2])*1000., linewidth = 4,label='True', color = 'r')
    # ax3.margins(0,0)    

    # fig_save_name = output_file_name_list[isc].replace(".txt", "") + '_true_vs_kalm_v.pdf'
    # fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

    r_error = np.zeros([n_kalm, 3])
    v_error = np.zeros([n_kalm, 3])
    r_error_mag = np.zeros([n_kalm])
    v_error_mag = np.zeros([n_kalm])
    r_error_square = np.zeros([n_kalm,3])
    v_error_square = np.zeros([n_kalm,3])
    for itime in range(n_kalm):
        r_error[itime, :] = r_kalm[itime,:] - r_comp[itime,:]
        v_error[itime, :] = v_kalm[itime,:] - v_comp[itime,:]
        r_error_square[itime, :] = r_error[itime, :]**2
        v_error_square[itime, :] = v_error[itime, :]**2
        r_error_mag[itime] = np.linalg.norm(r_error[itime, :])
        v_error_mag[itime] = np.linalg.norm(v_error[itime, :])
    r_rmse = np.sqrt( np.mean(r_error_square) )
    v_rmse = np.sqrt( np.mean(v_error_square) )
    # Plot error VS time
    fig_title = ''
    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')

    fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    gs = gridspec.GridSpec(2, 1)
    gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.14, wspace = 0.35)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    
    ## X
    y_label = 'Error (m)'
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_title('Magnitude of position difference r_kalm - r_true', weight = 'bold', fontsize = fontsize_plot)
    ax1.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax1.spines.itervalues()] # change the width of the frame of the figure
    ax1.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    ax1.xaxis.set_ticklabels("")
    ax1.scatter(x_axis, (r_error_mag)*1000., linewidth = 2,label='Kalman', color = 'b')
    #legend = ax1.legend(loc = 'upper right',  fontsize = fontsize_plot)
    ax1.margins(0,0)
    ax1.text( max(x_axis), max((r_error_mag)*1000.) - ( max((r_error_mag)*1000.) - min((r_error_mag)*1000.) )/15, "RMSE = " + '{:.2f}'.format(r_rmse*1000) + " m", fontsize = fontsize_plot, weight = 'bold', color = 'r', horizontalalignment = 'right')

    ## Y
    y_label = 'Error (m/s)'
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_title('Magnitude of velocity difference v_kalm - v_true', weight = 'bold', fontsize = fontsize_plot)
    ax2.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    ax2.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)
    [i.set_linewidth(2) for i in ax2.spines.itervalues()] # change the width of the frame of the figure
    ax2.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
    # ax2.xaxis.set_ticklabels("")
    ax2.scatter(x_axis, (v_error_mag)*1000., linewidth = 2,label='Kalman', color = 'b')
    ax2.margins(0,0)
    ax2.text( max(x_axis),  max((v_error_mag)*1000.) - ( max((v_error_mag)*1000.) - min((v_error_mag)*1000.) )/15, "RMSE = " + '{:.2f}'.format(v_rmse*100000) + " cm/s", fontsize = fontsize_plot, weight = 'bold', color = 'r', horizontalalignment = 'right', verticalalignment = 'top')


    fig_save_name = output_file_name_list[isc].replace(".txt", "") + '_error_mag.pdf'
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

    

    itime = 0
    mag_delta_r_temp = r_kalm[itime,:] - r_comp[itime,:]
    mag_delta_v_temp = v_kalm[itime,:] - v_comp[itime,:]
    print "Magnitude of delta r at time " + str(itime) + ": ", np.linalg.norm(mag_delta_r_temp) * 1000, "m"
    print "Magnitude of delta v at time " + str(itime) + ": ", np.linalg.norm(mag_delta_v_temp)*1000., "m/s"




    
