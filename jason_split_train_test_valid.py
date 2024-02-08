import json
#import argparse
import funcy
from sklearn.model_selection import train_test_split


ratio_train = 0.8 #args.ratio_train
ratio_valid = 0.1 #args.ratio_valid
ratio_test = 0.1 #args.ratio_test

import json
from sklearn.model_selection import train_test_split

# Load Jason annotation data
with open("./a_iwps/annotations/annotations.json", 'r') as f:
    data = json.load(f)
num_keys = len(data)
print("Number of keys in the JSON file:", num_keys)

keys = list(data.keys())

# Extract keys from the dictionary

import random

keys = list(data.keys())

#print(keys)

random.seed(13)
random.shuffle(keys)
#print("after")
#print(keys)

# Calculate split indices
total_keys = len(keys)
train_split_index = int(0.6 * total_keys)
valid_split_index = int(0.8 * total_keys)

# Split keys into three parts: train, validation, test
train_keys = keys[:train_split_index]
valid_keys = keys[train_split_index:valid_split_index]
test_keys = keys[valid_split_index:]

# Create dictionaries for each part
train_data = {key: data[key] for key in train_keys}
valid_data = {key: data[key] for key in valid_keys}
test_data = {key: data[key] for key in test_keys}

# Write each part to a new JSON file
with open('train_data.json', 'w') as f:
    json.dump(train_data, f, indent=4)

with open('valid_data.json', 'w') as f:
    json.dump(valid_data, f, indent=4)

with open('test_data.json', 'w') as f:
    json.dump(test_data, f, indent=4)

print("JSON data split into train, validation, and test sets and saved as train_data.json, valid_data.json, and test_data.json.")

import shutil
import os


for k in test_keys:
    shutil.copy("./a_iwps/patches/"+data[k]["filename"],"./test/")
for k in train_keys:
    shutil.copy("./a_iwps/patches/"+data[k]["filename"],"./train/")
for k in valid_keys:
    shutil.copy("./a_iwps/patches/"+data[k]["filename"],"./valid/")
