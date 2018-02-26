from os.path import dirname, abspath
from glob import glob
from utils import *

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from matplotlib.path import Path
import matplotlib.cm as cm


from time import time

start_time = time()

par_dir = dirname(dirname(abspath(__file__)))
dir_name = par_dir + '/data/MODIS_L3_JPL/aqua/chlA/'
#dir_name = par_dir + '/data/MODIS_L3_JPL/aqua/11um/'
dir_name_shp = par_dir + '/shp/'
years = glob(dir_name+'*')

# Grabs actual lat & lon from file. This way the plot fits nicely in the shapefile!
latlon_file = '/home/mwilson/work/GWF/data/MODIS_L3_JPL/aqua/chlA/2003/A20030012003031.L3m_MO_CHL_chlor_a_4km.nc'
latlon_grp  = Dataset(latlon_file)
lats = latlon_grp.variables['lat'][:]
lons = latlon_grp.variables['lon'][:]
latlon_grp.close()
'''
WARNING:
Masking has been disabled for the averaging.
'''

##GL
x_range = [2039,2568]
y_range = [935 ,1200]

latcorners = [lats[y_range[1]-1], lats[y_range[0]-1]] # -1 because the index are going the opposite way. We want bottom value of bin, not top!
loncorners = [lons[x_range[0]], lons[x_range[1]]]

nx = x_range[1]-x_range[0]
ny = y_range[1]-y_range[0]

lon = np.linspace(loncorners[0],loncorners[1],nx, endpoint=True)
lat = np.linspace(latcorners[0],latcorners[1],ny, endpoint=True)

map = create_map(loncorners, latcorners, 'i', 'laea', 90, -90)

lon,lat = np.meshgrid(lon,lat)
xx,yy = map(*(lon,lat))

jan  = 0
feb  = 0
mar  = 0
apr  = 0
may  = 0
jun  = 0
jul  = 0
aug  = 0
sep  = 0
octo = 0
nov  = 0
dec  = 0 

jan_array  = [] 
feb_array  = []
mar_array  = []
apr_array  = []
may_array  = []
jun_array  = []
jul_array  = []
aug_array  = []
sep_array  = []
octo_array = []
nov_array  = []
dec_array  = []




for year in years:
    months = glob(year+'/*.nc') #_SST_sst_4km
    for month in months:
        rootgrp = Dataset(month, 'r', format='NETCDF4')
        content = np.flipud(rootgrp.variables['chlor_a'][y_range[0]:y_range[1],x_range[0]:x_range[1]])
        #plt.pcolormesh(xx,yy,content)
        #plt.show()
        day_0 = month.split(year[-4:])[2]
        if day_0 == '001': #January
            jan += 1
            jan_array.append(content)
        elif day_0 == '032': #February
            feb += 1
            feb_array.append(content)
        elif day_0 == '060' or day_0 == '061': #March
            mar += 1
            mar_array.append(content)
        elif day_0 == '091' or day_0 == '092': #April
            apr += 1
            apr_array.append(content)
        elif day_0 == '121' or day_0 == '122': #May
            may += 1
            may_array.append(content)
        elif day_0 == '152' or day_0 == '153': #June
            jun += 1
            jun_array.append(content)
        elif day_0 == '182' or day_0 == '183': #July
            jul += 1
            jul_array.append(content)
        elif day_0 == '213' or day_0 == '214': #August
            aug += 1
            aug_array.append(content)
        elif day_0 == '244' or day_0 == '245': #September
            sep += 1
            sep_array.append(content)
        elif day_0 == '274' or day_0 == '275': #October
            octo += 1
            octo_array.append(content)
        elif day_0 == '305' or day_0 == '306': #November
            nov += 1
            nov_array.append(content)
        elif day_0 == '335' or day_0 == '336': #December
            dec += 1
            dec_array.append(content)
        rootgrp.close()
        
month_arr = np.array([np.array(jan_array), np.array(feb_array), np.array(mar_array), np.array(apr_array),\
            np.array(may_array), np.array(jun_array), np.array(jul_array), np.array(aug_array),\
            np.array(sep_array), np.array(octo_array), np.array(nov_array), np.array(dec_array)])

frequency = [jan, feb, mar, apr, may, jun, jul, aug, sep, octo, nov, dec]

avg_array = []
j = 0


#bins = np.arange(0,14,1)

for months in month_arr:
    total = 0
    for i,month_year in enumerate(months):     
        total += np.ma.masked_less(month_year,0)
    avg_array.append(total/len(months))
    
    cs = map.contourf(xx, yy, total/len(months))#, bins)
    plt.colorbar()
    plt.show()
    #plt.savefig(par_dir+'/plots/Average of Month:{}'.format(j+1))
    plt.clf()
    map.drawcoastlines()
    j+= 1
    

'''
rootgrp = Dataset(par_dir + '/output/avg_chl_occci.nc', 'w', format='NETCDF4')

month = rootgrp.createDimension('month', 12)
lat = rootgrp.createDimension('lat', ny)
lon = rootgrp.createDimension('lon', nx)

var_chl_avg = rootgrp.createVariable('avg_chl','f4',('lat','lon','month',),fill_value=-999)
var_lat = rootgrp.createVariable('latitude', 'f4', ('lat'))
var_lon = rootgrp.createVariable('longitude', 'f4', ('lon'))
var_month = rootgrp.createVariable('month', 'i4', ('month'))

lon = np.linspace(loncorners[0],loncorners[1],nx)
lat = np.linspace(latcorners[0],latcorners[1],ny)

var_lat[:] = lat[:]
var_lon[:] = lon[:]

for i in range(0,12):
    var_month[:] = i+1
    var_chl_avg[:,:,i] = avg_array[i]

rootgrp.close()

'''
    
    
