


import matplotlib
matplotlib.use("Agg") # without this line, when running this script from a cronjob we get an error "Unable to access the X Display, is $DISPLAY set properly?"
import os
import sys 
sys.path.append("../../kalman/spock_development_new_structure_kalman_dev/srcPython")
from read_input_file import *
from matplotlib import pyplot as plt
from find_in_read_input_order_variables import *
from read_spec_spock import *
import matplotlib.gridspec as gridspec
from mpl_toolkits.basemap import Basemap, shiftgrid
from collections import *
from matplotlib import colors
import matplotlib.ticker as ticker
import pickle
input_filename = sys.argv[1]
# PARAMETERS TO SET UP BEFORE RUNNING THIS SCRIPT
lat_grid_center_array = [0, 5, 10, 15, 20, 25, 30]#,40,50,60,70]#,80]  # !!!!!! should be [0, 10, 20, 30]
pickle_root = input_filename.replace(".txt","")
rlat_width = 500 # latitude width of the grid, in km
rlon_width = 500 # longitude width of the grid, in km
# end of PARAMETERS TO SET UP BEFORE RUNNING THIS SCRIPT

re = 6371.0 # mean Earth radius 
lat_grid_center_array = np.array(lat_grid_center_array) * np.pi / 180.
width_cell_array = [5, 10, 15, 20, 25] # in km
coverage_array = [70, 80, 90, 95, 99] # in pecentage in ASCENDING ORDER


color_array = ['k','cornflowerblue','r','g', 'm', 'gold', 'cyan', 'fuchsia', 'lawngreen', 'darkgray', 'green', 'chocolate']

lon_grid_center_array = np.arange(5, 360, 12) * np.pi / 180
nb_type_cell = len(width_cell_array)
nb_coverage = len(coverage_array)

width_cell_array = np.array(width_cell_array)
coverage_array = np.array(coverage_array)
    


# Read the ECEF position of the specular points. Note: if less tha 4 spec for a time then ecef components are equal to 99999999
#lon_spec, lat_spec, ecef_spec = read_spec_spock(input_filename)

lon_spec = lon_spec * np.pi / 180.
lat_spec = lat_spec * np.pi / 180.

# Sel<ecting only the specular ponts in the window (also called grid) defined by lon/lat_grid_center and lon/rlat_width, count the number of specular points in each cell (defined by width_cell) as a function of time
nb_lat_center = len(lat_grid_center_array)
nb_lon_center = len(lon_grid_center_array)
nb_time = ecef_spec.shape[2] # !!!!!!!!! remove "/ 4"
nb_sc = ecef_spec.shape[1]
nb_spec = ecef_spec.shape[0]
time_to_reach_coverage = np.zeros([nb_lat_center, nb_lon_center, nb_type_cell, nb_coverage]) - 1
#nb_cell_covered = np.zeros([nb_lat_center, nb_lon_center, nb_type_cell,  nb_time])
cell_array = []
#nb_cell_covered_average_over_lon = np.zeros([nb_lat_center, nb_type_cell, nb_time])
time_to_reach_coverage_average_over_lon = np.zeros([nb_lat_center, nb_type_cell, nb_coverage])

