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

par_dir         = dirname(dirname(abspath(__file__)))
dir_name        = '/media/mwilson/My Passport/Matthew/MODIS_1km_LST/Monthly/'
dir_name_shp    = par_dir + '/shp/'
data_files      = glob(dir_name+'*_NA_001.tif')

'''
WARNING:
Masking has been disabled for the averaging.
'''

latcorners = [ 39.861, 49.284] 
loncorners = [-94.004,-71.671]

nx = 1178                          
ny = 1771                          

xx = np.arange(0,nx*1*1000, 1000) #(latitude)
yy = np.arange(0,-ny*1*1000, -1000) #(longitude)

xx,yy =np.meshgrid(xx,yy)

map = create_map(loncorners, latcorners, 'i', 'laea', lat_0=90, lon_0=0)

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

for data in data_files:
    im = gdal.Open(data) # reads in tiff file
    content = im.ReadAsArray() 
    gt = im.GetGeoTransform()
    
    if gt[3] < 400000:  # the latter half of the files cover a bigger extent of land, so the content needs to be cropped.
        pass
    else:
        content = content[94:ny+94,0:nx]
    
    
    date_n = data.split('_')[7]
    month_n = int(date_n.split('.')[1]) - 1
    month_arr[month_n].append(content)
    '''
    fig, ax = plt.subplots()
    map.drawcoastlines()
    plt.pcolormesh(xx,yy,content)
    plt.show()
    '''
    

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



rootgrp = Dataset(par_dir + '/output/avg_sst_month_tif.nc', 'w', format='NETCDF4')

month = rootgrp.createDimension('month', 12)
lat = rootgrp.createDimension('lat', ny)
lon = rootgrp.createDimension('lon', nx)

var_chl_avg = rootgrp.createVariable('avg_sst','f4',('lat','lon','month',),fill_value=-999)
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
    
    
