#start=1257131340
#end=1257549313

if [ $# -eq 0 ]
then
	echo "Provide Run and chunk"
	exit 1
else
	echo "Run - $1, chunk $2"
	start=$(awk '{print $3}' ../times/gps_times_$1_analysis_$2.ini | sed -n '2p')
	end=$(awk '{print $3}' ../times/gps_times_$1_analysis_$2.ini | sed -n '3p')

	echo "GPS start $start" 
	echo "GPS end $end" 

	pycbc_create_injections --config-file one-chunk.ini --output-file $1/$2.hdf --seed 123 --gps-start-time $start --gps-end-time $end --time-step 200 --time-window 100
	
	python add_masses_and_eccentricity.py $1/$2.hdf
fi
