import json
import codecs
import os

# Read json and write to names file
with open('../names/name.json') as json_file:
    data = json.load(json_file)

    out_file = open("kobaco-face-hangul.names", "w")

    for idx, item in enumerate(data):
        out_file.write("{}, {}".format(idx, item))
        out_file.write("\n")

    out_file.close()
