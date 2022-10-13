import numpy as np
import ftplib
import datetime as dt
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

class DatLib:

    def __init__(self,meta):

        self.meta = meta

    ####
    
    def get_data_fromftp(self,dpath):

        index = zip(np.repeat(self.meta['year'],len(self.meta['month'])),np.tile(self.meta['month'],len(self.meta['year'])))

        ftp = ftplib.FTP(self.meta['source']); ftp.login()
        
        for y,m in index:

            path = '/intermagnet/'+self.meta['res']+'/'+self.meta['kind']+'/'+self.meta['format']+'/'+y+'/'+m+'/'
            lst = ftp.nlst(path)

            if int(m)<12:
                df_index = pd.date_range(start=m+'/1/'+y,end=str(int(m)+1)+'/1/'+y,freq='min',closed='left')
            else:
                df_index = pd.date_range(start=m+'/1/'+y,end='01/1/'+str(int(y)+1),freq='min',closed='left')

            for o in self.meta['obs']:

                print(y,m,o)

                dir = dpath+o+'/monthly'
                if not os.path.exists(dir):
                    os.makedirs(dir)

                pickle = dir+'/'+o+y+m+'.pkl'

                if not os.path.exists(pickle):
                    
                    files = [s for s in lst if o in s]
                    data = dict(); count=1

                    for f in files:

                        fshort = dir+'/'+f[-22:]
                        if not os.path.exists(fshort):
                            ftp.retrbinary('RETR '+f, open(fshort, 'wb').write)

                        df = pd.read_csv(fshort, delim_whitespace=True, compression='gzip', skiprows=26, header=None,
                                        names=['Date','Time','DOY','X','Y','Z','F'],parse_dates=[[0,1]],index_col=0)

                        os.remove(fshort)

                        if not df.empty:
                            data[str(count)]=df

                        count += 1

                    if bool(data):
                        data = pd.concat(data).droplevel(0).reindex(df_index).replace([99999.,88888.],np.nan)
                        data.to_pickle(pickle)
                    else:
                        print('No data available')
                      
        ftp.close()

    ####

    def combine_data(self,dpath,t):

        m = self.meta['month'][0]
        y = self.meta['year'][0]

        if int(m)<12:
            df_index = pd.date_range(start=m+'/1/'+y,end=str(int(m)+1)+'/1/'+y,freq='min',closed='left')
        else:
            df_index = pd.date_range(start=m+'/1/'+y,end='01/1/'+str(int(y)+1),freq='min',closed='left')

        data = {}
        counter = 0
        for o in self.meta['obs']:
        
            pickle = dpath+o+'/monthly/'+o+self.meta['year'][0]+self.meta['month'][0]+'.pkl'

            if os.path.exists(pickle):
                data[o] = pd.read_pickle(pickle).loc[:,['X','Y','Z']]
            else:
                #data[o] = pd.DataFrame(data = np.zeros((len(df_index),3))+np.nan, index = df_index, columns=['X','Y','Z'])
                self.meta['obs'] = np.delete(self.meta['obs'],counter)
                counter -= 1
            
            counter += 1
                
        data = pd.concat(data)
        self.data = data.iloc[np.in1d(data.index.get_level_values(1),t)]
        
    ####
    
    def get_pos_fromIAGA(self,pathIAGA):

        IAGAmeta = pd.read_csv(pathIAGA, sep=',',skiprows=1,usecols=[1,2,4,5,6],header=None,names=['code','gen','lat','lon','alt'])
        IAGAmeta_sel = IAGAmeta.loc[np.in1d(IAGAmeta['code'],[s.upper() for s in self.meta['obs']]),:]
        IAGAmeta_sel = IAGAmeta_sel.sort_values(by=['code','gen'],ascending=[True,False]).drop_duplicates(subset=['code'])
        self.meta['lon'] = IAGAmeta_sel['lon'].to_numpy()
        self.meta['lat'] = IAGAmeta_sel['lat'].to_numpy()
        self.meta['alt'] = np.array([float(h) for h in IAGAmeta_sel['alt']])
        if np.any(np.isnan(self.meta['alt'])):
            self.meta['alt'][np.isnan(self.meta['alt'])] = 0.

    ####

    def get_perturbation(self,dpath,rpath,t):

        import gd2gc
        import chaosmagpy
        from chaosmagpy import load_CHAOS_matfile
        from chaosmagpy.data_utils import mjd2000
        from chaosmagpy.model_utils import synth_values

        model = load_CHAOS_matfile(dpath+'CHAOS-7.2.mat')

        # time
        # len_time = int(len(self.data)/len(self.meta['obs']))
        len_time = len(t)
        #df_index = self.data.index.get_level_values(1)[:len_time]
        df_index = t
        
        time = np.linspace(mjd2000(t[0].year,t[0].month,t[0].day,t[0].hour,t[0].minute,t[0].second), mjd2000(t[-1].year,t[-1].month,t[-1].day,t[-1].hour,t[-1].minute,t[-1].second), num=len(df_index), endpoint=True)
        #time = np.linspace(mjd2000(int(self.meta['year'][0]),int(self.meta['month'][0]),1), mjd2000(int(self.meta['year'][0]),int(self.meta['month'][0])+1,1), num=len(df_index), endpoint=False)
        time = time.repeat(len(self.meta['obs']))
       
        # data
        B = self.data.to_numpy()
        lat = (90.-self.meta['lat']).repeat(len_time)
        lon = self.meta['lon'].repeat(len_time)
        alt = (self.meta['alt']/1000).repeat(len_time)

        # geodetic to geocentric
        X_gc, Z_gc, r, m, colat_gc = gd2gc.gdtogc_v(np.radians(lat),B[:,0],B[:,2],alt)
        B_SPH = pd.DataFrame(data=np.vstack([-Z_gc,-X_gc,B[:,1]]).T,index=self.data.index,columns=['B_r','B_theta','B_phi'])
        
        # Core and crustal fields (internal) from CHAOS-7 model
        Bi_r, Bi_theta, Bi_phi = model(time,r,np.degrees(colat_gc),lon,source_list='internal')
        #Bi_r, Bi_theta, Bi_phi = model(time,r,np.degrees(colat_gc),lon,source_list=['tdep','static','gsm','sm'])
        B_SPH_int = pd.DataFrame(data=np.vstack([Bi_r,Bi_theta,Bi_phi]).T,index=self.data.index,columns=['B_r','B_theta','B_phi'])
        
        # ####
        # fig,ax = plt.subplots(3,1,sharex=True,figsize=(8,5))
        # ax = ax.ravel()
        # #colors = ['blue','red','orange','green']
        # cmap = mpl.cm.get_cmap('jet')
        # colors = cmap(np.linspace(0,1,len(self.meta['obs'])))
        # c=0
        # for o in self.meta['obs']:
            # ax[0].plot(t,B_SPH_int.loc[o,:]['B_r'],colors[c])#,label=o)
            # ax[1].plot(t,B_SPH_int.loc[o,:]['B_theta'],colors[c])#,label=o)
            # ax[2].plot(t,B_SPH_int.loc[o,:]['B_phi'],colors[c])#,label=o)
           
            # c+= 1
        # #ax[0].legend(loc=1)
        # ax[0].set_xlim(t[0],t[-1])
        # ax[2].set_xlabel('Time (March 2015)')
        # ax[0].set_ylabel(r'B$_r$ [nT]')
        # ax[1].set_ylabel(r'B$_{\theta}$ [nT]')
        # ax[2].set_ylabel(r'B$_{\phi}$ [nT]')
        # ax[0].grid(); ax[1].grid(); ax[2].grid()
        # ax[0].set_title('Internal field components from CHAOS-7.2')
        # plt.show()
        # fig.savefig(rpath+'201503_Binternal_all.jpg',dpi=300,transparent=True,bbox_inches='tight')
        # ####
        
        # Field residuals (external)
        B_SPH_res = B_SPH.subtract(B_SPH_int)
        # geocentric to geodetic
        X_res,Z_res = gd2gc.gctogd_v(-B_SPH_res['B_theta'],-B_SPH_res['B_r'],m)
        B_res = pd.DataFrame(data=np.vstack([X_res,B_SPH_res['B_phi'],Z_res]).T,index=self.data.index,columns=['X_res','Y_res','Z_res'])

        self.data_res = B_res

        #B_res.loc['ngk',:].plot(y='X_res')
        #plt.show()

    ####