-
for itype in range(0,nb_type_cell): # !!!!!!!!!!
    #print itype, nb_type_cell-1
    width_cell = width_cell_array[itype]
    for ilat_center in range(0,nb_lat_center):# !!!!!!!!!!!!!
        lat_grid_center = lat_grid_center_array[ilat_center] # latitude of the center of the grid
        rlat_min_grid = re * lat_grid_center - rlat_width / 2.
        rlat_max_grid = re * lat_grid_center + rlat_width / 2.
        nb_cell_lat = (int) ( rlat_width / width_cell ) #( ( lat_max_grid - lat_min_grid ) / width_cell )
        rlat_max_grid_cell = rlat_min_grid + nb_cell_lat * width_cell # latitude of the cell of the grid that correspond to the highest latitude. 
        for ilon_center in range(nb_lon_center): #!!!!!!!!!!!

            lon_grid_center = lon_grid_center_array[ilon_center]
            rlon_min_grid = re * lon_grid_center - rlon_width / 2.
            rlon_max_grid = re * lon_grid_center + rlon_width / 2. 
            nb_cell_lon = (int) ( ( rlon_width ) / width_cell ) 
            rlon_max_grid_cell = rlon_min_grid + nb_cell_lon * width_cell # longitude of the cell of the grid that correspond to the highest longitude.
            nb_cell_in_grid = nb_cell_lon * nb_cell_lat
            where_in_grid = np.where(( re * np.cos(lat_spec[:,:,:]) * lon_spec[:, :, :] >= rlon_min_grid ) & ( re * np.cos(lat_spec[:,:,:]) * lon_spec[:, :, :] < rlon_max_grid_cell ) & ( re * lat_spec[:, :, :] >= rlat_min_grid ) & ( re * lat_spec[:, :, :] < rlat_max_grid_cell  ) & ( lat_spec[:, :, :] < 9999999 ) )
            indices_time_sorted = [i[0] for i in sorted(enumerate(where_in_grid[2]), key=lambda x:x[1])]
            which_spec = where_in_grid[0][indices_time_sorted]#[x for _,x in sorted(zip(where_in_grid[2],where_in_grid[0]))]#where_in_grid[0]
            which_sc = where_in_grid[1][indices_time_sorted]#[x for _,x in sorted(zip(where_in_grid[2],where_in_grid[1]))]#where_in_grid[1]
            which_time = where_in_grid[2][indices_time_sorted] #[x for _,x in sorted(zip(where_in_grid[2],where_in_grid[2]))]#where_in_grid[2]
            nb_time_spec_in_grid = len(which_time)
            icoverage = 0
            print itype, nb_type_cell-1, ilat_center, nb_lat_center-1, ilon_center,nb_lon_center-1,nb_time_spec_in_grid
            icell_save = []
            cell_ilon_ilat_itype = np.zeros([nb_cell_lat, nb_cell_lon])
            nb_cell_filled = np.zeros([nb_time])

            for itime in range( nb_time_spec_in_grid ):
                if itime > 0:
                    nb_cell_filled[which_time[itime-1]+1:which_time[itime]+1] = nb_cell_filled[which_time[itime-1]]


                lon_spec_in_grid = lon_spec[which_spec[itime], which_sc[itime], which_time[itime]]  
                lat_spec_in_grid = lat_spec[which_spec[itime], which_sc[itime], which_time[itime]]
                icell_lat = (int) ( ( re * lat_spec_in_grid - rlat_min_grid ) / width_cell )
                icell_lon = (int) ( ( re * np.cos(lat_spec_in_grid) * lon_spec_in_grid - rlon_min_grid ) / width_cell )


                if cell_ilon_ilat_itype[icell_lat, icell_lon] == 0: # if this cell has not been filled yet
                    nb_cell_filled[which_time[itime]] = nb_cell_filled[which_time[itime-1]] + 1
                    cell_ilon_ilat_itype[icell_lat, icell_lon] = 1

                    if icoverage < nb_coverage:
                        if nb_cell_filled[which_time[itime]] >= coverage_array[icoverage]/100. * nb_cell_in_grid:
                            time_to_reach_coverage[ilat_center, ilon_center, itype, icoverage] = which_time[itime] # since the specular file is every second, itime is moving one second by one second
                            icoverage = icoverage + 1

            nb_cell_filled[which_time[itime]+1:] = nb_cell_filled[which_time[itime]]
#            nb_cell_covered[ilat_center, ilon_center, itype, :] = nb_cell_filled * 100. / nb_cell_in_grid                    
            

#        nb_cell_covered_average_over_lon[ilat_center, itype, :] =  np.mean( nb_cell_covered[ilat_center, :, itype, :], axis = 0 )
        time_to_reach_coverage_average_over_lon[ilat_center, itype, :] = np.mean( time_to_reach_coverage[ilat_center, :, itype, :], axis = 0 )


#pickle.dump(nb_cell_covered_average_over_lon, open( "/raid4/cbv/coverage_temporal_spatial_relation/pickle/" + pickle_root + "_nb_cell_covered_average_over_lon", "w"))
pickle.dump(time_to_reach_coverage_average_over_lon, open( "/raid4/cbv/coverage_temporal_spatial_relation/pickle/" + pickle_root + "_time_to_reach_coverage_average_over_lon.pickle", "w"))


raise Exception

## Parameters for the figure
height_fig = 11.  # the width is calculated as height_fig * 4/3.
fontsize_plot = 20 
ratio_fig_size = 4./3


