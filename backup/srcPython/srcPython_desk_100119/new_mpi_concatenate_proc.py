# run: mpiexec -n 4 python new_mpi_concatenate_proc.py alt400-400_inc90-45_arg_per0-0_raan0-0_true_ano0-0_ecc0-0_f107100_quantile5_forward.txt (cbv on dec 15 2017)
#import ipdb
import sys
sys.path.append("/Users/cbv/Google Drive/Work/PhD/Research/Code/spock/srcPython")
#sys.path.append("/home1/cbussy/Code/spock/srcPython")
import fileinput
import time
import datetime
import numpy as np
import pylab as P
import os
import subprocess
from read_input_file import *

## NOTE 1: to use this script, the only parameter you have to set is the name of the main input file (first non-commented line below)
## NOTE 2: this can be run if only ONE REFERENCE satellite was run (first line of section #SPACECRAFTS in the main input file) (with ensembles of course)

main_input_file_name =  sys.argv[1]


# read input file
# read input file
input_variables, order_input_variables = read_input_file(main_input_file_name)
dt = input_variables[find_in_read_input_order_variables(order_input_variables, 'dt')];
nb_steps = input_variables[find_in_read_input_order_variables(order_input_variables, 'nb_steps')];
satellite_to_plot_path = input_variables[find_in_read_input_order_variables(order_input_variables, 'output_file_path_list')];
satellite_to_plot = input_variables[find_in_read_input_order_variables(order_input_variables, 'output_file_name_list')];
nb_ensembles_coe = input_variables[find_in_read_input_order_variables(order_input_variables, 'nb_ensembles_coe')];
nb_ensembles_attitude = input_variables[find_in_read_input_order_variables(order_input_variables, 'nb_ensembles_attitude')];
nb_ensembles_cd = input_variables[find_in_read_input_order_variables(order_input_variables, 'nb_ensembles_cd')];
ensemble_to_plot_temp = input_variables[find_in_read_input_order_variables(order_input_variables, 'ensembles_to_output')];
nb_ensembles_density = input_variables[find_in_read_input_order_variables(order_input_variables, 'nb_ensembles_density')]
nb_spacecraft = input_variables[find_in_read_input_order_variables(order_input_variables, 'nb_sc')]
compute_drag = input_variables[find_in_read_input_order_variables(order_input_variables, 'compute_drag')]



# Ensembles created by the propagator
ensemble_to_plot = []
for i in range(len(ensemble_to_plot_temp)):
    if (ensemble_to_plot_temp[i] == 'eci_r'):
        ensemble_to_plot.append('x_eci'); ensemble_to_plot.append('y_eci'); ensemble_to_plot.append('z_eci')
    if (ensemble_to_plot_temp[i] == 'eci_v'):
        ensemble_to_plot.append('vx_eci'); ensemble_to_plot.append('vy_eci'); ensemble_to_plot.append('vz_eci')
    if (ensemble_to_plot_temp[i] == 'geodetic'):
        ensemble_to_plot.append('longitude'); ensemble_to_plot.append('latitude'); ensemble_to_plot.append('altitude')
    if (ensemble_to_plot_temp[i] == 'power'):
        ensemble_to_plot.append('power')
    if (ensemble_to_plot_temp[i] == 'attitude'):
        ensemble_to_plot.append('pitch'); ensemble_to_plot.append('roll'); ensemble_to_plot.append('yaw')
    if (ensemble_to_plot_temp[i] == 'oe'):
        ensemble_to_plot.append('sma'); ensemble_to_plot.append('inclination'); ensemble_to_plot.append('eccentricity'); ensemble_to_plot.append('true_anomaly'); ensemble_to_plot.append('RAAN'); ensemble_to_plot.append('argument_perigee');
    if ((ensemble_to_plot_temp[i] == 'density') & (compute_drag == 1)):
        ensemble_to_plot.append('rho'); ensemble_to_plot.append('f107'); ensemble_to_plot.append('f107a'); ensemble_to_plot.append('ap'); 
    if (ensemble_to_plot_temp[i] == 'collision'):
        ensemble_to_plot.append('tca'); ensemble_to_plot.append('dca');
    if (ensemble_to_plot_temp[i] == 'cd'):
        ensemble_to_plot.append('cd');
    if (ensemble_to_plot_temp[i] == 'srp'):
        ensemble_to_plot.append('srp');

        
