#!/usr/bin/env python3

import pycbc
import numpy as np
from pycbc import filter, waveform, psd, conversions, detector
import sys
import h5py
from tqdm import tqdm
import argparse as ap

def gen_waveform(mass1, mass2, dec, ra, polarization, coa_phase, inclination, distance, delta_f, f_low, psd_list):	
	hp, hc = waveform.waveform.get_fd_waveform(approximant='IMRPhenomD',
													mass1=mass1,
													mass2=mass2,
													coa_phase=coa_phase,
													inclination=inclination,
													delta_f=delta_f,
													f_lower=f_low,
													f_ref=10.0,
													distance=distance)

	det_signal = {}
	tc = 1253977249.2340147
	det_list = ['H1', 'L1', 'V1', 'K1', 'I1']

	for k in range(len(psd_list)):
		ifo = det_list[k]
		detect = detector.Detector(ifo)
		fx, fy = detect.antenna_pattern(ra, dec, polarization, tc)
		det_signal[ifo] = hp*fx + hc*fy
	return det_signal

def read_injs(filename, distance_cutoff):
	hf = h5py.File(filename, 'r')
	mass1 = np.array(hf['mass1'][:])
	mass2 = np.array(hf['mass2'][:])
	dec = np.array(hf['dec'][:])
	ra = np.array(hf['ra'][:])
	polarization = np.array(hf['polarization'][:])
	coa_phase = np.array(hf['coa_phase'][:])
	inclination = np.array(hf['inclination'][:])
	distance = np.array(hf['distance'][:])
	eccentricity = np.array(hf['eccentricity'][:])
	if distance_cutoff == None:
		valid_ind = np.array(range(len(mass1)))
	else:
		valid_ind = np.where(distance < distance_cutoff)[0]

	return mass1, mass2, dec, ra, polarization, coa_phase, inclination, distance, eccentricity, valid_ind

# Command line parser
parser = ap.ArgumentParser()
parser.add_argument("--inj_file",
        required=True, 
        help="Provide injection file (.hdf)")
parser.add_argument("--psd_list",
        required=True, nargs='+',
        help="Provide (ASD) (.txt) files")
parser.add_argument("--delta_f",
        required=True, type=float,
        help="Specify delta_f for the analysis.")
parser.add_argument("--f_low",
        required=True, type=float,
        help="Specify lower frequency cutoff for match computation.")
parser.add_argument("--output",
        required=True, 
        help="Output file to store the match results (.hdf).")
parser.add_argument("--split-ind",
		type = int,
		help = "In case the user want to split the injection set into multiple parts (10 parts hardcoded atm). Specify the split index -- no. btw [0,9].")
parser.add_argument("--distance-cutoff",
        default=None, type=float,
        help="Specify the largest distance to restrict the number of match computations to only closer injections.")

args = parser.parse_args()
compute_sigmas = True 

delta_f = args.delta_f
f_low = args.f_low

print(args.psd_list)
print('Reading: ', args.inj_file)

mass1, mass2, dec, ra, polarization, coa_phase, inclination, distance, eccentricity, valid_ind = read_injs(args.inj_file, args.distance_cutoff)
mchirp = conversions.mchirp_from_mass1_mass2(mass1, mass2)
sigma = []
valid_mass1 = []
valid_mass2 = []
valid_mchirp = []
valid_ecc = []
valid_dist = []
inj_ind = []

indices_to_exe = np.array_split(valid_ind, 1000)[args.split_ind]

for k in tqdm(indices_to_exe):
	#if (mass1[k] + mass2[k] > 439):
	#	continue
	hp_dict = gen_waveform(mass1[k], mass2[k], dec[k], ra[k], polarization[k], coa_phase[k], \
								inclination[k], distance[k], delta_f, f_low, args.psd_list)

	network_snr = 0.0
	for ifo in hp_dict.keys():
		if ifo == 'H1':	
			PSD = psd.read.from_txt(args.psd_list[0], int((2048/delta_f)/2+1), delta_f, f_low, is_asd_file=True)
		elif ifo == 'L1':	
			PSD = psd.read.from_txt(args.psd_list[1], int((2048/delta_f)/2+1), delta_f, f_low, is_asd_file=True)
		elif ifo == 'V1':	
			PSD = psd.read.from_txt(args.psd_list[2], int((2048/delta_f)/2+1), delta_f, f_low, is_asd_file=True)
		elif ifo == 'K1':	
			PSD = psd.read.from_txt(args.psd_list[3], int((2048/delta_f)/2+1), delta_f, f_low, is_asd_file=True)
		elif ifo == 'I1':	
			PSD = psd.read.from_txt(args.psd_list[4], int((2048/delta_f)/2+1), delta_f, f_low, is_asd_file=True)
		else:
			raise ValueError('PSD corresponding to ifo: %s, not found' %ifo)

		hp = hp_dict[ifo]
		hp.resize(len(PSD))
		network_snr += filter.matchedfilter.sigma(hp, PSD, low_frequency_cutoff=f_low)**2		

		#print(mass1[k]+mass2[k], mass1[k]/mass2[k], network_snr)	
	sigma.append(np.sqrt(network_snr))
	valid_mchirp.append(mchirp[k])
	valid_mass1.append(mass1[k])
	valid_mass2.append(mass2[k])
	valid_ecc.append(eccentricity[k])
	valid_dist.append(distance[k])
	inj_ind.append(k)

with h5py.File(args.output, 'w') as hf:
	valid = hf.create_group('valid')
	valid.create_dataset('sigma', data=sigma)
	valid.create_dataset('mchirp', data=valid_mchirp)
	valid.create_dataset('mass1', data=valid_mass1)
	valid.create_dataset('mass2', data=valid_mass2)
	valid.create_dataset('distance', data=valid_dist),
	valid.create_dataset('eccentricity', data=valid_ecc)
	valid.create_dataset('inj_ind', data=inj_ind)

	full = hf.create_group('full')	
	full.create_dataset('mass1', data=mass1)
	full.create_dataset('mass2', data=mass2)
	full.create_dataset('distance', data=distance),
	full.create_dataset('eccentricity', data=eccentricity)
	full.create_dataset('mchirp', data=mchirp)

	hf.attrs.create('psd_list', data=args.psd_list)
	hf.attrs.create('sampling_freq', 1.0/delta_f)
	hf.attrs.create('f_low', f_low)

hf.close()

print('Success')
