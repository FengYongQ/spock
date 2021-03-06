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

import numpy as np
from sgp4.earth_gravity import wgs72old
from sgp4.io import twoline2rv

filename_tle = "/Users/cbv/cygnss_2017-03-20.txt"
file_tle = open(filename_tle)
read_file_tle = file_tle.readlines()
line1 = read_file_tle[0].replace("\r", "").replace("\n","") 
line2 = read_file_tle[1].replace("\r", "").replace("\n","")
sc_tle = twoline2rv(line1, line2, wgs72old)
r_eci_tle, v_eci_tle = sc_tle.propagate( sc_tle.epoch.year, sc_tle.epoch.month, sc_tle.epoch.day, sc_tle.epoch.hour, sc_tle.epoch.minute, sc_tle.epoch.second ) 

print r_eci_tle
