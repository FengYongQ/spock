# This script converts the ENG_PVT and ENG_ADCS files into SpOCK r/v measurement (for the Kalman filter) and  attittude readible files.
# ASSUMPTIONS:
# - ENG_PVT is in m and m/s
# - quaternions are same convention as in SpOCK

import sys
import numpy as np

# r/v
filename_to_convert = sys.argv[1]
file_to_convert = open(filename_to_convert)
filename_converted = '/'.join(filename_to_convert.split('/')[:-1]) + '/spock_' + filename_to_convert.split('/')[-1]
file_converted = open(filename_converted, "w")
read_file_to_convert = file_to_convert.readlines()

nb_skip = 1
nb_time_to_convert = len(read_file_to_convert) - nb_skip
nb_col = 9 # if the r/v is reported correctly at a given time, there should be 9 coluns. otherwise, ignore this time
print >> file_converted, "#Date position(km/s) velocity(km/s)\n#START"
for iline in range(nb_time_to_convert):
    nb_col_now = len(read_file_to_convert[iline + nb_skip].split())
    if (nb_col_now == nb_col):
        flag = read_file_to_convert[iline + nb_skip].split()[nb_col-1]
        if flag == '2': # if flag other than 2 hten ignore data for this time
            x = np.float(read_file_to_convert[iline + nb_skip].split()[2])/1000.
            y = np.float(read_file_to_convert[iline + nb_skip].split()[3])/1000.
            z = np.float(read_file_to_convert[iline + nb_skip].split()[4])/1000.
            vx = np.float(read_file_to_convert[iline + nb_skip].split()[5])/1000.
            vy = np.float(read_file_to_convert[iline + nb_skip].split()[6])/1000.
            vz = np.float(read_file_to_convert[iline + nb_skip].split()[7])/1000.
            print >> file_converted,  read_file_to_convert[iline + nb_skip].split()[1], format(x, ".15f") ,format(y, ".15f"),format(z, ".15f"),format(vx, ".15f"),format(vy, ".15f"),format(vz, ".15f")

file_converted.close()


# attitude
filename_to_convert = sys.argv[2]
file_to_convert = open(filename_to_convert)
filename_converted = '/'.join(filename_to_convert.split('/')[:-1]) + '/spock_' + filename_to_convert.split('/')[-1]
file_converted = open(filename_converted, "w")
read_file_to_convert = file_to_convert.readlines()

nb_skip = 1
nb_time_to_convert = len(read_file_to_convert) - nb_skip
nb_col = 7 # if the attitude is reported correctly at a given time, there should be 7 coluns. otherwise, ignore this time
print >> file_converted, "#BEGINNINGOFHEADER\n#ENDOFHEADER"
for iline in range(nb_time_to_convert):
    nb_col_now = len(read_file_to_convert[iline + nb_skip].split())
    if (nb_col_now == nb_col):
        flag = read_file_to_convert[iline + nb_skip].split()[nb_col-1]
        if flag == '0': # if flag other than 0 hten ignore data for this time
            print >> file_converted,  read_file_to_convert[iline + nb_skip].split()[1], read_file_to_convert[iline + nb_skip].split()[2], read_file_to_convert[iline + nb_skip].split()[3], read_file_to_convert[iline + nb_skip].split()[4], read_file_to_convert[iline + nb_skip].split()[5]  

print >> file_converted, "#ENDOFFILE"
file_converted.close()
