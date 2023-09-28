# LMD
Music- and Lyrics-driven Dance Synthesis

## Data Preparation Pipeline
- Contains modified EasyMocap module, data needs to be downloaded separately (refer to EasyMocap repository)
- 1_DOWNLOAD.py, ..., 5_LOAD.py: scripts for producing data, refer to the report
- JD2020_url.json: used by 1_DOWNLOAD.py to generate JD2020.json
- LMD_Dataset.py: the dataset class, takes in or create ...Dict.pt and ...indexing.json

## Songs_...
For the moment, only Songs_2020, Songs_2021 and Songs_2022 have the up-to-date dataformat (same as in the Dataset repository)
