#!/usr/bin/env python3

import sys, os, logging
import argparse as ap
import configparser
import pycbc
import corner

import numpy as np, glob,h5py,dynesty,corner,time
import pycbc
import numpy as np
from pycbc import filter, psd, waveform, types, conversions, cosmology

import pandas as pd
from scipy.special import logsumexp
from pycbc.pool import choose_pool
from dynesty.utils import resample_equal
from dynesty import utils as dyfunc
from dynesty import plotting as dyplot
import matplotlib.pyplot as plt

import time
import pickle

def gen_waveform(mass1, mass2, eccentricity, delta_f, f_low, f_ref):
    hp, hc = waveform.waveform.get_fd_waveform(approximant='TaylorF2Ecc',
                                                    mass1=mass1,
                                                    mass2=mass2,
                                                    delta_f=delta_f,
                                                    f_lower=f_low,
                                                    f_ref=f_ref,
                                                    eccentricity=eccentricity)

    return hp

class BaseLikelihood(object):
    def __init__(self,m1,m2,ecc,delta_f,f_low,f_ref,PSD_file,snr):
        self.m1 = m1
        self.m2 = m2
        self.ecc = ecc
        self.delta_f = delta_f
        self.f_low = f_low
        self.f_ref = f_ref
        self.PSD = psd.read.from_txt(PSD_file, int((1024.0/self.delta_f)/2+1), self.delta_f, self.f_low, is_asd_file=True)
        self.snr = snr       
 
        signal = gen_waveform(self.m1, self.m2, self.ecc, self.delta_f, self.f_low, self.f_ref)
        signal.resize(len(self.PSD))
        self.signal = types.frequencyseries.FrequencySeries(signal, self.delta_f)

    def __call__(self,theta):
        return self.log_likelihood(theta)

    def likelihood_norate(self,theta):
        pass

    def log_likelihood(self,theta):
        mchirp, q, ecc = theta
        template = gen_waveform(conversions.mass1_from_mchirp_q(mchirp, q),
                                conversions.mass2_from_mchirp_q(mchirp, q),
                                ecc, self.delta_f, self.f_low, self.f_ref)
        template.resize(len(self.PSD))

        logL = -self.snr**2*(1-filter.matchedfilter.match(self.signal, template, self.PSD, low_frequency_cutoff=self.f_low)[0])
        return logL
        
def prior_transform(u):
    # Unpack the unit cube samples
    u_a, u_b, u_c = u

    # Define the parameter ranges for each parameter
    a_min, a_max = conversions.mchirp_from_mass1_mass2(m1_inj,m2_inj)*(1-deltamc), conversions.mchirp_from_mass1_mass2(m1_inj,m2_inj)*(1+deltamc)
    b_min, b_max = q_min, q_max
    c_min, c_max = -4, np.log10(0.5)

    # Map the unit cube samples to the parameter space
    a = a_min + u_a * (a_max - a_min)
    b = b_min + u_b * (b_max - b_min)
    c = 10**(c_min + u_c * (c_max - c_min))

    # Return the parameters as a 1D array
    return np.array([a, b, c])

def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

# Command line parser
parser = ap.ArgumentParser()
parser.add_argument("--inj_file",
        help="Provide the injection file containing masses and distance params. (Use the --det-frame-injs if injs are in the detector frame.)")
parser.add_argument("--inj_ind",
		type=int,
        help="Provide the index for the injection")
parser.add_argument("--m1",
		type=float,
        help="Provide the mass1 of the injection")
parser.add_argument("--m2",
		type=float,
        help="Provide the mass2 of the injection")
parser.add_argument("--mchirp",
		type=float,
        help="Provide mchirp of the injection")
parser.add_argument("--ecc",
		type=float, required=True,
        help="Provide the eccentricity of the injection")
parser.add_argument("--delta_f",
		required=True, type=float,
        help="Provide the delta_f for the analysis")
parser.add_argument("--f_min",
		required=True, type=float,
        help="Provide the minimum frequency for the analysis")
