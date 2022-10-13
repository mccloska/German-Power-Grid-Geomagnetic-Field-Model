import sys
sys.path.append(sys.argv[1]+'./callable/')
dpath = sys.argv[2]
rpath = sys.argv[3]
import Obs
import numpy as np
import pandas as pd
import datetime as dt
import pickle

meta = {}
meta['res'] = 'minute'
meta['kind'] = 'definitive'
meta['format'] = 'IAGA2002'
meta['year'] = ['2014'] 												#['2015'#['2005']#np.array(['2003','2005','2009'])
meta['month'] = ['02'] 													#['03'] #['07']#['11']  #np.array([str(s).zfill(2) for s in np.arange(1,13,dtype='int')])
meta['obs'] = np.array(['bdv','bfe','bfo','clf','fur','mab','ngk','wic','wng']) #'hlp','bel','dou' #np.array(['abk','lyc','nur','sod','ups'])	#np.array(['bfo','fur','ngk','wng']) #np.array(['wic'])    
meta['source'] = 'ftp.seismo.nrcan.gc.ca'

# Initialize class object
x = Obs.DatLib(meta)

# Get observatory measurements from INTERMAGNET ftp server
x.get_data_fromftp(dpath+'INTERMAGNET/')
#t = pd.date_range(dt.datetime(year=2015,month=11,day=8,hour=23,minute=34,second=0),dt.datetime(year=2015,month=11,day=8,hour=23,minute=59,second=0),freq='min')
#t = pd.date_range(dt.datetime(year=2005,month=7,day=11,hour=0,minute=0,second=0),dt.datetime(year=2005,month=7,day=13,hour=23,minute=59,second=0),freq='min')
t = pd.date_range(dt.datetime(year=2014,month=2,day=1,hour=0,minute=0,second=0),dt.datetime(year=2014,month=2,day=28,hour=23,minute=59,second=59),freq='min')
#t = pd.date_range(dt.datetime(year=2015,month=3,day=22,hour=0,minute=0,second=0),dt.datetime(year=2015,month=3,day=23,hour=23,minute=59,second=0),freq='min')
x.combine_data(dpath+'INTERMAGNET/',t)

# Get observatory positions from IAGA Division 5
x.get_pos_fromIAGA(dpath+'IAGA_obs.csv')

# Get external field perturbations
x.get_perturbation(dpath,rpath,t)
		
# Save object (is needed to run Get_SECS in next step)
with open(dpath+'Obs_2014_02_19.obj', 'wb') as f:
	pickle.dump(x, f, pickle.HIGHEST_PROTOCOL)
