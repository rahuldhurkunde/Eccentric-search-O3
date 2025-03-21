#!/work/rahul.dhurkunde/searches/envs/ecc-search/bin/python3
""" Plot search sensitivity as a function of parameter bins
"""
import argparse, h5py, numpy, logging, matplotlib, sys
matplotlib.use('Agg')
from matplotlib.pyplot import cm
import pylab, pycbc.pnutils, pycbc.results, pycbc, pycbc.version
from pycbc import sensitivity, conversions
from lal import YRJUL_SI as lal_YRJUL_SI

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--version', action='version', version=pycbc.version.git_verbose_msg)
parser.add_argument('--verbose', action='count')
parser.add_argument('--injection-file', nargs='+',
                    help="Required. HDF format injection result file or space "
                    "separated list of files")
parser.add_argument('--output-file', required=True,
                    help='Destination file for the plot')
parser.add_argument('--bin-type', choices=['spin', 'mchirp', 'total_mass',
                                           'max_mass', 'eta',
                                           'template_duration', 'eccentricity'],
                    default='mchirp',
                    help="Parameter used to bin injections. Default 'mchirp'")
# FIXME: Make bins options properly optional, if no bins are specified then
# plot everything together
parser.add_argument('--constraint-param', choices=['mtotal', 'mchirp', 'eccentricity'],
                    help="Disentangle injections having same choosen param from the total population and compute sensitivity using only that sub-population.")
parser.add_argument('--constraint-value', type = float,
                    help="Injections having the specified value for --constraint-param will be used for sensitivity calculations.")
parser.add_argument('--constraint-value-tol', type = float,
                    help="Put a tolerance around --constraint-value to collect the sub-population.")

parser.add_argument('--bins', nargs='+',
                    help="Parameter bin boundaries, ex. 1.3 2.6 4.1")
parser.add_argument('--param-range', nargs='+',
                    help="Required. Total range to bin the params, ex. 1.0  4.0")
parser.add_argument('--nbins-param', type = int,
                    help="Required. Number of bins for the params, ex. 10")
parser.add_argument('--sig-type', choices=['ifar', 'fap', 'stat'],
                    default='ifar',
                    help="x-axis significance measure. Default 'ifar'")
parser.add_argument('--exclusive-sig', action='store_true',
                    help="Plot only exclusive injection FAR, not inclusive")
parser.add_argument('--sig-bins', nargs='*',
                   help="Boundaries of x-axis significance bins. If not given"
                        ", hard-coded defaults will be used"),
parser.add_argument('--dist-type', choices=['distance', 'volume', 'vt', 'rate'],
                    default='distance',
                    help="y-axis sensitivity measure. Default 'distance'")
parser.add_argument('--log-dist', action='store_true',
                    help='Plot the sensitivity axis in log scale')
parser.add_argument('--min-dist', type=float,
                    help="Lower y-axis limit for sensitive distance")
parser.add_argument('--max-dist', type=float,
                    help="Upper y-axis limit for sensitive distance")
parser.add_argument('--integration-method', default='pylal',
                    choices=['pylal', 'shell', 'mc', 'vchirp_mc'],
                    help="Sensitive volume estimation method. Default 'pylal'")
parser.add_argument('--dist-bins', type=int, default=100,
                    help="Number of distance bins for 'pylal' volume "
                         "estimation. Default 100")
parser.add_argument('--distance-param', choices=['distance', 'chirp_distance'],
                    help="Parameter D used to generate injection distribution "
                         "over distance, required for 'mc' volume estimation")
parser.add_argument('--distribution',
                    choices=['log', 'uniform', 'distancesquared', 'volume'],
                    help="Form of distribution over D, required by 'mc' method")
parser.add_argument('--limits-param', choices=['distance', 'chirp_distance'],
                    help="Parameter Dlim specifying limits of injection "
                         "distribution, used by 'mc' method. If not given, "
                         "will be set equal to --distance-param")
parser.add_argument('--max-param', type=float,
                    help="Maximum value of Dlim, used by 'mc' method. If not "
                         "given, the maximum injected value will be used")
parser.add_argument('--min-param', type=float,
                    help="Minimum value of Dlim, used by 'mc' method with log "
                         "distribution. If not given, min injected value will "
                         "be used")
