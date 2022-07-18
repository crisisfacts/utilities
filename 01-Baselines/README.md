# Baseline CrisisFACTS Implementations

This repository contains simple baseline implementations for the CrisisFACTS track.

Currently, we support the following baselines:

- `00-SimplePyTerrierBaseline.ipynb` - This baseline uses the [PyTerrier](https://pyterrier.readthedocs.io/) information retrieval platform to match social media/news content to the CrisisFACTS queries. Using this library, we produce two extractive summarization methods for scoring the `importance` of relevant content: Our first method 1) counts the number of queries a message matches, and the second 2) takes the of sum each message's relevance scores across all queries. We then produce two files from this baseline for submission.