# 2D visualization
itype = 2#3 # grid bin type
width_cell = width_cell_array[itype]
lat_grid_center_array = np.array(lat_grid_center_array)
ilat_center = np.where(lat_grid_center_array == 30)[0][0]#2
ilon_center = 9
lat_grid_center = lat_grid_center_array[ilat_center]
lon_grid_center = lon_grid_center_array[ilon_center]
lat_min_grid = lat_grid_center - lat_width / 2.
lat_max_grid = lat_grid_center + lat_width / 2.
nb_cell_lat = (int) ( ( lat_max_grid - lat_min_grid ) / width_cell )
lat_max_grid_cell = lat_min_grid + nb_cell_lat * width_cell # latitude of the cell of the grid that correspond to the highest latitude. 
lon_min_grid = (lon_grid_center - lon_width / 2.)%360
lon_max_grid = (lon_grid_center + lon_width / 2. )%360
nb_cell_lon = (int) ( ( lon_max_grid - lon_min_grid ) / width_cell ) 
lon_max_grid_cell = lon_min_grid + nb_cell_lon * width_cell # longitude of the cell of the grid that correspond to the highest longitude.
nb_cell_in_grid = nb_cell_lon * nb_cell_lat
cell_array_type_lon_lat_cumul = np.zeros([nb_time, nb_cell_lat, nb_cell_lon])# +1 for safety
cell_array_type_lon_lat = np.zeros([nb_time, nb_cell_lat, nb_cell_lon])# +1 for safety


where_in_grid = np.where(( lon_spec[:, :, :] >= lon_min_grid ) & ( lon_spec[:, :, :] < lon_max_grid_cell ) & ( lat_spec[:, :, :] >= lat_min_grid ) & ( lat_spec[:, :, :] < lat_max_grid_cell  ) & ( lat_spec[:, :, :] < 9999999 ) )
indices_time_sorted = [i[0] for i in sorted(enumerate(where_in_grid[2]), key=lambda x:x[1])]
which_spec = where_in_grid[0][indices_time_sorted]#[x for _,x in sorted(zip(where_in_grid[2],where_in_grid[0]))]#where_in_grid[0]
which_sc = where_in_grid[1][indices_time_sorted]#[x for _,x in sorted(zip(where_in_grid[2],where_in_grid[1]))]#where_in_grid[1]
which_time = where_in_grid[2][indices_time_sorted] #[x for _,x in sorted(zip(where_in_grid[2],where_in_grid[2]))]#where_in_grid[2]
nb_time_spec_in_grid = len(which_time)
cell_ilon_ilat_itype = np.zeros([nb_cell_lat, nb_cell_lon])
nb_cell_filled = np.zeros([nb_time])

for itime in range( nb_time_spec_in_grid ):
    print itime, nb_time_spec_in_grid
    if itime > 0:
        cell_array_type_lon_lat_cumul[which_time[itime-1]+1:which_time[itime]+1, :, :] = cell_array_type_lon_lat_cumul[which_time[itime-1], :, :]

    lon_spec_in_grid = lon_spec[which_spec[itime], which_sc[itime], which_time[itime]]  
    lat_spec_in_grid = lat_spec[which_spec[itime], which_sc[itime], which_time[itime]]
    icell_lat = (int) ( ( lat_spec_in_grid - lat_min_grid ) / width_cell )
    icell_lon = (int) ( ( lon_spec_in_grid - lon_min_grid ) / width_cell )


    if cell_ilon_ilat_itype[icell_lat, icell_lon] == 0: # if this cell has not been filled yet
        cell_ilon_ilat_itype[icell_lat, icell_lon] = 1

        cell_array_type_lon_lat_cumul[which_time[itime], icell_lat, icell_lon] =  1


cell_array_type_lon_lat_cumul[which_time[itime]+1:] = cell_array_type_lon_lat_cumul[which_time[itime]]

y_label = 'Latitude '+ u'(\N{DEGREE SIGN})'
x_label = 'Longitude '+ u'(\N{DEGREE SIGN})'
cmap = colors.ListedColormap(['azure', 'lightskyblue'])

#itime = 9 * 3600-1
itime_count = -1
for itime in np.arange( 0,  3 * 24 *3600 , 3600):
#for itime in np.arange( 0, 2, 1):
    itime_count = itime_count + 1
    print itime,  12 * 3600
    fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
    fig.suptitle('', y = 0.96,fontsize = (int)(fontsize_plot*1.1), weight = 'bold',)
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold
    gs = gridspec.GridSpec(1, 1)
    gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
    ax_2d = fig.add_subplot(gs[0, 0])


    nb_days_from_start = itime / 3600 / 24
    time_since_start_day = (int) ( np.floor(itime / 3600. / 24) )
    time_since_start_hour =(int) (  np.floor(  (itime / 3600. / 24 - time_since_start_day )*24) )
    time_since_start_min = (int) ( np.floor(( (itime / 3600. / 24 - time_since_start_day )*24 - time_since_start_hour ) * 60) )
    time_since_start_sec = (int) ( np.round( ( ( (itime / 3600. / 24 - time_since_start_day )*24 - time_since_start_hour ) * 60 - time_since_start_min ) * 60 ) )
    time_since_start = str(time_since_start_day) + 'd ' + str(time_since_start_hour) + 'h' + str(time_since_start_min) + "'"  + str(time_since_start_sec) + "''"
#    percentage_covered = nb_cell_covered[ilat_center, ilon_center, itype, itime]

    ax_2d_title = '2D visualization of coverage (lon = ' + str(lon_grid_center) + u'\N{DEGREE SIGN}'+ ', lat = ' + str(lat_grid_center) + u'\N{DEGREE SIGN})\n' + time_since_start + "- Coverage: " + format(percentage_covered, ".1f") + "%"
    
    ax_2d.set_title(ax_2d_title, weight = 'bold', fontsize  = (int)(fontsize_plot*1.1), y = 1.0)
    ax_2d.set_ylabel(y_label, weight = 'bold', fontsize  = fontsize_plot)
    ax_2d.set_xlabel(x_label, weight = 'bold', fontsize  = fontsize_plot)

    [i.set_linewidth(2) for i in ax_2d.spines.itervalues()] # change the width of the frame of the figure
    ax_2d.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
    plt.rc('font', weight='bold') ## make the labels of the ticks in bold

    # if lon_min_grid > 180:
    #     lon_min_grid_converted = lon_min_grid - 360
    # else:
    #     lon_min_grid_converted = lon_min_grid 
    # if lon_max_grid > 180:
    #     lon_max_grid_converted = lon_max_grid - 360
    # else:
    #     lon_max_grid_converted = lon_max_grid
    lon_min_grid_converted = lon_min_grid 
    lon_max_grid_converted = lon_max_grid 
    m = Basemap( projection       = 'cyl',
                 llcrnrlon        =  lon_min_grid_converted, #Lower Left  CoRNeR Longitude
                 urcrnrlon        =  lon_max_grid_converted , #Upper Right CoRNeR Longitude
                 llcrnrlat        = lat_min_grid  , #Lower Left  CoRNeR Latitude
                 urcrnrlat        = lat_max_grid,   #Upper Right CoRNeR Latitude
                 resolution       = 'i'  , # 'i', 'h'
                 suppress_ticks   = False,
                 ax = ax_2d,
                 )

    lon_arr = np.arange(lon_min_grid_converted,lon_max_grid_converted,width_cell)
    lat_arr = np.arange(lat_min_grid,lat_max_grid,width_cell)

    # draw grid
    data = cell_array_type_lon_lat_cumul[itime, : ,:]

    m.pcolormesh(lon_arr, lat_arr, data, cmap=cmap)

    specular_list = []
    point = namedtuple('point', ['x', 'y'])
    color = namedtuple('color', 'red green blue')
    specular = namedtuple('specular',('name',) +  point._fields  + color._fields + ('point_plot',))

    for isc in range(nb_sc):
        # Add on plot the specular points over one orbit
        for k in range(nb_spec):
            specular_list.append(specular)
            if itime > 3600:
                specular_list[k+isc*nb_spec].x, specular_list[k+isc*nb_spec].y =  m(lon_spec[k,isc,itime-3600:itime], lat_spec[k,isc,itime-3600:itime])
            else:
                specular_list[k+isc*nb_spec].x, specular_list[k+isc*nb_spec].y =  m(lon_spec[k,isc,:itime], lat_spec[k,isc,:itime])
            specular_list[k+isc*nb_spec].point_plot = m.scatter(specular_list[k+isc*nb_spec].x, specular_list[k+isc*nb_spec].y, marker='o', s = 50, color = 'b')


