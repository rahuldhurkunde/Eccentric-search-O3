import numpy as np
import h5py
import matplotlib.pyplot as plt
import sys
import pylab
from pycbc import waveform, psd, filter, conversions, detector
import pycbc
import argparse
from matplotlib.pyplot import cm
#rc('font', family='serif', weight = 'bold')
from matplotlib import rc
rc('text', usetex=True)

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return  array[idx], idx

# computing only for q=1 systems
def compute_inspiral_range(mchirp, PSD, snr):
	m1 = conversions.mass1_from_mchirp_q(mchirp, np.ones(len(mchirp)))
	m2 = conversions.mass2_from_mchirp_q(mchirp, np.ones(len(mchirp)))
	
	inspiral_dist = []
	for k in range(len(m1)):
		hp,hc = pycbc.waveform.waveform.get_fd_waveform(mass1=m1[k], mass2=m2[k], approximant='TaylorF2Ecc',
                                    f_lower=20.0, delta_f=PSD.delta_f, eccentricity=0.0, fref=20.0,
                                    delta_t=1/2048)
		
		detect = detector.Detector('H1')
		opt_ra, opt_dec = detect.optimal_orientation(1126259462.0)

		fx, fy = detect.antenna_pattern(opt_ra, opt_dec, 0.0, 1126259462.0)
		det_signal = hp*fx + hc*fy
		det_signal.resize(len(PSD))

		sigma1 = pycbc.filter.matchedfilter.sigma(det_signal, psd=PSD, low_frequency_cutoff=20.0)
		horizon_distance = sigma1 / snr
		inspiral_dist.append(horizon_distance/2.26)
	return inspiral_dist


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--data-file', nargs='+',
                    help="Required. HDF format data file or space "
                    "separated list of files")
parser.add_argument('--ifar', type = float, default = 100.0,
                    help="IFAR value to plot the sensitivity")
parser.add_argument('--output', required=True,
                    help='Destination file for the plot')
parser.add_argument('--inspiral-range', action='store_true',
					help='True(default) to plot analytical inspiral range')
parser.add_argument('--log-dist', action='store_true',
                    help='Plot the sensitivity axis in log scale')


args = parser.parse_args()
#color = iter(cm.rainbow(np.linspace(0, 1, len(args.data_file))))
color = iter(cm.GnBu(np.linspace(0.3,0.9,len(args.data_file))))

param_values = iter([1.21877079, 2.01903774, 2.93015605, 3.13926747])

if args.inspiral_range:
	param_values = iter([0.0, 0.05, 0.1, 0.2, 0.27, 0.29])

for datafile in args.data_file:
	c = next(color)
	print("Reading \t ", datafile)

	ifar_given = float(args.ifar)
	print("Given IFAR \t", ifar_given)

	f = h5py.File(datafile)
	ifar_arr = f['xvals'][:]
	ifar, idx = find_nearest(ifar_arr, ifar_given)
	print("Computing for IFAR", ifar, idx)

	reach = []
	xvals = []
	elow = []
	ehigh = []
	for key in f['data'].keys():
		reach.append(f['data/%s' %key][idx])
		xvals.append(float(key))
		elow.append(f['errorlow/%s' %key][idx])
		ehigh.append(f['errorhigh/%s' %key][idx])

	reach = np.array(reach)
	elow = np.array(elow)
	ehigh = np.array(ehigh)
	label = r'$\mathcal{M}_c$ = ' + '{}'.format(round(next(param_values),2))
	pylab.plot(xvals, reach, c=c, label=label)
	pylab.plot(xvals, reach, alpha=0.6, c='black')
	pylab.fill_between(xvals, reach - elow, reach + ehigh, facecolor=c,
					 edgecolor=c, alpha=0.6)

if args.inspiral_range:
	#Plot inspiral ranges
	snr = 8.0
	mchirp = np.linspace(min(xvals), max(xvals), 100)
	PSD = psd.read.from_txt('calculated_psd.txt', int((2048*64)/2+1), 1.0/64, 20.0)
	inspiral_dist = compute_inspiral_range(mchirp, PSD, snr)
	pylab.plot(mchirp, inspiral_dist, '--', color='black', label='inspiral-range with SNR %s' %snr)
	print('our-search', inspiral_dist[0], inspiral_dist[2])
	
	#PSD = psd.read.from_txt('aplus.txt', int((2048*64)/2+1), 1.0/64, 20.0)
	#inspiral_dist = compute_inspiral_range(mchirp, PSD, snr)
	#pylab.plot(mchirp, inspiral_dist, '--', color='black', label='inspiral-range with SNR %s' %snr)
	#print('aplus', inspiral_dist[0], inspiral_dist[2])
	
	#PSD = psd.read.from_txt('Asharp_strain.txt', int((2048*64)/2+1), 1.0/64, 20.0)
	#inspiral_dist = compute_inspiral_range(mchirp, PSD, snr)
	#pylab.plot(mchirp, inspiral_dist, '--', color='black', label='inspiral-range with SNR %s' %snr)
	#print('Asharp', inspiral_dist[0], inspiral_dist[2])

	#PSD = psd.read.from_txt('ce2.txt', int((2048*64)/2+1), 1.0/64, 20.0)
	#inspiral_dist = compute_inspiral_range(mchirp, PSD, snr)
	#pylab.plot(mchirp, inspiral_dist, '--', color='black', label='inspiral-range with SNR %s' %snr)

if args.log_dist:
    pylab.yscale('log')


pylab.xlabel('$e_{10}$', fontsize=18)
#pylab.xlabel('Mchirp')
pylab.ylabel('Sensitive distance (Mpc)', fontsize=14)
pylab.grid()
pylab.legend()
#plt.title('For IFAR %s' %args.ifar)
plt.savefig(args.output, dpi=600)
pylab.show()
