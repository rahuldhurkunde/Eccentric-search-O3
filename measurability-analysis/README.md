## This directory contains the scripts used and the results for measurable eccentric systems. 


## Scripts used for simplified parameter estimation



* <span style="text-decoration:underline;">dynesty-fisher.py </span>– Uses dynesty to sample over the $\mathcal{M}__c$, $q$ and $e_$ parameter space.
* <span style="text-decoration:underline;">fixed-q-fisher.py</span> – Similar to the above script, but fixes $q$ while sampling.


## Results

Measurable eccentric systems for various detector networks as a function of $\mathcal{M}_c, e$ for different SNR of the signal. We have provided the script **plot_measurable_ecc_parameters.py ** to visualize the regions of the parameter space that are deemed measurable for a given SNR: the areas that lie below the curve are deemed to have measurable eccentricity.


## Comparison plots

We have also added comparison plots for our simplified PE against a more robust PE estimation in which we vary six parameters.
