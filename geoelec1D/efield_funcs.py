#%%
import numpy as np
#import ftplib
import datetime as dt
import os
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.io.shapereader as shpreader
#import matplotlib.animation as animation
import matplotlib.ticker as mticker
import cartopy.crs as ccrs
from scipy.fft import fft, fftfreq,ifft
import matplotlib.pyplot as plt
import h5py
import cartopy
from matplotlib import colors, ticker, cm
from photutils import TukeyWindow
from math import factorial
from scipy.signal import detrend

plt.rc('font', size=14)

def FFT_B(B,dpath,rpath,t,step,save,label):
# Calculate and plot Fast Fourier Transform of time series
    B -= np.nanmean(B,axis=0)

    # Number of sample points
    N = len(B)
    # sampling rate (seconds)
    T = step 
    #window noisy wings
    #  w= (np.kaiser(len(Bx),beta=2))
    w = tukey(B.shape[0], 0.1) 
    y = B * w
    x = np.linspace(0.0, N*T, N, endpoint=False)
    # Find null values and interpolate
    mask = np.isfinite(y)
    yfilt = np.interp(x, x[mask], y[mask])
    # Detrend the data if necessary
    #yfilt = detrend(yfilt)
    yfft = fft(yfilt)
    xf = fftfreq(N, T)#[:N//2]
    all_freq = fftfreq(N,T)

    for i in range(0,len(all_freq)):
        if all_freq[i] == 0:
            all_freq[i] = 1e-99
    return all_freq, yfilt,yfft


def IFFT_E(freq,E,t):
# Calculate Inverse Fast Fourier Transform of time series
    
    x = t
    y = E
    mask = np.isfinite(y)
    yfilt = np.interp(x, x[mask], y[mask])
    yifft = ifft(yfilt)

    return yifft


def plot_bfield(t,Bx,By,Obs,grid_p,lat,lon,ax,type):
    
    orig_x_wng= Obs.data.X.wng
    orig_y_wng = Obs.data.Y.wng

    if type == 'B':
        # Plot B-field total mag.
        X = Bx
        Y = By
        y_txt = "B (nT)"
        max_X_idx = np.where(abs(X)== np.nanmax(abs(X)))
        max_Y_idx = np.where(abs(Y)== np.nanmax(abs(Y)))
        print('Max Bx = {} \n Timestamp = {}'.format(np.nanmax(abs(X)), t[max_X_idx]))
        print('Max By = {} \n Timestamp = {}'.format(np.nanmax(abs(Y)), t[max_Y_idx]))

    if type == 'dB':
        # Plot dB/dt 
        X = np.gradient(Bx, axis=0)
        Y = np.gradient(By, axis=0)
        X_wng = np.gradient(orig_x_wng)
        Y_wng = np.gradient(orig_y_wng)
        max_X_idx = np.where(abs(X_wng)== np.nanmax(abs(X_wng)))
        max_Y_idx = np.where(abs(Y_wng)== np.nanmax(abs(Y_wng)))
        print('Max dBx/dt = {} \n Timestamp = {} \n Index'.format(np.nanmax(abs(X_wng)), t[max_X_idx]),max_X_idx)
        print('Max dBy/dt = {} \n Timestamp = {}  \n Index'.format(np.nanmax(abs(Y_wng)), t[max_Y_idx]),max_Y_idx)

        y_txt = "dB/dt (nT)"

    if type == 'B_mean':
        # Plot B-field normalised by maximum
        X = Bx
        Y = By
        X -= np.nanmean(Bx,axis=0)
        Y -= np.nanmean(By,axis=0)

        X_wng = orig_x_wng
        Y_wng = orig_y_wng
        X_wng -= np.nanmean(orig_x_wng,axis=0)
        Y_wng -= np.nanmean(orig_y_wng,axis=0)
        
        max_X_idx = np.where(abs(X_wng)== np.nanmax(abs(X_wng)))
        max_Y_idx = np.where(abs(Y_wng)== np.nanmax(abs(Y_wng)))
        y_txt = "B - $\overline{B}$ (nT)"
        print('Max Bx - Bx_mean = {} \n Timestamp = {} \n Index'.format(np.nanmax(abs(X_wng)), t[max_X_idx]),max_X_idx)
        print('Max By - By_mean = {} \n Timestamp = {}  \n Index'.format(np.nanmax(abs(Y_wng)), t[max_Y_idx]),max_Y_idx)


    #ax.vlines(t[max_X_idx],ymin=-500,ymax=500,colors='black',zorder=2,linewidth=0.8)
    #ax.vlines(t[max_Y_idx],ymin=-500,ymax=500,colors='black',linestyles='--',zorder=3,linewidth=0.8)
    # Plot cinterpolated B-field
    #ax.plot(t, X*1E9,label='$B_{x}$  [%s,%s]'%(str(lat),str(lon)),c='darkred',zorder=0)
    #ax.plot(t, Y*1E9,label='$B_{y}$  [%s,%s]'%(str(lat),str(lon)),c='lightcoral',linestyle= '--',zorder=0)
    # Plot WNG obs. mag field (original measured values)
    ax.plot(t, Y_wng[1:], label='$B_{y}$ [WNG]',c='lightcoral',zorder=1)
    ax.plot(t, X_wng[1:],label='$B_{x}$ [WNG]',c='darkred',zorder=2)
    
    ax.grid()
 #   ax.set_xlabel("Time")
    ax.set_ylabel(y_txt)
   # max_arr = np.maximum(X_wng[np.isfinite(X_wng)],Y_wng[np.isfinite(Y_wng)])
   # min_arr = np.minimum(X_wng[np.isfinite(X_wng)],Y_wng[np.isfinite(Y_wng)])
    ax.set_ylim(-200,250)
    #ax.ylim(((np.amin(min_arr)*1E9)+(np.amin(min_arr)/10.)*1E9),((np.amax(max_arr)*1E9)+(np.amax(max_arr)/10)*1E9))
    #ax.title("B-Field (Germany) [%s]"%(str(grid_p)))
    ax.set_title("B-Field Germany")
    ax.legend(loc='upper right')
    #plt.show()

