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
np.set_printoptions(formatter={'float': '{: .3e}'.format}, threshold=np.nan)

# !!!!!!! MATRICES ARE IN M AND M/S

# Covariances matrices in ECI
mat_sc1 = [[ 6494.0796232671000000000000, -376.1385833452400000000000, 0.0000000000000000000000, 0.0159894841672130000000, -0.4942616773297700000000, 0.0000000000000000000000 ],

[ -376.1385833452400000000000, 22.5594651948940000000000, 0.0000000000000000000000, -0.0009883140442375300000, 0.0285694605771430000000, 0.0000000000000000000000 ],

[ 0.0000000000000000000000, 0.0000000000000000000000, 1.2050395223076000000000, 0.0000000000000000000000, 0.0000000000000000000000, -0.0000607087634449250000 ],

[ 0.0159894841672130000000, -0.0009883140442375300000,  0.0000000000000000000000,  0.0000000443727501925020, -0.0000012122341939459000, 0.0000000000000000000000], 

[-0.4942616773297700000000, 0.0285694605771430000000, 0.0000000000000000000000, -0.0000012122341939459000, 0.0000376229760367290000, 0.0000000000000000000000],

[ 0.0000000000000000000000, 0.0000000000000000000000, -0.0000607087634449250000, 0.0000000000000000000000, 0.0000000000000000000000,  0.0000000033903900107678 ] ]

# mat_sc1 = [[ 4, 4, 2, 3, -2,0],
# [0, 1, -2, -2, 2,0],
# [6, 12, 11, 2, -4,0],
# [9, 20, 10, 10, -6,0],
# [15, 28, 14, 5, -3,0],
# [0,0,0,0,0,1]]

mat_sc1 = np.array(mat_sc1)


mat_sc2 = [ [ 6494.2249318545000000000000, -376.1561166537300000000000, -0.0000449172919882650000, 0.0159921727609040000000, -0.4942721017592600000000, -0.0000000590183593374380 ],

[ -376.1561166537300000000000, 22.5606458218830000000000, 0.0000025501472714422000, -0.0009884645809796500000, 0.0285707587266520000000, 0.0000000034187295427319 ],

[-0.0000449172919882650000, 0.0000025501472714422000, 1.2046746471441000000000, -0.0000000001180334503685, 0.0000000034189216426795, -0.0000607153456131910000 ],

[ 0.0159921727609040000000, -0.0009884645809796500000, -0.0000000001180334503685, 0.0000000443830127867320, -0.0000012124371638594000, -0.0000000000001447705672 ],

[ -0.4942721017592600000000,  0.0285707587266520000000, 0.0000000034187295427319, -0.0000012124371638594000, 0.0000376237233528210000, 0.0000000000044920403553 ],

[ -0.0000000590183593374380, 0.0000000034187295427319, -0.0000607153456131910000, -0.0000000000001447705672, 0.0000000000044920403553, 0.0000000033920803457708 ] ]

mat_sc2 = np.array(mat_sc2)

# Diagonalization of the covariances matrices
# result_diag_mat_sc1 = np.linalg.eig(mat_sc1)
# mat_sc1_diagnoalized = np.identity(6) * result_diag_mat_sc1[0]
# mat_rot_sc1 = result_diag_mat_sc1[1]
# mat_rot_sc1_invert = np.linalg.inv(mat_rot_sc1)
# # # Check 
# # mat_temp_sc1 = mat_sc1.dot(mat_rot_sc1)
# # mat_rot_sc1_invert.dot(mat_temp_sc1) # should be equal to mat_sc1_diagnoalized (with small errors)

