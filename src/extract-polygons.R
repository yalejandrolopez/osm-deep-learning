library(sf)
library(ggplot2)
library(dplyr)
library(optparse)

#Argument parser
option_list = list(
  make_option(c("-i", "--input"), type="character", default=NULL,
              help="path to input csv with bounding boxes", metavar="character"),
  make_option(c("-o", "--output"),type="character", default=NULL,
              help="path to output geojson with bounding boxes", metavar="character")
) 

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

# read csv of bounding boxes
df = read.table(opt$input, sep = ",", header = T)

# convert bounding box values from pixels to meters
df[,2:5] = df[,2:5] * 0.1
head(df)

# convert bounding box values to coordinates
m = matrix(unlist(strsplit(df$img_name, "_")), ncol=4, byrow=T)
for ( i in 1:dim(m)[1]){

  m[[i,4]] = gsub(".tiff","", m[[i,4]])
  
}
m <- matrix(as.numeric(m), ncol = ncol(m))
colnames(m) = c("x1", "y1", "x2", "y2")
df$bbx1 = m[,c("x1")]
df$bbx2 = m[,c("x2")]
df$bby1 = m[,c("y1")]
df$bby2 = m[,c("y2")]

df$x1 = df$bbx1 + df$x1
df$x2 = df$bbx2 + df$x2
df$y1 = df$bby1 + df$y1
df$y2 = df$bby2 + df$y2
head(df)

# bounding box value to polygons
df = df %>% select(2:5)
ls = list()
geoms = list()
pols_df = data.frame(c(seq(1:nrow(df))))
colnames(pols_df) = c("c")
for (i in 1:nrow(df)){
  
  ls[i] = list(matrix(c(
    df$x1[i], df$y1[i], 
    df$x2[i], df$y1[i], 
    df$x2[i], df$y2[i], 
    df$x1[i], df$y2[i], 
    df$x1[i], df$y1[i]), 
    ncol =2, byrow = T))
  
  pols_df$c[i] = st_geometry(st_polygon(ls[i]))[1]
  
}

pols = st_sf(pols_df)
st_crs(pols) = st_crs("epsg:2056")
#pols = st_make_valid(pols)
plot(pols[])
# write to GeoJSON
st_write(pols, opt$output, driver = "GeoJSON", overwrite = T)