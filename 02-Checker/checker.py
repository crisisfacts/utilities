#!/runs/bin/venv/bin/python

import sys
import json

import logging
import argparse
from pathlib import Path

arg_parse = argparse.ArgumentParser(
    prog='checker.py',
    description='CrisisFACTS Submission File Checker',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
arg_parse.add_argument('--files', '-f',
                       help='Location of requests files',
                       default='/runs/aux/crisis')
arg_parse.add_argument(
    "--disable",
    type=str,
    choices=["requestIds", "importance", "queries", "sources"],
    default="",
    nargs='+',
    help="Which checks to disable"
)
arg_parse.add_argument('filename',
                help='Run file to check')
arguments = arg_parse.parse_args()

logging.basicConfig(filename=f'{arguments.filename}.errlog',
                    level=logging.DEBUG)

# Catch assertion failures and log them to the errlog
def excepthook(exctype, value, traceback):
    if issubclass(exctype, AssertionError):
        logging.getLogger().error(value)
        sys.exit(255)
    else:
        sys.__excepthook__(exctype, value, traceback)

sys.excepthook = excepthook

print("Format checking:", "enabled")

requestId_check = True
if "requestIds" in arguments.disable:
    requestId_check = False
print("Request ID checking:", "enabled" if requestId_check else "disabled")


importance_check = True
if "importance" in arguments.disable:
    importance_check = False
print("Importance checking:", "enabled" if importance_check else "disabled")


info_need_check = True
if "queries" in arguments.disable:
    info_need_check = False
print("Query checking:", "enabled" if info_need_check else "disabled")


sources_check = True
if "sources" in arguments.disable:
    sources_check = False
print("Source checking:", "enabled" if sources_check else "disabled")


# Get the file to check
in_file_path = arguments.filename
print("Checking file: [%s]" % in_file_path)




# Reach in our submission file
checkable_data = None
with open(in_file_path, "r") as in_file:
    checkable_data = [json.loads(line) for line in in_file]



# *****************************************************************************
# Check format, always happens
# *****************************************************************************
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

print("Format Check: Pass")

# *****************************************************************************
# Validate requestID is in the set of requests
# *****************************************************************************
if requestId_check:

    # Event numbers as a list
    event_list = [
        "001", # Lilac Wildfire 2017
        "002", # Cranston Wildfire 2018
        "003", # Holy Wildfire 2018
        "004", # Hurricane Florence 2018
        "005", # 2018 Maryland Flood
        "006", # Saddleridge Wildfire 2019
        "007", # Hurricane Laura 2020
        "008", # Hurricane Sally 2020
        "009", # Beirut Explosion, 2020
        "010", # Houston Explosion, 2020
        "011", # Rutherford TN Floods, 2020
        "012", # TN Derecho, 2020
        "013", # Edenville Dam Fail, 2020
        "014", # Hurricane Dorian, 2019
        "015", # Kincade Wildfire, 2019
        "016", # Easter Tornado Outbreak, 2020
        "017", # Tornado Outbreak, 2020 Apr
        "018", # Tornado Outbreak, 2020 March
    ]

    valid_requests = set()
    for event_number in event_list:
        file_loc = Path(arguments.files) / f'CrisisFACTS-{event_number}.requests.json'

        # Read in the list and parse as JSON
        this_event = json.load(open(file_loc, 'r'))
        for day in this_event:
            valid_requests.add(day["requestID"])

    # Keep track of the request IDs we've seen in the submission file
    found_requests = set()

    # Iterate through all elements in the submission, and ensure request IDs are valid
    for line_num, element in enumerate(checkable_data):
        assert element["requestID"] in valid_requests, "ERROR Line [%d]: Invalid request ID [%s]" % (line_num, element["requestID"])
        found_requests.add(element["requestID"])

    missing_requests = valid_requests.difference(found_requests)
    if len(missing_requests) > 0:
        print("Your submission is missing data for:")
        for missing_element in missing_requests:
            print("\t", missing_element)

        entered = input("\nIs this acceptable? [Y/n] ")
        assert entered.lower() == "y", "ERROR: Can't continue without user agreement"


    print("RequestID Check: Pass")

# *****************************************************************************
# Validate importance is a reasonable value
# *****************************************************************************
if importance_check:
    # Iterate through all elements in the submission, and ensure importance values numeric and in [0,1]
    for line_num, element in enumerate(checkable_data):
        assert element["importance"] >= 0 and element["importance"] <= 1, "ERROR Line [%d]: Invalid importance value, outside acceptable range [%f]" % (line_num, element["importance"])

    print("Importance Check: Pass")


# *****************************************************************************
# Validate information needs come from the known list
# *****************************************************************************
if info_need_check:
    query_set = {
        "CrisisFACTS-General-q001",
        "CrisisFACTS-General-q002",
        "CrisisFACTS-General-q003",
        "CrisisFACTS-General-q004",
        "CrisisFACTS-General-q005",
        "CrisisFACTS-General-q006",
        "CrisisFACTS-General-q007",
        "CrisisFACTS-General-q008",
        "CrisisFACTS-General-q009",
        "CrisisFACTS-General-q010",
        "CrisisFACTS-General-q011",
        "CrisisFACTS-General-q012",
        "CrisisFACTS-General-q013",
        "CrisisFACTS-General-q014",
        "CrisisFACTS-General-q015",
        "CrisisFACTS-General-q016",
        "CrisisFACTS-General-q017",
        "CrisisFACTS-General-q018",
        "CrisisFACTS-General-q019",
        "CrisisFACTS-General-q020",
        "CrisisFACTS-General-q021",
        "CrisisFACTS-General-q022",
        "CrisisFACTS-General-q023",
        "CrisisFACTS-General-q024",
        "CrisisFACTS-General-q025",
        "CrisisFACTS-General-q026",
        "CrisisFACTS-General-q027",
        "CrisisFACTS-General-q028",
        "CrisisFACTS-General-q029",
        "CrisisFACTS-General-q030",
        "CrisisFACTS-General-q031",
        "CrisisFACTS-General-q032",
        "CrisisFACTS-General-q033",
        "CrisisFACTS-General-q034",
        "CrisisFACTS-General-q035",
        "CrisisFACTS-General-q036",
        "CrisisFACTS-General-q037",
        "CrisisFACTS-General-q038",
        "CrisisFACTS-General-q039",
        "CrisisFACTS-General-q040",
        "CrisisFACTS-General-q041",
        "CrisisFACTS-General-q042",
        "CrisisFACTS-General-q043",
        "CrisisFACTS-General-q044",
        "CrisisFACTS-General-q045",
        "CrisisFACTS-General-q046",
        "CrisisFACTS-Accident-q001",
        "CrisisFACTS-Accident-q002",
        "CrisisFACTS-Accident-q003",
        "CrisisFACTS-Accident-q004",
        "CrisisFACTS-Accident-q005",
        "CrisisFACTS-Accident-q006",
        "CrisisFACTS-Accident-q007",
        "CrisisFACTS-Accident-q008",
        "CrisisFACTS-Accident-q009",
        "CrisisFACTS-Accident-q010",
        "CrisisFACTS-Flood-q001",
        "CrisisFACTS-Flood-q002",
        "CrisisFACTS-Hurricane-q001",
        "CrisisFACTS-Hurricane-q002",
        "CrisisFACTS-Hurricane-q003",
        "CrisisFACTS-Hurricane-q004",
        "CrisisFACTS-Hurricane-q06",
        "CrisisFACTS-Storm-q001",
        "CrisisFACTS-Storm-q002",
        "CrisisFACTS-Storm-q003",
        "CrisisFACTS-Tornado-q001",
        "CrisisFACTS-Tornado-q002",
        "CrisisFACTS-Tornado-q003",
        "CrisisFACTS-Tornado-q004",
        "CrisisFACTS-Tornado-q005",
        "CrisisFACTS-Wildfire-q001",
        "CrisisFACTS-Wildfire-q002",
        "CrisisFACTS-Wildfire-q003",
        "CrisisFACTS-Wildfire-q004",
        "CrisisFACTS-Wildfire-q005",
        "CrisisFACTS-Wildfire-q006",
    }

    # Iterate through all elements in the submission, and ensure informationNeeds comes from the list of valid queries
    for line_num, element in enumerate(checkable_data):
        # element["informationNeeds"] is optional so could be omitted or empty
        if "informationNeeds" not in element or len(element["informationNeeds"]) == 0:
            continue

        unknown_quries = set(element["informationNeeds"]).difference(query_set)
        assert len(unknown_quries) == 0, "ERROR: Unknown query in information needs field: [%s]" % ",".join(unknown_quries)

    print("Query Check: Pass")

# *****************************************************************************
# Validate sources  is a reasonable value
# *****************************************************************************
if sources_check:
    import re

    source_format_tfn = re.compile("CrisisFACTS-[0-9]+-(Twitter|Facebook|News)-[0-9]+-[0-9]+")
    source_format_reddit = re.compile("CrisisFACTS-[0-9]+-Reddit-s?[0-9]+-([0-9]+|c?[0-9]+-[0-9]+)")
    
    # Iterate through all elements in the submission, and ensure sources conform to the appropriate format
    for line_num, element in enumerate(checkable_data):
        for source in element["sources"]:
            assert source_format_tfn.match(source) or source_format_reddit.match(source), "ERROR Line [%d]: Invalid source [%s]" % (line_num, source)

    print("Sources Check: Pass")

print("Success! Passed all tests.")