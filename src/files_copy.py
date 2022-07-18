import os
import geopandas as gpd
import argparse
import shutil


parser = argparse.ArgumentParser(description="Move files")
parser.add_argument('--folder' , type=str  , help='Folder of new location')
args = parser.parse_args()
target_path = args.folder

files = os.listdir('labels')
images = os.listdir('img')
annotation = []
ls = ['school']

for i in files:
    shapes = os.listdir('labels/' + i)
    # shapes = os.listdir(r"C:\Users\user\Documents\Msc\MachineLearningImages\src\labels\\" + i)
    file = [x for x in shapes if x.endswith(".shp")][0]
    # layer = gpd.read_file(r"C:\Users\user\Documents\Msc\MachineLearningImages\src\labels\\" + i + '/' + file)
    layer = gpd.read_file('labels/' + i + '/' + file)
    layer = (layer.loc[layer['fclass'].isin(ls)]).reset_index()
    status = False
    if len(layer == 0):
        continue
    for j in range(len(layer)):
        if layer.area.iloc[j] < 30:
            status = True
    if status==True:
        status==False
        continue
    shutil.copytree('labels/'+shapes, target_path+'/labels/'+shapes)
    shutil.copyfile('img/'+ i + ".tiff", target_path + '/img/'+ i + ".tiff")


# osm = gpd.read_file("C:\\Users\\yalej\\Documents\\Msc\\MachineLearningImages\\osm-deep-learning\\osm-data\\gis_osm_pois_a_free_1.shp")
# labels = osm.copy()
# labels['fclass'].value_counts()
