import random
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import geopandas as gpd

# Load the land polygons from Natural Earth dataset
land_polygons = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Filter out only the land polygons
land_polygons = land_polygons[land_polygons['continent'] != 'Antarctica']

# Generate 10,000 points on the land
land_points = []
while len(land_points) < 10000:
    lon = random.uniform(-180, 180)
    lat = random.uniform(-90, 90)
    point = Point(lon, lat)
    for polygon in land_polygons['geometry']:
        if polygon.contains(point):
            land_points.append((lon, lat))
            break


file = open("rand_point.txt", "w")
for item in land_points:
    file.write(str(item) + "\n")

file.close()
