# This script is a copy paste of gps_tle.py on June 5 2018. It was adapted to include all GNSS satellites: GPS, Galileo, GLONASS, WASS/EGNOS/MSAS, BeiDou-2 + BeiDou-3 (more BeiDou-3 to be operational later)
# This script downloads the GNSS TLEs at the epoch specified by tle_epoch (the TLE right "before" (older than) tle_epoch). The input are the tle epoch and the SpOCK run directory where to store the TLEs. These are given as argumeents of this script
# Methodology: the TLEs are taken from space-track.org. But to do so, you need to put the name of the GNSS that are currently operational. Since I don't know how to find which GNSS are currently operational, I use celestrack.com, which has a link that directly gives the TLEs of the currently operational GNSS. But using this link only forces us to use the latest TLEs. So I use this link only to get the list of the NORAD ID of the current operational GNSS. Then I input this list on space-track.org to get the TLEs for this list for the tle_epoch chosen by the user
# Summary of methodology:
# 1- get latest TLEs of operational GNSS at celestrak
# 2- from the TLEs at celestrak, get the NORAD IDs of the operational GNSS
# 3- download TLEs of these GNSS from space-track for the epoch tle_epoch
# Assumptions:
## - tle_epoch must have the format "YYYY-MM-DD"

import os
from datetime import datetime, timedelta
import sys
import numpy as np

tle_epoch = sys.argv[1] # date of the GNSS TLEs to get # "2017-01-01"

# get latest TLEs of operational GNSS at celestrak     
log_filename = "log_gnss_tle_" + tle_epoch + ".txt"
# GPS
#os.system('wget --no-check-certificate https://www.celestrak.com/NORAD/elements/gps-ops.txt'+ " >> " + log_filename+ " 2>&1") # gps-ops.txt
# Glonass
#os.system('wget --no-check-certificate https://www.celestrak.com/NORAD/elements/glo-ops.txt'+ " >> " + log_filename+ " 2>&1") # glo-ops.txt
# Galileo
#os.system('wget --no-check-certificate https://www.celestrak.com/NORAD/elements/galileo.txt'+ " >> " + log_filename+ " 2>&1") # galileo.txt
# SBAS (= WASS/EGNOS/MSAS)
#os.system('wget --no-check-certificate https://www.celestrak.com/NORAD/elements/sbas.txt'+ " >> " + log_filename+ " 2>&1") # sbas.txt
# Beidou
#os.system('wget --no-check-certificate https://www.celestrak.com/NORAD/elements/beidou.txt'+ " >> " + log_filename+ " 2>&1") # beidou.txt

os.system("cat gps-ops.txt glo-ops.txt galileo.txt sbas.txt beidou.txt > gnss-ops.txt")


# from the TLEs at celestrak, get the NORAD IDs of the operational GNSS 
tle_celestrak = open("gnss-ops.txt")
read_tle_celestrak = tle_celestrak.readlines()
nb_tle = len(read_tle_celestrak) / 3
print nb_tle

norad_id_operational_gnss = []
norad_id_and_prn_operational_gnss = []
for itle in range(nb_tle):
    if 'PRN' in read_tle_celestrak[itle*3+0]: # PRN from 1 to 32
        prn = read_tle_celestrak[itle*3+0][read_tle_celestrak[itle*3+0].index('PRN')+4:read_tle_celestrak[itle*3+0].index('PRN')+6]
    norad_id = read_tle_celestrak[itle*3+2].split()[1]
    norad_id_operational_gnss.append(norad_id)
    norad_id_and_prn_operational_gnss.append([norad_id, prn])
tle_celestrak.close()

# rm file form celestrak
# os.system("rm gnss-ops.txt")

# download TLEs of these GNSS from space-track for the epoch tle_epoch 
## put NORAD ID in link
if ( len(sys.argv) > 2 ): # if the argument 'latest_tle' has been called than do not consider tle_epoch to download the TLE but download the latest TLE from space-track.org. The name of the TLE will still be "gnss_" + tle_epoch + ".txt"
    if ( sys.argv[2] == 'latest_tle' ):
        link_spacetrack = "https://www.space-track.org/basicspacedata/query/class/tle_latest/ORDINAL/1/NORAD_CAT_ID/" + norad_id_operational_gnss[0]
        for itle in range(nb_tle):
            link_spacetrack = link_spacetrack + "," + norad_id_operational_gnss[itle]
        link_spacetrack = link_spacetrack + "/predicates/OBJECT_NAME,TLE_LINE1,TLE_LINE2/format/3le/"
        ## Download with this link
        os.system('wget --no-check-certificate  --post-data="identity=cbv@umich.edu&password=cygnssisawesome" --cookies=on --keep-session-cookies --save-cookies=cookies.txt "https://www.space-track.org/ajaxauth/login" -olog')# !!! can't redirect in windows version > /dev/null 2>&1")
        name_tle = "gnss_" + tle_epoch  + ".txt"
        os.system('wget --no-check-certificate --limit-rate=100K --keep-session-cookies --load-cookies=cookies.txt ' + link_spacetrack + ' -O ' + name_tle)#!!! can't redirect in windows version + " > /dev/null 2>&1")

