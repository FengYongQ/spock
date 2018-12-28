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

import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.gridspec as gridspec
from matplotlib.colors import LogNorm
from matplotlib import pyplot as plt
import numpy as np
import pandas


df = pandas.read_excel('Results.xlsx')
#print the column names
days = df['Days'].values[:14002]
where_before_450_days = np.where(days < 450)[0]
phase = []
phase.append(df['FM01'].values[:14002])
phase.append(df['FM02'].values[:14002])
phase.append(df['FM04'].values[:14002])
phase.append(df['FM05'].values[:14002])
phase.append(df['FM06'].values[:14002])
phase.append(df['FM07'].values[:14002])
phase.append(df['FM08'].values[:14002])


days = days[where_before_450_days]
phase = np.array(phase)
phase = phase[:, where_before_450_days]


nb_sc = 8

name = ['FM01', 'FM02',  'FM04', 'FM05', 'FM06', 'FM07', 'FM08']
## Parameters for the figure
height_fig = 11 # the width is calculated as height_fig * 4/3.
fontsize_plot = 25
width_fig = height_fig * 4./3

color_arr = ['b', 'r','g', 'm', 'gold', 'cyan', 'darkgray',  'lawngreen', 'green', 'chocolate','cornflowerblue','fuchsia']

fig_title = ''
y_label = '$\Phi$ (' + u'\N{DEGREE SIGN})'
x_label = 'Days since launch'
fig = plt.figure(num=None, figsize=(width_fig, height_fig), dpi=80, facecolor='w', edgecolor='k')

fig.suptitle(fig_title, y = 0.965,fontsize = (int)(fontsize_plot*1.1), weight = 'normal',)
plt.rc('font', weight='normal') ## make the labels of the ticks in normal
gs = gridspec.GridSpec(1, 1)
gs.update(left = 0.11, right=0.87, top = 0.93,bottom = 0.12, hspace = 0.1)
ax = fig.add_subplot(gs[0, 0])
ax.set_ylabel(y_label, weight = 'normal', fontsize  = fontsize_plot)
ax.set_xlabel(x_label, weight = 'normal', fontsize  = fontsize_plot)
[i.set_linewidth(2) for i in ax.spines.itervalues()] # change the width of the frame of the figure
ax.tick_params(axis='both', which='major', labelsize=fontsize_plot, size = 10, width = 2, pad = 7) 
plt.rc('font', weight='normal') ## make the labels of the ticks in normal

for isc in range(7):# !!!! nb_sc): 
    ax.plot(days,phase[isc,:] , linewidth = 2, color = color_arr[isc], label = name[isc])

legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), numpoints = 1,  title="", fontsize = fontsize_plot, ncol=4)

yticks = np.arange(0,320,45)
ax.yaxis.set_ticks(yticks)



ax.margins(0,0)
ax.set_ylim(0,330)

fig_save_name = 'prelaunch_schedule.pdf'
fig.savefig(fig_save_name, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')  

