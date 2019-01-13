# This script was made for the beacon test campaing in White Sands, NM, in November 2018. The results were discussesd with Darren McKague.
# First need to run input_filename with spock
# then create the ground statino reports: python report_coverage_ground_station_for_sift_parallel_sftp.py beaconmiddle.txt
# then run this script


import ipdb
import sys

sys.path.append("/Users/cbv/Google Drive/Work/PhD/Research/Code/spock/srcPython")
#sys.path.append("/home/cbv/Code/spock/srcPython")

from utc2mst import *
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
from gs_radius import *
#from cygnss_read_spock_spec import *
import pyorbital.orbital

def radius_for_tissot(dist_km):
    return np.rad2deg(dist_km/6378.) # this is calculating using the Haversine formula



input_filename = 'beacon_1203.txt'
min_max_elev = 60. # all sc with a max elev wrt to gs that's lower than min_max_elev are excluded


var_in, var_in_order = read_input_file(input_filename)
output_file_path_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]; 
output_file_name_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')]; 
dt = var_in[find_in_read_input_order_variables(var_in_order, 'dt_output')]; 
nb_steps = var_in[find_in_read_input_order_variables(var_in_order, 'nb_steps')]; 
nb_sc = var_in[find_in_read_input_order_variables(var_in_order, 'nb_sc')]; 
date_start = var_in[find_in_read_input_order_variables(var_in_order, 'date_start')]
date_stop = var_in[find_in_read_input_order_variables(var_in_order, 'date_stop')]
filename_ground_station = var_in[find_in_read_input_order_variables(var_in_order, 'filename_ground_station')]

date_start_str = datetime.strftime(date_start,  "%Y-%m-%dT%H:%M:%S")
date_stop_str = datetime.strftime(date_stop,  "%Y-%m-%dT%H:%M:%S")


# paramaters for the animation
lat_min = -90
lat_max = 90
lon_min = -180
lon_max = 180
dt_ani = 24*3600 #180. # in seconds
is_cygnss = '1'


if filename_ground_station != "": # if ther is a ground station file in the main input file
    file_ground_station = open(filename_ground_station)
    read_file_ground_station = file_ground_station.readlines()
    nheader_gs = 0
    while (read_file_ground_station[nheader_gs][:6] != '#START'):
        nheader_gs = nheader_gs + 1
    nheader_gs = nheader_gs + 1
    nb_gs = 0
    while (read_file_ground_station[nb_gs+nheader_gs][:4] != '#END'):
        nb_gs = nb_gs + 1
    # read in the lat/lon/elev mask of each gs
    lat_gs = np.zeros([nb_gs]); lon_gs = np.zeros([nb_gs]); elev_gs = np.zeros([nb_gs]); name_gs = []
    for igs in range(nb_gs):
        name_gs.append( read_file_ground_station[igs + nheader_gs].split()[0] )
        lat_gs[igs] = np.float(read_file_ground_station[igs + nheader_gs].split()[1])
        lon_gs[igs] = np.float(read_file_ground_station[igs + nheader_gs].split()[2])
        elev_gs[igs] = np.float(read_file_ground_station[igs + nheader_gs].split()[4])
    file_ground_station.close()
if dt_ani < dt:
    print "***! The time step of the animation can't be smaller than the time step of the animation (" + str(dt) + " seconds). Therefore, it was set to " + str(dt) + " seconds. !***"
    dt_ani  = dt

var_to_read = ["date","latitude", "longitude", "altitude"]
spacecraft_list = []
point = namedtuple('point', ['x', 'y'])
color = namedtuple('color', 'red green blue')

