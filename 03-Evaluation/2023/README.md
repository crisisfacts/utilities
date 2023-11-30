# Evaluation Code for CrisisFACTS 2023

The directories here provide the framework for evaluation in CrisisFACTS 2023. This framework has three steps:

1. Merge runs submitted by CrisisFACTS participants into summaries that NIST assessors can evaluate (see `00-createSummaries`).

2. Take assessor span labels, combine them across assessors, and join them with the collapsed fact information to produce a list of labeled collapsed facts. This process produces the `final-annotated-facts-results.json` file that has the summaries, fact IDs, and assessor labels (see `01-mergeAnnotations`).

3. Combine assessor labels with collapsed-fact IDs and the collapsed-to-run fact-ID maps to perform scoring (see `02-scoreSubmissions`).

## Track Organizers vs. Participants

Much of this code is developed for track organizers to consume run submissions,  produce content for NIST assessors, and score runs. 

If you are a participant, you need only pay attention to step 3. For new submissions, you can match your submitted facts to the collapsed-fact data present in `collapsed-event-days`.