## NEED TO DEFINE inter_dur_sec before running newer_validate_sift_plot.py
import matplotlib.patches as mpatches
plot_selected_prn = 1 # if this is set to 1 then 2 PRNs selected for the overpass will also be reported at the bottom of the plot
color_gain = ['grey', 'blue', 'limegreen', 'red']
label_gain = ['0', '2-5', '6-10', '11-15']
handles_arr = []
for icat in range(len(label_gain)):
    handles_arr.append(mpatches.Patch(color=color_gain[icat], label=label_gain[icat]))

marker_ant = [10, 11]
dant_netcdf = [0, 0.15]
dant_spock = [0, -0.15]

start_date_interval = '2018-09-26T12:04:58' #2018-09-26T07:21:49' # fm01 2018-10-31T18:15:10, fm04 2018-10-31T18:30:53, fm03 2018-10-31T18:43:05
stop_date_interval = '2018-09-26T12:17:31'#'2018-09-26T07:33:49' # fm01 2018-10-31T18:27:34, fm04 2018-10-31T18:41:08, fm03 2018-10-31T18:55:32
start_date_interval_date = datetime.strptime(start_date_interval, "%Y-%m-%dT%H:%M:%S")
stop_date_interval_date = datetime.strptime(stop_date_interval, "%Y-%m-%dT%H:%M:%S") 
itime_start = np.where(date_spock_same_time_as_netcdf >= start_date_interval_date)[0][0]
itime_stop = np.where(date_spock_same_time_as_netcdf <= stop_date_interval_date)[0][-1] #itime_start + inter_dur_sec#np.where(date_spock_same_time_as_netcdf <= stop_date_interval_date)[0][-1]

# for itime_in in range(0,len(np.where(duration_first_and_second_score_2nd_half_wrong_or_star_conc > 0)[0]), len(np.where(duration_first_and_second_score_2nd_half_wrong_or_star_conc > 0)[0])/5):
#     print itime_in, len(np.where(duration_first_and_second_score_2nd_half_wrong_or_star_conc > 0)[0])
#     #itime_in = 10;
#     itime_fac = np.where(duration_first_and_second_score_2nd_half_wrong_or_star_conc > 0)[0][itime_in];
#     itime_start = itime_fac * delta_inter #time_second_gain_wrong_all_date[idate][itime_diff]#time_second_gain_wrong_all_date[idate][itime_diff] #time_diff_prn_all_date[idate][itime_diff]
#     itime_stop = itime_start + inter_dur_sec#np.where(nb_seconds_since_initial_epoch_spock_all_date[idate] >= nb_seconds_since_initial_epoch_



itime_fac = itime_start / delta_inter


# figure out the number of different prn (SpOCK and on-board) during that time intervals
prn_list = []
for itime in range(itime_start, itime_stop):
    for ispec in range(4):
        if ( gps_spock_all_date[idate][itime][ispec] in prn_list ) == False:
            prn_list.append(gps_spock_all_date[idate][itime][ispec])
        if ( gps_netcdf_all_date[idate][itime][ispec] in prn_list ) == False:
            prn_list.append(gps_netcdf_all_date[idate][itime][ispec])
prn_list = np.array(prn_list)
nprn = len(prn_list)
prn_list_sort = prn_list[np.argsort(prn_list)]
NCURVES = nprn
np.random.seed(101)
curves = [np.random.random(20) for i in range(NCURVES)]
values = range(NCURVES)
jet = cm = plt.get_cmap('jet') 
cNorm  = colors.Normalize(vmin=0, vmax=values[-1])
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

