import argparse, h5py, numpy, logging, matplotlib, sys
matplotlib.use('Agg')
from matplotlib.pyplot import cm
import pylab, pycbc.pnutils, pycbc.results, pycbc, pycbc.version
from pycbc import sensitivity, conversions
from lal import YRJUL_SI as lal_YRJUL_SI
import numpy as np

def get_missed_found_injections(inj_files, missed, found, xaxis):
	t = []
	print('Using sub-population', args.constraint_param, 'with value', args.constraint_value)
	for fi in args.injection_file:
		with h5py.File(fi, 'r') as f:
			# Get the found (at any FAR)/missed injection indices
			if args.constraint_value or args.constraint_param:
				temp_foundi = f['found_after_vetoes/injection_index'][:]
				temp_missedi = f['missed/after_vetoes'][:]

				if args.constraint_param == 'mtotal':
					mtotal_found = conversions.mtotal_from_mass1_mass2(f['injections/mass1'][:][temp_foundi], f['injections/mass2'][:][temp_foundi])
					mtotal_missed = conversions.mtotal_from_mass1_mass2(f['injections/mass1'][:][temp_missedi], f['injections/mass2'][:][temp_missedi])
					sub_pop_found_ind = numpy.where(numpy.abs(mtotal_found - args.constraint_value) <= args.constraint_value_tol )[0]

					foundi = temp_foundi[numpy.where(numpy.abs(mtotal_found - args.constraint_value) <= args.constraint_value_tol)[0]]
					missedi = temp_missedi[numpy.where(numpy.abs(mtotal_missed - args.constraint_value) <= args.constraint_value_tol)[0]]
					if len(foundi) == 0 or len(missedi) == 0:
						print('No sub-population found for %s = %s, Check the constraint-value' %(args.constraint_param, args.constraint_value))
						sys.exit()

				elif args.constraint_param == 'mchirp':
					mchirp_found = conversions.mchirp_from_mass1_mass2(f['injections/mass1'][:][temp_foundi], f['injections/mass2'][:][temp_foundi])
					mchirp_missed = conversions.mchirp_from_mass1_mass2(f['injections/mass1'][:][temp_missedi], f['injections/mass2'][:][temp_missedi])
					sub_pop_found_ind = numpy.where(numpy.abs(mchirp_found - args.constraint_value) <= args.constraint_value_tol)[0]

					foundi = temp_foundi[numpy.where(numpy.abs(mchirp_found - args.constraint_value) <= args.constraint_value_tol)[0]]
					missedi = temp_missedi[numpy.where(numpy.abs(mchirp_missed - args.constraint_value) <= args.constraint_value_tol)[0]]
					if len(foundi) == 0 or len(missedi) == 0:
						print('No sub-population found for %s = %s, Check the constraint-value' %(args.constraint_param, args.constraint_value))
						sys.exit()

				elif args.constraint_param == 'eccentricity':
					ecc_found = f['injections/eccentricity'][temp_foundi]
					ecc_missed = f['injections/eccentricity'][temp_missedi]
					sub_pop_found_ind = numpy.where(numpy.abs(ecc_found - args.constraint_value) <= args.constraint_value_tol)[0]

					foundi = temp_foundi[numpy.where(numpy.abs(ecc_found - args.constraint_value) <= args.constraint_value_tol)[0]]
					missedi = temp_missedi[numpy.where(numpy.abs(ecc_missed - args.constraint_value) <= args.constraint_value_tol)[0]]
					#print(fi, 'Found subpopulation', len(foundi))               
					if len(foundi) == 0 or len(missedi) == 0:
						print('No sub-population found for %s = %s, Check the constraint-value' %(args.constraint_param, args.constraint_value))
						sys.exit()
				
				else:
					print('Check constraining param and value')
					sys.exit()
			
				# retrieve IFAR values
				sig_exc = f['found_after_vetoes/ifar_exc'][:][sub_pop_found_ind]
				try:
					sig = f['found_after_vetoes/ifar'][:][sub_pop_found_ind]
				except KeyError:
					sig = numpy.array([])

			else:
				foundi = f['found_after_vetoes/injection_index'][:]
				missedi = f['missed/after_vetoes'][:]
				
				# retrieve IFAR values
				sig_exc = f['found_after_vetoes/ifar_exc'][:]
				try:
					sig = f['found_after_vetoes/ifar'][:]
				except KeyError:
					sig = numpy.array([])


			# retrieve injection parameters
			dist = f['injections/distance'][:]
			m1, m2 = f['injections/mass1'][:], f['injections/mass2'][:]
			s1x, s2x = f['injections/spin1x'][:], f['injections/spin2x'][:]
			s1z, s2z = f['injections/spin1z'][:], f['injections/spin2z'][:]
			# y-components not used but read them in for symmetry
			s1y, s2y = f['injections/spin1y'][:], f['injections/spin2y'][:]
			inc = f['injections/inclination'][:]
			eccentricity = f['injections/eccentricity'][:]
			
			mchirp = pycbc.pnutils.mass1_mass2_to_mchirp_eta(m1, m2)[0]
			if args.xaxis == 'mchirp':
				pvals = mchirp
			elif args.xaxis == 'eta':
				pvals = pycbc.pnutils.mass1_mass2_to_mchirp_eta(m1, m2)[1]
			elif args.xaxis == 'total_mass':
				pvals = m1 + m2
			elif args.xaxis == 'max_mass':
				pvals = numpy.maximum(m1, m2)
			elif args.xaxis == 'spin':
				pvals = get_spin(args.spin_frame, inc,
								 m1, m2, s1x, s1z, s2x, s2z)
			elif args.xaxis == 'template_duration':
				# Will default to SEOBNRv4 approximant value
				# Only valid/useful for non-spin or aligned-spin signals
				pvals = pycbc.pnutils.get_imr_duration(m1, m2, s1z, s2z,
													   f_low=args.f_lower)
			elif args.xaxis == 'eccentricity':
				pvals = eccentricity

			else:
				raise RuntimeError('Unrecognized --bin-type value!')
			
			# Add the current values to the arrays
			missed['dist']  = numpy.append(missed['dist'], dist[missedi])
			missed['param'] = numpy.append(missed['param'], pvals[missedi])
			missed['mchirp']= numpy.append(missed['mchirp'], mchirp[missedi])
			found['dist']   = numpy.append(found['dist'], dist[foundi])
			found['param']  = numpy.append(found['param'], pvals[foundi])
			found['mchirp'] = numpy.append(found['mchirp'], mchirp[foundi])
			found['sig']    = numpy.append(found['sig'], sig)
			found['sig_exc']= numpy.append(found['sig_exc'], sig_exc)

			print('Found injections ', len(found['dist']))
			# Time in years
			t.append(f.attrs['foreground_time_exc'] / lal_YRJUL_SI)

	fvalues = [found['sig_exc']]
	do_labels = [True]
	alphas = [.6]
	x_values = np.unique(found['param'])
	print('Total found:', len(found['param']), 'missed: ', len(missed['param']))
	return missed, found, t, fvalues, x_values


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--version', action='version', version=pycbc.version.git_verbose_msg)
parser.add_argument('--verbose', action='count')
parser.add_argument('--injection-file', nargs='+',
                    help="Required. HDF format injection result file or space "
                    "separated list of files")

