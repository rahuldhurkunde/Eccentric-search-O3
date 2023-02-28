import numpy as np
import h5py
import matplotlib.pyplot as plt
import sys
import pylab

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return  array[idx], idx

datafile = sys.argv[1]
print("Reading \t ", datafile)

ifar_given = float(sys.argv[2])
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
pylab.plot(xvals, reach, label='IFAR %g' %ifar)
pylab.plot(xvals, reach, alpha=0.6, c='black')
pylab.fill_between(xvals, reach - elow, reach + ehigh,
                   alpha=0.6)


pylab.xlabel('Eccentricity (20Hz)')
pylab.ylabel('Sensitive distance')
pylab.grid()
pylab.legend()
plt.title('For 1.4-1.4 type systems')
plt.savefig(sys.argv[3], dpi=600)
pylab.show()
