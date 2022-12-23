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
	m1_list = [1.0, 1.4, 3.0, 4.0, 2.0, 5.0, 6.0, 6.0, 7.0, 8.9]
	m2_list = [1.0, 1.4, 3.0, 4.0, 1.0, 1.0, 1.0, 2.0, 2.0, 1.9]
	ecc_list = np.random.uniform(0.0, 0.2, 50)

	# Assign the injections above values randomly
	ninjs = len(hf['spin1z'][:])
	mass1 = np.random.choice(m1_list, ninjs)	
	mass2 = np.random.choice(m2_list, ninjs)	
	eccentricity = np.random.choice(ecc_list, ninjs)

	# Add remaining params to the injection file
	with hf:
		hf.create_dataset("mass1", data=mass1)
		hf.create_dataset("mass2", data=mass2)
		hf.create_dataset("eccentricity", data=eccentricity)
	hf.close()

	print('mass1, mass2, eccentricity added to', filename)
