import re
import sys
import glob
import json
import pandas as pd

in_path_pre = sys.argv[1]
event_data_path = sys.argv[2]
out_path_pre = sys.argv[3]
meta_path = sys.argv[4]

# Read Event Data
event_data = {}
with open(event_data_path, "r") as in_file:
    event_data = json.load(in_file)

# open the files associated with this request ID
daily_fact_list_dfs = []
events = {k.partition("-r")[0] for k in event_data.keys()}
for event_id in sorted(events):
    print(event_id)

    summaries = []
    pattern = "%s/Collapsed-%s-*.json" % (in_path_pre, event_id)
    print("\t", pattern)
    for in_file_path in glob.glob(pattern):
        request_id = in_file_path\
            .rpartition("/")[-1]\
            .replace("Collapsed-", "")\
            .replace(".json", "")
        with open(in_file_path, "r") as in_file:

            fact_list = json.load(in_file)
            fact_list_df = pd.DataFrame(fact_list)
            fact_list_df["request_id"] = request_id
            fact_list_df["event_id"] = event_id

            daily_fact_list_dfs.append(fact_list_df)

# create the dataframe of all facts
entries_df = pd.concat(daily_fact_list_dfs)

# whitespace regex for cleaning up summaries
ws_re = re.compile("\s+")

per_request_meta = {}
per_request_summaries = []
for request_id, group in entries_df.groupby("request_id"):

    header_text = event_data[request_id]
    summary_text = "[%s - %s]\n" % (request_id, header_text)
    spans_list = []
    spans_facts = []
    last_span_start = len(summary_text)

    for idx, this_row in group.sort_values(by="importance").iterrows():
        fact_text = this_row["fact_text"] + ". "
        fact_text = ws_re.sub(" ", fact_text)
        summary_text += fact_text

        new_span_end = last_span_start+len(fact_text)
        spans_list.append((last_span_start, new_span_end))
        last_span_start = new_span_end

        spans_facts.append(this_row["collapsed_fact_id"])

    per_request_summaries.append({
        "title": request_id,
        "text": summary_text,
        "meta": {
            "request_id": request_id,
        }
    })

    per_request_meta[request_id] = {
        "text": summary_text,
        "meta": {
            "spans_list": spans_list,
            "spans_facts": spans_facts,
        }
    }

request_ids_file_map = {}
for event_id in sorted(events):
    request_ids_file_map[event_id] = open("%s/%s.jsonl" % (out_path_pre, event_id), "w")


# Sorting request IDs
def req_id_sorter(req_id):
    index = int(req_id.rpartition("-")[-1].replace("r",""))
    return index
per_request_summaries_sorted = sorted(per_request_summaries, key=lambda x: req_id_sorter(x["meta"]["request_id"]))


for entry in per_request_summaries_sorted:
    event_id = entry["meta"]["request_id"].rpartition("-")[0]
    request_ids_file_map[event_id].write("%s\n" % json.dumps(entry))

for f in request_ids_file_map.values():
    f.close()


with open(meta_path, "w") as out_file:
    out_file.write(json.dumps(per_request_meta))
        

