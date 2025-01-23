"""
json utils for importing and exporting .json files
"""
import json
import os

from as_maya_tools import USER_DATA_PATH


def write_json_file(file_name, data):
    """save json file with data
    :param str file_name: name of the json file to write
    :param dict data: dictionary formatted data to write into json file"""

    file_path = "{0}/{1}".format(USER_DATA_PATH, file_name)
    with open(file_path, 'w') as outFile:
        json.dump(data, outFile, indent=4)


def read_offset_json_file(file_name):
    """read in jason file data
    :param str file_name: name of the json file to read
    :return dict: contents of the json file"""

    file_path = "{0}/{1}".format(USER_DATA_PATH, file_name)
    if not file_path or not os.path.isfile(file_path):
        return None

    with open(file_path) as json_data:
        json_file_contents = json.load(json_data)
    return json_file_contents