height_fig = 11.  # the width is calculated as height_fig * 4/3.
fontsize_plot = 25      
ratio_fig_size = 4./3
fig_title = ''#Accuracy VS RCG
y_label = 'PRN'
x_label = 'Time (min)'
fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'normal',)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                                                                      
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.01)
ax = fig.add_subplot(gs[0, 0])
ax.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                       
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7,bottom=1,  left=1, right=1)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                           
gps_spock_value = []
gps_netcdf_value = []
for itime in range(itime_start, itime_stop):
    gps_spock_value_sub = []
    gps_netcdf_value_sub = []
    gain_spock_now = fom_spock_all_date[idate][itime]
    gain_sort_index = np.argsort(-gain_spock_now) # descending order
    for ispec in range(4):
        prn_spock = gps_spock_all_date[idate][itime][ispec]
        if which_ant_spock_all_date[idate][itime][ispec] == 2: # starboard
            iant_spock = 0
        elif which_ant_spock_all_date[idate][itime][ispec] == 3: # starboard
            iant_spock = 1
        prn_spock_value = np.where(prn_list_sort == prn_spock)[0][0]
        gps_spock_value_sub.append(prn_spock_value)        
        prn_netcdf = gps_netcdf_all_date[idate][itime][ispec]
        prn_netcdf_value = np.where(prn_list_sort == prn_netcdf)[0][0]
        gps_netcdf_value_sub.append(prn_netcdf_value)
        if which_ant_netcdf_all_date[idate][itime][ispec] == 2: # starboard
            iant_netcdf = 0
        elif which_ant_netcdf_all_date[idate][itime][ispec] == 3: # starboard
            iant_netcdf = 1

        if fom_spock_all_date[idate][itime][ispec] == 0: # !!!!!!!!!!! if change gain limmits then need to change also label_gain
            ax.scatter((nb_seconds_since_initial_epoch_spock_all_date[idate][itime]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60., prn_spock_value + dant_spock[iant_spock] + 0.95,  marker = '.', color = color_gain[0], s = 20)   
        elif ((fom_spock_all_date[idate][itime][ispec] >= 1) & (fom_spock_all_date[idate][itime][ispec] <= 5)):
            ax.scatter((nb_seconds_since_initial_epoch_spock_all_date[idate][itime]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60., prn_spock_value + dant_spock[iant_spock] + 0.95,  marker = '.', color = color_gain[1], s = 20)   
        elif ((fom_spock_all_date[idate][itime][ispec] >= 6) & (fom_spock_all_date[idate][itime][ispec] <= 10)):
            ax.scatter((nb_seconds_since_initial_epoch_spock_all_date[idate][itime]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60., prn_spock_value + dant_spock[iant_spock] + 0.95,  marker = '.', color = color_gain[2], s = 20)   
        elif ((fom_spock_all_date[idate][itime][ispec] >= 11) & (fom_spock_all_date[idate][itime][ispec] <= 15)):
            ax.scatter((nb_seconds_since_initial_epoch_spock_all_date[idate][itime]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60., prn_spock_value + dant_spock[iant_spock] + 0.95,  marker = '.', color = color_gain[3], s = 20)   
        else:
            print "***! Error: the gain is not between 0 and 15. !***"; sys.exit()

        ax.scatter((nb_seconds_since_initial_epoch_spock_all_date[idate][itime]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.,
                   prn_netcdf_value + dant_netcdf[iant_netcdf] + 1.05,  marker = '.', color = 'black', s=20)
    gps_spock_value.append(gps_spock_value_sub)
    gps_netcdf_value.append(gps_netcdf_value_sub)

if plot_selected_prn == 1:
    # FIRST HALF OF OVERPASS
    # time_first_score_1st_half_wrong_or_port[idate][itime_fac] represents all the steps in the first half of the overpass
    # for which the 1st PRN selected by SpOCK at the start of the itime_fac interval was not selected by on the on-board alrorithm or assigned to the aft antenna during the first half of the overpass
    # recall that each itime_fac interval last for inter_dur_sec steps (basically inter_dur_sec seconds, since comment for variable delta_inter)
    if (len(time_first_score_1st_half_wrong_or_port[idate][itime_fac]) > 0):
        xfirst = (nb_seconds_since_initial_epoch_spock_all_date[idate][time_first_score_1st_half_wrong_or_port[idate][itime_fac]]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.
        ax.scatter(xfirst, np.zeros([len(xfirst)])+0.35, color= 'black',  marker = '.', s = 20)
    ax.text(0,0.35,'1st (' + str(first_score[idate][itime_fac]) + ') gap: ', fontsize = fontsize_plot, weight = 'normal', horizontalalignment = 'right', verticalalignment = 'center')
    ax.text((nb_seconds_since_initial_epoch_spock_all_date[idate][itime_stop-1]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.,0.35,' ' +
            format(duration_first_score_1st_half_wrong_or_port_idate[idate][itime_fac] / 60 , ".1f" )  + "'/" + format(duration_first_score_2nd_half_wrong_or_star_idate[idate][itime_fac] / 60 ,".1f" ) + "'",
            fontsize = fontsize_plot, weight = 'normal', horizontalalignment = 'left', verticalalignment = 'center')
    if (len(time_second_score_1st_half_wrong_or_port[idate][itime_fac]) > 0):
        xsecond = (nb_seconds_since_initial_epoch_spock_all_date[idate][time_second_score_1st_half_wrong_or_port[idate][itime_fac]]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.
        ax.scatter(xsecond, np.zeros([len(xsecond)])+0., color= 'black',  marker = '.', s = 20)
    ax.text(0,0.,'2nd (' + str(second_score[idate][itime_fac]) + ') gap: ', fontsize = fontsize_plot, weight = 'normal', horizontalalignment = 'right', verticalalignment = 'center')
    ax.text((nb_seconds_since_initial_epoch_spock_all_date[idate][itime_stop-1]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.,0.,' ' +
            format(duration_second_score_1st_half_wrong_or_port_idate[idate][itime_fac] / 60 , ".1f") + "'/" + format(duration_second_score_2nd_half_wrong_or_star_idate[idate][itime_fac] / 60 , ".1f") + "'",
            fontsize = fontsize_plot, weight = 'normal', horizontalalignment = 'left', verticalalignment = 'center')


    # one of the two prns wrong
    if (len(time_first_or_second_score_1st_half_wrong_or_port[idate][itime_fac]) > 0):
        xfirst_or_second = (nb_seconds_since_initial_epoch_spock_all_date[idate][time_first_or_second_score_1st_half_wrong_or_port[idate][itime_fac]]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.
        ax.scatter(xfirst_or_second, np.zeros([len(xfirst_or_second)])-0.35, color= 'black',  marker = '.', s = 20)
    ax.text(0,-0.35, str(first_score[idate][itime_fac]) + '-' +  str(second_score[idate][itime_fac]) + ' gap: ', fontsize = fontsize_plot, weight = 'normal', horizontalalignment = 'right', verticalalignment = 'center')
    ax.text((nb_seconds_since_initial_epoch_spock_all_date[idate][itime_stop-1]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.,-0.35,' ' + format(duration_first_or_second_score_1st_half_wrong_or_port_idate[idate][itime_fac] / 60., ".1f") + "'/" + format(duration_first_or_second_score_2nd_half_wrong_or_star_idate[idate][itime_fac] / 60., ".1f"),
            fontsize = fontsize_plot, weight = 'normal', horizontalalignment = 'left', verticalalignment = 'center')

    # both prns wrong
    if (len(time_first_and_second_score_1st_half_wrong_or_port[idate][itime_fac]) > 0):
        xfirst_and_second = (nb_seconds_since_initial_epoch_spock_all_date[idate][time_first_and_second_score_1st_half_wrong_or_port[idate][itime_fac]]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.
        ax.scatter(xfirst_and_second, np.zeros([len(xfirst_and_second)])-0.35, color= 'red',  marker = '.', s = 20)


        # 2ND HALF OF OVERPASS + 130S
    if (len(time_first_score_2nd_half_wrong_or_star[idate][itime_fac]) > 0):
        xfirst = (nb_seconds_since_initial_epoch_spock_all_date[idate][time_first_score_2nd_half_wrong_or_star[idate][itime_fac]]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.
        ax.scatter(xfirst, np.zeros([len(xfirst)])+0.35, color= 'black',  marker = '.', s = 20)
    if (len(time_second_score_2nd_half_wrong_or_star[idate][itime_fac]) > 0):
        xsecond = (nb_seconds_since_initial_epoch_spock_all_date[idate][time_second_score_2nd_half_wrong_or_star[idate][itime_fac]]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.
        ax.scatter(xsecond, np.zeros([len(xsecond)])+0., color= 'black',  marker = '.', s = 20)


    # one of the two prns wrong
    if (len(time_first_or_second_score_2nd_half_wrong_or_star[idate][itime_fac]) > 0):
        xfirst_or_second = (nb_seconds_since_initial_epoch_spock_all_date[idate][time_first_or_second_score_2nd_half_wrong_or_star[idate][itime_fac]]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.
        ax.scatter(xfirst_or_second, np.zeros([len(xfirst_or_second)])-0.35, color= 'black',  marker = '.', s = 20)

    # both prns wrong
    if (len(time_first_and_second_score_2nd_half_wrong_or_star[idate][itime_fac]) > 0):
        xfirst_and_second = (nb_seconds_since_initial_epoch_spock_all_date[idate][time_first_and_second_score_2nd_half_wrong_or_star[idate][itime_fac]]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.
        ax.scatter(xfirst_and_second, np.zeros([len(xfirst_and_second)])-0.35, color= 'red',  marker = '.', s = 20)


    ax.plot([0, (nb_seconds_since_initial_epoch_spock_all_date[idate][itime_stop-1]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60.],
            [0.6,0.6], linestyle = 'dashed', linewidth = 2, color = 'black')
    ax.text(0,0.6,'--------------------', fontsize = fontsize_plot, weight = 'normal', horizontalalignment = 'right', verticalalignment = 'center')

tmax = (nb_seconds_since_initial_epoch_spock_all_date[idate][itime_stop]-nb_seconds_since_initial_epoch_spock_all_date[idate][itime_start])/60./2
tstar = tmax + 130/60.
ax.plot([tmax, tmax], [-0.6, -0.6 + 0.05], linewidth = 2, color = 'k')
ax.plot([tstar, tstar], [-0.6, -0.6 + 0.05], linewidth = 2, color = 'k')
ax.yaxis.set_ticks(np.arange(1, nprn+1))
ax.yaxis.set_ticklabels(prn_list_sort, fontsize = fontsize_plot)#, rotation='vertical')
ax.margins(0,0)
ax.set_ylim([-0.6, nprn+0.5])
ax.text(tmax, ax.get_ylim()[0], ' Tmax', rotation = 90, fontsize = fontsize_plot, horizontalalignment  = 'center', verticalalignment = 'bottom')
ax.text(tstar, ax.get_ylim()[0], ' Tmax+130s', rotation = 90, fontsize = fontsize_plot, horizontalalignment  = 'center', verticalalignment = 'bottom')
legend = ax.legend( loc='center left',  bbox_to_anchor=(1, 0.5), fontsize = fontsize_plot, handles=handles_arr, ncol=1, frameon=False, title = 'PRN gain')
legend.get_title().set_fontsize(str(fontsize_plot)) 

fig_save_name = '/Users/cbv/' + spock_input_filename.replace('.txt', '_') + 'itimeStart' + str(itime_start) + '_itimeStop' + str(itime_stop) + '_prn_select.pdf'
#'testfm0' + str(cygfm)+ '.pdf'#+str(itime_in) + '_score_3d_binom.pdf'#time_diagram_prn_spock_onboard_iday' + str(idate) + '_itimeStart' + str(itime_start) + '_itimeStop' + +str(itime_stop) + '.pdf'
fig.savefig(fig_save_name, facecolor=fig  .get_facecolor(), edgecolor='none', bbox_inches='tight')
print fig_save_name
