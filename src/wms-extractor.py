from owslib.wms import WebMapService
import geopandas as gpd
import argparse
import os, sys
import math
import numpy as np
from shapely.geometry import Polygon, LineString, Point

# Argument and parameter specification
parser = argparse.ArgumentParser(description="Tile generator tool (STDL)")
parser.add_argument('--labels' , type=str  , help='Label geographic file')
parser.add_argument('--size'   , type=int  , help='Tile size in meters' )
parser.add_argument('--output' , type=str  , help='Output directory', default='.')
args = parser.parse_args()

# import osm dataset
labels = gpd.read_file(args.labels)
labels = labels.to_crs(2056)

# select only labels for training
sel = ['fire_station', 'graveyard', 'hospital', 'park', 'pitch', 'playground', 'stadium', 'wastewater_plant', 'castle', 'college', 'dog_park', 'drinking_water', 'school', 'prison', 'zoo', 'fountain', 'theme_park', 'golf_course']

# classify different features as park - simplify
labels = labels[labels['fclass'].isin(sel)]
ls = ['pitch', 'dog_park', 'theme_park', 'playground']
labels.loc[labels.fclass.isin(ls),'fclass']='park'

# create tiles over all of Switzerland
shift_x = int(+round( args.size * 0. ))
shift_y = int(+round( args.size * 0. ))

# Prevent duplicated tiles
dupl = []

# Bootstrap tiles
geo_tiling = gpd.GeoDataFrame()

# Indexation
indexation = 0

# Parsing label geometries
for index, row in labels.iterrows():

    # Extract geometry vertex
    bbox = row['geometry'].bounds

    # round bounding box
    bbox_rlx = math.floor( ( bbox[0] - shift_x ) / args.size ) * args.size + shift_x
    bbox_rly = math.floor( ( bbox[1] - shift_y ) / args.size ) * args.size + shift_y
    bbox_rhx = math.ceil ( ( bbox[2] - shift_x ) / args.size ) * args.size + shift_x
    bbox_rhy = math.ceil ( ( bbox[3] - shift_y ) / args.size ) * args.size + shift_y

    # create grid over the rounded bounding box
    for x in range( bbox_rlx, bbox_rhx, args.size ):

        # create grid over the rounded bounding box
        for y in range( bbox_rly, bbox_rhy, args.size ):

            # compute tile lower corner
            g_x = x;
            g_y = y;

            # Prevent tile duplication
            if not ( g_x, g_y ) in dupl:
                
                # Add tile definition
                geo_tiling.loc[indexation,'geometry'] = Polygon( [ ( g_x, g_y ), ( g_x + args.size, g_y ), ( g_x + args.size, g_y + args.size ), ( g_x, g_y + args.size ), ( g_x, g_y ) ] )

                # Update index
                indexation = indexation + 1

                # Add tile to duplication stack
                dupl.append( ( g_x, g_y ) )

# Assign CRS to tiling dataframe
geo_tiling = geo_tiling.set_crs( crs = labels.crs )

# Remove empty tile, i.e. tiles that are not part of the label(s) mapping
geo_tiling = gpd.sjoin( geo_tiling, labels, how="inner" )

# Drop dublicated tiles
geo_tiling.drop_duplicates(subset=['geometry'],inplace=True)

# Filtering columns on tiling dataframe
geo_tiling = geo_tiling.loc[:, ['geometry']]

# extract geometry vertex
bboxes = np.zeros((len(geo_tiling),4))

tile_copy = geo_tiling.copy()
geo_tiling.reset_index(drop=True, inplace=True)
for i in range(len(geo_tiling)-1):

    for j in range(0,4):

        bboxes[i][j] = geo_tiling.geometry[i].bounds[j]

# extract polygons
clipped_labels = []
for i in range(len(geo_tiling)-1):

    clipped_labels.append(labels.clip(geo_tiling.geometry[i]))

for i in range(len(clipped_labels)):

    os.mkdir('labels/' +  str(int(bboxes[i][0])) +'_'+ str(int(bboxes[i][1])) +'_'+ str(int(bboxes[i][2])) + '_'+ str(int(bboxes[i][3])))

for i in range(len(clipped_labels)):

    clipped_labels[i].to_file('labels/' +  str(int(bboxes[i][0])) +'_'+ str(int(bboxes[i][1])) +'_'+ str(int(bboxes[i][2])) + '_'+ str(int(bboxes[i][3])) + '/' +  str(int(bboxes[i][0])) +'_'+ str(int(bboxes[i][1])) +'_'+ str(int(bboxes[i][2])) + '_'+ str(int(bboxes[i][3])) +  '.shp', driver = "ESRI Shapefile")

# extract GeoTiffs
wms = WebMapService('https://imageserver.gisdata.mn.gov/cgi-bin/wmsll?')
wms = WebMapService('https://wms.geo.admin.ch/service')
#print(wms.identification.type)
#wms.identification.version
#wms.identification.title
#wms.identification.abstract
#print(list(wms.contents))

layer = 'ch.swisstopo.swissimage'
print(wms[layer].title)
print(wms[layer].queryable)
print(wms[layer].opaque)
print(wms[layer].boundingBox)
print(wms[layer].boundingBoxWGS84)
print(wms[layer].crsOptions)
print(wms[layer].styles)

[op.name for op in wms.operations]
wms.getOperationByName('GetMap').methods
wms.getOperationByName('GetMap').formatOptions

# extract images
for i in range(len(bboxes)):
    img = wms.getmap(   layers=[layer],
                     #styles=['visual_bright'],
                     srs='EPSG:2056',
                     bbox=(bboxes[i][0], bboxes[i][1], bboxes[i][2], bboxes[i][3]),
                     size=(512, 512),
                     format='image/tiff',
                     transparent=True
                     )
    out = open('img/' + str(int(bboxes[i][0])) +'_'+ str(int(bboxes[i][1])) +'_'+ str(int(bboxes[i][2])) + '_'+ str(int(bboxes[i][3])) + '.tiff', 'wb')
    out.write(img.read())
    out.close()

os.remove('img/*.xml')