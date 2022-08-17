start=1257131340
end=1257549313

echo "GPS start $start" 
echo "GPS end $end" 

pycbc_create_injections --config-file one-chunk.ini --output-file one-chunk.hdf --seed 123 --gps-start-time $start --gps-end-time $end --time-step 200 --time-window 100
