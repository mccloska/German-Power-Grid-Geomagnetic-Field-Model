#%%
"""
Purpose: Main code to calculate geoelectric field using plane wave method given B-field SECS interpolated time series as input (from Geomag code)
         + 1-D Earth conductivity model (EURHOM)
         Method based on "Analysis of the impact of geomagnetic disturbances on the Austrian transmission grid," 2016 Power Systems Computation Conference (PSCC), 
                   2016, pp. 1-5, doi: 10.1109/PSCC.2016.7540833. (https://ieeexplore.ieee.org/abstract/document/7540833)

Input : SECS*.obj
        Obs*.obj

Author: Aoife McCloskey (aoifemccloskey91@gmail.com)
"""
import sys
# Call geomag module to import SECS 
sys.path.insert(0, 'C:/Users/mccl_ao/Documents/DLR/Codes/GIC_Project/geomag/callable')
import pickle
#import cartopy
import SECS 
import numpy as np
import efield_funcs
import matplotlib.pyplot as plt
from scipy.fftpack import ifft as ifft
import scipy
from scipy.signal import detrend
import matplotlib

# Local path to data 
dpath = 'C:/Users/mccl_ao/Documents/DLR/Data/geomag_leonie/efield_data/'
#local path to write data
rpath = 'C:/Users/mccl_ao/Documents/DLR/Data/geomag_leonie/efield_data/'
# Server path to SECS output data
dpath_secs = r'Y:/Iono-PDRV-NAV-NZ/Iono_WWE/SO_Projects/PROJECT_SW_on_PowerNetworks/80_Data/' 
rpath_secs = r'Y:/Iono-PDRV-NAV-NZ/Iono_WWE/SO_Projects/PROJECT_SW_on_PowerNetworks/30_Deliverables/' 
#%%
mu_0 = 4.*np.pi*1E-7
"""
# Import data to compare and validate Halbedl, ...,Bailey et al. (https://ieeexplore.ieee.org/abstract/document/7540833)

with open(dpath+'bailey_data/SECS_2015_03_22_WIC.obj', 'rb') as f:
	data = pickle.load(f)

with open(dpath+'bailey_data/Obs_2015_03_22_WIC.obj', 'rb') as f:
	Obs = pickle.load(f)


with open(dpath+'bailey_data/SECS_2015_03_22_red.obj', 'rb') as f:
	data = pickle.load(f)

with open(dpath+'bailey_data/Obs_2015_03_22_red.obj', 'rb') as f:
	Obs = pickle.load(f)

"""
# 2017 September storm data
with open(dpath_secs+'SECS_2017_09_07.obj', 'rb') as f:
	data = pickle.load(f)

with open(dpath_secs+'Obs_2017_09_07.obj', 'rb') as f:
	Obs = pickle.load(f)

Bx= data.BX_int
By= data.BY_int

t = Obs.data.loc[Obs.meta['obs'][0],:].index
date = Obs.meta['year'][0]+ Obs.meta['month'][0]
s_rate=60.
# Cut first time step as there are no values
t=t[1:]
#%%
# Convert to nT
Bx=Bx[1:,:]*1E-9
By=By[1:,:]*1E-9

#fig_efield = plt.figure()
# Number of grid points to calculate e-field
n_points=3
#n_points = len(Bx[0,:])

# Array to store values of E-field
arr_ex =  np.empty(shape=Bx.shape,dtype=np.complex_)
arr_ey =  np.empty(shape=By.shape,dtype=np.complex_)

# Extract longitude and latitude arrays + flatten (1D)
secslon_1d = data.meta['Bintlon'].flatten()
secslat_1d = data.meta['Bintlat'].flatten()

# set plot variable: 0 (no plot) , 1 (plot)
plot = 0
#%%
i=0
for grid_p in np.arange(200,203):

    print(grid_p)

    # Loop over each grid point for every time instance
    X = Bx[:,grid_p]
    Y = By[:,grid_p]
    
    # Calculate FFT of Bx and By
    freq, x_filt,fft_x = efield_funcs.FFT_B(X,dpath,rpath,t,s_rate,save=0,label='Bx')
    freq, y_filt, fft_y= efield_funcs.FFT_B(Y,dpath,rpath,t,s_rate,save=0,label='By')
      
    # Lat and lon point  
    lat_p = secslat_1d[grid_p]
    lon_p = secslon_1d[grid_p]
    print(lat_p, lon_p)
    
    if plot == 1: 
      fig_eb,(ax_eb1,ax_eb2,ax_eb3) = plt.subplots(3,1,figsize=(16,18)) 
    else:
      fig_eb, ax_eb1, ax_eb2, ax_eb3 = [0,0,0,0]

    # Calculate impedance values using 1D conductivity model 
    z = efield_funcs.conductivity_1D(freq,ax_eb1, lat_p, lon_p,rpath=rpath, plot_= plot)

    # Calculate e-field using 3D model (see function for more info)
    #z = efield_funcs.conductivity_3D(lat, lon, freq)

    N = len(freq)
    # Calculate E-field FFT using 
    Ex_fft = ((fft_y)*z)/mu_0
    Ey_fft = (-(fft_x)*z)/mu_0

    #plt_fftex = efield_funcs.plot_fft(freq,Ex_fft)
    #plt_fftey = efield_funcs.plot_fft(freq,Ey_fft)

    #Ex = ifft(Ex_fft + np.conj(np.roll(Ex_fft[::-1], 1))).real * 1000
    #Ey = ifft(Ey_fft + np.conj(np.roll(Ey_fft[::-1], 1))).real * 1000

    # Calculate Inverse Fourier Transform 
    Ex = efield_funcs.IFFT_E(freq,Ex_fft,t)*1000.
    Ey = efield_funcs.IFFT_E(freq,Ey_fft,t)*1000.

    # Method using conjugate
    #Ey= (np.real(ifft(Ex_fft + np.conj(np.roll(Ex_fft[::-1],1)))))* (1000.)
    #Ex= (np.real(ifft(Ey_fft + np.conj(np.roll(Ey_fft[::-1],1)))))* (1000.)

    arr_ex[:,i]= Ex
    arr_ey[:,i] = Ey
    i+=1

    if plot == 1:
      efield_funcs.plot_bfield(t,X,Y,Obs,grid_p,lat_p,lon_p, ax_eb2,type='B_mean')
      efield_funcs.plot_efield(t, Ex, Ey,grid_p,lat_p,lon_p,ax_eb3)

# save arrays to pickle format
"""
with open(rpath+'ex'+date+'.pkl','wb') as f:
    pickle.dump(arr_ex, f)
with open(rpath+'ey'+date+'.pkl','wb') as f:
    pickle.dump(arr_ey, f)
"""

#%%
#with open(dpath+'ex.pkl', 'rb') as f:
#	arr_ex = pickle.load(f)

#with open(dpath+'ey.pkl', 'rb') as f:im
 #   arr_ey = pickle.load(f)

#%%

#for step in np.arange(0,len(arr_ex),60):
 #   efield_funcs.plot_efield(data,arr_ex,arr_ey,dpath,rpath,t,Obs,step)
  # efield_funcs.plot_bfield(y,Bx,By,dpath,rpath,t,Obs,step,save=1)




#for step in np.arange(17000,21320,60): # every hour
#for step in [0]: # first minute of time interval

    #y.get_Bplot(Bx,By,dpath_secs,rpath_secs+'SECS_Maps/',t,step,x,save=0)


# %%