#    date_map = ax_2d.text((lon_min_grid_converted + lon_max_grid_converted)/2.,lat_min_grid + (lat_max_grid - lat_min_grid)/30., time_since_start + "\nCoverage: " + format(percentage_covered, ".1f") + "%", fontsize = fontsize_plot, weight = 'bold', horizontalalignment = 'center')




    m.drawcoastlines(linewidth=0.7, color='blue')
    m.drawmeridians(np.arange(lon_min_grid_converted,lon_max_grid_converted,width_cell) )
    m.drawparallels(np.arange(lat_min_grid,lat_max_grid,width_cell) )

    fig_save_name = '/Users/cbv/coverage_temporal_spatial_relation/plot/2d_visu/' + input_filename.replace(".txt", "") + '_2d_coverage_itime_' + str(itime_count) + '.png'
    fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')


    
raise Exception
# AVERAGE OVER ALL LONGITUDES

# Coverage vs time for different bin sizes
#for ilat_center in range(nb_lat_center):#for ilat_center in range(nb_lat_center): # !!!!!!!!!!

ilat_center = np.where(lat_grid_center_array == 30)[0][0]
lat_grid_center = lat_grid_center_array[ilat_center]
fig_title = 'Long. avg. temporal coverage VS time for different spatial resolutions - Grid at latitude ' + str(lat_grid_center) + u'\N{DEGREE SIGN}'
y_label = 'Coverage (%)'
x_label = 'Time (days)'
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

# for itype in range(nb_type_cell):#for itype in range(nb_type_cell): # !!!!!!!
#     ax.plot(np.arange(0, nb_time, 1) / 3600. / 24., nb_cell_covered_average_over_lon[ilat_center, itype, :],  linewidth = 4, color = color_array[itype], label = str(width_cell_array[itype]) + u'\N{DEGREE SIGN}')


ax.minorticks_off()
xticks = np.arange(0,np.max(nb_time) / 3600. / 24., 1)
xticks_label = []
for i in range(len(xticks)):
        xticks_label.append( format( xticks[i], ".0f" ) )
ax.xaxis.set_ticks(xticks)
ax.xaxis.set_ticklabels(xticks_label, fontsize = fontsize_plot)
    
ax.set_xlim([0, np.max(nb_time) / 3600. / 24.])
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="Width of bins", fontsize = fontsize_plot)
legend.get_title().set_fontsize(str(fontsize_plot))
fig_save_name = '/Users/cbv/coverage_temporal_spatial_relation/plot/' + input_filename.replace(".txt", "") + '_coverage_vs_time_latitude_' + str(lat_grid_center).replace(".","_") + '_average_over_lon.pdf'
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  


# Width of bin vs Time to reach coverage goal for different latitude center of the window, for one coverage
icoverage = 0
fig_title = 'Long. avg. spatial VS temporal coverage for different latitudes of the grid - Coverage goal ' + str(coverage_array[icoverage]) + '%'
y_label = 'Width of bin (lat/lon deg)'
x_label = 'Time to reach coverage goal (days)'

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

max_x = 0
for ilat_center in range(nb_lat_center): # !!!!!!!!!!!# a value is negative if the coverage never reached the coverage goal. SO we don't want it on the plot
    ax.scatter(time_to_reach_coverage_average_over_lon[ilat_center, np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage]/3600. / 24. > 0)[0], icoverage]/3600. / 24., width_cell_array[np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage]/3600. / 24. > 0)[0]], linewidth = 2, color = color_array[ilat_center], marker = 'o', s = 100)
    ax.loglog(time_to_reach_coverage_average_over_lon[ilat_center, np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage]/3600. / 24. > 0)[0], icoverage]/3600. / 24., width_cell_array[np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage]/3600. / 24. > 0)[0]], linewidth = 3, color = color_array[ilat_center], label = str(lat_grid_center_array[ilat_center]) + u'\N{DEGREE SIGN}')
    if np.max(time_to_reach_coverage_average_over_lon[ilat_center, np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage]/3600. / 24. > 0)[0], icoverage]/3600. / 24.) > max_x:
        max_x = np.max(time_to_reach_coverage_average_over_lon[ilat_center, np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage]/3600. / 24. > 0)[0], icoverage]/3600. / 24.)

