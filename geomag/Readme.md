## GICs code

This Python code is being developed in the framework of a DLR-SO-WWE project that aims at assessing the impact of space weather on the German power grid.

**Author**: Leonie Pick; DLR Institute for Solar-Terrestrial Physics, Leonie.Pick@dlr.de

#### 1) Code structure

+ **binder.ipy**: Top-level script from which individual pipeline scripts are being called. Run via IPython with *%run binder.ipy*
  + **Get_Obs.py**: Handles the acquisition and preprocessing of the geomagnetic observatory data using an object "x" from class "DatLib". Needs google sheet 'IAGA_obs.csv' exported from https://www2.bgs.ac.uk/iaga/vobs/
    + Module **Obs.py**: Class "DatLib" and associated methods (in ./callable/)
  + **Get_SECS.py**: Handles the spatial interpolation of the geomagnetic data using an object "y" from class "SECSLib". Based on the Matlab code provided as supplementary material to https://link.springer.com/chapter/10.1007%2F978-3-030-26732-2_2
    + Module **SECS.py**: Class "SECSLib" and associated methods (in ./callable/)

#### 2) Folders

The project folder is located on knnzfs01 at path = '/NZ_Projects/Iono-PDRV-NAV-NZ/Iono_WWE/SO_Projects/PROJECT_SW_on_Satellites/'

+ CPath (code): Wherever you clone the GitLab project (your home directory)
+ DPath (data): path+'80_Data'
+ RPath (results): path+'20_Deliverables'

#### 3) Dependencies

- Python (3.8.5)

- Numpy (1.19.1)
- Pandas (1.1.1)
- IPython (7.18.1)
- Matplotlib (3.3.1)
- Cartopy (0.18.0): Needs shape file 'gadm36_DEU_1.shp' from https://gadm.org/download_country_v3.html (in DPath/gadm36_DEU_shp/)

- Chaosmagpy (0.4): https://github.com/ancklo/ChaosMagPy; Needs model coefficients 'CHAOS-7.2.mat' from http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/ (in DPath)
- **gd2gc.py**: Conversion from geodetic (ellipsoidal) to geocentric (spherical) coordinates and back (in ./callable/)