for isc in range(nb_sc):
    var_out, var_out_order = read_output_file( output_file_path_list[isc] + output_file_name_list[isc], var_to_read )
    if isc == 0:
        date = var_out[find_in_read_input_order_variables(var_out_order, 'date')]
        date_round_sec = var_out[find_in_read_input_order_variables(var_out_order, 'date_round_sec')]
        date_datetime = var_out[find_in_read_input_order_variables(var_out_order, 'date_datetime')]
        date_datetime_round_sec = var_out[find_in_read_input_order_variables(var_out_order, 'date_datetime_round_sec')]
        nb_steps = len(date)
        lat = np.zeros([nb_sc, nb_steps]); lon = np.zeros([nb_sc, nb_steps]); alt = np.zeros([nb_sc, nb_steps])
        azim_sc  = np.zeros([nb_sc, nb_steps]); elev_sc = np.zeros([nb_sc, nb_steps])
    lat[isc, :] = var_out[find_in_read_input_order_variables(var_out_order, 'latitude')]
    alt[isc, :] = var_out[find_in_read_input_order_variables(var_out_order, 'altitude')]
    lon[isc, :] = var_out[find_in_read_input_order_variables(var_out_order, 'longitude')]

    # Elevation azimuth of sc wrt ground station
    azim_sc[isc, :], elev_sc[isc, :] = pyorbital.orbital.get_observer_look(lon[isc, :], lat[isc, :], alt[isc, :], np.array(date_datetime_round_sec), lon_gs[0], lat_gs[0], 0) # !!!!! last 0 for altitude of gs    
    spacecraft = namedtuple('spacecraft',('name',) +  point._fields + ('point_plot',) + ('marker_spacecraft',))
    spacecraft_list.append(spacecraft)

    spacecraft_list[isc].marker_spacecraft = '.'

    dt_index_sc = (int)(dt_ani / dt) # step for the index in lon and lat
    nb_steps_ani_sc = nb_steps / dt_index_sc 



contact_time = []
contact_time_elev_gt_threshold = []
for isc in range(nb_sc):
    contact_time_sub = []
    contact_time_elev_gt_threshold_sub = []
    gs_filename = output_file_path_list[isc] + 'coverage/report_all_by_' + output_file_name_list[isc]
    gs_file = open(gs_filename)
    read_gs_file = gs_file.readlines()
    nhead = 2
    nb_ct = len(read_gs_file) - nhead
    for ict in range(nb_ct):
        start = datetime.strptime( read_gs_file[ict + nhead].split()[1] + 'T' + read_gs_file[ict + nhead].split()[2], "%Y-%m-%dT%H:%M:%S" )
        end = datetime.strptime( read_gs_file[ict + nhead].split()[4] + 'T' + read_gs_file[ict + nhead].split()[5], "%Y-%m-%dT%H:%M:%S" )
        duration = np.float(read_gs_file[ict + nhead].split()[9].replace("(","") )
        elev_max = np.float(read_gs_file[ict + nhead].split('max_elev ')[1].split()[0])
        contact_time_sub.append([start, end, duration ])
        if elev_max >= min_max_elev:
            contact_time_elev_gt_threshold_sub.append([start, end, duration ])
    gs_file.close()

    contact_time.append(contact_time_sub)
    contact_time_elev_gt_threshold.append(contact_time_elev_gt_threshold_sub)

# Determine how long it takes for the beacon station to see all 8 sc
# If 2 or more sc are in sight, only consider the one that's in contact for the longest time
# This is because the beacon won't be able to be steered from on sc to another so quickly
# Actually, if for instance there's 2 sc, at the first overpass, consider the one that is in conact the longest
#for isc in range(nb_sc):


# FIGURES
satColors = ['black', 'blue', 'red', 'mediumorchid', 'dodgerblue', 'magenta', 'darkgreen', 'limegreen'] #['lime', 'blue', 'indigo', 'purple', 'dodgerblue', 'steelblue', 'seagreen', 'limegreen']
nb_sc = 8 # !!!!!!!!!
label_arr = ['FM05', 'FM04', 'FM02', 'FM01', 'FM08', 'FM06', 'FM07', 'FM03']
label_arr_conversion = [3, 2, 7, 1, 0, 5, 6, 4]

# Plot the coverage VS time for all sc (left) and on the right show 2d animtion 
width_fig = 15.
height_fig = width_fig * 3 /4
fontsize_plot = 20 # 9
color_arr = ['k','b','r','g','m', 'y']

iday = 0
nb_day = (int)( np.ceil((date_stop - date_start).total_seconds() / 3600./24) )

date_day_arr = np.array([date_start + timedelta(days=i) for i in np.arange(0, nb_day +1, 1)])

fig = plt.figure(num=None, figsize=(width_fig, height_fig), dpi=80, facecolor='w', edgecolor='k')
gs = gridspec.GridSpec(2, 1)
gs.update(left=0.12, right=0.97, top = 0.90,bottom = 0.06)
fig.suptitle('', fontsize = 22)
plt.rc('font', weight='normal') ## make the labels of the ticks in normal

istep_start = 0 # !!!!!!!!!! was 1
for istep in range(0,nb_steps_ani_sc):#!!!!!!!! was range(1,nb_steps_ani_sc):
    if date_datetime_round_sec[istep*dt_index_sc]  >= date_day_arr[iday]:
        if istep != istep_start : # nothing to remove for first map
            for ifill in range(len(fill_cont)):
                fill_cont[ifill].remove()                
                #del fill_cont[ifill]
            for ifill in range(len(fill_cont_elev_gt_threshold)):
                fill_cont_elev_gt_threshold[ifill].remove()                
        fill_cont_elev_gt_threshold = []
        fill_cont = []


        date_start_day = date_day_arr[iday]
        date_stop_day = date_day_arr[iday+1]
        max_xaxis = (date_stop_day - date_start_day).total_seconds()
        ax1 = fig.add_subplot(gs[0, 0])
        #ax1 = fig.add_subplot(111)
        ax1.set_title('', weight = 'normal', fontsize = 20,  y = 1.008) 
        ax1.tick_params(axis='both', which='major',  width = 2, pad = 6, labelsize=fontsize_plot, size = 10)
        #ax1.tick_params(axis='both', which='major', labelsize=16, size = 10, width = 2, pad = 7)
        [i.set_linewidth(2) for i in ax1.spines.itervalues()] # change the width of the frame of the figure
        path_folder_plot = '.'
        date_ref = date_start_day
        yticks = np.arange(0, 1, 1./nb_sc)
        ytick_labels = []


        ipdb.set_trace()
        for isc_temp in range(nb_sc):
            isc = label_arr_conversion[isc_temp]
            for icoverage in range( len(contact_time[isc]) ):
                #if ((contact_time[isc][icoverage][0] >= date_ref) & (contact_time[isc][icoverage][0] <= date_stop_day)):
                #print label_arr[isc], contact_time[isc][icoverage][0], contact_time[isc][icoverage][1]
                start_coverage_since_ref = ( contact_time[isc][icoverage][0] - date_ref ).total_seconds()
                end_coverage_since_ref = ( contact_time[isc][icoverage][1] - date_ref ).total_seconds()
                #ax1.plot([start_coverage_since_ref, end_coverage_since_ref], [isc * 1./nb_sc, isc * 1./nb_sc], linewidth = 20, color = satColors[isc])
                fill_cont.append(  ax1.fill_between([start_coverage_since_ref, end_coverage_since_ref], [isc_temp * 1./nb_sc-1./(6*nb_sc), isc_temp * 1./nb_sc-1./(6*nb_sc)],[ isc_temp * 1./nb_sc+1./(6*nb_sc),isc_temp * 1./nb_sc+1./(6*nb_sc)], color = satColors[isc], alpha = 0.15 ) )
                #fill_cont.append(fill_cont_temp.pop(0))
            for icoverage in range( len(contact_time_elev_gt_threshold[isc]) ):
                start_coverage_since_ref = ( contact_time_elev_gt_threshold[isc][icoverage][0] - date_ref ).total_seconds()
                end_coverage_since_ref = ( contact_time_elev_gt_threshold[isc][icoverage][1] - date_ref ).total_seconds()
                #ax1.plot([start_coverage_since_ref, end_coverage_since_ref], [isc * 1./nb_sc, isc * 1./nb_sc], linewidth = 20, color = satColors[isc])
                fill_cont_elev_gt_threshold.append(  ax1.fill_between([start_coverage_since_ref, end_coverage_since_ref], [isc_temp * 1./nb_sc-1./(6*nb_sc), isc_temp * 1./nb_sc-1./(6*nb_sc)],[ isc_temp * 1./nb_sc+1./(6*nb_sc),isc_temp * 1./nb_sc+1./(6*nb_sc)], color = satColors[isc]) )
                #fill_cont.append(fill_cont_temp.pop(0))


            ytick_labels.append(label_arr[isc])

        ax1.yaxis.set_ticks(yticks)
        ax1.yaxis.set_ticklabels(ytick_labels, fontsize = fontsize_plot)#, rotation='vertical')
        isc_temp = 0
        for ytick, color in zip(ax1.get_yticklabels(), satColors):
            isc = label_arr_conversion[isc_temp]
            ytick.set_color(satColors[isc])
            isc_temp = isc_temp + 1


        hour_time_step_xticks = 3
        hour_time_step_xticks_converted_in_seconds = hour_time_step_xticks * 3600
        xticks = np.arange(0, max_xaxis+hour_time_step_xticks_converted_in_seconds, hour_time_step_xticks_converted_in_seconds)
        date_list_str = []
        date_list = [date_start_day + timedelta(seconds=x) for x in np.arange(0, max_xaxis+hour_time_step_xticks_converted_in_seconds, hour_time_step_xticks_converted_in_seconds)]
        for i in range(len(xticks)):
            date_list_str.append( str(date_list[i])[11:16] + '\n' + datetime.strftime(date_list[i], "%b %-d"))
        ax1.xaxis.set_ticks(xticks) 
        ax1.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot)#, rotation='vertical')

        #ax1.set_xlim([16*3600,23*3600])
        ax1.set_xlim([0,max_xaxis])
        ax1.set_ylim([-1./nb_sc,1])
        ax1.margins(0,0) # autoscale both axes(fist value is for the x axis, second value for the y axis)

        ax1.legend( fontsize = fontsize_plot, loc = 4)
        #ax1.set_xlabel('Real time', fontsize = fontsize_plot, weight = 'normal')
        ax1.set_ylabel('', fontsize = fontsize_plot, weight = 'normal')

        iday = iday + 1
    if istep == istep_start:
        y_label = 'Latitude '+ u'(\N{DEGREE SIGN})'
        x_label = 'Longitude '+ u'(\N{DEGREE SIGN})'

        ax_2d = fig.add_subplot(gs[1, 0])
        ax_2d.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
        ax_2d.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)

        [i.set_linewidth(2) for i in ax_2d.spines.itervalues()] # change the width of the frame of the figure
        ax_2d.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 


        ## Plot the 2D map (continents) 
        m = Basemap( projection       = 'cyl',
                     llcrnrlon        = lon_min , #Lower Left  CoRNeR Longitude
                     urcrnrlon        = lon_max  , #Upper Right CoRNeR Longitude
                     llcrnrlat        = lat_min  , #Lower Left  CoRNeR Latitude
                     urcrnrlat        = lat_max,   #Upper Right CoRNeR Latitude
                     resolution       = 'l'  ,
                     suppress_ticks   = False,
                     ax = ax_2d,
                     )

        # color_continents = [65,105,225]
        # color_continents = np.array(color_continents) / 256.
        # color_water  = [100,149,237]
        # color_water = np.array(color_water) / 256.
        # m.fillcontinents(color=tuple(color_continents),lake_color=tuple(color_water))
        # m.drawmapboundary(fill_color=tuple(color_water))

        m.drawcoastlines(linewidth=0.3, color = 'blue')


    utc_str = date_round_sec[istep*dt_index_sc][:19].replace("/", "-").replace(" ", "T")
    ax_title = utc2mst(utc_str).replace("-", "/").replace("T", " ") + ' MST'#date_round_sec[istep*dt_index_sc][:19] + ' UTC'
    print utc_str, ax_title
    ax1.set_title(ax_title, weight = 'normal', fontsize = fontsize_plot , y = 1.00) 

    line_time = (date_datetime_round_sec[istep*dt_index_sc] - date_ref).total_seconds()
    line_time_plot_temp = ax1.plot([line_time, line_time], [-1./nb_sc, 1], linewidth = 2, linestyle = 'dashed', color = 'black')
    line_time_plot = line_time_plot_temp.pop(0)
    #ax_title = date[istep*dt_index_sc][:19] + ' UTC' # cheating with ':00'# str(date_start) + ' to ' + str(date_stop)
    #ax_2d.set_title(ax_title, weight = 'normal', fontsize  = (int)(fontsize_plot*1.1), y = 1.00)

    print "Step " + str(istep) + ' out of ' + str(nb_steps_ani_sc-1) 
    list_sc_in = [] # list of sc in sight of the gs # !!!!!! assumes only one sc
    azim_elev_text = []
    #  positions over one orbit
    for isc_temp in range(nb_sc):
        if is_cygnss == '1':
            isc = label_arr_conversion[isc_temp]
        else: 
            isc = isc_temp
        if lon[isc,istep*dt_index_sc] > 180:
            lon_plot = lon[isc,istep*dt_index_sc] - 360
        else:
            lon_plot = lon[isc,istep*dt_index_sc]
        spacecraft_list[isc_temp].x, spacecraft_list[isc_temp].y =  m(lon_plot, lat[isc,istep*dt_index_sc])
    # point on the plot                                                        
        if is_cygnss == '1':
            spacecraft_list[isc_temp].point_plot = m.scatter(spacecraft_list[isc_temp].x, spacecraft_list[isc_temp].y,  marker=spacecraft_list[isc_temp].marker_spacecraft, color = satColors[isc], s = 200, zorder = 4, label = label_arr[isc])
        else:
            spacecraft_list[isc_temp].point_plot = m.scatter(spacecraft_list[isc_temp].x, spacecraft_list[isc_temp].y,  marker=spacecraft_list[isc_temp].marker_spacecraft, color = satColors[isc], s = 200, zorder = 4, label = str(isc + 1))


        if ( elev_sc[isc, istep*dt_index_sc] >= elev_gs[igs] ):
            azim_elev_text.append( ax_2d.text(-135., 50-10*len(list_sc_in), format(elev_sc[isc, istep*dt_index_sc], ".0f") + ", " + format(azim_sc[isc, istep*dt_index_sc], ".0f"), fontsize = fontsize_plot, weight = 'normal', horizontalalignment = 'right', verticalalignment = 'top', color = satColors[isc]) )
            list_sc_in.append(isc_temp)
    nb_sc_in = len(list_sc_in)

    #date_map = ax_2d.text((lon_min + lon_max)/2.,lat_min + (lat_max - lat_min)/30.,date[istep*dt_index_sc][:16]+ ':00', fontsize = fontsize_plot, weight = 'bold', horizontalalignment = 'center') # cheating with ':00'
    
    if (istep == istep_start):
        legend = ax_2d.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="", fontsize = fontsize_plot,handlelength=0, handletextpad=0)
        #legend.get_title().set_fontsize(str(fontsize_plot))

        for isc_temp in range(len(legend.get_texts())):
            if is_cygnss == '1':
                isc = label_arr_conversion[isc_temp]
            else:
                isc = isc_temp
            legend.get_texts()[isc_temp].set_color(satColors[isc]) # set the label the same color as the plot
            legend.legendHandles[isc_temp].set_visible(False) # hide the line in the label



        
        # if there was a ground station file in the main input file
        # draw the contact circle on the Earth (projetion of cone in which the sc is in sight)
        if istep == istep_start:
            if filename_ground_station != "":
                for igs in range(nb_gs):
                    # assume that the altitude of the sc is constant and that it's the same for all sc
                    radius_gs_contact = gs_radius(alt[0, 0], elev_gs[igs])#!!!!!!!elev_gs[igs])
                    m.tissot(lon_gs[igs], lat_gs[igs], radius_for_tissot(radius_gs_contact), 100, fill=False, edgecolor='grey')
                    radius_min_max_elev = gs_radius(alt[0, 0], min_max_elev)#!!!!!!!elev_gs[igs])
                    m.tissot(lon_gs[igs], lat_gs[igs], radius_for_tissot(radius_min_max_elev), 100, fill=False, edgecolor='grey')
                    x, y =  m(lon_gs[igs], lat_gs[igs])
                    #m.scatter(x, y,  marker='*', color = 'grey', s = 100, zorder = 4) # position of gs


    fig_save_name = 'ani/' + str(istep) + '_' + str(nb_steps_ani_sc-1) + '.png'
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  
    for isc in range(nb_sc):
        spacecraft_list[isc].point_plot.remove()
    line_time_plot.remove()
    del  line_time_plot
    
    # Remove the elev azim of each sc in sight
    for isc_in in range(nb_sc_in):
        azim_elev_text[isc_in].remove()
    
    # if istep ==  1:
    #     raise Exceptio

    #raise Exception

video_name = input_filename.replace(".txt", "") + "_" + date_start_str.replace("-", "_").replace(":", "_") +  "_to_" +  date_stop_str.replace("-", "_").replace(":", "_") + ".mp4"
os.system('ffmpeg -y -r 30 -i ani/%d_' +  str(nb_steps_ani_sc-1) + '.png -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -vcodec libx264 -pix_fmt yuv420p ' + video_name)

#os.system('scp ' + video_name + " desk:")



# label_arr = ['FM05', 'FM04', 'FM02', 'FM01', 'FM08', 'FM06', 'FM07', 'FM03']
# label_arr_conversion = [3, 2, 7, 1, 0, 5, 6, 4]

#         for isc_temp in range(nb_sc):
#             isc = label_arr_conversion[isc_temp]

