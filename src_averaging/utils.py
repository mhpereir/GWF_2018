import shapefile
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal

from mpl_toolkits.basemap import Basemap
from matplotlib.path import Path

def read_tif(file_name):
    '''
    Opens the tiff file and returns the content. Assumes 1 band of information. 
    '''
    im = gdal.Open(file_name)
    content = im.ReadAsArray()
    gt = im.GetGeoTransform()
    return content, gt

def create_map(loncorners, latcorners, res, proj, lat_0, lon_0):
    '''
    Creates map with Basemap
    '''
    map = Basemap(resolution=res,projection=proj,\
                llcrnrlon=loncorners[0], llcrnrlat=latcorners[0],\
                urcrnrlon=loncorners[1], urcrnrlat=latcorners[1],\
                lat_0=lat_0,lon_0=lon_0, rsphere=6371228)

    map.drawcoastlines()
    #map.drawcountries()
    return map

def read_shp(file_name, list_index, *i_range):
    sf = shapefile.Reader(file_name)
    shape = list(sf.iterShapes())[list_index]
    x_lon = []
    y_lat = []
    
    if not i_range:
        i_range = [[0, len(shape.points)]]
            
    for ip in range(i_range[0][0],i_range[0][1]):
        x_lon.append(shape.points[ip][0])
        y_lat.append(shape.points[ip][1])
        
    return np.array(x_lon), np.array(y_lat)

def clip_content_index(xx_sf, yy_sf, xx, yy, content):
    max_xx_interest = max(xx_sf)
    max_yy_interest = max(yy_sf)

    min_xx_interest = min(xx_sf)
    min_yy_interest = min(yy_sf)

    for i,x in enumerate(xx[0:len(xx)-1]):
        if x <= min_xx_interest and xx[i+1] >= min_xx_interest:
            min_xx_index = i-1
        elif x <= max_xx_interest and xx[i+1] >= max_xx_interest:
            max_xx_index = i+1
            break
        
    for i,y in enumerate(yy[0:len(yy)-1]):
        if y >= max_yy_interest and yy[i+1] <= max_yy_interest:
            min_yy_index = i-1
        elif y >= min_yy_interest and yy[i+1] <= min_yy_interest:
            max_yy_index = i+1
            break
        
    xx_range = [min_xx_index, max_xx_index]
    yy_range = [min_yy_index, max_yy_index]
    
    xx_interest = [min_xx_interest, max_xx_interest]
    yy_interest = [min_yy_interest, max_yy_interest]
    
    content_clipped = content[yy_range[0]:yy_range[1],xx_range[0]:xx_range[1]]

    xx_clipped = np.array(xx[xx_range[0]:xx_range[1]],dtype=np.int32)
    yy_clipped = np.array(yy[yy_range[0]:yy_range[1]],dtype=np.int32)

    return xx_clipped, yy_clipped, content_clipped, xx_interest, yy_interest
    
def polygon_mask(xx_sf, yy_sf, xx, yy, inv):
    '''
    Creates polygon mask with shapefile points.
    Requires content grid space in same units as polygon mask points
    '''
    nx = len(xx[:,0])
    ny = len(yy[0,:])  
    
    polygon = np.array((xx_sf,yy_sf)).T
    path = Path(polygon)

    x,y = xx.flatten(), yy.flatten()
    
    points = np.vstack((x,y)).T
    grid = path.contains_points(points)
    if inv:
        grid = grid.reshape((nx, ny))
    else:
        grid = np.invert(grid.reshape((nx,ny)))
 
    return grid


