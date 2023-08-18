#!/runs/bin/venv/bin/python

import sys
import json
import logging
import argparse
from pathlib import Path

ap = argparse.ArgumentParser(description='Check a CrisisFACTs run for correctness.',
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument('--files', '-f',
                help='Location of requests files',
                default='/runs/aux/crisis')
ap.add_argument('--no_reqid_check',
                action='store_false',
                help='Should we skip the requestID check? (default: no)')
ap.add_argument('runfile',
                help='Run file to check')
args = ap.parse_args()

# Configure which checks to run
#  NOTE: Format checking always happens
requestId_check = args.no_reqid_check

logging.basicConfig(filename=f'{args.runfile}.errlog',
                    level=logging.DEBUG)

# Catch assertion failures and log them to the errlog
def excepthook(exctype, value, traceback):
    if issubclass(exctype, AssertionError):
        logging.getLogger().error(value)
        sys.exit(255)
    else:
        sys.__excepthook__(exctype, value, traceback)

sys.excepthook = excepthook

in_file_path = args.runfile
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
        "008" # Hurricane Sally 2020
    ]

    valid_requests = set()
    for event_number in event_list:
        file_loc = Path(args.files) / f'CrisisFACTS-{event_number}.requests.json'

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
    assert len(missing_requests) == 0, "ERROR: Submission file is missing responses for the following requests: " + ",".join(missing_requests)

    print("RequestID Check: Pass")



# TODO: Validate importance is reasonable
# TODO: Validate elements in sources and information needs are reasonable


print("Success! Passed all tests.")