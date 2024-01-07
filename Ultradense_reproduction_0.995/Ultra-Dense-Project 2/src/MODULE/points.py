from global_land_mask import globe
import random


# Enter the latitude and longitude to determine whether you are on land
def is_land(latitude,longitude):
    return globe.is_land(latitude,longitude)


points=[]
while len(points) < 1000:
    longitude = random.uniform(-180, 180)
    latitude = random.uniform(-90, 90)
    if is_land(latitude , longitude):
        points.append([longitude, latitude])

# Specify output file name
output_file = "points.txt"

# Write the contents of a two-dimensional list to a file
with open(output_file, 'w') as file:
    for row in points:
        # Convert each element in the dimension to a string, concatenated with spaces
        row_str = '\t'.join(str(item) for item in row)
        # Write each dimension to a file with a newline at the end
        file.write(row_str + '\n')