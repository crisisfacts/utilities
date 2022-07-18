#! /usr/bin/env python

import sys
import json


if len(sys.argv) < 2:
    print("Usage: %s <run_file_to_check.json>" % sys.argv[0], file=sys.stderr)
    sys.exit(-1)


in_file_path = sys.argv[1]
print("Checking file: [%s]" % in_file_path)

# class Fact:
#     requestID : str
#     factText : str
#     unixTimestamp : int
#     importance : float
#     sources : List[str] = []
#     streamID : str
#     informationNeeds: [] = []


checkable_data = None
with open(in_file_path, "r") as in_file:
    checkable_data = json.load(in_file)

for line_num, element in enumerate(checkable_data):

    # String types
    assert type(element["requestID"]) == str, "ERROR, Line [%d]: requestID type is not str" % line_num
    assert type(element["factText"]) == str, "ERROR, Line [%d]: factText type is not str" % line_num

    assert "streamID" in element, "ERROR, Line [%d]: streamID  not in element" % line_num
    if element["streamID"] is not None:
        assert type(element["streamID"]) == str, "ERROR, Line [%d]: requestID type is not str" % line_num
    
    # int types
    assert type(element["unixTimestamp"]) == int, "ERROR, Line [%d]: unixTimestamp type is not int" % line_num

    # float types
    assert type(element["importance"]) == float, "ERROR, Line [%d]: importance type is not float" % line_num

    # List types
    assert type(element["sources"]) == list, "ERROR, Line [%d]: sources type is not list" % line_num
    assert len(element["sources"]) > 0, "ERROR, Line [%d]: sources must be non-empty" % line_num

    if element["informationNeeds"] is not None:
        assert type(element["informationNeeds"]) == list, "ERROR, Line [%d]: informationNeeds type is not list" % line_num


# TODO: Validate requestID is in the set of requests
# TODO: Validate importance is reasonable
# TODO: Validate elements in sources and information needs are reasonable


print("Success! No errors found.")