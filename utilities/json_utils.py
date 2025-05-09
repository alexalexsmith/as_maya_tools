"""
json utils for importing and exporting .json files
"""
import json
import os


def write_json_file(file_path, file_name, data):
    """
    save json file with data
    :param str file_path: file_path to write
    :param str file_name: name of the json file to write
    :param dict data: dictionary formatted data to write into json file"""

    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open("{0}/{1}.json".format(file_path, file_name), 'w') as outFile:
        json.dump(data, outFile, indent=4)


def read_offset_json_file(file_path, file_name):
    """read in jason file data
    :param str file_path: file_path to read
    :param str file_name: name of the json file to read
    :return dict: contents of the json file"""

    json_file_path = "{0}/{1}.json".format(file_path, file_name)
    if not file_path or not os.path.isfile(json_file_path):
        return None

    with open(json_file_path) as json_data:
        json_file_contents = json.load(json_data)
    return json_file_contents