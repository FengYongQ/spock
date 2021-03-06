# This script creates the input-params.txt used in beacon-sig-gen
# Inputs:
# - PRN csv filename (with path)
# - sp3 filename (with path) 

import ipdb
from pathlib import Path
def cygnss_beacon_write_input_waveform(csv_filename, sp3_filename):

    # csv_filename = 'PRN_20_eeeeetruncated.csv'
    # sp3_filename = 'ieeeeeegs20254.sp3'
    output_dir =  csv_filename.replace('.csv','_') + sp3_filename.replace('.sp3','')
    filename_input = 'input-params.txt'

    file_input = open(filename_input, 'w')
    print >> file_input, "; TDS Beacon Signal Generator Input Parameters\n\
\n\
; Operation Mode\n\
; Determines the way in which the paths between receiver,\n\
; transmitter and specular point are used to affect the\n\
; total delay and Doppler\n\
; 1 = standard operation mode\n\
; 2 = bench top mode: ignore path between beacon and receiver\n\
; 3 = static mode: ignore all delay and Doppler due to geometry\n\
operation_mode=2\n\
\n\
; Center frequency, MHz\n\
center_freq=1575.42\n\
\n\
; Waveform output file signal strength scale factor (0.0 to 1.0)\n\
wave_output_scale_factor=0.5\n\
\n\
; Waveform output sample rate (MHz)\n\
sample_rate=5.0\n\
\n\
; Big endian output file byte order\n\
; True for big endian, false for little endian\n\
; (This switch currently doesn't control anything. Maybe later.))\n\
big_endian=false\n\
\n\
; Overpass CSV file path. This file is created by the TDS-1 Beacon\n\
;  Overpass Planner (tds-bop) application and is named pass_N.csv, where\n\
;  N is the tds-bop pass number.\n\
; The file path may be relative to the currrent directory or\n\
;  absolute. Always use / as directory delimiter (even on Windows).\n\
;  Defaults to the current working directory.\n\
pass_csv_file_path=" + csv_filename + "\n\
\n\
; DDM test pattern file path. May be relative to the current directory or\n\
;  absolute. Always use / as directory delimiter (even on Windows).\n\
;  Defaults to the current working directory.\n\
ddm_pattern_file_path=pattern_goodvibes_v2.bin\n\
\n\
; SP3 file path. This is the most recent SP3 file available from the IGS\n\
;  FTP server at ftp://igscb.jpl.nasa.gov/pub/product/\n\
;  Note that the SP3 files on the ftp server are compressed and must\n\
;  be decompressed (unzipped) for beacon-sig-gen usage.\n\
; May be relative to the currrent directory or\n\
;  absolute. Always use / as directory delimiter (even on Windows).\n\
;  Defaults to the current working directory.\n\
sp3_file_path=" + sp3_filename + "\n\
\n\
; Output file directory. All the files created by beacon-sig-gen are\n\
;  written to this directory.\n\
;  May be relative to the currrent directory or\n\
;  absolute. Always use / as directory delimiter (even on Windows).\n\
;  Defaults to the current working directory.\n\
output_directory=" + output_dir + "\n\
\n\
; Fiducial delay (seconds)\n\
;  The fiducial is an absence of reflected GPS power in the waveform.\n\
;  The fiducial delay is the number of seconds between the start of\n\
;  transmission and the start of the fiducial.\n\
fiducial_delay=0\n\
\n\
; Fiducial duration (seconds)\n\
fiducial_duration=0\n"

    file_input.close()
    return output_dir