parser.add_argument("--f_ref",
		required=True, type=float,
        help="Provide the reference frequency at which eccentricity is defined")
parser.add_argument("--psd",
		required=True, 
        help="Provide the ASD file")
parser.add_argument("--snr",
        required=True, type=float,
		default=10.0,
        help="Provide the snr of the injection")
parser.add_argument("--ncores",
        required=True, type=int,
		default=10,
        help="Provide the ncores")
parser.add_argument("--det-frame-injs",
			action='store_true',
			help="Use this option when injection masses are in the detector frame")
parser.add_argument("--from-list-det-frame-injs",
			action='store_true',
			help="Use this option to read injection masses (det-frame) from a list")

parser.add_argument("--deltaq",
        required=True, type=float,
        help="Specify the deltaq, q prior in (q - qmin, q + qmax)")
parser.add_argument("--deltamc",
        required=True, type=float,
        help="Specify the deltamc, mc prior in (mc*(1-deltamc), mc*(1+deltamc))")


args = parser.parse_args()
global m1_inj 
global m2_inj
global q_max
global q_min
global deltamc

if args.det_frame_injs:
	#Directly sampling in the detector frame 
	hf = h5py.File(args.inj_file, 'r')
	m1_list = hf['mass1'][:]	
	m2_list = hf['mass2'][:]

elif args.from_list_det_frame_injs:
	mchirp = np.full(500, args.mchirp)
	q = np.linspace(1, 60, 500)
	m1_list = conversions.mass1_from_mchirp_q(mchirp, q)
	m2_list = conversions.mass2_from_mchirp_q(mchirp, q)

else:
	#Read the injection masses and distances and then convert them to detector frame
	hf = h5py.File(args.inj_file, 'r')
	mchirp = hf['src_mchirp'][:]
	q = hf['src_q'][:]
	src_m1 = conversions.mass1_from_mchirp_q(mchirp,q)
	src_m2 = conversions.mass2_from_mchirp_q(mchirp,q)
	redshift = cosmology.redshift(hf['distance'][:])
	m1_list = src_m1*(1+redshift)
	m2_list = src_m2*(1+redshift)

ecc_list = np.full(len(m1_list), args.ecc)

#Use a single inj for the Fischer analysis corresponding to the given inj_ind
m1_inj = m1_list[args.inj_ind]
m2_inj = m2_list[args.inj_ind]
ecc_inj = ecc_list[args.inj_ind]
q_inj = m1_inj/m2_inj
if q_inj - args.deltaq < 0:
	q_min = 1.0
else:
	q_min = q_inj - args.deltaq
q_max = q_inj + args.deltaq
deltamc = args.deltamc


print('Computing for injection :', m1_inj, m2_inj, ecc_inj, '\n using cores:', args.ncores, '\n with setting: ', 'delta_f', args.delta_f, 'f_min', args.f_min)
start = time.time()

#Create the likelihood object
likelihood_fn = BaseLikelihood(m1_inj,m2_inj,ecc_inj,args.delta_f,args.f_min,args.f_ref,args.psd,args.snr)

#Run the Dynesty sampler with ncores
ncores = args.ncores
pool = choose_pool(ncores)
pool.size=ncores
sampler = dynesty.NestedSampler(likelihood_fn, prior_transform, 3, nlive=1000, pool=pool)
sampler.run_nested(dlogz=0.1)

results = sampler.results

#Saving output
#path = os.mkdir('{}/{}'.format(os.getcwd(),args.snr))
#print('path', path)
#savefile = '{}/{}/{}-{}-{}.pkl'.format(os.getcwd(), args.snr, m1_inj, m2_inj, ecc_inj)
savefile = '{}_{}_{}_{}.pkl'.format(m1_inj, m2_inj, ecc_inj, args.inj_ind)
print('save', savefile)
save_object(results, savefile)

end = time.time()
print('Saved succesfully')
print('Time taken', end-start)