def plot_efield(t,Ex,Ey,grid_p,lat,lon,ax):
        
    # Plot the computed geoelectric field time series ()
    
    ax.plot(t, ((Ex))*1E3, label='$E_{x}$ [%s,%s]'%(str(lat),str(lon)),zorder=0)
    # calculate smoothed time series
    #xhat = savitzky_golay(Ex, 5,3)
    #ax.plot(t, xhat*1E3, label='Smooth $E_{x}$',zorder=2, linewidth=0.7)
    ax.plot(t, ((Ey))*1E3,label='$E_{y}$ [%s,%s]'%(str(lat),str(lon)),zorder=1)
    #yhat = savitzky_golay(Ey, 5, 3)
    #ax.plot(t, yhat*1E3,label='Smooth $E_{y}$',zorder=3,linewidth=0.7)
    #ax.vlines(t[120],ymin=-500,ymax=500,colors='black')
    ax.grid()
    max_arr = np.maximum(Ex.real,Ey.real)
    min_arr = np.minimum(Ex.real,Ey.real)
    max_Ex_idx = np.where(abs(Ex)== np.nanmax(abs(Ex)))
    max_Ey_idx = np.where(abs(Ey)== np.nanmax(abs(Ey)))
    print('Max Ex = {} \n Timestamp = {} \n Index'.format(np.nanmax(abs(Ex)), t[max_Ex_idx]),max_Ex_idx)
    print('Max Ey = {} \n Timestamp = {} \n Index'.format(np.nanmax(abs(Ey)), t[max_Ey_idx]),max_Ey_idx)
  #  ax.vlines(t[max_Ex_idx],ymin=-500,ymax=500,colors='black',zorder=2,linewidth=0.8)
 #   ax.vlines(t[max_Ey_idx],ymin=-500,ymax=500,colors='black',linestyles='--',zorder=3,linewidth=0.8)

    ax.set_ylim(((np.amin(min_arr)*1E3)+(np.amin(min_arr)/10.)*1E3),((np.amax(max_arr)*1E3)+(np.amax(max_arr)/10)*1E3))
    ax.set_ylabel("E (mV/km)")
    ax.set_title("E-Field Germany")
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_fft(freq,fft):
# Calculate and plot Fast Fourier Transform of time series

    plt.clf()
    N = len(fft)
    f = freq[:N//2]
    plt.plot(f, (fft[0:N//2]))
    #plt.plot(f, (2.0/N * (np.abs(fft[0:N//2]))))
    #plt.plot(freq, ((fft)))
    plt.grid()
    plt.xlim(0,0.01)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("FFT")
   # plt.yscale('log')
    plt.show()

def conductivity_1D(frequencies,ax,lat_p,lon_p,rpath, plot_):
    # Calculate impedance
    model_no = eurisgic(lat_p,lon_p)
    
    mu = 4.*np.pi*1E-7

    """
    
    #British Columbia Model (Bailey)
    resistivities = [500.,160.,20.,100.,300.,100.,10.,1.]
    thicknesses = [4000,6000,5000,20000,65000,300000,200000]

    # Botler Model 1994
    resistivities = [40000.,4000.,700,1.]
    thicknesses = [30000.,15000.,355000.]
    
    """
    if model_no == 0:
            #Model 0
        lat_0= np.arange(52, 55,0.5)
        lon_0 = np.arange(2,5,0.5)
        resistivities = [1, 5000, 1, 10] # check ocean conductivity values (CHANGE)
        thicknesses= [2000, 6000, 4000] # CHANGE

    elif model_no == 47:
        #Model 47 [1]

        lat_47= np.arange(50, 55,0.5)
        lon_47 = np.arange(5,8,0.5)
        resistivities = [1, 5000, 1, 10] 
        thicknesses = [2000, 6000, 4000]

    elif model_no == 471:
        #Model 47a [471]

        lat_47a= np.arange(50, 52,0.5)
        lon_47a = np.arange(2,5,0.5)
        resistivities = [1, 5000, 1, 10] 
        thicknesses = [2000, 6000, 4000]

    elif model_no == 12:
        #Model 12

        lat_12= np.arange(52, 55,0.5)
        lon_12 = np.arange(8,12,0.5)
        resistivities = [1, 200, 0.5, 200, 1000, 10] 
        thicknesses = [4000, 4000, 1500, 2000, 100000]

    elif model_no == 13:
        #Model 13

        lat_13= np.arange(50, 55,0.5)
        lon_13 = np.arange(8,12,0.5)
        resistivities = [1,200,0.5,200,1000,10] 
        thicknesses = [4000, 4000,1500,2000,100000]

    elif model_no == 15:
        #Model 15

        lat_15= np.arange(48, 50,0.5)
        lon_15 = np.arange(8,12,0.5)
        resistivities = [1,200,0.5,200,1000,10] 
        thicknesses = [4000,4000,1500,2000,100000]
        
    elif model_no == 11:    
            #Model 11

        lat_11= np.arange(52, 55,0.5)
        lon_11 = np.arange(12,16,0.5)
        resistivities = [200, 0.5, 1000, 10] 
        thicknesses = [5000,1000,100000]

    elif model_no == 14:
                    #Model 14

        lat_14= np.arange(50, 52,0.5)
        lon_14 = np.arange(12,16,0.5)
        resistivities = [1,200,0.5,1000,10] 
        thicknesses = [2000,10000,1000,100000]
        
    elif model_no == 16:
        #Model 16

        lat_16= np.arange(48, 50,0.5)
        lon_16 = np.arange(12,16,0.5)
        resistivities = [1500,500,800,10] 
        thicknesses = [20000,20000,110000]

    elif model_no == 35:
        #Model 35

        lat_35= np.arange(48, 50,0.5)
        lon_35 = np.arange(5,8,0.5)
        resistivities = [40,30,1000,20] 
        thicknesses = [2000,3000,150000]

    elif model_no == 37:
        #Model 37

        lat_37= np.arange(44, 48,0.5)
        lon_37 = np.arange(2,5,0.5)
        resistivities = [10,1500,70000,10000,80] 
        thicknesses = [800,6000,8000,55000]

    elif model_no == 38:
        #Model 38

        lat_38= np.arange(48, 50,0.5)
        lon_38 = np.arange(2,5,0.5)
        resistivities = [10,10000,5] 
        thicknesses = [700,95000]

    elif model_no == 39:
        # Model 39 (Austria) (Bailey)
        
        lat_39= np.arange(46, 48,0.5)
        lon_39 = np.arange(12,16,0.5)
        resistivities = [1000,300,1000] 
        thicknesses = [55000,45000]

    elif model_no == 54:
        #Model 54
        lat_54= np.arange(44,47,0.5)
        lon_54 = np.arange(8,16,0.5)
        resistivities = [100,1000,4] 
        thicknesses = [10000,90000]

    elif model_no == 55:
        # Model 55
        
        lat_55= np.arange(44, 48,0.5)
        lon_55 = np.arange(5,8,0.5)
        resistivities = [110,30,10000,90] 
        thicknesses = [900,1100,150000]

    elif model_no == 551:
        # model 55a [551]

        lat_55a= np.arange(46, 48,0.5)
        lon_55a = np.arange(8,12,0.5)
        resistivities = [110,30,10000,90] 
        thicknesses = [900,1100,150000]
    
    
    n = len(resistivities)  
    surface_impedances = np.zeros(len(frequencies))
    i = 0

    for frequency in frequencies:

        w =  2.*np.pi*frequency;       
        impedances = list(range(n))
        # Impedance of the half-space bottomw layer
        impedances[n-1] = np.sqrt(1j*w*mu*resistivities[n-1]);
        for j in range(n-2,-1,-1):
            resistivity = resistivities[j];        
            thickness = thicknesses[j];
            # Propagation Constant (induction parameter)
            gamma_n = np.sqrt((1j*w * mu * (1./resistivity)));
            # Intrinisic Impedance
            z0_n =  np.sqrt(1j*w*mu*(resistivity));
            # Exponential Factor
            e_n = np.exp(-2.*gamma_n*thickness);
            # Impedance of layer below
            belowImpedance = impedances[j + 1];
            #reflection coefficient
            r_n = (z0_n-belowImpedance)/(belowImpedance+z0_n);
            alpha_n = r_n*e_n; 
            # Impedance of j-layer
            Z_n = z0_n * ((1. - alpha_n)/(1. + alpha_n));
            impedances[j] = Z_n;

        #Impedance of top layer
        #print(impedances)
        Z = impedances[0];
        absZ = abs(Z);
        surface_impedances[i]=(absZ)
        apparentResistivity = (absZ * absZ)/(w);
        phase = np.arctan2(Z.imag, Z.real);
        i += 1

       # print(frequency, '\t', apparentResistivity, '\t', phase,Z.real);
    
    if plot_ == 1:
        ax.plot(frequencies[0:len(frequencies)//2]*1E3,surface_impedances[0:len(frequencies)//2]*1E3)
        #plt.plot(frequencies,surface_impedances*1E3)
        ax.set_ylim(0,((np.amax(abs(surface_impedances))*1E3)+((np.amax(abs(surface_impedances))/10)*1E3)))
        ax.set_xlim(0,8.4)
        ax.set_xlabel("Frequency [mHz]")
        ax.set_ylabel("Z($\omega$) [m$\Omega$]")
        ax.set_title("Impedances (Model #%s)"%(str(model_no)))
        ax.grid()
        #fig.savefig(rpath+'impedances_'+str(model_no)+'.png',dpi=300,bbox_inches='tight')
        #plt.show()
    return surface_impedances


def conductivity_3D(lat, lon, frequencies):
    # Uses 3-D conductivity model sourced from https://globalconductivity.ocean.ru/

    f= h5py.File(r'C:/Users/mccl_ao/Documents/DLR/Codes/GIC_Project/MODEL-VER-5.mat','r')

    # Investigate saved variables
    variables = f.keys() 


    model_data  = f['MODEL']
    lats = f['LATGRID']
    lons = f['LONGRID']
    lats_1d = lats[0,:]
    lons_1d = lons[:,0]

    # Finsing where input lat,lon matches best to model grid points
    diff_lat = np.abs(lats_1d-lat)
    diff_lon = np.abs(lons_1d-lon)
    idx_lat = np.where(diff_lat == diff_lat.min())
    idx_lon = np.where(diff_lon == diff_lon.min())


    depths = np.arange(0,len(model_data),1)
    resistivities = []
    thicknesses = [100 for i in range(len(depths)+1)]
    for l_depth in depths:
        # Extract layer conductivity for specific lon, lat point
        layer_con = model_data[l_depth,idx_lon[0][0],idx_lat[0][0]]
        resistivities.append(1./layer_con)
    
    # Using 3D conductivity model to compute E-field (https://globalconductivity.ocean.ru/)
    print('Resistivities: ', resistivities)
    mu = 4.*np.pi*1E-7
    n = len(resistivities)
    surface_impedances = np.zeros(len(frequencies))
    i = 0

    for frequency in frequencies:

        w =  2*np.pi*frequency;       
        impedances = list(range(n))
        # Impedance of the half-space bottomw layer
        impedances[n-1] = np.sqrt(1j*w*mu*resistivities[n-1]);
        for j in range(n-2,-1,-1):
            #print(j)
            resistivity = resistivities[j];        thickness = thicknesses[j];
            # Propagation Constant (induction parameter)
            gamma_n = np.sqrt((1j*w * mu * (1./resistivity)));
            # Intrinisic Impedance
            z0_n =  np.sqrt(1j*w*mu*(resistivity));
            # Exponential Factor
            e_n = np.exp(-2.*gamma_n*thickness);
            # Impedance of layer below
            belowImpedance = impedances[j + 1];
            #reflection coefficient
            r_n = (belowImpedance-z0_n)/(belowImpedance+z0_n);
            alpha_n = r_n*e_n; 
            # Impedance of j-layer
            Z_n = z0_n * ((1. + alpha_n)/(1. - alpha_n));
            impedances[j] = Z_n;

        #Impedance of top layer
        Z = impedances[0];
        absZ = abs(Z);
        surface_impedances[i]=(absZ)
        apparentResistivity = (absZ * absZ)/(w);
        phase = np.arctan2(Z.imag, Z.real);
        i += 1

        #print(frequency, '\t', apparentResistivity, '\t', phase,Z.real);
    plt.plot(frequencies[0:len(frequencies)//2]*1E3,surface_impedances[0:len(frequencies)//2]*1E3)
    #plt.plot(frequencies,surface_impedances*1E3)
    plt.ylim(0,7)
    plt.xlim(0,9)
    plt.xlabel("Frequency [mHz]")
    plt.ylabel("Z($\omega$) [m$\Omega$]")
    plt.title("Impedances (3D Model)")
    plt.grid()
    plt.show()
    
    return surface_impedances


def plot_vecE(self,Ex,Ey,dpath,rpath,t,Obs,step,save):
    """
    !! WORK IN PROGRESS - not yet functional!!
    Purpose: Plotting vector map of Efield over Germany
    Adapted from geomag/SECS.py
    Errors: Showing strange E-field vectors
    """
    a1=np.min(self.meta['Bintlat'].reshape(-1,1))-1; a2=np.max(self.meta['Bintlat'].reshape(-1,1))+1
    a3=np.min(self.meta['Bintlon'].reshape(-1,1))-1.5; a4=np.max(self.meta['Bintlon'].reshape(-1,1))+1.5

    fig = plt.figure(figsize=(8,8))
    #ax = plt.axes(projection=ccrs.LambertConformal(central_longitude=(a3+a4)/2,central_latitude=(a1+a2)/2,cutoff=20))
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=(a3+a4)/2,globe=None))

    # Total E-field
    E_vec = abs(Ex+1j*Ey)*1E3
    E_max = np.nanmax(E_vec)
    E_min = np.nanmin(E_vec)
    Ex = abs(Ex)*1E3
    Ey=abs(Ey)*1E3
    #cLimE = [-100, np.max(Jext)]

    cmap = plt.get_cmap('coolwarm')
    #jext = ax.pcolormesh(Jlon,Jlat,Jext.reshape(np.shape(Jlat)),cmap=cmap,vmin=cLimE[0],vmax=cLimE[1],
    #                   transform=ccrs.PlateCarree())

    ax.scatter(self.meta['Bintlon'],self.meta['Bintlat'],transform=ccrs.PlateCarree(),zorder=1,s=7,color='black')
    
    jscale = 100; width = .005; headwidth = 3; headlength = 4; escale = 100;       
    #ims = []
    #for step in range(len(t)):
    jvec = ax.quiver(self.meta['Bintlon'],self.meta['Bintlat'],Ex[step,:].reshape(np.shape(self.meta['Bintlon'])),Ey[step,:].reshape(np.shape(self.meta['Bintlat'])),E_vec[step,:].reshape(np.shape(self.meta['Bintlon'])),
                cmap=cmap,pivot='tail',scale=escale,width=width,headwidth=headwidth,headlength=headlength,
                transform=ccrs.PlateCarree(),clim=[E_min,E_max],zorder=2)
    #ims.append([jvec])
        
    fig.colorbar(jvec,label=r'E [mV/km]')
    ax.set_title(t[step].strftime('%m/%d/%Y, %H:%M:%S'))
    
    # Magnetometers
    ax.plot(Obs.meta['lon'],Obs.meta['lat'],transform=ccrs.PlateCarree(),marker='o',linewidth=0,label='IMAGE magnetometers',color='lime',zorder=3)
    for o in range(len(Obs.meta['obs'])):
        ax.text(Obs.meta['lon'][o],Obs.meta['lat'][o],Obs.meta['obs'][o],fontsize=10,transform=ccrs.PlateCarree(),verticalalignment='top',horizontalalignment='left',zorder=5)

    # Coastlines & German border
    shape = dpath+'gadm36_DEU_shp/gadm36_DEU_1.shp'
    adm1_shapes = list(shpreader.Reader(shape).geometries())
    ax.add_geometries(adm1_shapes, ccrs.PlateCarree(), edgecolor='dimgray', facecolor='silver', zorder=0, alpha=0.2)
    ax.coastlines(resolution='10m', color='dimgray', zorder=4)
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0, color='white', alpha=1, linestyle='--',zorder=4)
    gl.top_labels = False
    gl.right_labels = False
    #ax.gridlines()
    #ax.legend()
    
    #ani = animation.ArtistAnimation(fig, ims, interval=50)#, blit=True,repeat_delay=1000)
    #plt.show()
    
    if save == 1:
        fig.savefig(rpath+'efield_1d'+str(step)+'.jpg',dpi=300,transparent=True,bbox_inches='tight')

    ####


def tukey(size, taper):
# Function to define a Tukey window
        taper = TukeyWindow(alpha=taper)
        data = taper((size, size))
        #plt.plot(data[size//2,:])
        return(data[size//2,:])


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')

def eurisgic(lat_p,lon_p):
    
    # Purpose: 16 conductivity models to represent Germany + surrounding area (source: EURHOM model; Adam et. al 2012)
    # Input: lat_p (geographic latitude; float)
    #        lon_p (geographic longitude; float)
    # Restrictions: min lat: 47
    #               max lat: 55
    #               min lon: 2
    #               max lon: 16
    # Returns: No. of closest conductivity model for given lat,lon point


    #Model 0
    lat_0= np.arange(52, 55,0.5)
    lon_0 = np.arange(2,5,0.5)
    resistivity_0 = [1, 5000, 1, 10] # check ocean conductivity values (CHANGE)
    thickness_0 = [2000, 6000, 4000] # CHANGE

    #Model 47 [1]

    lat_47= np.arange(50, 55,0.5)
    lon_47 = np.arange(5,8,0.5)
    resistivity_47 = [1, 5000, 1, 10] 
    thickness_47 = [2000, 6000, 4000]

    #Model 47a [471]

    lat_47a= np.arange(50, 52,0.5)
    lon_47a = np.arange(2,5,0.5)
    resistivity_47a = [1, 5000, 1, 10] 
    thickness_47a = [2000, 6000, 4000]

    #Model 12

    lat_12= np.arange(52, 55,0.5)
    lon_12 = np.arange(8,12,0.5)
    resistivity_12 = [1, 200, 0.5, 200, 1000, 10] 
    thickness_12 = [4000, 4000, 1500, 2000, 100000]

    #Model 13

    lat_13= np.arange(50, 52,0.5)
    lon_13 = np.arange(8,12,0.5)
    resistivity_13 = [1,200,0.5,200,1000,10] 
    thickness_13 = [4000, 4000,1500,2000,100000]

    #Model 15

    lat_15= np.arange(48, 50,0.5)
    lon_15 = np.arange(8,12,0.5)
    resistivity_15 = [1,200,0.5,200,1000,10] 
    thickness_15 = [4000,4000,1500,2000,100000]
    
    #Model 11

    lat_11= np.arange(52, 55,0.5)
    lon_11 = np.arange(12,16,0.5)
    resistivity_11 = [200, 0.5, 1000, 10] 
    thickness_11 = [5000,1000,100000]

        
    #Model 14

    lat_14= np.arange(50, 52,0.5)
    lon_14 = np.arange(12,16,0.5)
    resistivity_14 = [1,200,0.5,1000,10] 
    thickness_14 = [2000,10000,1000,100000]
    
    #Model 16

    lat_16= np.arange(48, 50,0.5)
    lon_16 = np.arange(12,16,0.5)
    resistivity_16 = [1500,500,800,10] 
    thickness_16 = [20000,20000,110000]

    #Model 35

    lat_35= np.arange(48, 50,0.5)
    lon_35 = np.arange(5,8,0.5)
    resistivity_35 = [40,30,1000,20] 
    thickness_35 = [2000,3000,150000]

    #Model 37

    lat_37= np.arange(45, 48,0.5)
    lon_37 = np.arange(2,5,0.5)
    resistivity_37 = [10,1500,70000,10000] 
    thickness_37 = [80,800,6000,8000,55000]

    #Model 38

    lat_38= np.arange(48, 50,0.5)
    lon_38 = np.arange(2,5,0.5)
    resistivity_38 = [10,10000] 
    thickness_38 = [5,7000,95000]


    #Model 39
    
    lat_39= np.arange(46, 48,0.5)
    lon_39 = np.arange(12,16,0.5)
    resistivity_39 = [10,1500,70000,10000] 
    thickness_39 = [80,800,6000,8000,55000]


    #Model 54
    lat_54= np.arange(44,47,0.5)
    lon_54 = np.arange(8,16,0.5)
    resistivity_54 = [100,1000] 
    thickness_54 = [4,10000,90000]


    # Model 55
    
    lat_55= np.arange(44, 48,0.5)
    lon_55 = np.arange(5,8,0.5)
    resistivity_55 = [110,30,10000,90] 
    thickness_55 = [900,110,150000]

    # model 55a [551]

    lat_55a= np.arange(46, 48,0.5)
    lon_55a = np.arange(8,12,0.5)
    resistivity_55a = [110,30,10000,90] 
    thickness_55a = [900,110,150000]


    model_list = ['Model 0', 'Model 47','Model 47a','Model 12', 'Model 13','Model 15', 'Model 11', 'Model 14', 'Model 16', 'Model 35','Model 37','Model 38','Model 39', 'Model 54', 'Model 55', 'Model 55a']
    init_data = {'Model':model_list, 'Model_No':[0,47,471,12,13,15,11,14,16,35,37,38,39,54,55,551],'Min_Lat':[52,50,50,52,50,48,52,50,48,48,45,48,46,44,44,46],'Max_Lat':[55,55,52,55,52,50,55,52,50,50,48,50,48,47,48,48 ],  'Min_Lon':[2,5,2,8,8,8,12,12,12,5,2,2,12,8,5,8],'Max_Lon':[5,8,5,12,12,12,16,16,16,8,5,5,16,16,8,12]}
    df = pd.DataFrame(init_data)

    # Find closest model that matches lat/lon grid point
    model = df[((df.Min_Lat <= lat_p) & (df.Max_Lat >= lat_p)) & ((df.Min_Lon <= lon_p)&(df.Max_Lon >= lon_p))]
    print(model)
    model_no= model.Model_No.iloc[0]

    return model_no