# result_diag_mat_sc2 = np.linalg.eig(mat_sc2)
# mat_sc2_diagnoalized = np.identity(6) * result_diag_mat_sc2[0]
# mat_rot_sc2 = result_diag_mat_sc2[1]
# mat_rot_sc2_invert = np.linalg.inv(mat_rot_sc2)
lambda_sc1, mat_rot_sc1 = np.linalg.eig(mat_sc1)
mat_sc1_diagnoalized = np.identity(6) * lambda_sc1 
mat_rot_sc1_invert = np.linalg.inv(mat_rot_sc1)
#print lambda_sc1
print mat_rot_sc1_invert
print ""
#print mat_rot_sc2_invert


lambda_sc2, mat_rot_sc2 = np.linalg.eig(mat_sc2)
mat_sc2_diagnoalized = np.identity(6) * lambda_sc2 
mat_rot_sc2_invert = np.linalg.inv(mat_rot_sc2)
#print lambda_sc2
print mat_rot_sc2_invert
#print mat_rot_sc2_invert
# # Check 
# mat_temp_sc2 = mat_sc2.dot(mat_rot_sc2)
# mat_rot_sc2_invert.dot(mat_temp_sc2) # should be equal to mat_sc2_diagnoalized (with small errors)       


raise Exception



# INITIAL POSITIONS AND VELOCITIES IN ECI !!!!!!!!! IN M AND M/S
## SC1
r_eci_sc1 = [153446.7645602800, 41874155.8695660000, 0.0000000000 ]
v_eci_sc1 = [3066.8747609105, -11.3736149565, 0.0000000000 ]

r_eci_sc1 = np.array(r_eci_sc1)
v_eci_sc1 = np.array(v_eci_sc1)

## SC2
r_eci_sc2 = [153447.2642029000, 41874156.3699030000, 4.9999660258]
v_eci_sc2 = [3066.8647607073, -11.3636148179, -0.0000013581]

r_eci_sc2 = np.array(r_eci_sc2)
v_eci_sc2 = np.array(v_eci_sc2)

# CONVERT DIAGONAL ELEMENTS OF DIAGONALIZED MATRICES TO ECI 
sigma_sc1_in_diagonal_basis = result_diag_mat_sc1[0]
sigma_sc1_in_eci = mat_rot_sc1_invert.dot(sigma_sc1_in_diagonal_basis)

sigma_sc2_in_diagonal_basis = result_diag_mat_sc2[0]
sigma_sc2_in_eci = mat_rot_sc2_invert.dot(sigma_sc2_in_diagonal_basis)

# PRINT RESULTS IN KM AND KM/S (UNITS OF SpOCK)
print "SC1"
print '(' + '{0:.26f}'.format(r_eci_sc1[0]/1000.) + '; ' + '{0:.26f}'.format(r_eci_sc1[1]/1000.) + '; ' + '{0:.26f}'.format(r_eci_sc1[2]/1000.) + ') ' +   '(' + '{0:.26f}'.format(v_eci_sc1[0]/1000.) + '; ' + '{0:.26f}'.format(v_eci_sc1[1]/1000.) + '; ' + '{0:.26f}'.format(v_eci_sc1[2]/1000.) + ')'
print '(' + '{0:.26f}'.format(sigma_sc1_in_eci[0]/1000.) + '; ' + '{0:.26f}'.format(sigma_sc1_in_eci[1]/1000.) + '; ' + '{0:.26f}'.format(sigma_sc1_in_eci[2]/1000.) + ') ' +   '(' + '{0:.26f}'.format(sigma_sc1_in_eci[3]/1000.) + '; ' + '{0:.26f}'.format(sigma_sc1_in_eci[4]/1000.) + '; ' + '{0:.26f}'.format(sigma_sc1_in_eci[5]/1000.) + ')'