else:
    link_spacetrack = "https://www.space-track.org/basicspacedata/query/class/tle/NORAD_CAT_ID/" + norad_id_operational_gnss[0]
    for itle in range(nb_tle):
        link_spacetrack = link_spacetrack + "," + norad_id_operational_gnss[itle]

    ## Take all TLEs from tle_epoch minus one month to tle_epoch. We do that because we want the tle right older than tle_epoch. so we get all these tles and save only the most recent one for each gnss. one month is arbitrary but it's to make sure that at least one tle for each gnss was published (usualy they are published about every day so technically don't need to go back a month back)
    tle_epoch_minus_one_month = datetime.strftime(datetime.strptime(tle_epoch, "%Y-%m-%d") - timedelta(days = 10), "%Y-%m-%d")
    link_spacetrack = link_spacetrack + "/EPOCH/" + tle_epoch_minus_one_month + "--" + tle_epoch + "/predicates/OBJECT_NAME,TLE_LINE1,TLE_LINE2/format/3le/"
    ## Order by NORAD ID (each NORAD ahs many TLEs because it's all TLEs since tle_epoch)
    link_spacetrack = link_spacetrack + "orderby/NORAD_CAT_ID/"
    ## Download with this link
    os.system('wget --no-check-certificate  --post-data="identity=cbv@umich.edu&password=cygnssisawesome" --cookies=on --keep-session-cookies --save-cookies=cookies.txt "https://www.space-track.org/ajaxauth/login" -olog'+ " >> " + log_filename)#!!! can't redirect in windows version > /dev/null 2>&1")
    name_tle = "gnss_" + tle_epoch  + "_temp.txt"
    os.system('wget --no-check-certificate --limit-rate=100K --keep-session-cookies --load-cookies=cookies.txt ' + link_spacetrack + ' -O ' + name_tle+ " >> " + log_filename+ " 2>&1")#!!! can't redirect in windows version + " > /dev/null 2>&1")
    ## This TLE file contains too many TLEs for each GNSS. Indeed, for each GNSS, we only want the most recent TLE  of the list (so the TLE right "before" (older than) tle_epoch). But this file is arranged by epoch (in addition to be arranged by NORAD ID). So for each NORAD ID, take only the last TLE
    tle_spacetrack = open(name_tle)
    read_tle_spacetrack = tle_spacetrack.readlines()
    nb_tle = len(read_tle_spacetrack) / 3
    name_new_tle = "gnss_" + tle_epoch  + ".txt"
    new_tle_spacetrack_name = name_new_tle
    new_tle_spacetrack = open(name_new_tle, "w+")
    read_new_tle_spacetrack = new_tle_spacetrack.readlines()
    itle = 0
    cou = 0
    while itle < nb_tle:
        current_norad = read_tle_spacetrack[itle*3+2].split()[1]
        new_norad = current_norad
        while new_norad == current_norad:
            itle = itle + 1
            if (itle < nb_tle):
                new_norad = read_tle_spacetrack[itle*3+2].split()[1]
                norad_id_operational_gnss.append(read_tle_spacetrack[itle*3+2].split()[1])
            else:
                break
        if itle < nb_tle+1:
            print >> new_tle_spacetrack, read_tle_spacetrack[(itle-1)*3].replace("\r", "").replace("\n", "")
            print >> new_tle_spacetrack, read_tle_spacetrack[(itle-1)*3+1].replace("\r", "").replace("\n", "")
            print >> new_tle_spacetrack, read_tle_spacetrack[(itle-1)*3+2].replace("\r", "").replace("\n", "")


    tle_spacetrack.close()
    new_tle_spacetrack.close()

    # rm the spacetrack tle file with all tles (the one that for each gnss has all tles between tle_epoch minus a month and tle_epoch)
    #os.system("rm -f " + name_tle+ " >> " + log_filename)
    os.system("rm -f login cookies.txt log"+ " >> " + log_filename)


# CAN'T DO THE PRN STUFF BELOW BECAUSE NOT ALL GNSS HAVE A PRN
# # Nor add the PRN of each GNSS on the first line (before the name of the GNSS)
# new_tle_spacetrack_name_with_prn = name_new_tle
# new_tle_spacetrack_name_without_prn = name_new_tle.replace('.txt', '_without_prn.txt')
# os.system("cp " + name_new_tle + " " + new_tle_spacetrack_name_without_prn)
# new_tle_spacetrack_without_prn = open(new_tle_spacetrack_name_without_prn, "r")
# read_new_tle_spacetrack_without_prn = new_tle_spacetrack_without_prn.readlines()
# nb_tle = len(read_new_tle_spacetrack_without_prn) / 3
# new_tle_spacetrack_with_prn = open(new_tle_spacetrack_name_with_prn, "w+")
# read_new_tle_spacetrack_with_prn = new_tle_spacetrack_with_prn.readlines()
# norad_id_and_prn_operational_gnss_arr = np.array(norad_id_and_prn_operational_gnss)
# for itle in range( nb_tle):
#     norad_id = read_new_tle_spacetrack_without_prn[itle*3+2].split()[1]
#     where_prn = np.where(norad_id_and_prn_operational_gnss_arr == norad_id)[0][0]
#     prn = norad_id_and_prn_operational_gnss_arr[where_prn, 1]
#     print >> new_tle_spacetrack_with_prn, 'PRN ' + prn, read_new_tle_spacetrack_without_prn[itle*3].replace('\n','')
#     print >> new_tle_spacetrack_with_prn, read_new_tle_spacetrack_without_prn[itle*3+1].replace('\n','')
#     print >> new_tle_spacetrack_with_prn, read_new_tle_spacetrack_without_prn[itle*3+2].replace('\n','')
    

# new_tle_spacetrack_with_prn.close()
# new_tle_spacetrack_without_prn.close()

# os.system("rm -f " + new_tle_spacetrack_name_without_prn)
