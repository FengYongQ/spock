# This script creates the input-params.txt used in sat-bop
# Inputs:
# - start_time (%Y-%m-%dT%H:%M:%S)
# - end_time
# - cygfm (1 to 8)

import ipdb
from pathlib import Path
def cygnss_beacon_write_input_satbop(start_time, end_time, cygfm):
    start_time_dd = start_time[0:10].replace('-', '/')
    start_time_hh = start_time[11:]

    end_time_dd = end_time[0:10].replace('-', '/')
    end_time_hh = end_time[11:]

    gps_tle_filename = 'gps_' + start_time[0:10] + '_beacon.txt'
    cygnss_tle_filename = 'CYGFM0' + str(cygfm) + '_' + start_time[0:10] + '.txt'

    output_dir = start_time[0:10].replace('-', '') + '_' + end_time[0:10].replace('-', '') + '_fm0' + str(cygfm) + '/'
    filename_input = 'input-params.txt'

    file_input = open(filename_input, 'w')
    print >> file_input, '; Satellite Beacon Overpass Planner Input Parameters\n\
\n\
; Start of planning period, UTC\n\
start_date=' + start_time_dd + '\n\
start_time=' + start_time_hh + '\n\
\n\
; End of planning period, UTC\n\
end_date=' + end_time_dd + '\n\
end_time=' + end_time_hh + '\n\
\n\
; Beacon latitude, +/-deg N, 0-90\n\
beacon_lat=32.86843\n\
\n\
; Beacon longitude, +/-deg E, 0-180\n\
beacon_long=-106.12885\n\
\n\
; Beacon altitude, WGS-84, km\n\
beacon_alt=1.21559\n\
\n\
 Minimum rx satellite elevation, degrees\n\
 Overpasses must achieve at least this elevation\n\
 angle to be considered acceptable.\n\
min_elev_angle=60.0\n\
\n\
; GPS TLE file path. May be relative to the current directory or\n\
;  absolute. Always use / as directory delimiter (even on Windows).\n\
;  Defaults to the current working directory.\n\
gps_tle_file_path=' + gps_tle_filename + '\n\
\n\
; Rx satellite TLE file path. May be relative to the current directory or\n\
;  absolute. Always use / as directory delimiter (even on Windows).\n\
;  Defaults to the current working directory.\n\
rx_sat_tle_file_path=' + cygnss_tle_filename + '\n\
\n\
; Output directory. May be relative to the current directory or\n\
;  absolute. Always use / as directory delimiter (even on Windows).\n\
;  Defaults to the current working directory.\n\
output_directory=' + output_dir[:-1] + '\n' #[:-1] to remove the '/' at the end


    file_input.close()
    return cygnss_tle_filename, gps_tle_filename, output_dir