# from mpi4py import MPI
# comm = MPI.COMM_WORLD
# iProc_python = comm.Get_rank()
# nProcs_python = comm.Get_size()
iProc_python = 0
nProcs_python = 1

## Nb of ensembles
nb_ensembles_array = [nb_ensembles_coe, nb_ensembles_attitude, nb_ensembles_cd, nb_ensembles_density]
nb_ensembles = np.max(nb_ensembles_array)

if ( (nb_ensembles_array[i] > 0 ) &  (nb_ensembles_array[i] < nb_ensembles) ) :
    cygnb_ensembles = nb_ensembles_array[i]

## number of processors
for isat in range(nb_spacecraft):
    # open any file to get the number of processors
    dir_final_output_ensemble = satellite_to_plot_path[isat] + 'ensemble/'
    if len([f for f in os.listdir(dir_final_output_ensemble) if os.path.isfile(os.path.join(dir_final_output_ensemble, f))]) > 0:
        ex_ensemble_file = [f for f in os.listdir(dir_final_output_ensemble) if os.path.isfile(os.path.join(dir_final_output_ensemble, f))][0]
        nProcs = (int)(open(dir_final_output_ensemble + ex_ensemble_file).readlines()[5].split('-')[1].split()[0])
    elif os.path.exists('/'.join(satellite_to_plot_path[0].split('/')[0:-2]) + '/collision/dca/'):
        if len([f for f in os.listdir('/'.join(satellite_to_plot_path[0].split('/')[0:-2]) + '/collision/dca/')]) > 0:
            nProcs = (int)([f for f in os.listdir('/'.join(satellite_to_plot_path[0].split('/')[0:-2]) + '/collision/dca/')][0].split('-')[1].split('_')[0])
        else:
            'Could not find any processor file to concatenate. The program will stop.'; raise Exception;
    else:
        'Could not find any processor file to concatenate. The program will stop.'; raise Exception;
    nb_ensemble_to_plot = len(ensemble_to_plot)
    nb_ensemble_to_plot_per_iProc_python = nb_ensemble_to_plot/nProcs_python
    nb_ensemble_to_plot_left = nb_ensemble_to_plot - (nb_ensemble_to_plot_per_iProc_python * nProcs_python)
    iStart = 0
    for i in range(iProc_python):
        iStart = iStart + nb_ensemble_to_plot_per_iProc_python
        if ((i < nb_ensemble_to_plot_left) & (iProc_python > 0)):
            iStart = iStart + 1
    iEnd = iStart+nb_ensemble_to_plot_per_iProc_python
    if (iProc_python < nb_ensemble_to_plot_left):
        iEnd = iEnd + 1
    nb_ensemble_per_proc = int(np.floor(nb_ensembles / nProcs))
    nb_ensembles_ok = nb_ensemble_per_proc * nProcs

    # Create folder for iproc files
    if os.path.isdir(satellite_to_plot_path[isat]+"ensemble/proc_files") == False:
        os.system("mkdir "+satellite_to_plot_path[isat]+"ensemble/proc_files &>/dev/null")       
#     else:
# #        os.system("rm -Rf " + satellite_to_plot_path[isat]+"ensemble/proc_files/* &>/dev/null")
# #        print ""
#    comm.barrier
    # Create folder for final output ensemble files
    dir_final_output_ensemble = satellite_to_plot_path[isat]+"ensemble/"
    

