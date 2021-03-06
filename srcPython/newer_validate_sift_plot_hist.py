# Histogram of time when the two top scores PRN is not selected during 1st half of overpass OR assigend to the port antenna
height_fig = 11.  # the width is calculated as height_fig * 4/3.
fontsize_plot = 25      
ratio_fig_size = 4./3
fig_title = 'Distribution of the total gap time (PRN not selected onboard\nor assigned to aft ant.) during 1st half of overpass'#Accuracy VS RCG
y_label = 'Percentage'
x_label = 'Gap time (min)'
y_max_axis = 35
fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 1.08,fontsize = (int)(fontsize_plot*1.1), weight = 'normal',)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                                                                                                                                                                  
gs = gridspec.GridSpec(1, 2)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.17, wspace = 0.1)
min_bin = 0.00001 # not eaxctaly 0 so that elements with a gap of 0 min are excluded from the histrogram ( we
# don't want them to be counted in the [0, 1] bin)
max_bin = interv_dur
bin_size = 1. # in min
plt.rc('font', weight='normal') ## make the labels of the ticks in bold
# Or
ax_title = '1 of 2 PRNs not selected onboard\nor assigned to aft ant.'
ax = fig.add_subplot(gs[0, 0])
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_title(ax_title, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                                                                                                                       
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
yhist = duration_first_or_second_score_1st_half_wrong_or_port_conc / 60.
hist_first_data = np.histogram(yhist, np.arange(min_bin, max_bin + bin_size, bin_size))#, range = [range_min, range_max])
bin_array_temp = hist_first_data[1]
bin_array = ( bin_array_temp[:-1] + np.roll(bin_array_temp,-1)[:-1] ) /2.
binsize_actual = bin_array[1] - bin_array[0]
hist_first = hist_first_data[0] * 100. / len(yhist)
ax.bar(bin_array, hist_first, binsize_actual)
percentage_yhist = len(np.where(yhist != 0)[0]) * 100./ len(yhist) # this should be the same as np.sum(hist_first)
ax.text(0.98,0.98,format(100-percentage_yhist, ".0f") + '% of overpasses:\nboth PRNs selected onboard\nand assigned to fore ant.\nfor the ENTIRE 1st half\n(100-sum all bins)', fontsize = fontsize_plot, transform = ax.transAxes, horizontalalignment = 'right', verticalalignment = 'top')
y_max = np.max(hist_first)*1.1
ax.margins(0,0)
ax.set_ylim([0, y_max_axis])
# And
ax = fig.add_subplot(gs[0, 1])
ax_title = 'Both PRNs not selected onboard\nor assigned to aft.'
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_title(ax_title, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                                                                                                                       
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
yhist = duration_first_and_second_score_1st_half_wrong_or_port_conc / 60.
hist_first_data = np.histogram(yhist, np.arange(min_bin, max_bin + bin_size, bin_size))#, range = [range_min, range_max])
bin_array_temp = hist_first_data[1]
bin_array = ( bin_array_temp[:-1] + np.roll(bin_array_temp,-1)[:-1] ) /2.
binsize_actual = bin_array[1] - bin_array[0]
hist_first = hist_first_data[0] * 100. / len(yhist)
ax.bar(bin_array, hist_first, binsize_actual)
percentage_yhist = len(np.where(yhist != 0)[0]) * 100./ len(yhist) # this should be the same as np.sum(hist_first)
ax.text(0.98,0.98,format(100-percentage_yhist, ".1f") + '% of overpasses:\nat least 1 of the 2\nPRNs selected onboard\nand assigned to fore ant.\nfor the ENTIRE 1st half\n(100-sum all bins)', fontsize = fontsize_plot, transform = ax.transAxes, horizontalalignment = 'right', verticalalignment = 'top')
y_max = np.max(hist_first)*1.1
ax.margins(0,0)
ax.set_ylim([0, y_max_axis])
ax.yaxis.set_ticklabels([])
fig.set_figheight(height_fig)
fig.set_figwidth(height_fig*ratio_fig_size)
fig_save_name = '/Users/cbv/' + spock_input_filename.replace('.txt','_') + 'beacon_hist_prn_not_selected_or_port_1st_half.pdf'#
#fig_save_name = '/Users/cbv/' + spock_input_filename.replace('.txt','_') + 'beacon_hist_prn_not_selected_or_port_1st_half_optimize_1st_half_only.pdf'#
fig.savefig(fig_save_name, facecolor=fig  .get_facecolor(), edgecolor='none', bbox_inches='tight')

################################################################################################################################################
################################################################################################################################################

# Histogram of time when the two top scores PRN is not selected OR assigend to the port antenna starting at second half + 130s
height_fig = 11.  # the width is calculated as height_fig * 4/3.
fontsize_plot = 25      
ratio_fig_size = 4./3
fig_title = 'Distribution of the total gap time (PRN not selected onboard\nor assigned to fore ant.) during 2nd half of overpass full DDM'#Accuracy VS RCG
y_label = 'Percentage'
x_label = 'Gap time (min)'
y_max_axis = 100
fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 1.08,fontsize = (int)(fontsize_plot*1.1), weight = 'normal',)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                                                                                                                                                                  
gs = gridspec.GridSpec(1, 2)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.17, wspace = 0.1)
min_bin = 0.00001 # not eaxctaly 0 so that elements with a gap of 0 min are excluded from the histrogram ( we
# don't want them to be counted in the [0, 1] bin)
max_bin = interv_dur
bin_size = 1. # in min
plt.rc('font', weight='normal') ## make the labels of the ticks in bold
# Or
ax_title = '1 of 2 PRNs not selected onboard\nor assigned to fore ant.'
ax = fig.add_subplot(gs[0, 0])
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_title(ax_title, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                                                                                                                       
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
yhist = duration_first_or_second_score_2nd_half_wrong_or_star_conc / 60.
hist_first_data = np.histogram(yhist, np.arange(min_bin, max_bin + bin_size, bin_size))#, range = [range_min, range_max])
bin_array_temp = hist_first_data[1]
bin_array = ( bin_array_temp[:-1] + np.roll(bin_array_temp,-1)[:-1] ) /2.
binsize_actual = bin_array[1] - bin_array[0]
hist_first = hist_first_data[0] * 100. / len(yhist)
ax.bar(bin_array, hist_first, binsize_actual)
percentage_yhist = len(np.where(yhist != 0)[0]) * 100./ len(yhist) # this should be the same as np.sum(hist_first)
ax.text(0.98,0.98,format(100-percentage_yhist, ".1f") + '% of overpasses:\nboth PRNs selected onboard and\nassigned to aft ant. for the\nENTIRE 2nd half full DDM.\n(100-sum all bins)', fontsize = fontsize_plot, transform = ax.transAxes, horizontalalignment = 'right', verticalalignment = 'top')
y_max = np.max(hist_first)*1.1
ax.margins(0,0)
ax.set_ylim([0, y_max_axis])
# And
ax = fig.add_subplot(gs[0, 1])
ax_title = 'Both PRNs not selected onboard\nor assigned to fore.'
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_title(ax_title, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                                                                                                                       
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
yhist = duration_first_and_second_score_2nd_half_wrong_or_star_conc / 60.
hist_first_data = np.histogram(yhist, np.arange(min_bin, max_bin + bin_size, bin_size))#, range = [range_min, range_max])
bin_array_temp = hist_first_data[1]
bin_array = ( bin_array_temp[:-1] + np.roll(bin_array_temp,-1)[:-1] ) /2.
binsize_actual = bin_array[1] - bin_array[0]
hist_first = hist_first_data[0] * 100. / len(yhist)
ax.bar(bin_array, hist_first, binsize_actual)
percentage_yhist = len(np.where(yhist != 0)[0]) * 100./ len(yhist) # this should be the same as np.sum(hist_first)
ax.text(0.98,0.98,format(100-percentage_yhist, ".1f") + '% of overpasses:\nat least 1 of the 2\nPRNs selected onboard and\nassigned to aft ant. for the\nENTIRE 2nd half full DDM\n(100-sum all bins)', fontsize = fontsize_plot, transform = ax.transAxes, horizontalalignment = 'right', verticalalignment = 'top')
y_max = np.max(hist_first)*1.1
ax.margins(0,0)
ax.set_ylim([0, y_max_axis])
ax.yaxis.set_ticklabels([])
fig.set_figheight(height_fig)
fig.set_figwidth(height_fig*ratio_fig_size)
fig_save_name = '/Users/cbv/' + spock_input_filename.replace('.txt','_') + 'beacon_hist_prn_not_selected_or_star_2nd_half_full_ddm.pdf'#
#fig_save_name = '/Users/cbv/' + spock_input_filename.replace('.txt','_') + 'beacon_hist_prn_not_selected_or_star_2nd_half_full_ddm_optimize_1st_half_only.pdf'#
fig.savefig(fig_save_name, facecolor=fig  .get_facecolor(), edgecolor='none', bbox_inches='tight')




################################################################################################################################################
################################################################################################################################################





################################################################################################################################################
################################################################################################################################################


# Histogram of time when the two top scores PRN is not selected during 1st half of overpass (or, and)
height_fig = 11.  # the width is calculated as height_fig * 4/3.
fontsize_plot = 25      
ratio_fig_size = 4./3
fig_title = 'Distribution of the total gap time (PRN not selected onboard)\nduring 1st half of overpass'#Accuracy VS RCG
y_label = 'Percentage'
x_label = 'Gap time (min)'
y_max_axis = 35
fig = plt.figure(num=None, figsize=(height_fig * ratio_fig_size, height_fig), dpi=80, facecolor='w', edgecolor='k')
fig.suptitle(fig_title, y = 1.045,fontsize = (int)(fontsize_plot*1.1), weight = 'normal',)
plt.rc('font', weight='normal') ## make the labels of the ticks in bold                                                                                                                                                                  
gs = gridspec.GridSpec(1, 2)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.17, wspace = 0.1)
min_bin = 0.00001 # not eaxctaly 0 so that elements with a gap of 0 min are excluded from the histrogram ( we
# don't want them to be counted in the [0, 1] bin)
max_bin = interv_dur
bin_size = 1. # in min
plt.rc('font', weight='normal') ## make the labels of the ticks in bold
# Or
ax_title = '1 of 2 PRNs not selected onboard'
ax = fig.add_subplot(gs[0, 0])
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_title(ax_title, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                                                                                                                       
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
yhist = duration_first_or_second_score_1st_half_wrong_conc / 60.
hist_first_data = np.histogram(yhist, np.arange(min_bin, max_bin + bin_size, bin_size))#, range = [range_min, range_max])
bin_array_temp = hist_first_data[1]
bin_array = ( bin_array_temp[:-1] + np.roll(bin_array_temp,-1)[:-1] ) /2.
binsize_actual = bin_array[1] - bin_array[0]
hist_first = hist_first_data[0] * 100. / len(yhist)
ax.bar(bin_array, hist_first, binsize_actual)
percentage_yhist = len(np.where(yhist != 0)[0]) * 100./ len(yhist) # this should be the same as np.sum(hist_first)
ax.text(0.98,0.98,format(100-percentage_yhist, ".0f") + '% of overpasses:\nboth PRNs selected onboard\nfor the ENTIRE 1st half\n(100-sum all bins)', fontsize = fontsize_plot, transform = ax.transAxes, horizontalalignment = 'right', verticalalignment = 'top')
y_max = np.max(hist_first)*1.1
ax.margins(0,0)
ax.set_ylim([0, y_max_axis])
# And
ax = fig.add_subplot(gs[0, 1])
ax_title = 'Both PRNs not selected onboard'
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_title(ax_title, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure                                                                                                                                       
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7)
yhist = duration_first_and_second_score_1st_half_wrong_conc / 60.
hist_first_data = np.histogram(yhist, np.arange(min_bin, max_bin + bin_size, bin_size))#, range = [range_min, range_max])
bin_array_temp = hist_first_data[1]
bin_array = ( bin_array_temp[:-1] + np.roll(bin_array_temp,-1)[:-1] ) /2.
binsize_actual = bin_array[1] - bin_array[0]
hist_first = hist_first_data[0] * 100. / len(yhist)
ax.bar(bin_array, hist_first, binsize_actual)
percentage_yhist = len(np.where(yhist != 0)[0]) * 100./ len(yhist) # this should be the same as np.sum(hist_first)
ax.text(0.98,0.98,format(100-percentage_yhist, ".0f") + '% of overpasses:\nat least 1 of the 2\nPRNs selected onboard\nfor the ENTIRE 1st half\n(100-sum all bins)', fontsize = fontsize_plot, transform = ax.transAxes, horizontalalignment = 'right', verticalalignment = 'top')
y_max = np.max(hist_first)*1.1
ax.margins(0,0)
ax.set_ylim([0, y_max_axis])
ax.yaxis.set_ticklabels([])
fig.set_figheight(height_fig)
fig.set_figwidth(height_fig*ratio_fig_size)
fig_save_name = '/Users/cbv/' + spock_input_filename.replace('.txt','_') + 'beacon_hist_prn_not_selected_1st_half.pdf'#
#fig_save_name = '/Users/cbv/' + spock_input_filename.replace('.txt','_') + 'beacon_hist_prn_not_selected_1st_half_optimize_1st_half_only.pdf'#
fig.savefig(fig_save_name, facecolor=fig  .get_facecolor(), edgecolor='none', bbox_inches='tight')

