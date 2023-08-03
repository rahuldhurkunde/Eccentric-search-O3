#python library/custom_sens.py --dist-type distance --dist-bins 50  --integration-method mc --distance-param chirp_distance --xaxis mchirp  --distribution uniform   --injection-file inj_results/*.hdf --hdf-out $1 --verbose --constraint-param eccentricity --constraint-value $2 --constraint-value-tol 0.01 --ifar 100.0


#Use this to compute rate versus eccentricity for different values of mchirp
python library/custom_sens.py --dist-type distance  --dist-bins 50  --integration-method mc --distance-param chirp_distance --xaxis eccentricity --custom-xvalues 0.0 0.05 0.1 0.2 0.27 0.29 --distribution uniform   --injection-file inj_results/*.hdf --hdf-out $1 --verbose --constraint-param mchirp --constraint-value $2 --constraint-value-tol 0.01 --ifar 100.0 

# Use this for individual plots --  3 input options!!
#python library/custom_sens.py --dist-type distance  --dist-bins 50  --integration-method mc --distance-param chirp_distance --xaxis eccentricity --custom-xvalues 0.0 0.05 0.1 0.2 0.27 --distribution uniform   --injection-file $1 --hdf-out $2 --verbose --constraint-param mchirp --constraint-value $3 --constraint-value-tol 0.01 --ifar 1000.0 


#mchirp = [1.21877079,2.01903774,2.93015605,3.13926747]



