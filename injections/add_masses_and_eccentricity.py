import numpy as np
import h5py
from pycbc import conversions
import sys

filename = sys.argv[1]
if filename == []:
	sys.exit('Please provide a injection (.hdf) file')

else:
	hf = h5py.File(filename, 'r+')

	# List of parameter values to choose from
	m1_list = np.array([1.4, 5.5, 6.0, 7.0])
	m2_list = np.array([1.4, 1.1, 2.0, 2.0])
	ecc_list = np.array([0.0, 0.05, 0.1, 0.2, 0.27, 0.29])
	
	#m1_list = np.array([1.2, 1.4, 3.0, 5.5, 6.0, 7.0])
	#m2_list = np.array([1.2, 1.4, 3.0, 1.1, 2.0, 2.0])
	#ecc_list = np.array([0.0, 0.05, 0.1, 0.15, 0.2, 0.27, 0.29])

	# Assign the injections above values randomly
	ninjs = len(hf['spin1z'][:])
	rand_val = np.random.randint(0, 4, ninjs)
	mass1 = m1_list[rand_val]	
	mass2 = m2_list[rand_val]	

	rand_ecc = np.random.randint(0, 6, ninjs)
	eccentricity = ecc_list[rand_ecc]
	mchirp = conversions.mchirp_from_mass1_mass2(mass1, mass2)

	#Get distance from chirp_distance
	chirp_distance = hf['chirp_distance'][:]
	distance = conversions.distance_from_chirp_distance_mchirp(chirp_distance, mchirp)

	# Add remaining params to the injection file
	with hf:
		hf.create_dataset("mass1", data=mass1)
		hf.create_dataset("mass2", data=mass2)
		hf.create_dataset("eccentricity", data=eccentricity)
		hf.create_dataset("distance", data=distance)
	hf.close()

	print('mass1, mass2, eccentricity and distance added to', filename)
