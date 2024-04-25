# Eccentric search for Neutron star-black hole (NSBH) and binary neutron star (BNS) mergers within O3 advanced LIGO and advanced VIRGO data
**[Rahul Dhurkunde]<sup>1, 2</sup>, Alexander H. Nitz<sup>3</sup>,**

<sub>1. [Max-Planck-Institut for Gravitationsphysik (Albert-Einstein-Institut), D-30167 Hannover, Germany](http://www.aei.mpg.de/obs-rel-cos)</sub>  
<sub>2. Leibniz Universitat Hannover, D-30167 Hannover, Germany</sub>  
<sub>3. Department of Physics, Syracuse University, Syracuse, NY 13244, USA </sub>

<img src="https://images.indianexpress.com/2021/06/NSBH-merger-graphic.png" width=700/>

*(Image credits: Soheb Mandhai)*

## Introduction ##
The possible formation histories of neutron star binaries remain unresolved by current gravitational-wave catalogs. The detection of an eccentric binary system could be vital in constraining compact binary formation models. We present the first search for aligned spin eccentric neutron star-black hole binaries (NSBH) and the most sensitive search for aligned-spin eccentric binary neutron star (BNS) systems using data from the third observing run of the advanced LIGO and advanced Virgo detectors. No new statistically significant candidates are found; we constrain the local merger rate to be less than 150 $\text{Gpc}^{-3}\text{Yr}^{-1}$ for binary neutron stars in the field, and, 50, 100, and 70 $\text{Gpc}^{-3}\text{Yr}^{-1}$ for neutron star-black hole binaries in globular clusters, hierarchical triples and nuclear clusters, respectively, at the 90$\%$ confidence level if we assume that no sources have been observed from these populations. We predict the capabilities of upcoming and next-generation observatory networks; we investigate the ability of three LIGO (A#) detectors and Cosmic Explorer CE (20km) + CE (40km) to use eccentric binary observations for determining the formation history of neutron star binaries. We find that 2 -- 100 years of observation with three A# observatories are required before we observe clearly eccentric NSBH binaries; this reduces to only 10 days -- 1 year with the CE detector network. CE will 
observe tens to hundreds of measurably eccentric binaries from
each of the formation models we consider.

A preprint version of the paper is available on arXiv. This release contains the following:
* Search
    * Configuration files for the search, template bank, and injections used for the analysis.
* Search results
    * List of top candidates 
    * The search sensitivity as a function of mchirp and eccentricity (HDF5 files).
* Constraints 
  * Population synthesis data -- Mchirp and eccentricity samples.
  * Noise ASDs used to compute the optimal SNRs for the idealized searches.
  * Jupyter-lab notebooks to obtain the 90 % upper limits on the local merger rate.
* Measurability analysis
  * Scripts to compute the simplified Bayesian inference.
  * Dictionary of measurable binary sources for given SNRs (keys). 


** The simulated data for the idealized searches is not provided due to the file size limit on GITHUB. This can be made available upon reasonable requests    

## License and Citation

![Creative Commons License](https://i.creativecommons.org/l/by-sa/3.0/us/88x31.png "Creative Commons License")

This work is licensed under a [Creative Commons Attribution-ShareAlike 3.0 United States License](http://creativecommons.org/licenses/by-sa/3.0/us/).

We encourage use of these data in derivative works. If you use the material provided here, please cite the paper using the reference:
