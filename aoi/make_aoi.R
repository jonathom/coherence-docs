library(sf)
cou <- read_sf("/home/petra/Downloads/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp")
belfr <- cou[cou$SUBUNIT == "Belgium" | cou$SUBUNIT == "France",]
plot(st_geometry(belfr))

belfr_c <- st_crop(belfr, xmin = -7, xmax = 12, ymin = 37.8, ymax = 59.7)

plot(belfr_c)
all <- st_union(belfr_c)
bor <- st_geometry(all)

library(geojsonsf)
write(sf_geojson(st_as_sf(bor)), "/home/petra/Downloads/belgium_france.geojson")
