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
import os
import sys

# list_run = ['more_output_but_no_coll_1126_ok_quartile_f107_1_quartile_ap_1.txt',
#             'more_output_but_no_coll_1126_ok_quartile_f107_2_quartile_ap_2.txt',
#             'more_output_but_no_coll_1126_ok_quartile_f107_3_quartile_ap_3.txt',
#             'more_output_but_no_coll_1126_ok_quartile_f107_4_quartile_ap_4.txt',
#             'more_output_but_no_coll_1126_ok_quartile_f107_5_quartile_ap_5.txt',
#             'more_output_but_no_coll_1126_ok_quartile_f107_6_quartile_ap_6.txt',
#             'more_output_but_no_coll_1126_ok_quartile_f107_7_quartile_ap_7.txt',
#             'more_output_but_no_coll_1126_ok_quartile_f107_8_quartile_ap_8.txt',
#             'more_output_but_no_coll_1126_ok_quartile_f107_9_quartile_ap_9.txt']

list_run = ['just_unperturbed_with_tca_storm_static_32600ens_min_dist_coll_1_2m.txt']
#            'just_unperturbed_with_tca_storm_dynamic_32600ens_min_dist_coll_1_2m.txt']
n = len(list_run)
for i in range(n):
    print i, n-1
    # os.chdir("/raid4/cbv/installation_spock/spock/run_collision/output")
    # os.system("tar -zxvf " + list_run[i].replace(".txt","_out.tar.gz"))

    os.system("/usr/local/bin/mpirun -np 12 python mpi_concatenate_proc.py run_collision " + list_run[i])
    # also mpi_distance_ensemble_to_main_sc
# for plot along cross radial f107 ap runs
    os.system("/usr/local/bin/mpirun -np 12 python mpi_distance_ensemble_to_main_sc.py run_collision " + list_run[i] + " f107 ap rho latitude")#f107 ap rho latitude true_anomaly argument_perigee")

# for collision runs
#    os.system("/usr/local/bin/mpirun -np 12 python mpi_distance_ensemble_to_main_sc.py run_collision " + list_run[i] + " x_eci y_eci z_eci tca dca")
