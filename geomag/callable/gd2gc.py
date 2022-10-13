from numpy import *
from pdb import *

def gdtogc_v(cltgd, xgd, zgd, alt):
#     FUNCTION - conversion of position and vector from geodetic,
#     i.e. spheroidal,to geocentric, i.e. spherical, coordinates
#     using WGS84  spheroid
#
#     First author: unknown
#     21/01/2003-Modified to better meet FORTRAN std. V. Lesur
#     23/11/2004-Modified From gdtogc.f for vector V. Lesur
#     22/01/2010-Modified for use as R routine I. Michaelis
#
#     ARGUMENTS -
#     Name         Type  I/O  Description
#     ----         ----  ---  -----------
#     cltgd        dble   I   geodetic colatitude (rad)
#     xgd          dble   I   North vector component
#     zgd          dble   I   East vector component
#     alt          dble   I   altitude above sea-level (km)
#     cltgc        dble   O   geocentic colatitude (rad)
#     xgc          dble   O   North vector component geocentric
#     zgc          dble   O   East vector component geocentric
#     r            dble   O   radius from centre of earth (km)
#
      cltgd = array(cltgd, ndmin=1)
      xgd   = array(xgd, ndmin=1)
      zgd   = array(zgd, ndmin=1)
      alt   = array(alt, ndmin=1)
    
      one   = cltgd
      ct    = cos(one)
      st    = sin(one)
#      a2    = 40680631.6
#      b2    = 40408296.0
      a2    = 6378.137*6378.137
      b2    = 6356.7523142*6356.7523142
      one   = a2*st*st
      two   = b2*ct*ct
      three = one + two
      rho   = sqrt(three)
      r     = sqrt(alt*(alt + 2.0*rho) + (a2*one + b2*two)/three)
      cd    = (alt + rho)/r
      sd    = (a2 - b2)/rho*ct*st/r
      one   = ct
      ct    = ct*cd -  st*sd
      st    = st*cd + one*sd
      cltgc = arctan2(st,ct)
      xgc   = xgd*cd - zgd*sd
      zgc   = zgd*cd + xgd*sd

      m = zeros([len(alt),3,3])
      m[:,0,0] =  cd
      m[:,0,2] = -sd
      m[:,1,1] =   1
      m[:,2,0] =  sd
      m[:,2,2] =  cd

      return xgc, zgc, r, m, cltgc
      
def gctogd_v(xgc, zgc, m):
	  
      dim = shape(xgc)
      
      sd = zeros(dim)+m[0,2,0]
      cd = zeros(dim)+m[0,0,0]

      xgd = xgc*cd + zgc*sd
      zgd = zgc*cd - xgc*sd

      return xgd, zgd
