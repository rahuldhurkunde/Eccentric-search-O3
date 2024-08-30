import h5py
import numpy as np
import matplotlib.pyplot as plt
import sys
from pycbc import conversions
from scipy.interpolate import interp1d, griddata, RegularGridInterpolator, Rbf

fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot()

efile = 'O3-results-e.hdf'
e_dict = h5py.File(efile)

mcfile = 'O3-results-mc.hdf'
mc_dict = h5py.File(mcfile)

for key in e_dict.keys():
    e = e_dict[key]
    mc = mc_dict[key]    

    x = np.linspace(np.log10(min(e_dict[key])), np.log10(max(e_dict[key])), 500)
    interp = interp1d(np.log10(e), mc, fill_value='extrapolate', kind='linear')
    snr = np.full(x.shape, float(key))

    ax.scatter(x, interp(x), label=float(key))
    ax.scatter(np.log10(e), mc, marker='x', color='black')

plt.grid()
plt.ylabel('$\mathcal{M}_c$')
plt.xlabel('log(e)')
plt.legend(title='SNR')
#plt.savefig('2d.png', dpi=600)
plt.show()