parser.add_argument('--spin-frame', choices=['line-of-sight', 'orbit'],
                    default='orbit', help='Frame convention used by injections '
                    'for specifying spin vectors. LAL versions after summer '
                    '2015 should use the orbit convention, which is the '
                    'default choice here.')
parser.add_argument('--hdf-out', help='HDF file to save curve data')
parser.add_argument('--f-lower', default=20, type=float, help='Low frequency '
                    'cutoff for calculating template durations')

args = parser.parse_args()

if args.bins:
	param_bins = args.bins
else:
	param_bins = numpy.linspace(float(args.param_range[0]), float(args.param_range[1]), args.nbins_param)

if len(param_bins) < 2:
    raise RuntimeError("At least 2 injection bin boundaries are required!")

if args.integration_method == 'mc' and (args.distance_param is None or \
                                        args.distribution is None):
    raise RuntimeError("The 'mc' method requires --distance-param and "
                       "--distribution !")
if args.integration_method == 'mc' and args.limits_param is None:
    args.limits_param = args.distance_param

if args.verbose:
    log_level = logging.INFO
    logging.basicConfig(format='%(asctime)s : %(message)s', level=log_level)

logging.info('Read in the data')

def get_spin(frame, inc, m1, m2, s1x, s1z, s2x, s2z):
    # 'spin' means effective spin along orbital angular momentum
    if frame == 'line-of-sight':
        s1 = s1x * numpy.sin(inc) + s1z * numpy.cos(inc)
        s2 = s2x * numpy.sin(inc) + s2z * numpy.cos(inc)
    elif frame == 'orbit':
        s1, s2 = s1z, s2z
    else:
        raise RuntimeError('Unknown spin frame!')
    return (m1 * s1 + m2 * s2) / (m1 + m2)

# initialize injection arrays and duration
# mchirp is required for Monte-Carlo method for dchirp distributed inj
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
t = 0.

print('Using sub-population', args.constraint_param, 'with value', args.constraint_value)

