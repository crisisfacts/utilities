# Scoring Summaries

This directory does the heavy lifting for evaluation. The main scripts participants should care about the three `00-*.ipynb` notebooks, as these three perform the main scoring functions against NIST assessors (`00-AssessorScoring.ipynb`), using BERTScore (`00-AutoSummaryScoring.BERTScore.ipynb`), and using ROUGE (`00-AutoSummaryScoring.Rouge.ipynb`).

## Required Files

To run these scripts, you need several files that have been provided:

- `collapsed-event-days` directory, which contains the list of facts for each request ID and the associated raw facts from submissions. 
    - If you are a participant and want to run your new submission against NIST assessors, you can modify files here to include your new submitted facts in the `relevant_facts` field for a given `collapsed_fact_id`.

- `submissions` directory, which contains submissions in the CrisisFACTS gzipped, newline-delimited JSON format (see `02-Checker/checker.py` for format guidance). 
    - You can put new submissions here to have them scored against the ROUGE and BERTScore summaries.

- `submissions.csv`, which contains metadata for submitted runs.

- `final-annotated-facts-results.json`, which contains the summaries, NIST assessor annotations, and fact IDs for each request-ID/event-day pair.

- `CrisisFACTs-2022to2023.topics.withSummaries.json`, which contains the CrisisFACTS events (i.e., topics) and their event-wide summaries.
