#!/usr/env python
import subprocess
import sys
import glob

run = sys.argv[1]
chunk = sys.argv[2]
print('Run ', run, 'Chunk', chunk)

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


cache = True 

if cache == True:
	cache_file = 'runs/{}/{}/partial_workflow.map'.format(run, chunk)
	print('CACHE FILE USED \n', cache_file, '\n')
	wf_name = 'gwv4'

elif cache == False:
	print('OG workflow')
	wf_name = 'gw'

print('CHECK workflow name \n', wf_name, '\n')

configs = glob.glob("config/*.ini")
configs.append("times/gps_times_{}_analysis_{}.ini".format(run, chunk))
configs.append(data)

if cache == True:
	outdir = 'runs/{}/{}/{}'.format(run, chunk, wf_name)
else:
	outdir = 'runs/{}/{}'.format(run, chunk)

print('Outdir \t', outdir)
print(configs)

if cache == True:
	subprocess.run(["pycbc_make_coinc_search_workflow",
					"--workflow-name", "{}".format(wf_name),
					"--cache-file", "{}".format(cache_file),
					"--config-overrides", "results_page:output-path:html",
					"--output-dir", "{}".format(outdir),
					"--config-files"] + configs)
else:
	subprocess.run(["pycbc_make_coinc_search_workflow",
					"--workflow-name", "{}".format(wf_name),
					"--config-overrides", "results_page:output-path:html",
					"--output-dir", "{}".format(outdir),
					"--config-files"] + configs)

