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


** The simulated data for the idealized searches is not provided due to the file size limit on GITHUB. This can be made available upon reasonable requests.    


# Constraints on the local merger rate 

## Modeled predicted rates


<table>
  <tr>
   <td>Isolated binary (Belczynski et al. (2018a))
   </td>
   <td>[8.0, 50.0]
   </td>
  </tr>
  <tr>
   <td>Globular cluster (Arca Sedda (2020b))
   </td>
   <td> <=0.1
   </td>
  </tr>
  <tr>
   <td>Triples (Trani et al. (2021))
   </td>
   <td>[0.04, 0.34]
   </td>
  </tr>
  <tr>
   <td>Nuclear cluster (Fragione et al. (2019))
   </td>
   <td>[0.06. 0.1]
   </td>
  </tr>
</table>



## Observational constraints for O3


<table>
  <tr>
   <td>Isolated binary (Belczynski et al. (2018a))
   </td>
   <td>149.02243058810643
   </td>
  </tr>
  <tr>
   <td>Globular cluster (Arca Sedda (2020b))
   </td>
   <td>53.36526395563427
   </td>
  </tr>
  <tr>
   <td>Triples (Trani et al. (2021))
   </td>
   <td>97.976810617951
   </td>
  </tr>
  <tr>
   <td>Nuclear cluster (Fragione et al. (2019))
   </td>
   <td>70.44463776334753
   </td>
  </tr>
</table>



## Idealized constraints for various detector networks

We have estimated constraints for an idealized search that covers the entire parameter space of the astrophysical model, and captures the signal SNR perfectly.  We provide three different types of constraints on each population:



* Full population
* Eccentric systems above a fixed eccentricity >= 0.01
* Measurable eccentric systems


### <span style="text-decoration:underline;">Full population constraints </span>



* Three Asharp detectors

<table>
  <tr>
   <td>
Isolated binary (Belczynski et al. (2018a))
   </td>
   <td>0.48555766392578537
   </td>
  </tr>
  <tr>
   <td>Globular cluster (Arca Sedda (2020b))
   </td>
   <td>0.10645969508981815
   </td>
  </tr>
  <tr>
   <td>Triples (Trani et al. (2021))
   </td>
   <td>0.0778671896131999
   </td>
  </tr>
  <tr>
   <td>Nuclear cluster (Fragione et al. (2019))
   </td>
   <td>0.10731093611667676
   </td>
  </tr>
</table>




* CE (40km baseline) + CE(20km baseline)

<table>
  <tr>
   <td>
Isolated binary (Belczynski et al. (2018a))
   </td>
   <td>0.0021919213943572277
   </td>
  </tr>
  <tr>
   <td>Globular cluster (Arca Sedda (2020b))
   </td>
   <td>0.0011257530053556922
   </td>
  </tr>
  <tr>
   <td>Triples (Trani et al. (2021))
   </td>
   <td>0.0010080234416283082
   </td>
  </tr>
  <tr>
   <td>Nuclear cluster (Fragione et al. (2019))
   </td>
   <td>0.001082967826882465
   </td>
  </tr>
</table>



### <span style="text-decoration:underline;">Fixed ecc >= 0.01 constraints</span>



* Three Asharp detectors

<table>
  <tr>
   <td>
Isolated binary (Belczynski et al. (2018a))
   </td>
   <td>677.3529411764706
   </td>
  </tr>
  <tr>
   <td>Globular cluster (Arca Sedda (2020b))
   </td>
   <td>3.330922765403529
   </td>
  </tr>
  <tr>
   <td>Triples (Trani et al. (2021))
   </td>
   <td>0.1157658744520851
   </td>
  </tr>
  <tr>
   <td>Nuclear cluster (Fragione et al. (2019))
   </td>
   <td>0.12335693701993637
   </td>
  </tr>
</table>




* CE (40km baseline) + CE(20km baseline)

<table>
  <tr>
   <td>
Isolated binary (Belczynski et al. (2018a))
   </td>
   <td>2.6722573839662442,
   </td>
  </tr>
  <tr>
   <td>Globular cluster (Arca Sedda (2020b))
   </td>
   <td>0.034350762054564186
   </td>
  </tr>
  <tr>
   <td>Triples (Trani et al. (2021))
   </td>
   <td>0.0014993702562062906
   </td>
  </tr>
  <tr>
   <td>Nuclear cluster (Fragione et al. (2019))
   </td>
   <td>0.0012444783733012645
   </td>
  </tr>
</table>



### <span style="text-decoration:underline;">Measurable eccentric systems</span>



* Three Asharp detectors

<table>
  <tr>
   <td>
Isolated binary (Belczynski et al. (2018a))
   </td>
   <td>1279.0
   </td>
  </tr>
  <tr>
   <td>Globular cluster (Arca Sedda (2020b))
   </td>
   <td> 8.53
   </td>
  </tr>
  <tr>
   <td>Triples (Trani et al. (2021))
   </td>
   <td>0.7375
   </td>
  </tr>
  <tr>
   <td>Nuclear cluster (Fragione et al. (2019))
   </td>
   <td>0.2632
   </td>
  </tr>
</table>




* CE (40km baseline) + CE(20km baseline)

<table>
  <tr>
   <td>
Isolated binary (Belczynski et al. (2018a))
   </td>
   <td>1.712
   </td>
  </tr>
  <tr>
   <td>Globular cluster (Arca Sedda (2020b))
   </td>
   <td>0.06979
   </td>
  </tr>
  <tr>
   <td>Triples (Trani et al. (2021))
   </td>
   <td>0.009821
   </td>
  </tr>
  <tr>
   <td>Nuclear cluster (Fragione et al. (2019))
   </td>
   <td>0.004279
   </td>
  </tr>
</table>



## License and Citation

![Creative Commons License](https://i.creativecommons.org/l/by-sa/3.0/us/88x31.png "Creative Commons License")

This work is licensed under a [Creative Commons Attribution-ShareAlike 3.0 United States License](http://creativecommons.org/licenses/by-sa/3.0/us/).

We encourage use of these data in derivative works. If you use the material provided here, please cite the paper using the reference:
