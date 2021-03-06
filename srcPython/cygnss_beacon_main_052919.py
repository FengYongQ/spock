# For a given interval of time and FM, this script runs all steps necessary to select 2 PRNs.
# Inputs:
# - start_time_const: UTC start time of the full constellation overpass (midnight MT -> 6 am UTC) (YYYY-MM-DDTHH:MM:SS)
# - end_time_const: UTC end time of the full constellation overpass (6 am MT -> 12 pm UTC) (YYYY-MM-DDTHH:MM:SS)
# - dir_run_spock: path where the SpOCK outputs file should go
# Outputs:
# - the two PRNs that should be selected for the csv files inputs of the waveform generator
# Assumptions:
# - cygnss_main_satbop.py has been run on Windows first and the overpass schedule copied to srbwks2014-0008 in work/spockOut/beacon/overpassSchedule
# - the overpass schedule must include all 8 overpasses (one per FM)

import sys
sys.path.append('/Users/cbv/work/spock/srcPython')
import os
from cygnss_read_spock_spec_bin import *
from read_input_file import *
from datetime import datetime, timedelta
import numpy as np
from numpy import unravel_index
from matplotlib import pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches



try:
    operation = sys.argv[1] # 'predict', 'select'. If 'predict' then run SpOCK to predict SP locations. If 'select' then run the algorithm to select the 2 PRNs for each FM overpass (meaning that 'predict' should have been run at some point before)
except IndexError:
    print "***! The argument should be 'predict' or 'select'. !***\n***! The program will stop. !***"; sys.exit();
# PARAMETERS TO SET BEFORE RUNNING THIS SCRIPT
start_time_const = '2019-05-20T17:00:00'
end_time_const = '2019-05-20T22:00:00'
dir_run_spock = '/Users/cbv/work/spockOut/beacon/'
# end of PARAMETERS TO SET BEFORE RUNNING THIS SCRIPT

color_gain = ['grey', 'blue', 'limegreen', 'red']
label_gain = ['0', '2-5', '6-10', '11-15']
handles_arr = []
for icat in range(len(label_gain)):
    handles_arr.append(mpatches.Patch(color=color_gain[icat], label=label_gain[icat]))


if dir_run_spock[-1] != '/':
    dir_run_spock = dir_run_spock + '/'

if ((operation != 'predict') & (operation != 'select')):
    print "***! The argument should be 'predict' or 'select'. !***\n***! The program will stop. !***"; sys.exit();
    
# Predict the position of the specuilar points using SpOCK
if operation == 'predict':
    os.system("python spock_cygnss_spec_parallel_beacon.py " + start_time_const + " " + end_time_const + " spec")
    sys.exit()
    

print 'For each FM, selecting the two PRNs...'
# Read the schedule of overpasses generated using sat-bop.py on Windows
filename_schedule = 'schedule_overpass_' + start_time_const[:10] + '.txt'
#os.system('scp -p desk:work/spockOut/beacon/overpassSchedule/' + filename_schedule + ' overpassSchedule/')
try:
    file_schedule = open(filename_schedule, 'r')
except IOError:
    print 'The overpass schedule file "' + filename_schedule + '" could not be found.'; sys.exit()
    
read_file_schedule = file_schedule.readlines()
nheader = 0
while read_file_schedule[nheader][:2] != '20':
    nheader = nheader + 1
start_time_fm_temp = []
end_time_fm_temp = []
cygfm_temp = []
for isc in range(8):
    start_time_fm_temp.append(read_file_schedule[isc+nheader].split()[0])
    end_time_fm_temp.append(read_file_schedule[isc+nheader].split()[1])
    cygfm_temp.append((int)(read_file_schedule[isc+nheader].split()[4]))
cygfm_temp = np.array(cygfm_temp)
index_sort_cygfm_temp = np.argsort(cygfm_temp)
start_time_fm = np.array(start_time_fm_temp)[index_sort_cygfm_temp]
end_time_fm = np.array(end_time_fm_temp)[index_sort_cygfm_temp]

# Properties of figures
height_fig = 11.  # the width is calculated as height_fig * 4/3.
fontsize_plot = 25      
ratio_fig_size = 4./3
fig_title = ''#Accuracy VS RCG
y_label = 'PRN'
x_label = 'Time (min)'

# For each FM
cygfm_to_spock_nb = [4,3,8,2,1,6,7,5] # ['41884', '41885', '41886', '41887', '41888', '41889', '41890', '41891']
first_score_fm = np.zeros([8])
second_score_fm = np.zeros([8])
for cygfm in range(1, 9):
    ## Read the specular point output files from SpOCK
    if start_time_fm[cygfm-1] != '':
        print "   Reading SpOCK specular file for FM0" + str(cygfm) + "..."
        # if cygfm == 1: # !!!!!!!! remove this if condition. It was pu here at some point because FM01 was rolled by 10 deg on Oct 31 2018, but it should not be here anymore
        #     spock_input_filename = "spock_spec_start_" + start_time_const.replace(":", "_") + "_end_" + end_time_const.replace(":", "_") + "_roll10deg.txt"
        # else:
        spock_input_filename = "spock_spec_start_" + start_time_const.replace(":", "_") + "_end_" + end_time_const.replace(":", "_") + ".txt" 
        var_in, var_in_order = read_input_file(spock_input_filename)
        dt_spock_output = var_in[find_in_read_input_order_variables(var_in_order, 'dt_output')]; 
        output_file_path_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_path_list')]; 
        output_file_name_list = var_in[find_in_read_input_order_variables(var_in_order, 'output_file_name_list')];
        gps_name_list_spock = var_in[find_in_read_input_order_variables(var_in_order, 'gps_name')];
        isc =  cygfm_to_spock_nb[cygfm-1] - 1
        spec_spock_filename = output_file_path_list[isc] + "specular_" + output_file_name_list[isc] # !!!!! before 01/24/2019
        data_spec = cygnss_read_spock_spec_bin(spec_spock_filename.replace('.txt','.bin'), gps_name_list_spock, dt_spock_output, 1) 
        date_spock = data_spec[0]; lon_spock = data_spec[1]; lat_spock = data_spec[2]; fom_spock = data_spec[3]; gps_spock = data_spec[4]; normpower_spock = data_spec[5]; x_cyg_spock = data_spec[6]; y_cyg_spock = data_spec[7]; z_cyg_spock = data_spec[8]; x_gps_spock = data_spec[9]; y_gps_spock = data_spec[10]; z_gps_spock = data_spec[11];  x_spec_spock = data_spec[12]; y_spec_spock = data_spec[13]; z_spec_spock = data_spec[14]; nb_spec_spock = data_spec[15];  el_spec_spock = data_spec[16]; az_spec_spock = data_spec[17]; el_gps_from_cyg_spock = data_spec[18];  el_spec_not_int_spock = data_spec[19]; az_spec_not_int_spock = data_spec[20]
        date_spock = np.array(date_spock); gps_spock = np.array(gps_spock); fom_spock = np.array(fom_spock)
        ## Generate a time diagram showing all PRNs selected between start_time_fm and end_time_fm

        start_time_fm_date = datetime.strptime(start_time_fm[cygfm-1], "%Y-%m-%dT%H:%M:%S")
        end_time_fm_date = datetime.strptime(end_time_fm[cygfm-1], "%Y-%m-%dT%H:%M:%S")
        inter_dur_sec = (int)((end_time_fm_date-start_time_fm_date).total_seconds())
        itime = np.where(date_spock == start_time_fm_date)[0][0]
                # BLOCK BELOW IF LOOKING AT BINOMIAL SCORE METRIC
        score_prn = np.zeros([33,33])
        gap_prn = np.zeros([33, 33])
        prn_list = []
        for iin in range(inter_dur_sec):
            for ispec in range(4):
                if ( gps_spock[itime+iin][ispec] in prn_list ) == False:
                    prn_list.append(gps_spock[itime+iin][ispec])
        prn_list = np.array(prn_list)
        nprn = len(prn_list)
        prn_list_sort = prn_list[np.argsort(prn_list)]
        for iin in range(inter_dur_sec): #array([ 7,  8, 11, 16, 18, 27])
            iout = -1
            for prn_out in prn_list_sort[:-1]: # no need to look at the last element since all combinations ahve already been considered #array([ 7,  8, 11, 16, 18, 27])
                prn_out_is_gap = 0
                #ipdb.set_trace()
                iout = iout + 1
                if len(np.where(gps_spock[itime+iin] == prn_out)[0]) > 0: #the prn is selected by SpOCK at this particular time
                    iprn_out = np.where(gps_spock[itime+iin] == prn_out)[0][0]
                    gain_out = fom_spock[itime+iin][iprn_out]
                    if gain_out == 0:# if the gain is 0, count it as a gap (since SpOCK is very different from onboard for gains of 0) 
                        prn_out_is_gap = 1
                else:
                    gain_out = 0 # !!!!!! used ot be -1 to penalize non selected prn
                    prn_out_is_gap = 1
                for prn_in in prn_list_sort[iout+1:]:
                    prn_in_is_gap = 0
                    if len(np.where(gps_spock[itime+iin] == prn_in)[0]) > 0: #the prn is selected by SpOCK at this particular time
                        iprn_in = np.where(gps_spock[itime+iin] == prn_in)[0][0]
                        gain_in = fom_spock[itime+iin][iprn_in]
                        max_gain_out_in = np.max([gain_out, gain_in])
                        if gain_in == 0: # if the gain is 0, count it as a gap (since SpOCK is very different from onboard for gains of 0)
                            prn_in_is_gap = 1
                    else:
                        gain_in = 0 # !!!!!! used ot be -1 to penalize non selected prn
                        max_gain_out_in = np.max([gain_out, gain_in])
                        prn_in_is_gap = 1
                    score_prn[prn_out, prn_in] = score_prn[prn_out, prn_in] + max_gain_out_in
                    if ((prn_out_is_gap == 1) | (prn_in_is_gap == 1)):
                        gap_prn[prn_out, prn_in] = gap_prn[prn_out, prn_in] + 1
                    if ((prn_out_is_gap == 1) & (prn_in_is_gap == 1)):
                        gap_prn[prn_out, prn_in] = gap_prn[prn_out, prn_in] + 10000 # we won't to exclude the possiblity of choosing this combination since both prn have the gap at the same time
                    
        # comb =  unravel_index(score_prn.argmax(), score_prn.shape)
        # first_score_idate.append(comb[0])
        # second_score_idate.append(comb[1])
        score_index_sort_temp = np.dstack(np.unravel_index(np.argsort(score_prn.ravel()), score_prn.shape))
        score_index_sort = score_index_sort_temp[0, :, :] # sorted array of combinations that give the ghihest score (ascending order)
        ncomb = (nprn*(nprn-1))/2/2# total number of combinaiton. /2 because combinaiton [X,Y] is the same as [Y,X]. another/2 because we want to look only at the laf top scores
        icomb = -1
        found_comb_without_gap = 0
        gap_prn_here = np.zeros([ncomb])
        while icomb >= -ncomb: # go through score_index_sort from the combination that gives the higeshest score (score_index_sort[-1,:]) to the combination that gives the lowest score (score_index_sort[-ncomb, :])
            comb_now = score_index_sort[icomb, :]
            prn_out_here = comb_now[0]
            prn_in_here = comb_now[1]
            gap_prn_here[icomb] = gap_prn[prn_out_here, prn_in_here]
            if gap_prn_here[icomb] == 0: # found a combination with no gap at all during the time interval so that's the optimum combination
                found_comb_without_gap = 1
                optim_comb = score_index_sort[icomb, :]
                icomb = -10000 # to get out of the while
            else:
                icomb = icomb-1
        if found_comb_without_gap == 0: # if none of the combinations had no gap (ie if all combinations had at least one second gap) then take the combination with the smallest amount of gap
            imin_gap = np.where(gap_prn_here == np.min(gap_prn_here))[0][0]
            optim_comb = score_index_sort[-ncomb + imin_gap]

        first_score_fm[cygfm-1] = optim_comb[0]
        second_score_fm[cygfm-1] = optim_comb[1]



    ## Time diagram PRNs selected by SpOCK vs time
        itime_start = itime
        itime_stop = itime_start + inter_dur_sec

        NCURVES = nprn
        np.random.seed(101)
        curves = [np.random.random(20) for i in range(NCURVES)]
        values = range(NCURVES)
        jet = cm = plt.get_cmap('jet') 
        cNorm  = colors.Normalize(vmin=0, vmax=values[-1])
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)


        ax_title = 'FM' + str(cygfm) + ': ' + start_time_fm[cygfm-1].replace('T', ' ') + ' to ' + end_time_fm[cygfm-1][11:19] + ' UTC -> PRNs ' +\
            str((int)(first_score_fm[cygfm-1])) + ', ' +  str((int)(second_score_fm[cygfm-1]))
        fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
        fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'normal',)
        plt.rc('font', weight='normal') ## make the labels of the ticks in bold                                                                      
        gs = gridspec.GridSpec(1, 1)
        gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
        ax = fig.add_subplot(gs[0, 0])
        ax.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
        ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
        ax.set_title(ax_title, weight = 'normal', fontsize  = fontsize_plot)
        [i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                       
        ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
        plt.rc('font', weight='normal') ## make the labels of the ticks in bold                           
        for iin in range(itime_start, itime_stop):
            gain_spock_now = fom_spock[iin, :]
            gain_sort_index = np.argsort(-gain_spock_now) # descending order
            xaxis = ((date_spock[iin] - date_spock[itime_start]).total_seconds()) / 60.
            for ispec in range(4):
                prn_spock = gps_spock[iin, ispec]
                prn_spock_value = np.where(prn_list_sort == prn_spock)[0][0]
                # if (ispec == gain_sort_index[0]): # top PRN gain
                #     ax.scatter(xaxis, prn_spock_value + 1.0,  marker = '.', color = 'blue',s = 90)
                # elif (ispec == gain_sort_index[1]): # second to top PRN gain
                #     ax.scatter(xaxis, prn_spock_value + 1.0,  marker = '.', color = 'blue',s = 20)
                # else:
                #     ax.scatter(xaxis, prn_spock_value + 1.0,  marker = '.', color = 'blue', alpha = 0.06, s=20)
                if fom_spock[iin, ispec] == 0: # !!!!!!!!!!! if change gain limmits then need to change also label_gain
                    ax.scatter(xaxis, prn_spock_value + 1.0,  marker = '.', color = color_gain[0], s = 90)   
                elif ((fom_spock[iin, ispec] >= 1) & (fom_spock[iin, ispec] <= 5)):
                    ax.scatter(xaxis, prn_spock_value + 1.0,  marker = '.', color = color_gain[1], s = 90)   
                elif ((fom_spock[iin, ispec] >= 6) & (fom_spock[iin, ispec] <= 10)):
                    ax.scatter(xaxis, prn_spock_value + 1.0,  marker = '.', color = color_gain[2], s = 90)   
                elif ((fom_spock[iin, ispec] >= 11) & (fom_spock[iin, ispec] <= 15)):
                    ax.scatter(xaxis, prn_spock_value + 1.0,  marker = '.', color = color_gain[3], s = 90)   
                else:
                    print "***! Error: the gain is not between 0 and 15. !***"; sys.exit()
                
        dt_xlabel =  1. # min
        xticks = np.arange(0, inter_dur_sec/60.+1, dt_xlabel)
        date_list_str = []
        date_list = [date_spock[itime_start] + timedelta(seconds=(x-xticks[0])*60.) for x in xticks]
        for i in range(len(xticks)):
            date_list_str.append( str(date_list[i])[11:19] )
        ax.xaxis.set_ticks(xticks)
        ax.xaxis.set_ticklabels(date_list_str, fontsize = fontsize_plot, rotation=60, horizontalalignment = 'center')

        ax.yaxis.set_ticks(np.arange(1, nprn+1))
        ax.yaxis.set_ticklabels(prn_list_sort, fontsize = fontsize_plot)
        ax.margins(0,0)
        ax.set_ylim([0.5, nprn+0.5])
        fig_save_name = '/Users/cbv/fm' + str(cygfm) + '_prn'  + str((int)(first_score_fm[cygfm-1])) + '_' +  str((int)(second_score_fm[cygfm-1])) + '_from_' + \
                        start_time_fm[cygfm-1].replace('-','').replace(':','') + '_to_' + end_time_fm[cygfm-1].replace('-','').replace(':','') + '_utc.pdf'
        # fig_save_name = '/Users/cbv/fm' + str(cygfm) + '_prnX_Y_from_' + \
        #     start_time_fm[cygfm-1].replace('-','').replace(':','') + '_to_' + end_time_fm[cygfm-1].replace('-','').replace(':','') + '_utc.pdf'

        legend = ax.legend( loc='center left',  bbox_to_anchor=(1, 0.5), fontsize = fontsize_plot, handles=handles_arr, ncol=1, frameon=False, title = 'PRN gain')
        legend.get_title().set_fontsize(str(fontsize_plot)) 
        fig.savefig(fig_save_name, facecolor=fig  .get_facecolor(), edgecolor='none', bbox_inches='tight')


        
raise Exception
# download CYGNSS and GPS TLEs in the format required by sat-bop.py

## GPS TLE. gps_tle.py was called in spock_cygnss_spec_parallel_beacon.py but the format of the TLE is not the same as in gps_tle_beacon.py. gps_tle_beacon.py outputs in the same format as required by sat-bop
#os.system("gps_tle_beacon.py " + start_time_const[0:10])

## CYGNSS TLE. cygnss_tle.py was called in spock_cygnss_spec_parallel_beacon.py but sat-bop requires one TLE per FM, and each TLE must be 3 lines (firs tline is name of FM)

#


# csv_filename = 'FM03_2018-10-31/pass_1_PRN_21.csv' #'outputCygnssOct/FM03/pass_5_PRN_10.csv'

# date, prn, target_lat, target_lon, target_alt, target_ecef_x, target_ecef_y, target_ecef_z, target_rx_sat_look_angle_az, target_rx_sat_look_angle_el, target_rx_sat_range, sp_lat, sp_lon, sp_ecef_pos_x, sp_ecef_pos_y, sp_ecef_pos_z, sp_gain, rx_sub_sat_lat, rx_sub_sat_lon, rx_sat_ecef_pos_x, rx_sat_ecef_pos_y, rx_sat_ecef_pos_z, rx_sat_ecef_vel_x, rx_sat_ecef_vel_y, rx_sat_ecef_vel_z, tx_sat_ecef_pos_x, tx_sat_ecef_pos_y, tx_sat_ecef_pos_z, rx_power = beacon_read_csv(filename)


# to verify with newer_validate_sift.py (so copy paste in the terminal where you run newer_validate_sift, not in the temrinal where you run cygnss_beacon_main):
idate = 0 # need to set
date_start = datetime(2018, 10, 31, 18, 15, 10) # need to set 
date_stop = datetime(2018, 10, 31, 18, 27, 34)  # need to set 
itime_start = np.where(nb_seconds_since_initial_epoch_spock_all_date[idate] == (date_start - date_spock[0]).total_seconds())[0][0]
print (nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start] - nb_seconds_since_initial_epoch_spock_all_date[idate][0])/3600. # should be the number of hours of date_start
# (example if date_start is datetime(2018, 9, 26, 12, 4, 58) then should print 12.0825)
itime_stop = np.where(nb_seconds_since_initial_epoch_spock_all_date[idate] == (date_stop - date_spock[0]).total_seconds())[0][0]
