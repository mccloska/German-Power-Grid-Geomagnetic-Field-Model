import numpy as np
#import ftplib
import datetime as dt
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
#import sklearn.metrics as metrics
from shapely.geometry import Polygon, MultiLineString
#from collections import Counter

class SECSLib:

    def __init__(self,meta):

        self.meta = meta

    ####
    
    def get_SECSgrids(self, dpath, Obs):
         
        # Parameters
        dlat = self.meta['dlat_Sgrid']; dlon = self.meta['dlon_Sgrid']
        minlat = np.nanmin(Obs.meta['lat']); maxlat = np.nanmax(Obs.meta['lat'])
        minlon = np.nanmin(Obs.meta['lon']); maxlon = np.nanmax(Obs.meta['lon'])
        a1=np.floor(minlat/dlat)*dlat;  a2=np.ceil(maxlat/dlat)*dlat
        b1=np.floor(minlon/dlon)*dlon;  b2=np.ceil(maxlon/dlon)*dlon
                
        #self.meta['SECSlat'], self.meta['SECSlon'] = np.meshgrid(np.arange(a1-4.5*dlat,a2+4.5*dlat,dlat), np.arange(b1-4.5*dlon,b2+4.5*dlon+dlon,dlon)) #SECS poles
        self.meta['SECSlat'], self.meta['SECSlon'] = np.meshgrid(np.arange(a1-dlat,a2+3*dlat,dlat), np.arange(b1,b2+dlon,dlon)) #SECS poles
        self.meta['Npole'] = len(self.meta['SECSlat'].reshape(-1,1)) # Number of SECS poles

        #self.meta['Jlat'], self.meta['Jlon'] = np.meshgrid(np.arange(a1,a2,dlat),np.arange(b1,b2,dlon)) #equivalent currents
        #self.meta['Bintlat'] = self.meta['Jlat']; self.meta['Bintlon'] = self.meta['Jlon']  #magnetic field
        #self.meta['Neq'] = len(self.meta['Jlat'].reshape(-1,1))      # Number of Jeq points
        
    ####
    
    def get_Igrid_old(self, dpath):
        
        # Parameters
        dlat = self.meta['dlat_Igrid']; dlon = self.meta['dlon_Igrid']
        minlat = 44; maxlat = 58
        minlon = 5; maxlon = 16
        
        # Grid lines (latitude)
        coords = np.arange(minlat,maxlat,dlat)
        grid = [((minlon,i),(maxlon,i)) for i in coords]
        lines = MultiLineString(grid)
        
        # Polygon
        shape = dpath+'gadm36_DEU_shp/gadm36_DEU_0.shp'
        poly = list(shpreader.Reader(shape).geometries())[0]          
        #x, y = poly[89].exterior.coords.xy
        
        # Intersection of lines with polyon
        inter = lines.intersection(poly[89])
        inter_lon = []; inter_lat = []
        
        for i in inter:
            x,y = i.coords.xy
            inter_lon.append(x.tolist())
            inter_lat.append(y.tolist())
        inter_lat = np.array([item for sublist in inter_lat for item in sublist])
        inter_lon = np.array([item for sublist in inter_lon for item in sublist])
                
        # Create grid from intersection points
        grid_lon = []; grid_lat = []
        for l in inter_lat:
            idx = np.where(inter_lat==l)[0]
            lons = np.arange(inter_lon[idx[0]],inter_lon[idx[-1]]+dlon/2,dlon)
            grid_lon.append(lons.tolist())
            grid_lat.append(inter_lat[idx[0]].repeat(len(lons)).tolist())
        grid_lat = np.array([item for sublist in grid_lat for item in sublist])
        grid_lon = np.array([item for sublist in grid_lon for item in sublist])
        
        ####
        # # Plotting (for verification)
        # fig = plt.figure(figsize=(8,8))
        # ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=10,globe=None))
        # ax.add_geometries([poly[89]], ccrs.PlateCarree(), edgecolor='dimgray', zorder=0, alpha=0.2)
        # ax.coastlines(resolution='10m', color='dimgray', zorder=1)
        # ax.add_geometries(lines, ccrs.PlateCarree(), edgecolor='dimgray', zorder=2, alpha=0.2)
        # ax.scatter(grid_lon, grid_lat, transform=ccrs.PlateCarree(),color='black', zorder=3)
        # plt.show()
        ####
        
        self.meta['Bintlat'] = grid_lat; self.meta['Bintlon'] = grid_lon
        self.meta['Jlat'] = self.meta['Bintlat']; self.meta['Jlon'] = self.meta['Bintlon']
        self.meta['Neq'] = len(self.meta['Jlat'].reshape(-1,1))         # Number of Jeq points
    
    ####
    
    def get_Igrid(self, dpath):
        
        # Parameters
        dlat = self.meta['dlat_Igrid']; dlon = self.meta['dlon_Igrid']
        
        minlat = 46; maxlat = 50 #AUT: polygon 56
        minlon = 9; maxlon = 18
        polyNumber = 56
        # minlat = 44; maxlat = 58  #DEU: polygon 71
        # minlon = 5; maxlon = 16
        # polyNumber = 71
        
        # Grid lines (latitude)
        coords = np.arange(minlat,maxlat,dlat)
        grid = [((minlon,i),(maxlon,i)) for i in coords]
        lines = MultiLineString(grid)
        
        # Polygon
        shape = dpath+'TM_WORLD_BORDERS-0.3/TM_WORLD_BORDERS-0.3.shp'
        poly = list(shpreader.Reader(shape).geometries())[polyNumber]
        #x, y = poly.exterior.coords.xy
        
        # Find potential country polygons:
        # count = 0
        # for p in poly:
            # inter = lines.intersection(p)
            # inter_lon = []; inter_lat = []
            # if inter:
                # print(count)
            # count += 1
       
        # Intersection of lines with polyon
        inter = lines.intersection(poly)
        inter_lon = []; inter_lat = []
        
        for i in inter:
            x,y = i.coords.xy
            inter_lon.append(x.tolist())
            inter_lat.append(y.tolist())
        inter_lat = np.array([item for sublist in inter_lat for item in sublist])
        inter_lon = np.array([item for sublist in inter_lon for item in sublist])
                
        # Create grid from intersection points
        grid_lon = []; grid_lat = []
        for l in inter_lat:
            idx = np.where(inter_lat==l)[0]
            lons = np.arange(inter_lon[idx[0]],inter_lon[idx[-1]]+dlon/2,dlon)
            grid_lon.append(lons.tolist())
            grid_lat.append(inter_lat[idx[0]].repeat(len(lons)).tolist())
        grid_lat = np.array([item for sublist in grid_lat for item in sublist])
        grid_lon = np.array([item for sublist in grid_lon for item in sublist])
        
        ####
        # # Plotting (for verification)
        # fig = plt.figure(figsize=(8,8))
        # ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=10,globe=None))
        # ax.add_geometries([poly], ccrs.PlateCarree(), edgecolor='dimgray', zorder=0, alpha=0.2)
        # ax.coastlines(resolution='10m', color='dimgray', zorder=1)
        # ax.add_geometries(lines, ccrs.PlateCarree(), edgecolor='dimgray', zorder=2, alpha=0.2)
        # ax.scatter(grid_lon, grid_lat, transform=ccrs.PlateCarree(),color='black', zorder=3)
        # plt.show()
        ####
        
        self.meta['Bintlat'] = grid_lat; self.meta['Bintlon'] = grid_lon
        self.meta['Jlat'] = self.meta['Bintlat']; self.meta['Jlon'] = self.meta['Bintlon']
        self.meta['Neq'] = len(self.meta['Jlat'].reshape(-1,1))         # Number of Jeq points
        
    #####
    
    def sub_SECS_2D_DivFree_magnetic(self,thetaB,phiB,thetaSECS,phiSECS,Rb,Rsecs):

        # Calculation of transfer matrix T that relates the (ground) magnetic field to the SECS representation so that:
        # B_i = T_ij * Idf
        # i   = {r,theta,phi}              vector components
        # B   = [B_i(1),B_i(2),...]        measuremens
        # Idf = [Idf(1'), Idf(2'),...]     scaling factors
        #
        #Assume units: [B]=nT, [Idf]=A and [length]=km
        #
        # Input:
        # thetaB,phiB: Co-latitude and longitude of the magnetometer stations, [radian], Nb-dimensional vectors
        # thetaSECS,phiSECS: Co-latitude and longitude of the DF SECS, [radian], Nsecs-dimensional vectors
        # Rb,Rsecs: Radii of the spheres where magnetometers and DF SECS are located, [km], scalars
        #
        # Output:
        # ma    tBradial,matBtheta,matBphi: (Nb,Nsecs)-matrices that relate SECS scaling factors to the magnetic field
        #
        # Heikki V, March 2010, matlab 7.8.0.347 (R2009a)

        # Number of points where B is calculated and scaling factors are given
        Nb = len(thetaB[0,:])                # should be column vector alrealy
        Nsecs = len(thetaSECS.reshape(-1,1)) # should be column vector already
        matBradial = np.zeros((Nb,Nsecs))*np.nan
        matBtheta = np.zeros((Nb,Nsecs))*np.nan
        matBphi = np.zeros((Nb,Nsecs))*np.nan

        if np.size(Rsecs)!=1:
            print('\n  Sorry, input parameter Rsecs must be scalar \n\n')
            return

        # If Rb is scalar, use same radius for all points.
        Rb += 0*thetaB;

        # Ratio of the radii, smaller/larger
        suhde = np.zeros(np.shape(thetaB))+np.min(np.append(Rb,Rsecs))/np.max(np.append(Rb,Rsecs))

        # There is a common factor mu0/(4*pi)=1e-7. Also 1/Rb is a common factor
        # If scaling factors are in [A], radii in [km] and magnetic field in [nT]  --> extra factor of 1e6
        kerroin = 0.1 / Rb

        # Loop over B positions
        for n in range(Nb):

            #cos and square of sin of co-latitude in the SECS-centered system
            #See Eq.(A5) and Fig. 14 of Vanhamaki et al.(2003)
            CosThetaPrime = np.cos(thetaB[0,n]) * np.cos(thetaSECS) + np.sin(thetaB[0,n]) * np.sin(thetaSECS) * np.cos(phiSECS-phiB[0,n])
            Sin2ThetaPrime = (1-CosThetaPrime**2)

            #sin and cos of angle C, divided by sin(theta')
            #See Eqs. (A2)-(A5) and Fig. 14 of Vanhamaki et al.(2003)
            ind = np.where(Sin2ThetaPrime > 1e-10)[0]
            SinC = np.zeros(np.shape(CosThetaPrime))
            CosC = np.zeros(np.shape(CosThetaPrime))
            SinC[ind] = np.sin(thetaSECS[ind]) * np.sin(phiSECS[ind]-phiB[0,n])/Sin2ThetaPrime[ind]
            CosC[ind] = (np.cos(thetaSECS[ind]) - np.cos(thetaB[0,n])*CosThetaPrime[ind]) / (np.sin(thetaB[0,n])*Sin2ThetaPrime[ind])

            #auxiliary variable
            juuri=np.sqrt(1 - 2*suhde[0,n] * CosThetaPrime + suhde[0,n]**2)

            if Rb[0,n] < Rsecs:
                apuVertical = 1
                #See Eq. (10) of Amm and Viljanen (1999)
                apuHorizontal = -kerroin[0,n] * ((suhde[0,n]-CosThetaPrime)/juuri + CosThetaPrime)
            elif Rb[0,n] > Rsecs:
                apuVertical = suhde[0,n]
                #See Eq. (A8) of Amm and Viljanen (1999)
                apuHorizontal = -kerroin[0,n] * ((1-suhde[0,n]*CosThetaPrime) / juuri - 1)
            else:
                #Rb[0,n] == Rsecs
                apuVertical = 1
                #Actually horizontal field is not well defined, but this is the average.
                #See Eqs. (10) and (A8) of Amm and Viljanen (1999)
                apuHorizontal = -kerroin[0,n] * (juuri + CosThetaPrime - 1)/2

            #See Eqs. (9) and (A7) of Amm and Viljanen (1999)
            matBradial[n,:] = apuVertical * kerroin[0,n] * (1./juuri.reshape(-1,1).squeeze() - 1)
            matBtheta[n,:] = (apuHorizontal.reshape(-1,1) * CosC.reshape(-1,1)).squeeze()
            matBphi[n,:] = (-apuHorizontal.reshape(-1,1) * SinC.reshape(-1,1)).squeeze()

        return matBradial, matBtheta, matBphi

    ####
    
   # def sub_where(c,a,b):
   # 
   #     # Returns a where c is nonzero and b where c is zero.
   #     # Usually the arguments are arrays, and if they are, they must be of similar dimensions.
   # 
   #     a += 0*c
   #     b += 0*c #not neccesary
   # 
   #     y = a
   #     ind = np.where(c == 0)[0]
   #     y[ind] = b[ind]
   # 
   #     return y 

    ####

    def sub_inv_SVD(self, matB):

        # Calculate the inverse of a given matrix M usingcsingular value decomposition (SVD)
        # M: Original matrix
        # epsSVD: Regularization parameter, scalar, 0 <= epsSVD <= 1
        # invM: Inverse matrix

        # Functions called:
        # - sub_where

        M = matB
        epsSVD = self.meta['epsSVD']

        l1 = len(M[:,0])
        l2 = len(M[0,:])

        #print('Calculating SVD of a [%d,%d] matrix ...',l1,l2)
        U,S,V = np.linalg.svd(M,full_matrices=False)
        #print('Done')

        lkms = np.min([l1,l2])
        # Vector s is ordered so that s(n)>=s(n+1) and all s(n)>=0
        # s = np.diag(S[:lkms,:lkms])
        s = S.reshape(-1,1)
        U = -U[:,:lkms]
        V = -V.T[:,:lkms]

        # Calculate the inverse matrix
        slim = epsSVD*s[0,0]
        lkm1 = np.sum(s<=slim)
        #print('epsilon=',epsSVD, ', singular values range from ', s[0], 'to ', s[lkms-1])
        #print('-->',lkm1,' values smaller than ', slim, 'deleted (of ', lkms, ' values)')

        ###
        c = s[:,0]<=slim
        a = 0
        b = 1./s[:,0]

        a += 0*c
        b += 0*c #not neccesary

        y = a
        ind = np.where(c == 0)[0]
        y[ind] = b[ind]

        ###
            
        #InvM = np.matmul(V,np.matmul(np.diag(sub_where(s[:,0]<=slim,0,1./s[:,0])),U.T))
        InvM = np.matmul(V,np.matmul(np.diag(y),U.T))
        #InvM_test = np.linalg.pinv(M,slim)

        return InvM
    
    ####
    
    def get_SECSfactors(self,M,Obs):
         
        #X_res = np.array([-789.5, -199.9, -32.9, -483.1, -11.7]).reshape(self.meta['Nt'],self.meta['Nstat'],order='F').T
        #Y_res = np.array([133.1, -3.7, -9.3, -14.4, 11.2]).reshape(self.meta['Nt'],self.meta['Nstat'],order='F').T
        #Z_res = np.array([-87.3, -255.5, -101.7, -270.8, -79.6]).reshape(self.meta['Nt'],self.meta['Nstat'],order='F').T
         
        Bvecs = np.zeros((2*self.meta['Nstat'],self.meta['Nt']))*np.nan
        #Bvecs[np.arange(0,2*self.meta['Nstat'],2),:] = -Obs.data_res['X_res'].values.reshape(self.meta['Nt'],self.meta['Nstat'],order='F').T 
        #Bvecs[np.arange(1,2*self.meta['Nstat'],2),:] = Obs.data_res['Y_res'].values.reshape(self.meta['Nt'],self.meta['Nstat'],order='F').T
        Bvecs[np.arange(0,2*self.meta['Nstat'],2),:] = -Obs.data['X'].values.reshape(self.meta['Nt'],self.meta['Nstat'],order='F').T 
        Bvecs[np.arange(1,2*self.meta['Nstat'],2),:] = Obs.data['Y'].values.reshape(self.meta['Nt'],self.meta['Nstat'],order='F').T
        #Bvecs[np.arange(0,2*self.meta['Nstat'],2),:] = -X_res
        #Bvecs[np.arange(1,2*self.meta['Nstat'],2),:] = Y_res
                
        Idf = np.matmul(M,Bvecs) #small deviation from matlab code

        return Idf

    ####
    
    def sub_SECS_2D_DivFree_vector(self):

        # Calculation of matrices matVtheta and matVphi which give the theta- and phi-components of a vector field
        # from the scaling factors of div-free spherical elementary current systems (DF SECS)
        # Vtheta = matVtheta * Idf, where
        # Vtheta = [Vtheta(1) Vtheta(2) ...]' vector of theta-components
        # Idf = [Idf(1') Idf(2') ...]' vector of scaling factors

        # INPUT
        # thetaV,phiV: Co-latitude and longitude of points where the vector field is to be calculated,
        #              [radian], Nv-dimensional vectors
        # thetaSECS,phiSECS: Co-latitude and longitude of the DF SECS, [radian], Nsecs-dimensional vectors
        # radius: Radius of the sphere where the calculation takes place, [km], scalar
        # LimitAngle: Half-width of the uniformly distributed SECS, [radian], scalar or Nsecs-dimensional vector

        # OUTPUT
        # matVtheta,matVphi: (Nv,Nsecs)-matrices that relate SECS scaling factors to the vector field

        # NOTE: Each individual SECS is assumed to be uniformly distributed inside a spherical cap with
        # half angle 'LimitAngle'. This removes the singularity at the pole of the SECS. Outside the
        # cap this kin of SECS has exactly the same field as the traditional singular SECS defined by Amm (1998).

        # Heikki V, March 2010, matlab 7.8.0.347 (R2009a)

        # theta- and phi-directions are badly defined at the poles of the spherical coordinate system, but no check
        # is done here...

        thetaV = np.radians(90.-self.meta['Jlat']).reshape(-1,1)
        phiV = np.radians(self.meta['Jlon']).reshape(-1,1)
        thetaSECS = np.radians(90.-self.meta['SECSlat'].reshape(-1,1,order='F'))
        phiSECS = np.radians(self.meta['SECSlon'].reshape(-1,1,order='F'))
        radius = self.meta['Rext']
        LimitAngle = 0

        # Number of points where V is calculated and scaling factors are given
        Nv = len(thetaV.reshape(-1,1))
        Nsecs = len(thetaSECS.reshape(-1,1))
        matVtheta = np.zeros((Nv,Nsecs))*np.nan
        matVphi = np.zeros((Nv,Nsecs))*np.nan

        # if LimitAngle is scalar, use it for every SECS
        if np.isscalar(LimitAngle):
            LimitAngle += np.zeros(np.shape(thetaSECS))

        # This is a common factor in all components
        CommonFactor = 1./(4*np.pi*radius)

        # Loop over vector field positions
        for n in range(Nv):

            # cosine of co-latitude in the SECS-centered system
            # See Eq. (A5) and Fig. 14 of Vanhamaki et al.(2003)
            CosThetaPrime=np.cos(thetaV[n])*np.cos(thetaSECS) + np.sin(thetaV[n])*np.sin(thetaSECS)*np.cos(phiSECS-phiV[n])

            # sin and cos of angle C, multiplied by sin(theta').
            # See Eqs. (A2)-(A5) and Fig. 14 of Vanhamaki et al.(2003)
            SinC = np.sin(thetaSECS)*np.sin(phiSECS-phiV[n])
            CosC = (np.cos(thetaSECS) - np.cos(thetaV[n])*CosThetaPrime) / np.sin(thetaV[n])

            # Find those SECS poles that are far away from the calculation point
            distant = (CosThetaPrime < np.cos(LimitAngle))

            # vector field proportional to cot(0.5*CosThetaPrime), see Eq. (2) of Vanhamaki et al.(2003)
            dummy = CommonFactor / (1-CosThetaPrime[distant])
            matVtheta[n,distant.squeeze()] = dummy * SinC[distant]
            matVphi[n,distant.squeeze()] = dummy * CosC[distant]

            # Assume that the curl of a DF SECS is uniformly distributed inside LimitAngle
            # --> field proportional to a*tan(0.5*CosThetaPrime), where a=cot(0.5*LimitAngle)^2
            dummy = CommonFactor * np.arctan(0.5*LimitAngle[~distant])**2 / (1+CosThetaPrime[~distant])
            matVtheta[n,~(distant.squeeze())] = dummy * SinC[~distant]
            matVphi[n,~(distant.squeeze())] = dummy * CosC[~distant]

        return matVtheta, matVphi
        
        #Iext = Idf[:self.meta['Npole'],:]
        #JXext = -np.matmul(matVtheta,Iext).T           #northward component
        #JYext = np.matmul(matVphi,Iext).T              #eastward component

        #return JXext, JYext

    ####
    
    def get_Jplot(self,JXext,JYext,dpath,rpath,t,step,Obs,save):

        a1=np.min(self.meta['Jlat'].reshape(-1,1))-1; a2=np.max(self.meta['Jlat'].reshape(-1,1))+1
        a3=np.min(self.meta['Jlon'].reshape(-1,1))-1.5; a4=np.max(self.meta['Jlon'].reshape(-1,1))+1.5

        fig = plt.figure(figsize=(8,8))
        #ax = plt.axes(projection=ccrs.LambertConformal(central_longitude=(a3+a4)/2,central_latitude=(a1+a2)/2,cutoff=20))
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=(a3+a4)/2,globe=None))

        # Equivalent currents
        Jext = abs(JXext+1j*JYext)
        Jext_max = np.nanmax(Jext)
        Jext_min = np.nanmin(Jext)
        #cLimE = [-100, np.max(Jext)]
        
        cmap = plt.get_cmap('coolwarm')
        #jext = ax.pcolormesh(Jlon,Jlat,Jext.reshape(np.shape(Jlat)),cmap=cmap,vmin=cLimE[0],vmax=cLimE[1],
        #                   transform=ccrs.PlateCarree())

        ax.scatter(self.meta['SECSlon'],self.meta['SECSlat'],transform=ccrs.PlateCarree(),zorder=1,s=7,color='black')
        
        jscale = 5000; width = .005; headwidth = 3; headlength = 4;        
        #ims = []
        #for step in range(len(t)):
        jvec = ax.quiver(self.meta['Jlon'],self.meta['Jlat'],JYext[step,:].reshape(np.shape(self.meta['Jlon'])),JXext[step,:].reshape(np.shape(self.meta['Jlat'])),Jext[step,:].reshape(np.shape(self.meta['Jlat'])),
                    cmap=cmap,scale=jscale,width=width,headwidth=headwidth,headlength=headlength,pivot='tail',
                    transform=ccrs.PlateCarree(),clim=[Jext_min,Jext_max],zorder=2)
        #ims.append([jvec])
            
        fig.colorbar(jvec,label=r'J$_{\mathrm{ext}}$ [A/km]')
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
        plt.show()
        
        if save == 1:
            fig.savefig(rpath+'Test_Case/Jplot_'+str(step)+'.jpg',dpi=300,transparent=True,bbox_inches='tight')

    ####

    def get_Bplot(self,BX_int,BY_int,dpath,rpath,t,start,end,t0,Obs,save):
        
        BX_int -= np.nanmean(BX_int,axis=0)
        BY_int -= np.nanmean(BY_int,axis=0)
                        
        a1=np.min(self.meta['Bintlat'].reshape(-1,1))-1; a2=np.max(self.meta['Bintlat'].reshape(-1,1))+1
        a3=np.min(self.meta['Bintlon'].reshape(-1,1))-1.5; a4=np.max(self.meta['Bintlon'].reshape(-1,1))+1.5

        fig, ax = plt.subplots(3,1,gridspec_kw={'width_ratios': [1],'height_ratios': [1, 1, 2.75]},figsize=[6,6])
        ax = ax.ravel()
        
        ax, colors = self.get_Bval0(dpath, rpath, t, start, end, Obs, ax)
        time1 = ax[0].axvline(t[t0],color='dimgray',linewidth=3,alpha=0.5); time2 = ax[1].axvline(t[t0],color='dimgray',linewidth=3,alpha=0.5)
        
        ax[2] = plt.subplot(212,projection=ccrs.PlateCarree(central_longitude=(a3+a4)/2,globe=None))
        #cax = plt.axes([0.89, 0.050, 0.02, 0.427])
        cax = plt.axes([0.86, 0.057, 0.02, 0.413]) #0.86
        #fig.subplots_adjust(left=0.13,bottom=0.05,top=0.99,right=0.88) #right=0.85
        fig.subplots_adjust(left=0.13,bottom=0.05,top=0.99,right=0.85) #right=0.85

        B_int = abs(BX_int+1j*BY_int)
        B_int_max = np.nanmax(B_int[start:end])
        B_int_min = np.nanmin(B_int[start:end])
                
        cmap = plt.get_cmap('cool')
        #Bint = ax.pcolormesh(Blon,Blat,Bext.reshape(np.shape(Blat)),cmap=cmap,vmin=cLimE[0],vmax=cLimE[1],
        #                   transform=ccrs.PlateCarree())

        ax[2].scatter(self.meta['SECSlon'],self.meta['SECSlat'],transform=ccrs.PlateCarree(),zorder=1,s=4,color='dimgray',alpha=0.3)
        
        bscale = 2000; width = .002; headwidth = 3; headlength = 4; #800 for dB
        
        Bvec = ax[2].quiver(self.meta['Bintlon'],self.meta['Bintlat'],BY_int[start+t0,:].reshape(np.shape(self.meta['Bintlon'])),BX_int[start+t0,:].reshape(np.shape(self.meta['Bintlat'])),
            B_int[start+t0,:].reshape(np.shape(self.meta['Bintlat'])),
            cmap=cmap,scale=bscale,width=width,headwidth=headwidth,headlength=headlength,pivot='tail',
            transform=ccrs.PlateCarree(),clim=[B_int_min,B_int_max],zorder=2)
        
        #time
        title = ax[2].text(0.2,0.95,t[t0].strftime('%Y/%m/%d-%H:%M UT'),transform=ax[2].transAxes, ha="center", va="center", fontsize=10) #'%m/%d/%Y, %H:%M UT'
        
        #fig.colorbar(Bvec,label=r'||dB$_{\mathrm{ext}}$/dt|| [nT/min]',cax=cax)
        fig.colorbar(Bvec,label=r'||(B-$\overline{\mathrm{B}}$)$_{\mathrm{ext}}$|| [nT]',cax=cax)
        #fig.colorbar(Bvec,label=r'B$_{\mathrm{ext}}$ [nT]',cax=cax)
        
        # INTERMAGNET Magnetometers
        for o in range(len(Obs.meta['obs'])):
            ax[2].plot(Obs.meta['lon'][o],Obs.meta['lat'][o],transform=ccrs.PlateCarree(),marker='o',linewidth=0,color=colors[o],zorder=3)
            ax[2].text(Obs.meta['lon'][o],Obs.meta['lat'][o],Obs.meta['obs'][o],fontsize=10,transform=ccrs.PlateCarree(),verticalalignment='top',horizontalalignment='left',zorder=5)
            
        #Bobs_res = abs(Obs.data_res['X_res']+1j*Obs.data_res['Y_res'])
        #Bobs = ax.quiver(Obs.meta['lon'],Obs.meta['lat'],Obs.data_res['Y_res'].loc[:,t[step]].values,Obs.data_res['X_res'].loc[:,t[step]].values,Bobs_res.loc[:,t[step]].values,
        #                cmap=cmap,scale=bscale,width=width,headwidth=headwidth,headlength=headlength,pivot='tail',
        #                transform=ccrs.PlateCarree(),clim=[B_int_min,B_int_max],zorder=6)

        # Coastlines & German border
        shape = dpath+'gadm36_DEU_shp/gadm36_DEU_1.shp'
        adm1_shapes = list(shpreader.Reader(shape).geometries())
        ax[2].add_geometries(adm1_shapes, ccrs.PlateCarree(), edgecolor='dimgray', facecolor='silver', zorder=0, alpha=0.2)
        #for AUSTRIA
        #shape = dpath+'TM_WORLD_BORDERS-0.3/TM_WORLD_BORDERS-0.3.shp'
        #adm1_shapes = list(shpreader.Reader(shape).geometries())[56]
        #ax[2].add_geometries([adm1_shapes], ccrs.PlateCarree(), edgecolor='dimgray', facecolor='silver', zorder=0, alpha=0.2)
        ax[2].coastlines(resolution='10m', color='dimgray', zorder=4)
        gl = ax[2].gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0, color='white', alpha=1, linestyle='--',zorder=4)
        gl.top_labels = False
        gl.right_labels = False
        #ax[2].gridlines()
        
        # def update_quiver(num, Q, BY_int, BX_int, t, start):
            
            # U = BY_int[start+num,:].reshape(np.shape(self.meta['Bintlon']))
            # V = BX_int[start+num,:].reshape(np.shape(self.meta['Bintlat']))
            # C = B_int[start+num,:].reshape(np.shape(self.meta['Bintlat']))

            # Q.set_UVC(U,V,C)
            
            # title.set_text(t[num].strftime('%Y/%m/%d-%H:%M UT')) #'%m/%d/%Y, %H:%M UT'
            # time1.set_xdata(t[num]); time2.set_xdata(t[num])
            
            # return Q,time1,time2,title,
        
        # anim = animation.FuncAnimation(fig, update_quiver, frames=np.arange(0,end-start+1,2), fargs=(Bvec, BY_int, BX_int, t, start), interval=100, blit=False, repeat=False)
        plt.show()
        
        if save == 1:
            #anim.save(rpath+'Test_Case/B/Bplot.mp4',writer='ffmpeg',dpi=300)
            #anim.save(rpath+'20170908_dB_new.mp4',writer='ffmpeg',dpi=300)
            #anim.save(rpath+'20170908_dB_new.gif',writer='imagemagick')
            #anim.save(rpath+'20150322_dB_WIC.gif',writer='imagemagick')
            #fig.savefig(rpath+'Test_Case/dB/Bplot_'+str(step)+'.jpg',dpi=300,transparent=True,bbox_inches='tight')
            fig.savefig(rpath+'201709_B_snap2.jpg',dpi=300,transparent=True,bbox_inches='tight')

    ####

    def get_Bval0(self,dpath,rpath,t,start,end,Obs,ax):
        
        cmap = matplotlib.cm.get_cmap('jet')
        colors = cmap(np.linspace(0,1,self.meta['Nstat']))
        
        #comp_orig = ['X_res','Y_res']
        comp_orig = ['X','Y']
        comp_names = [r'X-$\overline{\mathrm{X}}$',r'Y-$\overline{\mathrm{Y}}$']
        #comp_names = [r'dX/dt',r'dY/dt']
        
        for comp in range(len(comp_orig)):
            
            #orig = Obs.data_res[comp_orig[comp]].values.reshape(-1,self.meta['Nstat'],order='F')
            #orig = Obs.data[comp_orig[comp]].values.reshape(-1,self.meta['Nstat'],order='F')
            orig = Obs.data[comp_orig[comp]].values.reshape(-1,self.meta['Nstat'],order='F')
            orig = orig-np.nanmean(orig,axis=0)
            #orig = np.gradient(orig,axis=0)
           
            for o in range(self.meta['Nstat']):
                print(Obs.meta['obs'][o],comp,np.nanargmax(abs(orig[start:end,o])))
                if Obs.meta['obs'][o] != 'wng':
                    ax[comp].plot(t,orig[start:end,o],label=Obs.meta['obs'][o],color=colors[o],linewidth=0.8)
                else:
                    ax[comp].plot(t,orig[start:end,o],label=Obs.meta['obs'][o],color=colors[o],linewidth=1)
                ax[comp].set_ylabel(comp_names[comp]+' [nT]') # [nT/min]
                
            if comp == 0:
                loc = 2
                bbox_to_anchor = (-.01,1.3)
                ax[comp].set_xticklabels([])
            else:
                loc = 3
                bbox_to_anchor = (-.01,-.5)
                ax[comp].set_xlabel('Time [2014/02/dd-hh]')
                
            #ax[comp].legend(ncol=int(self.meta['Nstat']/2),loc=loc,bbox_to_anchor=bbox_to_anchor,fontsize=8)
            ax[comp].set_xlim([t[0],t[-1]])
            #ax[comp].set_ylim([-250,250])
            ax[comp].set_xticks(t[::60*3])
            ax[comp].set_xticklabels(str(ti.day).zfill(2)+'-'+str(ti.hour).zfill(2) for ti in t[::60*3])
            ax[comp].grid(True)
            
        return ax, colors
        
    ####
    
    def get_Bval(self,BX_val,BY_val,dpath,rpath,t,Obs,mode,save):
                    
        fig,ax = plt.subplots(2,1,sharex=True,sharey=True,figsize=(8,5))
        ax = ax.ravel()
        plt.subplots_adjust(hspace=0.05,left=0.12,right=0.97,bottom=0.2,top=0.99)

        cmap = matplotlib.cm.get_cmap('jet')
        colors = cmap(np.linspace(0,1,self.meta['Nstat']))

        hwin = 30
        tred = np.arange(hwin,len(t)-hwin,1)
        comp_orig = ['X_res','Y_res']
        comp_val = [BX_val,BY_val]
        comp_names = ['X','Y']
        metrics = np.zeros((len(tred),self.meta['Nstat'],len(comp_orig)))

        for comp in range(len(comp_orig)):
    
            orig = Obs.data_res[comp_orig[comp]].values.reshape(-1,self.meta['Nstat'],order='F')
            #orig = Obs.data_res.loc['ngk',comp_orig[comp]].values.reshape(-1,1,order='F')
                
            for o in range(self.meta['Nstat']):
            #for o in range(1):
                count = 0
                for c in tred:
                    #mae = metrics.mean_absolute_error(x_orig[:,o],BX_val[:,o])
                    #rmse = metrics.mean_squared_error(x_orig[:,o],BX_val[:,o],squared=False)
                    #---#
                    #mae = np.nanmean(abs(x_orig[c-hwin:c+hwin,o]-BX_val[c-hwin:c+hwin,o]))
                    rmse = np.sqrt(np.nanmean((orig[c-hwin:c+hwin,o]-comp_val[comp][c-hwin:c+hwin,o])**2))
                    metrics[count,o,comp] = rmse
                    count +=1
            
                #mae = np.nanmean(abs(x_orig[:,o]-BX_val[:,o]))
                rmse = np.sqrt(np.nanmean((orig[:,o]-comp_val[comp][:,o])**2))
                #diff = orig[:,o]-comp_val[comp][:,5]
                #rmse = np.sqrt(np.nanmean((diff-np.nanmean(diff))**2))
                label = ' (RMSE='+str(np.around(rmse,2))+')'
                if mode == 0:
                    #ax[comp].plot(t,orig[:,o]-comp_val[comp][:,o],label=Obs.meta['obs'][o]+label,color=colors[o])
                    #diff = orig[:,o]-comp_val[comp][:,5]
                    #ax[comp].plot(t,diff - np.nanmean(diff),label=Obs.meta['obs'][5]+label,color='orange')
                    ax[comp].plot(t,orig[:,o],label=Obs.meta['obs'][o],color=colors[o])
                else:
                    ax[comp].plot(t[tred],metrics[:,o,comp],label=Obs.meta['obs'][o]+label,color=colors[o])

            if mode == 0:   
                #ax[comp].set_ylabel(r'Pred.-Obs. '+comp_names[comp]+' [nT]')
                ax[comp].set_ylabel(r'Obs. '+comp_names[comp]+' [nT]')
            else:
                ax[comp].set_ylabel(r'RMSE '+comp_names[comp]+' [nT] ('+str(hwin*2)+' min)') #'MAE ('+str(hwin*2)+' min)'

            if comp == 0:
                loc = 2
                bbox_to_anchor = (-.01,1.3)
            else:
                loc = 3
                bbox_to_anchor = (-.01,-.5)
                ax[comp].set_xlabel('Time [min]')
            
                ax[comp].legend(ncol=int(self.meta['Nstat']/2),loc=loc,bbox_to_anchor=bbox_to_anchor,fontsize=8)
            ax[comp].grid(True)

        plt.show()
        
        if save == 1:
            #fig.savefig(rpath+'Test_Case/RMSE_00.jpg',dpi=300,transparent=True,bbox_inches='tight')
            fig.savefig(rpath+'20170908_B.jpg',dpi=300,transparent=True,bbox_inches='tight')
    
    def get_Hplot(self,Obs,dpath,rpath,t,start, end,save):

        orig_X = Obs.data['X'].values.reshape(-1,self.meta['Nstat'],order='F')
        orig_Y = Obs.data['Y'].values.reshape(-1,self.meta['Nstat'],order='F')
        orig_H=abs(np.sqrt(orig_X**2+orig_Y**2))

       # fig, ax = plt.subplots(1,1,gridspec_kw={'width_ratios': [1],'height_ratios': [1, 1, 2.75]},figsize=[6,6])
        #ax = ax.ravel()
        labels=list(Obs.meta['obs'])
        fig, ax = plt.subplots()
        cmap = matplotlib.cm.get_cmap('jet')
        cs = cmap(np.linspace(0,1,self.meta['Nstat']))
        orig_H = orig_H-np.nanmean(orig_H,axis=0)
        #orig_H = np.gradient(orig_H,axis=0)
        for o in range(self.meta['Nstat']):
            ax.plot(t,orig_H[start:end,o],label=labels[o],color=cs[o])
        ax.set_xlim([t[0],t[-1]])
        #ax.set_ylim([-250,250])
        ax.set_xticks(t[::60*3])
        ax.set_xticklabels(str(ti.day).zfill(2)+'-'+str(ti.hour).zfill(2) for ti in t[::60*3])
        #ax.legend(fontsize=8)
        ax.set_ylabel('H - $\overline{\mathrm{H}}$ [nT]')
        #ax.set_ylabel('dH/dt [nT/min]')
        ax.set_xlabel('Time [2014/02/dd-hh]')

        ax.grid(True)

        plt.show()

    ####
