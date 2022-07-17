import os
import geopandas as gpd

files = os.listdir('labels')
images = os.listdir('img')
annotation = []
print(len(images))
for i in files:
    if i+".tiff" not in images:
        if i+".tiff"=="2540000_1151000_2540500_1151500.tiff":
            print(i+".tiff")
        continue

    #files = os.listdir(r"C:\Users\user\Documents\Msc\MachineLearningImages\src\labels")
    #i = files[0]
    shapes = os.listdir('labels/' + i)
    #shapes = os.listdir(r"C:\Users\user\Documents\Msc\MachineLearningImages\src\labels\\" + i)
    file = [x for x in shapes if x.endswith(".shp")][0]
    #layer = gpd.read_file(r"C:\Users\user\Documents\Msc\MachineLearningImages\src\labels\\" + i + '/' + file)
    layer = gpd.read_file('labels/' + i +'/'+ file)
    for j in range(len(layer)):
        if layer.area.iloc[j]<30:
            continue
        #Expand bounds

        deltax = ((layer.bounds.iloc[j].maxx- layer.bounds.iloc[j].minx)*0.15) #30% divided by 2 for each bound
        deltay = ((layer.bounds.iloc[j].maxy - layer.bounds.iloc[j].miny) * 0.15)  # 30% divided by 2 for each bound

        minx = int(layer.bounds.iloc[j].minx - deltax)
        maxx = int(layer.bounds.iloc[j].maxx - deltax)
        miny = int(layer.bounds.iloc[j].miny - deltay)
        maxy = int(layer.bounds.iloc[j].maxy - deltay)

        #compare with image (cannot have limit over the image)
        win_minx,win_miny, win_maxx,win_maxy =i.split("_")
        win_minx = int(win_minx)
        win_miny = int(win_miny)
        win_maxx = int (win_maxx)
        win_maxy = int(win_maxy)

        #otherwise standarize
        if minx<win_minx:
            minx = win_minx
        if maxx>win_maxx:
            maxx = win_maxx
        if miny<win_miny:
            miny = win_miny
        if maxy>win_maxy:
            maxy = win_maxy

        minx2 = minx - win_minx
        maxx2 = maxx - win_minx
        miny2 = win_maxy - maxy
        maxy2 = win_maxy - miny

        annotation.append('img/'+i+".tiff,"+ str(int(minx2/0.1)) +","+str(int(miny2/0.1))+","+str(int(maxx2/0.1))+","+str(int(maxy2/0.1))+","+layer.iloc[0]['fclass'])


textfile = open("src/"+"annotate.txt", "w")
for element in annotation:
    textfile.write(element + "\n")
textfile.close()


#osm = gpd.read_file("C:\\Users\\yalej\\Documents\\Msc\\MachineLearningImages\\osm-deep-learning\\osm-data\\gis_osm_pois_a_free_1.shp")
#labels = osm.copy()
#labels['fclass'].value_counts()