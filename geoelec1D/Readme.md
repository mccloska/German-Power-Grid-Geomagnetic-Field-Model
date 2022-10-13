## geoelec1D (1-D Geoelectric Field Code)

This Python code is being developed in the framework of a DLR-SO-WWE project that aims at assessing the impact of space weather on the German power grid. 

**Author**: Aoife McCloskey; DLR Institute for Solar-Terrestrial Physics, aoife.mccloskey@dlr.de (alt:aoifemccloskey91@gmail.com)

#### 1) Code structure

+ **geoelec_calc_main.py**: Main script, run via IPython with *%run geoelec_calc_main.py*
  + **efield_funcs.py**: Contains all functions called in geoelec_calc_main
    + Module **SECS.py**: Class "SECSLib" and associated methods (in geomag/callable/)

#### 2) Folders

The project folder is located on knnzfs01 at path = '/NZ_Projects/Iono-PDRV-NAV-NZ/Iono_WWE/SO_Projects/PROJECT_SW_on_PowerNetworks/'


+ DPath (data): path+'80_Data'
+ RPath (results): path+'20_Deliverables'

#### 3) Dependencies

- Python (3.8.5)

- Numpy (1.2.3)
- Pandas (1.1.2)
- IPython (7.18.1)
- Matplotlib (3.3.2)
- Scipy (1.6.2)
