import h5py
import numpy as np
from pycbc import waveform, psd, filter, conversions
import time

np.random.seed(1)

def compute_ecc_maximized_match(hpe, PSD, m1, m2, s1z, s2z, ecc):
	temp_matches = []
	temp_ecc_list = np.linspace(0.75*ecc, ecc, 25)
	for i in range(len(temp_ecc_list)):
		temp_ecc = temp_ecc_list[i] 
		hp, hc = waveform.get_fd_waveform(approximant='TaylorF2Ecc',
									mass1=m1,
									mass2=m2,
									spin1z=0.05,
									spin2z=-0.05,
									delta_f = hpe.delta_f,
									eccentricity = temp_ecc,
									f_lower = 10.0,
									f_ref = 20.0)

		hp.resize(int(len(hpe)/2+1))
		temp_matches.append(filter.match(hpe, hp, psd=PSD, low_frequency_cutoff=10.0)[0])
	
	max_match_ind = np.argmax(temp_matches)
	return temp_matches[max_match_ind], temp_ecc_list[max_match_ind]  


def sample_m1_m2_uniformly(nsamples):
	m1_samples = []
	m2_samples = []

	while len(m1_samples) < nsamples:
		# Sample m1 and m2 from a uniform distribution between 1 and 9
		m1 = np.random.uniform(1.5, 9)
		m2 = np.random.uniform(1.5, 9)
		
		# Check if the pair satisfies the constraints
		if m1 >= m2 and m1 + m2 <= 10.0:
			m1_samples.append(m1)
			m2_samples.append(m2)
	return m1_samples, m2_samples

m1_list, m2_list = sample_m1_m2_uniformly(30)

ecc_list = np.linspace(0.0, 0.28, 10)

with open('data.txt', 'w') as file:
	matches = []	
	count = 0
	for k in range(len(m1_list)):
		m1 = m1_list[k]
		m2 = m2_list[k]
		
		for ecc in ecc_list:
			print('Computing for ', m1, m2, ecc)
			start = time.time()
			hpe, hce = waveform.get_td_waveform(approximant='teobresums',
										mass1=m1,
										mass2=m2,
										spin1z=0.05,
										spin2z=-0.05,
										delta_t = 1.0/2048,
										eccentricity = ecc,
										f_lower = 10.0,
										f_ref = 20.0)

			#PSD = psd.analytical.aLIGOZeroDetHighPower(int(len(hpe)/2+1), hpe.delta_f, low_freq_cutoff=20)
			#PSD = psd.read.from_txt('o3psd.txt',int(len(hpe)/2+1), hpe.delta_f, low_freq_cutoff=20, is_asd_file=False)
			PSD = psd.read.from_txt('Asharp_strain.txt',int(len(hpe)/2+1), hpe.delta_f, low_freq_cutoff=10, is_asd_file=True)

			match, best_ecc_val = compute_ecc_maximized_match(hpe, PSD, m1, m2, 0.0, 0.0, ecc)
			
			matches.append(match)
			
			end = time.time()
			print(count, 'Time for one param execution', end-start)
			count += 1
			row = f"{m1} {m2} {ecc} {match} {best_ecc_val} \n"
			file.write(row)