parser.add_argument('--constraint-param', choices=['mtotal', 'mchirp', 'eccentricity'],
                    help="Disentangle injections having same choosen param from the total population and compute sensitivity using only that sub-population.")
parser.add_argument('--constraint-value', type = float,
                    help="Injections having the specified value for --constraint-param will be used for sensitivity calculations.")
parser.add_argument('--constraint-value-tol', type = float,
                    help="Put a tolerance around --constraint-value to collect the sub-population.")

parser.add_argument('--dist-type', choices=['distance', 'volume', 'vt', 'rate'],
                    default='distance',
                    help="y-axis sensitivity measure. Default 'distance'")
parser.add_argument('--log-dist', action='store_true',
                    help='Plot the sensitivity axis in log scale')

parser.add_argument('--integration-method', default='pylal',
                    choices=['pylal', 'shell', 'mc', 'vchirp_mc'],
                    help="Sensitive volume estimation method. Default 'pylal'")
parser.add_argument('--distribution',
                    choices=['log', 'uniform', 'distancesquared', 'volume'],
                    help="Form of distribution over D, required by 'mc' method")

parser.add_argument('--distance-param', choices=['distance', 'chirp_distance'],
                    help="Parameter D used to generate injection distribution "
                         "over distance, required for 'mc' volume estimation")