ax.minorticks_off()
xticks = np.arange(0,np.max(nb_time) / 3600. / 24., 1)
xticks_label = []
for i in range(len(xticks)):
        xticks_label.append( format( xticks[i], ".0f" ) )
ax.xaxis.set_ticks(xticks)
ax.xaxis.set_ticklabels(xticks_label, fontsize = fontsize_plot)
        
ylim_save = [ax.get_ylim()[0], ax.get_ylim()[1]]
yticks = width_cell_array
yticks_label = []
for i in range(len(yticks)):
    yticks_label.append( str( width_cell_array[i] ) )
ax.yaxis.set_ticks(yticks)
ax.yaxis.set_ticklabels(yticks_label, fontsize = fontsize_plot)#, rotation='vertical')

ax.set_xlim([0, max_x*1.1])
ax.set_ylim(ylim_save)

legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="Grid lat.", fontsize = fontsize_plot)
legend.get_title().set_fontsize(str(fontsize_plot))

fig_save_name = '/Users/cbv/coverage_temporal_spatial_relation/plot/' + input_filename.replace(".txt", "") + '_diff_latitude_coverage_' + str(coverage_array[icoverage]).replace(".","_") + '_average_over_lon.pdf'
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  


# Width of bin vs Time to reach coverage goal for different coverage goals, at one latittude
ilat_center = np.where(lat_grid_center_array == 30)[0][0]
lat_grid_center = lat_grid_center_array[ilat_center]
fig_title = 'Long. avg. spatial VS temporal coverage for different coverage goals - Grid at latitude ' + str(lat_grid_center) + u'\N{DEGREE SIGN}'
y_label = 'Width of bin (lat/lon deg)'
x_label = 'Time to reach coverage goal (days)'
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

max_x = 0
for icoverage in range(nb_coverage):  # a value is negative if the coverage never reached the coverage goal. SO we don't want it on the plot        
    ax.scatter(time_to_reach_coverage_average_over_lon[ilat_center, np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage] > 0)[0], icoverage]/3600. / 24., width_cell_array[np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage] > 0)[0]], linewidth = 2, color = color_array[icoverage], marker = 'o', s = 100)
    ax.loglog(time_to_reach_coverage_average_over_lon[ilat_center, np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage] > 0)[0], icoverage]/3600. / 24., width_cell_array[np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage] > 0)[0]], linewidth = 3, color = color_array[icoverage], label = str(coverage_array[icoverage]) + "%")
    if np.max(time_to_reach_coverage_average_over_lon[ilat_center, np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage] > 0)[0], icoverage]/3600. / 24.) > max_x:
        max_x = np.max(time_to_reach_coverage_average_over_lon[ilat_center, np.where(time_to_reach_coverage_average_over_lon[ilat_center, :, icoverage] > 0)[0], icoverage]/3600. / 24.)



ax.minorticks_off()
xticks = np.arange(0,np.max(nb_time) / 3600. / 24., 1)
xticks_label = []
for i in range(len(xticks)):
        xticks_label.append( format( xticks[i], ".0f" ) )
ax.xaxis.set_ticks(xticks)
ax.xaxis.set_ticklabels(xticks_label, fontsize = fontsize_plot)
        
ylim_save = [ax.get_ylim()[0], ax.get_ylim()[1]]
yticks = width_cell_array
yticks_label = []
for i in range(len(yticks)):
    yticks_label.append( str( width_cell_array[i] ) )
ax.yaxis.set_ticks(yticks)
ax.yaxis.set_ticklabels(yticks_label, fontsize = fontsize_plot)#, rotation='vertical')

ax.set_xlim([0, max_x*1.1])
ax.set_ylim(ylim_save)


    
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="Cov. goal", fontsize = fontsize_plot)
legend.get_title().set_fontsize(str(fontsize_plot))

    
fig_save_name = '/Users/cbv/coverage_temporal_spatial_relation/plot/' + input_filename.replace(".txt", "") + '_diff_coverage_latitude_' + str(lat_grid_center).replace(".","_") + '_average_over_lon.pdf'
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  


raise Exception
# ONE LONGITUDE IN PARTICULAR
# Coverage vs time for different latitude center of the grid
ilat_center = 3
ilon_center = 0
lat_grid_center = lat_grid_center_array[ilat_center]
fig_title = 'Temporal coverage VS time for different spatial resolutions - Grid at latitude ' + str(lat_grid_center) + u'\N{DEGREE SIGN}'
y_label = 'Coverage (%)'
x_label = 'Time (days)'
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

