# Creating Summaries from Submissions

This folder contains scripts for merging participant runs into summaries that will be manually assessed by NIST assessors.

__NOTE__: Participants need not run the code in this directory. We maintain this code here for future track organizers who want to replicate our evaluation methodology.

## Generating Event-Day Summaries

The scripts below, run in order, will produce a directory of daily summaries needed for NIST assessment.

### Prerequisite Files

To run the scripts below, you need the following files:

- `metadata` : A text file of colon-separated fields that NIST produces as part of the run-submission process.

- `event_data.json` : A JSON file listing all the request IDs for events in CrisisFACTS 2023.

### Scripts

- `00-GenerateRunData.ipynb` : This notebook converts the NIST-provided submission metadata (`run.metadata.tsv`) in the `submissions.csv` file, which contains metadata associated with each submitted run. This metadata includes run tag, team, descriptions of how the submission operates (e.g., how it calculates importance, which platforms it uses, etc), and priority. We use this submissions file to determine which runs to include in manual evaluation, as we only include submissions with priority <= 2.

- `01-Merger.ipynb` : This notebook selects runs to include from `submissions.csv` via the `priority` column and merges facts from all relevant runs into a common set of files for each request-id/event-day pair. We will use these files to de-duplicate submitted facts in the next step. For each included run, we group facts by request-id (again, event-day pair) and copy these facts to a single file all facts from all included submissions that are produced for this request-id. After running this script, we have an `event-day` directory with one file for each request-id, and each file contains all submitted facts from all included runs for that event-day.

- `02-Deduplicate.ipynb` : For pooling, we need to de-duplicate similar facts across all submitted runs. This notebook handles this de-duplication using BERTScore to identify similar facts. In prior years, we de-duplicated using `streamID` from the CrisisFACTS data, but this approach is problematic for abstractive runs. We consider two facts as duplicates if they have a BERTScore > some threshold (0.91 for CrisisFACTS 2023). We then merge these duplicate facts into a collapsed meta-fact, where the text of the meta-fact is the text most similar to its neighboring facts and importance is the maximum importance across all neighboring facts. We chose "maximum" here to ensure that a run composed of facts that many other systems ranked as low importance still get included in the resulting dataset (i.e., if we used average importance, a run that returned facts that other runs tagged as low importance would potentially be excluded from evaluation).

- `03-collapsedFacts2Prodigy.py` : After de-duplicating facts into our collapsed-fact set, we use this script to merge these facts into a summary in the format that [Prodi.gy](https://prodi.gy/) understands. This script produces a single file for every CrisisFACTS event, and each document in this file is a summary for a request-id/event-day pair. This script takes as input 1) the prefix to the directory of collapsed facts per request-id (e.g., `collapsed-event-days`), 2) the `event_data.json` file that lists all request IDs, 3) an output prefix for a directory to store the collapsed summaries in Prodi.gy format, and 4) a meta-data file that maps spans in the Prodi.gy format to the collapsed facts we have constructed.

## Loading Prodi.gy

Once we have created the `collapsed-event-days-summaries.k=512` directory and `collapsed-event-days-summaries.k=512.meta.json` file, you can use the Prodi.gy `spans.manual` recipe to load them into the Prodi.gy interface. We use the following:

    $ prodigy spans.manual crisisfacts001 blank:en ./collapsed-event-days-summaries.k=512/CrisisFACTS-001.jsonl --label USEFUL_FACT,REDUNDANT_FACT,POOR_FACT,LAGGED_FACT

You would run this command for each event summary file. Assessors then can access the web instance for a single event and can annotate all event-day pairs in that event.
