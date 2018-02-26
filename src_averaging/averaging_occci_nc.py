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
dir_name = '/media/mwilson/750GB/OCCCI/ChlA/'
dir_name_shp = par_dir + '/shp/'
years = glob(dir_name+'*')

# Grabs actual lat & lon from file. This way the plot fits nicely in the shapefile!
latlon_file = '/media/mwilson/750GB/OCCCI/ChlA/1997/ESACCI-OC-L3S-CHLOR_A-MERGED-1M_MONTHLY_4km_GEO_PML_OCx-199709-fv3.1.nc'
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

month_arr = [[],
              [],
              [],
              [],
              [],
              [],
              [],
              [],
              [],
              [],
              [],
              []]


for year in years:
    months = glob(year+'/*.nc') #_SST_sst_4km
    for month in months:
        month_n = int(month.split('-')[-2][-2::]) - 1
        rootgrp = Dataset(month, 'r', format='NETCDF4')
        content = np.flipud(rootgrp.variables['chlor_a'][0,y_range[0]:y_range[1],x_range[0]:x_range[1]])
        
        month_arr[month_n].append(content)
        rootgrp.close()  


#bins = np.arange(0,14,1)
avg_array = []
for j,months in enumerate(month_arr):
    total = 0
    for i,month_year in enumerate(months):     
        total += np.ma.masked_less(month_year,0)
    avg_array.append(total/len(months))
    
    cs = map.contourf(xx, yy, total/len(months))#, bins)
    plt.colorbar()
    #plt.show()
    plt.savefig(par_dir+'/plots/Average of Month:{}'.format(j+1))
    plt.clf()
    map.drawcoastlines()
    


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


    
    