for fi in args.injection_file:
    with h5py.File(fi, 'r') as f:

        # Get the found (at any FAR)/missed injection indices
        if args.constraint_value or args.constraint_param:
            temp_foundi = f['found_after_vetoes/injection_index'][:]
            temp_missedi = f['missed/after_vetoes'][:]
            
            if args.constraint_param == 'mtotal':
               mtotal_found = conversions.mtotal_from_mass1_mass2(f['injections/mass1'][temp_foundi], f['injections/mass2'][temp_foundi])
               mtotal_missed = conversions.mtotal_from_mass1_mass2(f['injections/mass1'][temp_missedi], f['injections/mass2'][temp_missedi])
               sub_pop_found_ind = numpy.where(numpy.abs(mtotal_found - args.constraint_value) <= args.constraint_value_tol )[0]
               
               foundi = temp_foundi[numpy.where(numpy.abs(mtotal_found - args.constraint_value) <= args.constraint_value_tol)[0]]
               missedi = temp_missedi[numpy.where(numpy.abs(mtotal_missed - args.constraint_value) <= args.constraint_value_tol)[0]]
               if len(foundi) == 0 or len(missedi) == 0:
                   print('No sub-population found for %s = %s, Check the constraint-value' %(args.constraint_param, args.constraint_value))
                   sys.exit()            

            elif args.constraint_param == 'mchirp':
               mchirp_found = conversions.mchirp_from_mass1_mass2(f['injections/mass1'][temp_foundi], f['injections/mass2'][temp_foundi])
               mchirp_missed = conversions.mchirp_from_mass1_mass2(f['injections/mass1'][temp_missedi], f['injections/mass2'][temp_missedi])
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

        else:
            foundi = f['found_after_vetoes/injection_index'][:]
            missedi = f['missed/after_vetoes'][:]

        # retrieve injection parameters
        dist = f['injections/distance'][:]
        m1, m2 = f['injections/mass1'][:], f['injections/mass2'][:]
        s1x, s2x = f['injections/spin1x'][:], f['injections/spin2x'][:]
        s1z, s2z = f['injections/spin1z'][:], f['injections/spin2z'][:]
        # y-components not used but read them in for symmetry
        s1y, s2y = f['injections/spin1y'][:], f['injections/spin2y'][:]
        inc = f['injections/inclination'][:]
        #eccentricity = f['injections/eccentricity'][:]

        mchirp = pycbc.pnutils.mass1_mass2_to_mchirp_eta(m1, m2)[0]
        if args.bin_type == 'mchirp':
            pvals = mchirp
        elif args.bin_type == 'eta':
            pvals = pycbc.pnutils.mass1_mass2_to_mchirp_eta(m1, m2)[1]
        elif args.bin_type == 'total_mass':
            pvals = m1 + m2
        elif args.bin_type == 'max_mass':
            pvals = numpy.maximum(m1, m2)
        elif args.bin_type == 'spin':
            pvals = get_spin(args.spin_frame, inc,
                             m1, m2, s1x, s1z, s2x, s2z)
        elif args.bin_type == 'template_duration':
            # Will default to SEOBNRv4 approximant value
            # Only valid/useful for non-spin or aligned-spin signals
            pvals = pycbc.pnutils.get_imr_duration(m1, m2, s1z, s2z,
                                                   f_low=args.f_lower)
        elif args.bin_type == 'eccentricity':
            pvals = eccentricity
        else:
            raise RuntimeError('Unrecognized --bin-type value!')

        if args.sig_type == 'stat':
            if args.constraint_param and args.constraint_value:
                sig_exc = f['found_after_vetoes/stat'][:][sub_pop_found_ind]
                sig = None
            else:
                sig_exc = f['found_after_vetoes/stat'][:]
                sig = None
        elif args.sig_type == 'ifar':
            if args.constraint_param and args.constraint_value:
                sig_exc = f['found_after_vetoes/ifar_exc'][:][sub_pop_found_ind]
                try:
                    sig = f['found_after_vetoes/ifar'][:][sub_pop_found_ind]
                except KeyError:
                    sig = numpy.array([])
            else:
                sig_exc = f['found_after_vetoes/ifar_exc'][:]
                try:
                    sig = f['found_after_vetoes/ifar'][:]
                except KeyError:  # multiifo inj files may not have inclusive FAR
                    sig = numpy.array([])
        elif args.sig_type == 'fap': 
            if args.constraint_param and args.constraint_value:
                sig_exc = f['found_after_vetoes/fap_exc'][:][sub_pop_found_ind]
                try:
                    sig = f['found_after_vetoes/fap'][:][sub_pop_found_ind]
                except KeyError:
                    sig = numpy.array([])
            else:
                sig_exc = f['found_after_vetoes/fap_exc'][:]
                try:
                    sig = f['found_after_vetoes/fap'][:]
                except KeyError:  # multiifo inj files may not have inclusive FAR
                    sig = numpy.array([])


        else:
            raise RuntimeError('Unrecognized --sig-type value!')

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
        if args.dist_type == 'vt' or args.dist_type == 'rate':
            t += f.attrs['foreground_time_exc'] / lal_YRJUL_SI

# Parameter bin legend labels
labels = {
    'mchirp'     : "$ M_{\\rm chirp} \in [%5.2f, %5.2f] M_\odot $",
    'eta'        : "$ \\eta \in [%5.2f, %5.2f] $",
    'total_mass' : "$ M_{\\rm total} \in [%5.2f, %5.2f] M_\odot $",
    'max_mass'   : "$ {\\rm max}(m_1, m_2) \in [%5.2f, %5.2f] M_\odot $",
    'spin'       : "$ \\chi_{\\rm eff} \in [%5.2f, %5.2f] $",
    'template_duration' : "$ \\tau \in [%5.2f, %5.2f] s $",
	'eccentricity':  "$ e \in [%5.2f, %5.2f] $"
}

ylabel = xlabel = ""

# Set up significance values for x-axis
if args.sig_type == 'stat':
    xlabel = 'Ranking Statistic Value'
    if args.sig_bins:
        x_values = [float(v) for v in args.sig_bins]
    else:
        x_values = numpy.arange(9, 14, .05)
elif args.sig_type == 'ifar':
    xlabel = 'Inverse False Alarm Rate (years)'
    if args.sig_bins:
        x_values = [float(v) for v in args.sig_bins]
    else:
        x_values = 10. ** (numpy.arange(2, 4, .05))
elif args.sig_type == 'fap':
    xlabel = 'False Alarm Probability'
    if args.sig_bins:
        x_values = [float(v) for v in args.sig_bins]
    else:
        x_values = 10. ** -numpy.arange(1, 7)

