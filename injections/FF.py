import pycbc
import numpy as np
import matplotlib.pyplot as plt
from pycbc import waveform, psd, filter, conversions
import sys
import h5py
import time
import math

def generate_templates(bank):
	start = time.time()
	hf = h5py.File(bank)
	m1 = hf['mass1'][:]
	m2 = hf['mass2'][:]
	s1z = hf['spin1z'][:]
	s2z = hf['spin2z'][:]
	ecc = hf['eccentricity'][:]
	tb_tau0 = hf['tau0'][:] 

	templates = []
	for k in range(len(m1)):                  ## Change this
		hp, hc = waveform.get_fd_waveform(approximant = 'TaylorF2Ecc',
											mass1 = m1[k],
											mass2 = m2[k],
											spin1z = s2z[k],
											spin2z = s1z[k],
											eccentricity = ecc[k],
											delta_f = 1.0/64,
											f_lower = 20.0)
		templates.append(hp)
	end = time.time()
	print('Total', len(templates), 'templates generated in ', end-start)
	return m1, m2, tb_tau0, templates

def generate_injection(m1, m2, s1z, s2z, ecc):
	hp, hc = waveform.get_td_waveform(approximant = 'EccentricTD',
										mass1 = m1,
										mass2 = m2,
										spin1z = s2z,
										spin2z = s1z,
										eccentricity = ecc,
										delta_t = 1.0/2048,
										f_lower = 20.0)
	return hp.to_frequencyseries(delta_f=1.0/64), hc.to_frequencyseries(delta_f=1.0/64)

def find_nearest(array,value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return idx-1
    else:
        return idx

def find_template_indices(tb_tau0, inj_tau0, tau0_threshold):
	low = inj_tau0 - tau0_threshold
	low_ind = find_nearest(tb_tau0, low)
	high = inj_tau0 + tau0_threshold
	high_ind = find_nearest(tb_tau0, high)

	indices = np.array(range(low_ind, high_ind+1))	
	return indices

def compute_matches(bank_m1, bank_m2, tb_tau0, templates, injections):
	hf = h5py.File(injections)
	m1 = hf['mass1'][:]
	m2 = hf['mass2'][:]
	s1z = hf['spin1z'][:]
	s2z = hf['spin2z'][:]
	ecc = hf['eccentricity'][:]
	print('Total injections ', len(m1))

	PSD = pycbc.psd.analytical.aLIGOZeroDetHighPower(int(64*2048), 1.0/64, 20.0)

	FF = []
	for inj in range(len(m1)):
		injp, injc = generate_injection(m1[inj], m2[inj], s1z[inj], s2z[inj], ecc[inj])
		injp.resize(len(PSD))
		
		inj_tau0 = conversions.tau0_from_mass1_mass2(m1[inj], m2[inj], 20.0)
		indices = find_template_indices(tb_tau0, inj_tau0, tau0_threshold)
		print(len(indices), ' templates for inj', inj)

		matches = []
		start = time.time()
		for k in indices:
			templates[k].resize(len(PSD))
			temp_match = filter.match(templates[k], injp, psd=PSD, low_frequency_cutoff=20.0)[0]
			matches.append(temp_match)
		end = time.time()
		best_temp = indices[np.argmax(matches[inj])]
		FF.append(np.max(matches))

		print(inj, 'inj done', 'FF = ', FF[inj], 'Inj tau0', inj_tau0, 'template tau0', tb_tau0[best_temp], 'in', end-start)
	return FF 


tau0_threshold = 0.5

bank = '/work/rahul.dhurkunde/searches/eccentric-bns-search/banks/spinecc/mtotal-10_ecc-0.28_spin-0.1/small_bank_sorted.hdf'
inj_file = sys.argv[1]
print("!!! Check the files !!! \n \t", bank, '\n \t', inj_file)

bank_m1, bank_m2, tb_tau0, templates = generate_templates(bank)

FF = compute_matches(bank_m1, bank_m2, tb_tau0, templates, inj_file)
np.savetxt('matches.txt', matches)