# for itype in range(nb_type_cell):
#     ax.plot(np.arange(0, nb_time, 1) / 3600. / 24., nb_cell_covered[ilat_center, itype, :],  linewidth = 4, color = color_array[itype], label = str(width_cell_array[itype]) + u'\N{DEGREE SIGN}')
    
ax.set_xlim([0, np.max(nb_time) / 3600. / 24.])
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="Width of bins", fontsize = fontsize_plot)
legend.get_title().set_fontsize(str(fontsize_plot))
fig_save_name = '/Users/cbv/coverage_temporal_spatial_relation/plot/coverage_vs_time_latitude_' + str(lat_grid_center).replace(".","_") + '.pdf'
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  


# Width of bin vs Time to reach coverage goal for different latitude center of the window, for one coverage
icoverage = 3
fig_title = 'Spatial VS temporal coverage for different latitudes of the grid - Coverage goal ' + str(coverage_array[icoverage]) + '%'
y_label = 'Width of bin (lat/lon deg)'
x_label = 'Time to reach coverage goal (days)'
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

for ilat_center in range(nb_lat_center): # a value is negative if the coverage never reached the coverage goal. SO we don't want it on the plot
    ax.scatter(time_to_reach_coverage[ilat_center, np.where(time_to_reach_coverage[ilat_center, :, icoverage]/3600. / 24. > 0)[0], icoverage]/3600. / 24., width_cell_array[np.where(time_to_reach_coverage[ilat_center, :, icoverage]/3600. / 24. > 0)[0]], linewidth = 2, color = color_array[ilat_center], marker = 'o', s = 100)
    ax.plot(time_to_reach_coverage[ilat_center, np.where(time_to_reach_coverage[ilat_center, :, icoverage]/3600. / 24. > 0)[0], icoverage]/3600. / 24., width_cell_array[np.where(time_to_reach_coverage[ilat_center, :, icoverage]/3600. / 24. > 0)[0]], linewidth = 3, color = color_array[ilat_center], label = str(lat_grid_center_array[ilat_center]) + u'\N{DEGREE SIGN}')

legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="Cov. goal", fontsize = fontsize_plot)
legend.get_title().set_fontsize(str(fontsize_plot))
ax.set_xlim([0, np.max(nb_time) / 3600. / 24.])
    
fig_save_name = '/Users/cbv/coverage_temporal_spatial_relation/plot/diff_latitude_coverage_' + str(coverage_array[icoverage]).replace(".","_") + '.pdf'
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  


# Width of bin vs Time to reach coverage goal for different coverage goals, at one latittude
lat_grid_center = lat_grid_center_array[ilat_center]
fig_title = 'Spatial VS temporal coverage for different coverage goals - Grid at latitude ' + str(lat_grid_center) + u'\N{DEGREE SIGN}'
y_label = 'Width of bin (lat/lon deg)'
x_label = 'Time to reach coverage goal (days)'
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

for icoverage in range(nb_coverage):  # a value is negative if the coverage never reached the coverage goal. SO we don't want it on the plot        
    ax.scatter(time_to_reach_coverage[ilat_center, np.where(time_to_reach_coverage[ilat_center, :, icoverage] > 0)[0], icoverage]/3600. / 24., width_cell_array[np.where(time_to_reach_coverage[ilat_center, :, icoverage] > 0)[0]], linewidth = 2, color = color_array[icoverage], marker = 'o', s = 100)
    ax.plot(time_to_reach_coverage[ilat_center, np.where(time_to_reach_coverage[ilat_center, :, icoverage] > 0)[0], icoverage]/3600. / 24., width_cell_array[np.where(time_to_reach_coverage[ilat_center, :, icoverage] > 0)[0]], linewidth = 3, color = color_array[icoverage], label = str(coverage_array[icoverage]) + "%")

legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints = 1,  title="Cov. goal", fontsize = fontsize_plot)
legend.get_title().set_fontsize(str(fontsize_plot))
ax.set_xlim([0, np.max(nb_time) / 3600. / 24.])
    