# gather all output files from different processors
    for eee in range(iStart, iEnd):
        if ( ( ensemble_to_plot[eee] != "tca" ) &  ( ensemble_to_plot[eee] != "dca" ) ):
            if  (( ensemble_to_plot[eee] != "cd" ) & ( ensemble_to_plot[eee] != "srp")):
                for i in range(nProcs):
                    name_file_iproc = satellite_to_plot_path[isat] + 'ensemble/iproc_'+str(i+1)+'-'+str(nProcs)+'_'+ensemble_to_plot[eee]+'_'+satellite_to_plot[isat]
                    file_iproc = open(name_file_iproc,'r') 
                    a = file_iproc.readlines()
                    nb_header = 0 # need to calcaulte nb_header for each file because sometimes SpOCK outptues weird characters in header so add a line
                    while a[nb_header].split()[0] != '#START':
                        nb_header = nb_header + 1
                    nb_header = nb_header +1 
                    nb_steps = len(a) - nb_header # !!!!!!!!!!!this has been added between when computing collisions the time of output stop at end of time spanning TCA

                    if (i == 0):
                        line_iproc = ["" for x in range(nb_steps)]
                        x_alltime_ensemble = np.zeros([nb_steps, nb_ensembles_ok])
                        time_iproc = ["" for x in range(nb_steps)]

                    for line_count in range(nb_steps):
                        line_iproc[line_count] = (a[nb_header+line_count]).split(' ')
                        if (i == 0):
                            time_iproc[line_count] = line_iproc[line_count][0] + ' ' + line_iproc[line_count][1]
                        for ensemble_temp in range(nb_ensemble_per_proc):
                            ensemble = ensemble_temp + nb_ensemble_per_proc * i
                            x_alltime_ensemble[line_count][ensemble] = float( line_iproc[line_count][ensemble_temp+2]  )

                    file_iproc.close()
                    #subprocess.call(['mv', name_file_iproc, satellite_to_plot_path[isat] + 'ensemble/proc_files/'])

                both_time_ensemble = ["" for x in range(nb_steps)]
                for i in range(nb_steps):
                    str_ensemble = ' '
                    for j in range(nb_ensembles_ok):
                        str_ensemble = str_ensemble +  str(x_alltime_ensemble[i][j]) + ' '
                    both_time_ensemble[i] = time_iproc[i] + str_ensemble

                filename = 'ensemble_'+ensemble_to_plot[eee]+'_'+satellite_to_plot[isat]
                header_file = ''
                for i in range(nb_header):
                    if i == nb_header-1:
                        a[i] = a[i].replace("\n","")
                    header_file = header_file + a[i]
                np.savetxt(dir_final_output_ensemble+filename,both_time_ensemble, fmt='%s',header = header_file,comments = '')
            elif ( ensemble_to_plot[eee] != "cd" ):
                for i in range(nProcs):
                    name_file_iproc = satellite_to_plot_path[isat] + 'ensemble/iproc_'+str(i+1)+'-'+str(nProcs)+'_'+ensemble_to_plot[eee]+'_'+satellite_to_plot[isat]
                    file_iproc = open(name_file_iproc,'r') 
                    a = file_iproc.readlines()
                    nb_header = 0 # need to calcaulte nb_header for each file because sometimes SpOCK outptues weird characters in header so add a line
                    while a[nb_header].split()[0] != '#START':
                        nb_header = nb_header + 1
                    nb_header = nb_header +1 
                    nb_steps = len(a) - nb_header # !!!!!!!!!!!this has been added between when computing collisions the time of output stop at end of time spanning TCA

                    if (i == 0):
                        x_alltime_ensemble = np.zeros([nb_ensembles_ok])
                        #ipdb.set_trace()
                    line_count = 0
                    line_iproc[line_count] = (a[nb_header+line_count]).split(' ')
                    for ensemble_temp in range(nb_ensemble_per_proc):
                        ensemble = ensemble_temp + nb_ensemble_per_proc * i
                        x_alltime_ensemble[ensemble] = float( line_iproc[line_count][ensemble_temp+2]  )

                    file_iproc.close()
                    #subprocess.call(['mv', name_file_iproc, satellite_to_plot_path[isat] + 'ensemble/proc_files/'])

                
                
                both_time_ensemble = ["" for x in range(1)]
                str_ensemble = ''
                for j in range(nb_ensembles_ok):
                    str_ensemble = str_ensemble +  str(x_alltime_ensemble[j]) + ' '
                both_time_ensemble[0] =  str_ensemble

                filename = 'ensemble_'+ensemble_to_plot[eee]+'_'+satellite_to_plot[isat]
                header_file = ''
                for i in range(nb_header):
                    if i == nb_header-1:
                        a[i] = a[i].replace("\n","")
                    header_file = header_file + a[i]
                np.savetxt(dir_final_output_ensemble+filename,both_time_ensemble, fmt='%s',header = header_file,comments = '')
            elif ( ensemble_to_plot[eee] != "srp" ):
                for i in range(nProcs):
                    name_file_iproc = satellite_to_plot_path[isat] + 'ensemble/iproc_'+str(i+1)+'-'+str(nProcs)+'_'+ensemble_to_plot[eee]+'_'+satellite_to_plot[isat]
                    file_iproc = open(name_file_iproc,'r') 
                    a = file_iproc.readlines()
                    nb_header = 0 # need to calcaulte nb_header for each file because sometimes SpOCK outptues weird characters in header so add a line
                    while a[nb_header].split()[0] != '#START':
                        nb_header = nb_header + 1
                    nb_header = nb_header +1 
                    nb_steps = len(a) - nb_header # !!!!!!!!!!!this has been added between when computing collisions the time of output stop at end of time spanning TCA

                    if (i == 0):
                        x_alltime_ensemble = np.zeros([nb_ensembles_ok])
                        #ipdb.set_trace()
                    line_count = 0
                    line_iproc[line_count] = (a[nb_header+line_count]).split(' ')
                    for ensemble_temp in range(nb_ensemble_per_proc):
                        ensemble = ensemble_temp + nb_ensemble_per_proc * i
                        x_alltime_ensemble[ensemble] = float( line_iproc[line_count][ensemble_temp+2]  )

                    file_iproc.close()
                    #subprocess.call(['mv', name_file_iproc, satellite_to_plot_path[isat] + 'ensemble/proc_files/'])

                
                
                both_time_ensemble = ["" for x in range(1)]
                str_ensemble = ''
                for j in range(nb_ensembles_ok):
                    str_ensemble = str_ensemble +  str(x_alltime_ensemble[j]) + ' '
                both_time_ensemble[0] =  str_ensemble

                filename = 'ensemble_'+ensemble_to_plot[eee]+'_'+satellite_to_plot[isat]
                header_file = ''
                for i in range(nb_header):
                    if i == nb_header-1:
                        a[i] = a[i].replace("\n","")
                    header_file = header_file + a[i]
                np.savetxt(dir_final_output_ensemble+filename,both_time_ensemble, fmt='%s',header = header_file,comments = '')



        else:
            if isat == 0:
                output_run_dir = '/'.join(satellite_to_plot_path[0].split('/')[0:-2])
                print ensemble_to_plot[eee], iProc_python
                for i in range(nProcs):
                    name_file_iproc =output_run_dir + '/collision/' + ensemble_to_plot[eee] + '/iproc_'+str(i+1)+'-'+str(nProcs)+'_'+ensemble_to_plot[eee]+'_'+ output_run_dir.split('/')[-1] + ".txt"
                    filename = output_run_dir + '/collision/' + ensemble_to_plot[eee] + '/ensemble_'+ensemble_to_plot[eee]+'_'+ output_run_dir.split('/')[-1] + ".txt"
                    os.system("cat " + name_file_iproc + " >> " + filename)
                #     file_iproc =  open(name_file_iproc,'r') 
                #     a = file_iproc.readlines()
                #     x_alltime_ensemble_list = []
                #     for j in range(len(a[0])): # always only one line in dca or tca file
                #         x_alltime_ensemble_list.append(a[0].split()[j])
                #     file_iproc.close()
                #     #subprocess.call(['mv', name_file_iproc, satellite_to_plot_path[isat] + 'ensemble/proc_files/'])

                # both_time_ensemble = ["" for x in range(nb_steps)]
                # for i in range(nb_steps):
                #     str_ensemble = ' '
                #     for j in range(nb_ensembles_ok):
                #         str_ensemble = str_ensemble +  str(x_alltime_ensemble[i][j]) + ' '
                #     both_time_ensemble[i] =  str_ensemble

                # filename = 'ensemble_'+ensemble_to_plot[eee]+'_'+satellite_to_plot[isat]
                # header_file = ''
                # for i in range(nb_header  ):
                #     if i == 10:
                #         a[i] = a[i].replace("\n","")
                #     header_file = header_file + a[i]
                # np.savetxt(dir_final_output_ensemble+filename,both_time_ensemble, fmt='%s',header = header_file,comments = '')

