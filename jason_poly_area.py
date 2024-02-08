
def compute_polygon_area(vertices_x, vertices_y):
    # Add the first point to the end of the list to complete the loop
    vertices_x.append(vertices_x[0])
    vertices_y.append(vertices_y[0])

    # Initialize the area variable
    area = 0

    # Compute the area using the Shoelace formula
    for i in range(len(vertices_x) - 1):
        area += (vertices_x[i] * vertices_y[i + 1]) - (vertices_x[i + 1] * vertices_y[i])

    # Return the absolute value of half the computed area
    return abs(area) / 2

# Compute the area of each polygon

import json
from sklearn.model_selection import train_test_split

# Load Jason annotation data
with open("/mnt/data/Rajitha/MAPLE/Training_03/files/Training/dataset_00_to_06/test/via_region_data.json", 'r') as f:
    data = json.load(f)
num_keys = len(data)
print("Number of keys in the JSON file:", num_keys)

# Extract keys from the dictionary
keys = list(data.keys())

total_keys = len(keys)

# Create dictionaries for each part
print("file:","ID:","Area(pix)")
for k in keys:
    #print(k,data[k]["filename"])
    json_data=data[k]
    ID=0;
    for region in json_data["regions"]:
        vertices_x = region["shape_attributes"]["all_points_x"]
        vertices_y = region["shape_attributes"]["all_points_y"]
        area = compute_polygon_area(vertices_x, vertices_y)
        print(json_data['filename'],":",ID,":",area)
        ID+=1