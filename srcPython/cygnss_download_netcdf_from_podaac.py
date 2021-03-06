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

# This scriptdownloads L1 netcdf files from
# https://podaac-tools.jpl.nasa.gov/drive/files/allData/cygnss/L1/v2.1
# inputs: date_start, date_stop, cygfm, save_dir


import os
from datetime import datetime, timedelta

date_start = '2019-04-09' # 
date_stop = '2019-04-14'
#'2018-10-16' '2018-10-24' Oct 16-25 2018
#'2018-11-06' '2018-11-14' Nov 6-Nov 15 2018
#'2018-12-18' '2018-12-26' Dec 18-25 2018
#'2019-01-10' '2019-01-18' Jan 10-19 2019
#'2019-02-17' '2019-02-25' Feb 17-26 2019
#'2019-03-20' '2019-03-28' Mar 20-29 2019
#'2019-04-15' '2019-04-23' Apr 15-24 2019
#'2019-05-15' '2019-05-23' May 15-24 2019
#'2019-06-15' '2019-06-23' JJun 15-24 2019
#'2019-07-15' '2019-07-23' Jul 15-24 2019
#'2019-08-15' '2019-08-23' Aug 15-24 2019

podaac_path = "https://podaac-tools.jpl.nasa.gov/drive/files/allData/cygnss/L1/v2.1/"#!!!!!! before 072919 used to be "ftp://podaac.jpl.nasa.gov/allData/cygnss/L1/v2.1/" but then podaac stopped the ftp option
save_dir = '/Users/cbv/cygnss/netcdfPodaac/'#'/Volumes/Seagate_Expansion_Drive/netcdf/' 

#cygfm = 1 # 1 to 8
# '/Users/cbv/cygnss/netcdf/' # with slash at the end. the year
# will be added as a sub-directory


date_start_date = datetime.strptime(date_start, "%Y-%m-%d")
date_stop_date = datetime.strptime(date_stop, "%Y-%m-%d")


date_here = date_start_date
while date_here <= date_stop_date:
    yy = date_here.strftime('%Y')
    doy = date_here.strftime('%j')

    if (os.path.isdir(save_dir + yy + '/' + str(doy).zfill(3)) == False):
        os.system("mkdir " + save_dir + yy + '/' + str(doy).zfill(3))
    icygfm = -1
    for cygfm in range(3, 4):
        icygfm = icygfm + 1
        if icygfm == 0:
            name_netcdf_podaac = []
            name_netcdf_local = []
            list_netcdf = []
            list_cyg = []
            filename_list =  save_dir + yy + '/'  + str(doy).zfill(3) +\
            '/index.html'
            os.system("wget --user=charlesbv --password=OfTUKtBGYkZLdIeC2@m " + podaac_path +yy + '/'  + str(doy).zfill(3) + "/ -O " + filename_list)
            #os.system("wget " + podaac_path +
                      #yy + '/'  + str(doy).zfill(3) + "/ -O " + filename_list)
            file_list = open(filename_list)
            r_file_list = file_list.readlines()
            n = len(r_file_list)
            for i in range(n):
                l = r_file_list[i]
                if '.nc</a>' in l:
                    name_netcdf_podaac.append(l.split('href=')[1].split('>')[0])
                    name_netcdf_local.append( save_dir + yy + '/'  + \
                        str(doy).zfill(3) + '/' + \
                        name_netcdf_podaac[-1].split('/')[-1][:-1] )
                    list_netcdf.append(name_netcdf_local)
                    list_cyg.append(\
                    name_netcdf_local[-1].split('cyg0')[1].split('.')[0])
        if (str(cygfm) in list_cyg) == True: # if file exists
            index_list = list_cyg.index(str(cygfm))
            # print "wget " + name_netcdf_podaac[index_list] +\
            #     " -O " + name_netcdf_local[index_list] 
            os.system( "wget --user=charlesbv --password=OfTUKtBGYkZLdIeC2@m https://podaac-tools.jpl.nasa.gov/" + name_netcdf_podaac[index_list] + \
                " -O " + name_netcdf_local[index_list] )
    date_here = date_here + timedelta(days = 1)
