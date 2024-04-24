if [ $# -eq 0 ]
then
	echo "Provide the dir"
	exit 1
else
		dir=$1
		echo "Executing in dir $dir"
		for i in {0..19}; do
		start=`echo "28.0* $i + 40.0" | bc`
		end=`echo "28.0* ($i + 1) + 40.0" | bc`
		echo $i $start $end

		OMP_NUM_THREADS=1 \
		condor_run -a accounting_group=cbc.prod.search -a request_memory=10000 unbuffer pycbc_brute_bank \
		--verbose \
		--output-file $dir/part-$i.hdf \
		--minimal-match 0.965 \
		--tolerance .005 \
		--buffer-length 4 \
		--sample-rate 2048 \
		--tau0-threshold 0.5 \
		--approximant TaylorF2Ecc \
		--tau0-crawl 10 \
		--tau0-start $start \
		--tau0-end $end \
		--params mass1 mass2 spin1z spin2z eccentricity long_asc_nodes \
		--min 1.0  1.0 -0.1 -0.1 0.0  0.0 \
		--max 9.0  9.0  0.1  0.1 0.28 6.283  \
		--max-mtotal 10.0 \
		--psd-file ../o3psd.txt \
		--seed 1 \
		--low-frequency-cutoff 20.0  >  $dir/$i.out &
		done
fi