if args.hdf_out:
    plotdict = {}
    plotdict['xvals'] = x_values

# Switches for plotting inclusive/exclusive significance
color = iter(cm.rainbow(numpy.linspace(0, 1, len(param_bins)-1)))
if not args.exclusive_sig:
    fvalues = [found['sig'], found['sig_exc']]
    do_labels = [True, False]
    alphas = [.8, .3]
else:
    fvalues = [found['sig_exc']]
    do_labels = [True]
    alphas = [.6]

fig = pylab.figure()
# Cycle over parameter bins plotting each in turn
for j in range(len(param_bins)-1):
    c = next(color)

    # cycle over inclusive / exclusive significance if available
    for sig_val, do_label, alpha in zip(fvalues, do_labels, alphas):
        if sig_val[0] is None:
            logging.info('Skipping exclusive significance')
            continue

        left  = float(param_bins[j])
        right = float(param_bins[j+1])
        logging.info('Injections between param values %5.2f and %5.2f' %
                     (left, right))

        # Get distance of missed injections within parameter bin
        binm = numpy.logical_and(missed['param'] >= left,
                                 missed['param'] < right)
        m_dist = missed['dist'][binm]

        # Abort if the bin has too few triggers
        if len(m_dist) < 2:
           continue

        vols, vol_errors = [], []

        # Slice up found injections in parameter bin
        binf = numpy.logical_and(found['param'] >= left,
                                 found['param'] < right)
        binfsig  = sig_val[binf]

        # Calculate each sensitive distance at a given significance threshold
        for x_val in x_values:
            logging.info('Thresholding on significance at %5.2f' % x_val)
            # Count found inj towards sensitivity if IFAR/stat exceeds threshold
            # or if FAP value is less than threshold
            if args.sig_type == 'ifar' or args.sig_type == 'stat':
                loud = binfsig >= x_val
                quiet = binfsig < x_val
            elif args.sig_type == 'fap':
                loud = binfsig <= x_val
                quiet = binfsig > x_val

            # Distances of inj found above threshold
            f_dist = found['dist'][binf][loud]
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

                print('Ezzz', len(f_dist), len(m_dist_full))
                if args.integration_method == 'mc':
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
            reach, ehigh, elow = 2.303*10**9/(vols*t), 2.303*10**9/(t*vol_errors), 2.303*10**9/(t*vol_errors)

        label = labels[args.bin_type] % (left, right) if do_label else None
        pylab.plot(x_values, reach, label=label, c=c)
        pylab.plot(x_values, reach, alpha=alpha, c='black')
        pylab.fill_between(x_values, reach - elow, reach + ehigh,
                           facecolor=c, edgecolor=c, alpha=alpha)
        if label and args.hdf_out:
            data_val = '%.3f'% ((right+left)/2.0)
            plotdict['data/%s' % data_val] = reach
            plotdict['errorhigh/%s' % data_val] = ehigh
            plotdict['errorlow/%s' % data_val] = elow

if args.hdf_out:
    outfile = h5py.File(args.hdf_out,'w')
    for key in plotdict.keys():
        outfile.create_dataset(key, data=plotdict[key])

ax = pylab.gca()

if args.log_dist:
    ax.set_yscale('log')

if args.sig_type != 'stat':
    ax.set_xscale('log')

if args.sig_type == 'fap':
    ax.invert_xaxis()

if args.min_dist is not None:
    pylab.ylim(ymin=args.min_dist)
if args.max_dist is not None:
    pylab.ylim(ymax=args.max_dist)

pylab.ylabel(ylabel)
pylab.xlabel(xlabel)

pylab.grid()
pylab.legend(loc='lower left')

pycbc.results.save_fig_with_metadata(fig, args.output_file,
     title="Sensitive %s vs %s: binned by %s using %s method"
            % (args.dist_type.title(), args.sig_type.upper(),
               args.bin_type, args.integration_method),
     caption="Sensitive %s as a function of Significance:"
             "Lighter lines represent the significance without"
             " including injections in their own background,"
             " while darker lines include each injection"
             " individually in the background. The integration"
             " method used is based on %s."
             % (args.dist_type.title(), args.integration_method),
     cmd=' '.join(sys.argv))