print "\nSC2"
print '(' + '{0:.26f}'.format(r_eci_sc2[0]/1000.) + '; ' + '{0:.26f}'.format(r_eci_sc2[1]/1000.) + '; ' + '{0:.26f}'.format(r_eci_sc2[2]/1000.) + ') ' +   '(' + '{0:.26f}'.format(v_eci_sc2[0]/1000.) + '; ' + '{0:.26f}'.format(v_eci_sc2[1]/1000.) + '; ' + '{0:.26f}'.format(v_eci_sc2[2]/1000.) + ')'
print '(' + '{0:.26f}'.format(sigma_sc2_in_eci[0]/1000.) + '; ' + '{0:.26f}'.format(sigma_sc2_in_eci[1]/1000.) + '; ' + '{0:.26f}'.format(sigma_sc2_in_eci[2]/1000.) + ') ' +   '(' + '{0:.26f}'.format(sigma_sc2_in_eci[3]/1000.) + '; ' + '{0:.26f}'.format(sigma_sc2_in_eci[4]/1000.) + '; ' + '{0:.26f}'.format(sigma_sc2_in_eci[5]/1000.) + ')'




########## AT EPOCH 
mat_sc1_at_epoch = [[ 0.0571252902397250000000, -0.0237273881030220000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000 ],
[ -0.0237273881030220000000, 0.0728747097602750000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000 ],
[0.0000000000000000000000, 0.0000000000000000000000, 0.0400000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000],
[0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000,0.0000000100000000000000, 0.0000000000000000000000, 0.0000000000000000000000],[ 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000100000000000000 , 0.0000000000000000000000], 
[ 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000100000000000000 ]]

mat_sc2_at_epoch = [[ 0.0571350527281940000000, -0.0237306258748420000000, -0.0000000028335521063916, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000 ],
[ -0.0237306258748420000000, 0.0728649472718050000000, 0.0000000039242344917333, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000 ],
[-0.0000000028335521063916, 0.0000000039242344917333, 0.0400000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000],
[0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000,0.0000000100000000000000, 0.0000000000000000000000, 0.0000000000000000000000],[ 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000100000000000000 , 0.0000000000000000000000], 
[ 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000000000000000000, 0.0000000100000000000000 ]]


r_eci_sc1_at_epoch = [-33552459.2740560000, -23728303.0480150000, 0.0000000000]
v_eci_sc1_at_epoch = [-1828.9971793970, 2534.1074695609, 0.0000000000]
r_eci_sc1_at_epoch = np.array(r_eci_sc1_at_epoch)
v_eci_sc1_at_epoch = np.array(v_eci_sc1_at_epoch)


r_eci_sc2_at_epoch = [-33547125.4859640000, -23734789.4461360000, -2.8340295187]
v_eci_sc2_at_epoch = [-1829.5395947473, 2533.7604928826, 0.0003025433]
r_eci_sc2_at_epoch = np.array(r_eci_sc2_at_epoch)
v_eci_sc2_at_epoch = np.array(v_eci_sc2_at_epoch)


print "SC1 AT EPOCH"
print '(' + '{0:.26f}'.format(r_eci_sc1_at_epoch[0]/1000.) + '; ' + '{0:.26f}'.format(r_eci_sc1_at_epoch[1]/1000.) + '; ' + '{0:.26f}'.format(r_eci_sc1_at_epoch[2]/1000.) + ') ' +   '(' + '{0:.26f}'.format(v_eci_sc1_at_epoch[0]/1000.) + '; ' + '{0:.26f}'.format(v_eci_sc1_at_epoch[1]/1000.) + '; ' + '{0:.26f}'.format(v_eci_sc1_at_epoch[2]/1000.) + ')'

print "SC2 AT EPOCH"
print '(' + '{0:.26f}'.format(r_eci_sc2_at_epoch[0]/1000.) + '; ' + '{0:.26f}'.format(r_eci_sc2_at_epoch[1]/1000.) + '; ' + '{0:.26f}'.format(r_eci_sc2_at_epoch[2]/1000.) + ') ' +   '(' + '{0:.26f}'.format(v_eci_sc2_at_epoch[0]/1000.) + '; ' + '{0:.26f}'.format(v_eci_sc2_at_epoch[1]/1000.) + '; ' + '{0:.26f}'.format(v_eci_sc2_at_epoch[2]/1000.) + ')'



