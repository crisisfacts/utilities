#!/usr/bin/env python
import numpy as np
import json
import glob
import gzip


extractive_pool_depth = 16
abstractive_pool_depth = 16




with open("CrisisFACTs-2022.facts.json", "r") as in_file:
    facts = json.load(in_file)

event_request_fact_count_map = {}

total_fact_count = 0
for event in facts:
    event_name = event["event"]
    event_id = event["eventID"]
    event_requests = event["summaryRequests"]
    event_factsXrequests = event["factsByRequest"]

    print(event_id, event_name)
    for event_request in event_requests:
        req_id = event_request["requestID"]        
        this_req_facts = event_factsXrequests[req_id]
        fact_count = len(this_req_facts)
        fact_collection = [fact["fact"] for fact in this_req_facts]
        
        print("\t", req_id, fact_count)
        event_request_fact_count_map[req_id] = fact_count



def construct_pools(event_request_fact_list, pool_depth):
    event_request_pools = {}
    
    for event_request,candidate_pool in event_request_fact_list.items():
        print(event_request)
        print("\t", "Candidate Count:", len(candidate_pool))

        fact_rows = []
        for fact_stream_id,fact_entries in candidate_pool.items():
            max_import = np.mean([fact["importance"] for fact in fact_entries])
            fact_rows.append((fact_stream_id, max_import))

        sorted_facts = sorted(fact_rows, key=lambda f: f[1], reverse=True)
        pooled_facts = [
            {"stream_id": f_id, "rank": f_rank, "importance": f_import, "matches":len(candidate_pool[f_id]), "entries": candidate_pool[f_id]} 
            for f_rank,(f_id,f_import) in enumerate(sorted_facts[:pool_depth])
        ]

        event_request_pools[event_request] = pooled_facts
        print("\t", "Pool Size:", len(pooled_facts))
        
    return event_request_pools



# Take the top-k facts from each run and each event-request pair per run
#. We also merge facts based on their streamID to keep track of facts
#. multiple systems have returned
event_request_fact_list = {k:{} for k in event_request_fact_count_map.keys()}
for f in glob.glob("to.pool.extractive/*.json.gz"):
    
    this_run_id = f.partition("/")[-1].replace(".json.gz", "")
    print(f, "-->", this_run_id)
    
    this_run_event_request_facts = {k:[] for k in event_request_fact_count_map.keys()}
    with gzip.open(f, "r") as in_file:
        for line_ in in_file:
            line = line_.decode("utf8")
            
            entry = json.loads(line)
            
            this_run_event_request_facts[entry["requestID"]].append(entry)
            
    for event_request,this_fact_list in this_run_event_request_facts.items():
        sorted_fact_list = sorted(this_fact_list, key=lambda v: v["importance"], reverse=True)
        
        this_event_request_k = event_request_fact_count_map[event_request]
        for this_top_fact in sorted_fact_list[:this_event_request_k]:

            this_stream_id = this_top_fact["streamID"]
            assert this_stream_id is not None
            
            event_request_stream_pool = event_request_fact_list[event_request].get(this_top_fact["streamID"], [])
            
            this_top_fact["_internal_run_id"] = this_run_id
            event_request_stream_pool.append(this_top_fact)
            
            event_request_fact_list[event_request][this_top_fact["streamID"]] = event_request_stream_pool
            
            
            
event_request_pools = construct_pools(event_request_fact_list, pool_depth=extractive_pool_depth)

total_pool_size = sum([len(v) for v in event_request_pools.values()])
print("Total Pool Size:", total_pool_size)


with open("extractive_pools.depth=%d.json" % extractive_pool_depth, "w") as out_file:
    json.dump(event_request_pools, out_file)
    
    





# Take the top-k facts from each run and each event-request pair per run
#. We also merge facts based on exact match of text to keep track of facts
#. multiple systems have returned

event_request_fact_list_abstractive = {k:{} for k in event_request_fact_count_map.keys()}
for f in glob.glob("to.pool.abstractive/*.json.gz"):
    
    this_run_id = f.partition("/")[-1].replace(".json.gz", "")
    print(f, "-->", this_run_id)
    
    this_run_event_request_facts = {k:[] for k in event_request_fact_count_map.keys()}
    with gzip.open(f, "r") as in_file:
        for line_ in in_file:
            line = line_.decode("utf8")
            
            entry = json.loads(line)
            
            this_run_event_request_facts[entry["requestID"]].append(entry)
            
    for event_request,this_fact_list in this_run_event_request_facts.items():
        sorted_fact_list = sorted(this_fact_list, key=lambda v: v["importance"], reverse=True)
        
        this_event_request_k = event_request_fact_count_map[event_request]
        for this_top_fact in sorted_fact_list[:this_event_request_k]:
            
            fact_id = hash(this_top_fact["factText"].lower())
            event_request_stream_pool = event_request_fact_list_abstractive[event_request].get(fact_id, [])
            
            this_top_fact["_internal_run_id"] = this_run_id
            event_request_stream_pool.append(this_top_fact)
            
            event_request_fact_list_abstractive[event_request][fact_id] = event_request_stream_pool
            

event_request_pools_abstractive = construct_pools(event_request_fact_list_abstractive, pool_depth=abstractive_pool_depth)
total_pool_size = sum([len(v) for v in event_request_pools_abstractive.values()])
print("Total Pool Size:", total_pool_size)


with open("abstractive_pools.depth=%d.json" % abstractive_pool_depth, "w") as out_file:
    json.dump(event_request_pools_abstractive, out_file)
    