parser.add_argument('--dist-bins', type=int, default=100,
                    help="Number of distance bins for 'pylal' volume "
                         "estimation. Default 100")
parser.add_argument('--limits-param', choices=['distance', 'chirp_distance'],
                    help="Parameter Dlim specifying limits of injection "
                         "distribution, used by 'mc' method. If not given, "
                         "will be set equal to --distance-param")
parser.add_argument('--min-param', type=float,
                    help="Minimum value of Dlim, used by 'mc' method with log "
                         "distribution. If not given, min injected value will "
                         "be used")
parser.add_argument('--max-param', type=float,
                    help="Maximum value of Dlim, used by 'mc' method. If not "
                         "given, the maximum injected value will be used")

parser.add_argument('--xaxis', choices=['mtotal', 'mchirp', 'eccentricity'],
                    default='mchirp',
                    help="x-axis significance measure. Default 'mchirp'")
parser.add_argument('--custom-xvalues', nargs='+', type=float,
                    help="custom values for the xaxis, ex. 0.0 0.1 0.2")
parser.add_argument('--ifar', nargs='+', type=float,
                    help="IFAR values, ex. 10.0 100.0 1000.0")
parser.add_argument('--hdf-out', help='HDF file to save curve data')

args = parser.parse_args()
if args.verbose:
    log_level = logging.INFO
    logging.basicConfig(format='%(asctime)s : %(message)s', level=log_level)

if args.integration_method == 'mc' and (args.distance_param is None or \
                                        args.distribution is None):
    raise RuntimeError("The 'mc' method requires --distance-param and "
                       "--distribution !")
if args.integration_method == 'mc' and args.limits_param is None:
    args.limits_param = args.distance_param

ifar_values = args.ifar

if args.hdf_out:
    plotdict = {}
    plotdict['xvals'] = ifar_values 

missed = {
    'dist'  : numpy.array([]),
    'param' : numpy.array([]),
    'mchirp': numpy.array([]),
}
found = {
    'dist'  : numpy.array([]),
    'param' : numpy.array([]),
    'mchirp': numpy.array([]),
    'sig'   : numpy.array([]),
    'sig_exc' : numpy.array([]),
}
# Parameter bin legend labels
labels = {
    'mchirp'     : "$ M_{\\rm chirp} \in [%5.2f, %5.2f] M_\odot $",
    'eta'        : "$ \\eta \in [%5.2f, %5.2f] $",
    'total_mass' : "$ M_{\\rm total} \in [%5.2f, %5.2f] M_\odot $",
    'max_mass'   : "$ {\\rm max}(m_1, m_2) \in [%5.2f, %5.2f] M_\odot $",
    'eccentricity':  "$ e \in [%5.2f, %5.2f] $"
}
ylabel = xlabel = ""

missed, found, t, fvalues, x_values = get_missed_found_injections(args.injection_file, missed, found, args.xaxis)
obs_time = np.sum(np.unique(t))

print('Total observation time in years: ', obs_time)
do_labels = [True]
alphas = [.6]

if args.custom_xvalues:
	x_values = args.custom_xvalues
print(x_values)

#x_values = np.array([1.21877079, 2.01903774, 2.93015605, 3.13926747])

fig = pylab.figure()
# Cycle over parameter bins plotting each in turn
for xval in x_values:

# cycle over inclusive / exclusive significance if available
	for sig_val, do_label, alpha in zip(fvalues, do_labels, alphas):
		if sig_val[0] is None:
			logging.info('Skipping exclusive significance')
			continue

		logging.info('Injections with param values %5.2f' %
					 xval)

		# Get distance of missed injections within parameter bin
		binm = np.where(missed['param'] == xval)[0]
		m_dist = missed['dist'][binm]

		# Abort if the bin has too few triggers
		if len(m_dist) < 2:
			continue

		vols, vol_errors = [], []

		# Slice up found injections in parameter bin
		binf = np.where(found['param'] == xval)[0]
		binfsig  = sig_val[binf]

		# Calculate each sensitive distance at a given significance threshold
		for ifar in ifar_values:
			logging.info('Thresholding on significance at %5.2f' % ifar)
			# Count found inj towards sensitivity if IFAR/stat exceeds threshold
			# or if FAP value is less than threshold
			loud = binfsig >= ifar 
			quiet = binfsig < ifar

			# Distances of inj found above threshol, td
			f_dist = found['dist'][binf][loud]
			print('fvalues sum', sum(sig_val))
			# Distances of inj found below threshold
			fm_dist = found['dist'][binf][quiet]

			# Add distances of 'quiet' found injections to the missed list
			m_dist_full = numpy.append(m_dist, fm_dist)

			# Choose the volume estimation method
			if args.integration_method == 'shell':
				vol, vol_err = sensitivity.volume_shell(f_dist, m_dist_full)
			elif args.integration_method == 'pylal':
				vol, vol_err = sensitivity.volume_binned_pylal(f_dist,
								 m_dist_full, bins=args.dist_bins)
			elif args.integration_method in ['mc', 'vchirp_mc']:
				found_mchirp = found['mchirp'][binf][loud]
				missed_mchirp = numpy.append(missed['mchirp'][binm],
								 found['mchirp'][binf][quiet])

				if args.integration_method == 'mc':
					print('Lengths \t: ', len(f_dist), len(m_dist_full), len(found_mchirp), len(missed_mchirp))
					vol, vol_err = sensitivity.volume_montecarlo(f_dist,
										m_dist_full, found_mchirp, missed_mchirp,
										args.distance_param, args.distribution,
										args.limits_param, args.min_param, args.max_param)
				else: # vchirp_mc
					vol, vol_err = sensitivity.chirp_volume_montecarlo(
										f_dist, m_dist_full, found_mchirp, missed_mchirp,
										args.distance_param, args.distribution,
										args.limits_param, args.min_param, args.max_param)

			vols.append(vol)
			vol_errors.append(vol_err)
			logging.info('Vol_errors %5.2f' % ((vol-vol_err)/vol))

		vols = numpy.array(vols)
		vol_errors = numpy.array(vol_errors)

		if args.dist_type == 'distance':
			ylabel = 'Sensitive Distance (Mpc)'
			reach, ehigh, elow = sensitivity.volume_to_distance_with_errors(vols, vol_errors)
		elif args.dist_type == 'volume':
			ylabel = "Sensitive Volume (Mpc$^3$)"
			reach, ehigh, elow = vols, vol_errors, vol_errors
		elif args.dist_type == 'vt':
			ylabel = "Volume $\\times$ Time (yr Mpc$^3$)"
			pylab.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

			reach, ehigh, elow = vols * t, vol_errors * t, vol_errors * t

		elif args.dist_type == 'rate':
			ylabel = "Rate (Yr^{-1} Gpc^{-3})"
			pylab.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
		
			obs_time = np.sum(np.unique(t))
			reach, ehigh, elow = 2.303*10**9/(vols*obs_time), 2.303*10**9/obs_time/vol**2*vol_errors, 2.303*10**9/obs_time/vol**2*vol_errors

		#label = labels[args.bin_type] % (xval) if do_label else None
		pylab.plot(xval, reach, label=args.constraint_value)
		pylab.plot(xval, reach, alpha=alpha, c='black')
		pylab.fill_between(xval, reach - elow, reach + ehigh, alpha=alpha)

		if args.hdf_out:
			data_val = '%.3f'% (xval)
			plotdict['data/%s' % data_val] = reach
			plotdict['errorhigh/%s' % data_val] = ehigh
			plotdict['errorlow/%s' % data_val] = elow

if args.hdf_out:
    outfile = h5py.File(args.hdf_out,'w')
    for key in plotdict.keys():
        outfile.create_dataset(key, data=plotdict[key])
    outfile.attrs.create('obs_time', data=obs_time)

ax = pylab.gca()

if args.log_dist:
    ax.set_yscale('log')

pylab.ylabel(ylabel)
pylab.xlabel(xlabel)

pylab.grid()
pylab.legend(loc='lower left')

#pycbc.results.save_fig_with_metadata(fig, args.output_file,
#     title="Sensitive: binned using %s method"
#            % (args.integration_method),
#     caption="Sensitive %s as a function of Significance:"
#             "Lighter lines represent the significance without"
#             " including injections in their own background,"
#             " while darker lines include each injection"
#             " individually in the background. The integration"
#             " method used is based on %s."
#             % (args.dist_type.title(), args.integration_method),
#     cmd=' '.join(sys.argv))

