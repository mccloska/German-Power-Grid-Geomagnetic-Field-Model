import sys
sys.path.append(sys.argv[1]+'./callable/')
dpath = sys.argv[2]
rpath = sys.argv[3]
import SECS
import numpy as np
import pandas as pd
import datetime as dt
import pickle
import matplotlib.pyplot as plt
#from scipy.interpolate import splev, splrep

#with open(dpath+'Obs.obj', 'rb') as f: x = pickle.load(f)           		# Obs object (x)   
#with open(dpath+'Obs_2017_09_07.obj', 'rb') as f: x = pickle.load(f)    	# Obs object (x)  
with open(dpath+'Obs_2014_02_19.obj', 'rb') as f: x = pickle.load(f)   
#with open(dpath+'Obs_noFUR.obj', 'rb') as f: x = pickle.load(f)            
#with open(dpath+'Obs_noWNG.obj', 'rb') as f: x = pickle.load(f)           
#with open(dpath+'Obs_noBFO.obj', 'rb') as f: x = pickle.load(f)  

t = x.data.loc[x.meta['obs'][0],:].index

# SECs setup
meta = {}
 
meta['dlat_Sgrid'] = .5
meta['dlon_Sgrid'] = .5
meta['dlat_Igrid'] = .5 #0.6
meta['dlon_Igrid'] = .5 #1.4
meta['RE'] = 6371.2
meta['Rext'] = meta['RE']+110
meta['epsSVD'] = 0.05
meta['separation'] = False
meta['Nt'] = len(t)
meta['Nstat'] = len(x.meta['obs'])

# Initialize class object
y = SECS.SECSLib(meta)                                                  # SECS object (y)               

# Grids
y.get_SECSgrids(dpath,x)
#y.get_Igrid(dpath)
y.get_Igrid_old(dpath)

# Transfer matrix
thetaB = np.radians(90.-x.meta['lat'].reshape(1,-1))
phiB = np.radians(x.meta['lon'].reshape(1,-1))
thetaSECS = np.radians(90.-y.meta['SECSlat'].reshape(-1,1,order='F'))
phiSECS = np.radians(y.meta['SECSlon'].reshape(-1,1,order='F'))
#---#
#thetaB2 = np.radians(90.-xAll.meta['lat'].reshape(1,-1))
#phiB2 = np.radians(xAll.meta['lon'].reshape(1,-1))
#---#
Tr,Ttheta,Tphi = y.sub_SECS_2D_DivFree_magnetic(thetaB,phiB,thetaSECS,phiSECS,y.meta['RE'],y.meta['Rext'])
#Tr2,Ttheta2,Tphi2 = y.sub_SECS_2D_DivFree_magnetic(thetaB2,phiB2,thetaSECS,phiSECS,y.meta['RE'],y.meta['Rext'])
#---#
T = np.zeros((2*y.meta['Nstat'],y.meta['Npole']))*np.nan
T[np.arange(0,2*y.meta['Nstat'],2),:] = Ttheta
T[np.arange(1,2*y.meta['Nstat'],2),:] = Tphi

# Pseudo-iunverse of transfer matrix 
T_inv = y.sub_inv_SVD(T)

# Scaling factors
Idf = y.get_SECSfactors(T_inv,x)

# Calculate Jeq at the output grid
# MJtheta, MJphi = y.sub_SECS_2D_DivFree_vector()
#---#
Iext = Idf[:y.meta['Npole'],:]
# JXext = -np.matmul(MJtheta,Iext).T        
# JYext = np.matmul(MJphi,Iext).T 

# Calculate B at the output grid
thetaB_int = np.radians(90.-y.meta['Bintlat']).reshape(-1,1).T
phiB_int = np.radians(y.meta['Bintlon']).reshape(-1,1).T
#---#
Tr_int,Ttheta_int,Tphi_int = y.sub_SECS_2D_DivFree_magnetic(thetaB_int,phiB_int,thetaSECS,phiSECS,y.meta['RE'],y.meta['Rext'])
#---#
y.BX_int = -np.matmul(Ttheta_int,Iext).T      
y.BY_int = np.matmul(Tphi_int,Iext).T

## Use raw data from just one obervatory for the whole grid
#y.BX_int = np.tile(x.data['X'].values, (y.meta['Neq'],1)).T
#y.BY_int = np.tile(x.data['Y'].values, (y.meta['Neq'],1)).T

# Calculate B at the observatory locations (for validation)
#BX_val = -np.matmul(Ttheta,Iext).T      
#BY_val = np.matmul(Tphi,Iext).T 
#y.get_Bval(BX_val,BY_val,dpath,rpath+'Validation/',t,x,mode=0,save=0)

# Get dB/dt at the output grid
dBX_int = np.gradient(y.BX_int,axis=0)
dBY_int = np.gradient(y.BY_int,axis=0)
# Calculate H  
H = np.sqrt(y.BX_int**2+y.BY_int**2)
#dH/dt
dH_int= np.gradient(H,axis=0)
#spl = splrep(np.arange(0,len(t),1), BX_int[:,0],s=0)
#x_new = np.arange(0,len(t),1)
#dBX_int2 = splev(x_new, spl, der=1)

# Mapping
start = 25920 #60*13
end = 27361 #len(y.BX_int) #60*12#60*19
snap = 370 #1143 #1265 #121
##for step in range(len(t)):
##for step in np.arange(0,len(t),60): # every hour
##for step in [0]: # first minute of time interval
##y.get_Jplot(JXext,JYext,dpath,rpath+'SECS_Maps/',t,step,x,save=0)
##y.get_Bplot(BX_int,BY_int,dpath,rpath+'SECS_Maps/',t,step,x,save=1)
#y.get_Bplot(dBX_int,dBY_int,dpath,rpath+'SECS_Maps/',t[start:end+1],start,end+1,snap,x,save=0)
y.get_Bplot(y.BX_int,y.BY_int,dpath,rpath+'SECS_Maps/',t[start:end+1],start,end+1,snap,x,save=0)


y.get_Hplot(x,dpath,rpath,t[start:end],start,end,save=0)

#%%
# Save object
#with open(dpath+'SECS_2017_09_07.obj', 'wb') as f:
#	pickle.dump(y, f, pickle.HIGHEST_PROTOCOL)