fig_save_name = '/Users/cbv/coverage_temporal_spatial_relation/plot/diff_coverage_latitude_' + str(lat_grid_center).replace(".","_") + '.pdf'
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  








                
# for ilat_center in range(nb_lat_center):
#     cell_array_lat = []
#     for ilon_center in range(nb_lon_center):
#         lon_grid_center = lon_grid_center_array[ilon_center]
#         if lon_grid_center < 0:
#             lon_grid_center  = lon_grid_center + 360 # convert to from 0 to + 360

#         lat_grid_center = lat_grid_center_array[ilat_center] # latitude of the center of the grid
#         lat_min_grid = lat_grid_center - lat_width / 2.
#         lat_max_grid = lat_grid_center + lat_width / 2.
#         lon_min_grid = (lon_grid_center - lon_width / 2.)%360
#         lon_max_grid = (lon_grid_center + lon_width / 2. )%360
#         cell_array_lon_lat = []
#         for itype in range(nb_type_cell):
#             print 'type cell ' + str(itype) + ' out of ' + str( nb_type_cell - 1 ) + ' / ilon ' + str(ilon_center) + ' out of ' + str(nb_lon_center-1) + ' / ilat ' + str(ilat_center)  + ' out of ' + str(nb_lat_center-1) 
#             #itype = 1
#             #icoverage = 0
#             width_cell = width_cell_array[itype]

#             nb_cell_lon = (int) ( ( lon_max_grid - lon_min_grid ) / width_cell ) 
#             nb_cell_lat = (int) ( ( lat_max_grid - lat_min_grid ) / width_cell ) 
#             nb_cell_in_grid = nb_cell_lon * nb_cell_lat
#             cell_array_type_lon_lat = np.zeros([nb_cell_lat+1, nb_cell_lon+1])# +1 for safety
#             icell_save = []
#             icoverage = 0
#             for itime in range(nb_time):
#                 #print itime, nb_time
#                 for isc in range(nb_sc):
#                     for ispec in range(nb_spec):
#                         if ( ( lon_spec[ispec, isc, itime] >= lon_min_grid ) & ( lon_spec[ispec, isc, itime] < lon_max_grid ) & ( lat_spec[ispec, isc, itime] >= lat_min_grid ) & ( lat_spec[ispec, isc, itime] < lat_max_grid  ) & ( lat_spec[ispec, isc, itime] < 9999999 ) ): # if the specular point in the window we're looking at
#                         #if ( ( lon_spec[ispec, isc, itime] >= lon_min_grid ) & ( lon_spec[ispec, isc, itime] < lon_max_grid - width_cell ) & ( lat_spec[ispec, isc, itime] >= lat_min_grid ) & ( lat_spec[ispec, isc, itime] < lat_max_grid - width_cell ) & ( lat_spec[ispec, isc, itime] < 9999999 ) ): # if the specular point in the window we're looking at
#                             icell_lat = (int) ( ( lat_spec[ispec, isc, itime] - lat_min_grid ) / width_cell )
#                             icell_lon = (int) ( ( lon_spec[ispec, isc, itime] - lon_min_grid ) / width_cell )
#                             if ([icell_lat, icell_lon] in icell_save) == False:
#                                 icell_save.append([icell_lat, icell_lon])
#                             cell_array_type_lon_lat[icell_lat, icell_lon] = cell_array_type_lon_lat[icell_lat, icell_lon] + 1

#                 # nb_cell_covered_per_lat = np.zeros([nb_cell_lat])
#                 # for icell_lat in range(nb_cell_lat):
#                 #     nb_cell_covered_per_lat[icell_lat] = len(np.where( cell_array_type_lon_lat[icell_lat, :] > 0)[0])
#                 nb_cell_covered[ilat_center, ilon_center, itype, itime] = len(icell_save) *100. / nb_cell_in_grid   #np.sum( nb_cell_covered_per_lat) / nb_cell_in_grid * 100
#                 if icoverage < nb_coverage:
#                     if  nb_cell_covered[ilat_center, ilon_center, itype, itime] >= coverage_array[icoverage]:
#                         time_to_reach_coverage[ilat_center, ilon_center, itype, icoverage] = itime # since the specular file is every second, itime is moving one second by one second
#                         icoverage = icoverage + 1

#             cell_array_lon_lat.append( cell_array_type_lon_lat )
#         cell_array_lat.append( cell_array_lon_lat )
#     cell_array.append( cell_array_lat ) 
