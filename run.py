#!/usr/env python
import subprocess
import sys
import glob

bank = sys.argv[1]
run = sys.argv[2]
chunk = sys.argv[3]
print(bank, run, chunk)

if run == 'O1':
    data = 'data/data_O1.ini'
elif run == 'O2' and chunk == '15p':
    data = 'data/data_15p.ini'
elif run == 'O2' and int(chunk) <= 18:
    data = 'data/data_O2_twoifo.ini'
elif run == 'O2' and int(chunk) >= 19:
    data = 'data/data_O2.ini'
elif run == 'O3':
    data = 'data/data_O3.ini'
elif run == 'O3b':
    data = 'data/data_O3b.ini'
elif run == 'test':
    data = 'data/data_test.ini'

print('CHECK CACHE FILE BEING USED \n')

configs = glob.glob("config/*.ini")
#configs.append("bank/bank_{}.ini".format(bank))
configs.append("times/gps_times_{}_analysis_{}.ini".format(run, chunk))
configs.append(data)
outdir = 'runs/{}/{}/{}'.format(bank, run, chunk)

print(outdir)
print(configs)
subprocess.run(["pycbc_make_coinc_search_workflow",
                "--workflow-name", "gw",
				"--config-overrides", "results_page:output-path:html",
                "--output-dir", "{}".format(outdir),
                "--config-files"] + configs)
