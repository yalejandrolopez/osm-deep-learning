import os
import time

import geopandas as gpd
import argparse
import shutil
import statistics
import pandas as pd
from shapely.geometry import Polygon


parser = argparse.ArgumentParser(description="Move files")
parser.add_argument('--l' , type=str, help='WMS layer', default="osm-data/gis_osm_pois_a_free_1.shp")
parser.add_argument('--img' , type=str  , help='Folder of images', default="img/")
parser.add_argument('--output' , type=str  , help='folder to write labels', default="labels/")
args = parser.parse_args()
images = args.img

files = os.listdir(images)
labels = gpd.read_file(args.l)
labels = labels.to_crs(2056)

# select only labels for training
sel = ['graveyard', 'pitch']
# classify different features as park - simplify
labels = labels[labels['fclass'].isin(sel)]
print(labels['fclass'].value_counts())
time.sleep(15)

labels['area']=labels.geometry.area
labels_mean = labels.groupby(['fclass']).agg({'area':'mean'}).reset_index()
labels_mean.columns=['fclass','area_mean']
labels_dev = labels.groupby(['fclass'])['area'].apply(lambda x: statistics.stdev(x)).reset_index()
labels_dev.columns=["fclass","area_dev"]

labesl_1 = pd.merge(labels_mean, labels_dev, on="fclass")
labesl_2 = pd.merge(labels, labesl_1, on="fclass")
labesl_2 = labesl_2.loc[(labesl_2.area < labesl_2.area_mean + 2* labesl_2.area_dev) &
             (labesl_2.area > labesl_2.area_mean - 2* labesl_2.area_dev)]

grid = gpd.GeoDataFrame()
for file in files:
    file = file.replace(".tiff", "")
    x1,y1,x2,y2 = file.split("_")
    long_points = [int(x1), int(x1), int(x2), int(x2), int(x1)]
    lat_points = [int(y1), int(y2), int(y2), int(y1), int(y1)]
    polygon_geom = Polygon(zip(long_points, lat_points))
    crs = {'init': 'epsg:2056'}
    sq = gpd.GeoDataFrame(index=[file.replace(".tiff", "")], crs=crs, geometry=[polygon_geom])
    grid = pd.concat([grid, sq])
sjoin = gpd.sjoin(labesl_2, grid)
sjoin.rename(columns={'area':'areas'},inplace=True)
sjoin.areas = sjoin.area
sjoin = (sjoin.loc[sjoin.areas>100])
sjoin.reset_index(drop=True)

print(sjoin.columns)

for i in sjoin.index_right.unique():
    path = os.path.join(args.output, i)
    os.mkdir(path)
    new_label = sjoin.loc[sjoin.index_right==i]
    new_label.reset_index(drop=True)
    new_label[['osm_id', 'fclass', 'name', 'geometry']].to_file(path+"/"+str(i)+".shp")


#labels = labels.sample(1000)
#print(labels['fclass'].value_counts())
#ls = ['graveyard', 'park']

ann = pd.read_csv("C:\\Users\\yalej\\Documents\\Msc\\MachineLearningImages\\osm-deep-learning\\src\\annotate.txt")
ann['graveyard'].value_counts()