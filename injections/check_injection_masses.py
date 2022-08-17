import h5py
import numpy as np
import matplotlib.pyplot as plt
import sys

hf = h5py.File(sys.argv[1])
mass1 = hf['mass1'][:]
mass2 = hf['mass2'][:]
mtotal = mass1 + mass2
q = np.divide(mass1, mass2)

#bank = '/work/rahul.dhurkunde/searches/eccentric-bns-search/banks/spinecc/mtotal-10_ecc-0.28_spin-0.1/small_bank.hdf'
bank = '/work/rahul.dhurkunde/searches/eccentric-bns-search/banks/spinecc/mtotal-10_ecc-0.28_spin-0.1/mtotal-10_ecc-0.28_spin-0.1.hdf'
print("!!! Check the bank file !!! \n", bank)

hf = h5py.File(bank)
bank_m1 = hf['mass1'][:]
bank_m2 = hf['mass2'][:]
bank_mtotal = bank_m1 + bank_m2
bank_q = np.divide(bank_m1, bank_m2)

plt.scatter(bank_mtotal, bank_q, label = 'templates')
plt.scatter(mtotal, q, label = 'injection')
plt.legend()
plt.show()
