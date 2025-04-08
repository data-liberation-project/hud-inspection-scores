# HUD Inspection Scores Scraper

This repository aims to extract and collect data published by the [US Department of Housing and Urban Development](https://www.hud.gov/). 

Some examples of reports published include: 
- [Public Housing Inspection Scores in a .xls file (Excel spreadsheet)]([https://www.hud.gov/program_offices/housing/mfh/rems/remsinspecscores/remsphysinspscores).
    - Last updated: February 2025
- [Historical Physical Inspection Scores with Location Information)](https://www.huduser.gov/portal/datasets/pis.html)
	- Last updated: March 2021
- [Assorted HUD Multifamily Data](https://www.hud.gov/program_offices/housing/mfh/mfdata)
	- Last updated: February 2025

Scripts download the original Excel spreadsheets, parse the files, and generate a JSONL, a file format where each line contains a JSON object. This file format allows for multiple overlapping datasets to be concatenated and deduped with simple text tools.

## Running the Code Yourself
- Ensure you have Python 3 installed
- From this repository, run `python3 -m venv virtual_env` to create its virtual environment
- Run `. virtual_env/bin/activate` to activate the virtual environment
- Run pip install -r requirements.txt to install the necessary Python libraries

- To download new data files from HUD:
```
  make download    # download new raw .xls files, if any (20s)
  make parse       # parse from .xls/x to .jsonl (100s)
  make combined    # combine all .jsonl into toplevel jsonl (200s)
  make package     # generate .jsonl.zip and .csv.zip

```

## Data Folder

In the [data/fetched folder](https://github.com/data-liberation-project/hud-inspection-scores/tree/stable/data/fetched), you can find the raw HUD files. The majority are Excel spreadsheets. Filenames start with the reported last-modified date from the http response headers.

In the [data/converted folder](https://github.com/data-liberation-project/hud-inspection-scores/tree/stable/data/converted), you can find the HUD files, now converted to JSONL files. 

In the [data/output folder](https://github.com/data-liberation-project/hud-inspection-scores/tree/stable/data/output), the data has all been combined and normalized into two tables, so it's easy to take any slice of the unified data over time and/or geography and plug it directly into your favorite analysis tool:
1. `hud-properties.jsonl` with a unique key `property_id`
2. `hud-inspections.jsonl`, such that (`property_id`, `date`) identifies a unique inspection row

### Investigating Discrepancies

The recorded attributes of these public house and multifamily properties fluctuate over time, and in fact the scores for inspections *in the past* sometimes change from release to release, in ways both major and minor.

Where the values are different, we always use the most recent value, assuming good faith from the data providers and an overall tendency towards greater accuracy.

To facilitate direct investigation of these discrepancies, `make combine` also generates two `diffs` files, `hud-properties-diffs.jsonl` and `hud-inspections-diffs.jsonl`. These files have the following structure:

|origin                |attr   |oldvalue  |newvalue  |inspection\_id |property\_id |date        |score  |
|----------------------|-------|----------|----------|---------------|-------------|------------|-------|
|2020\-09\-18\-multifami|score  |53b       |53        |651883         |800019065    |2020\-02\-25|53     |
|2020\-09\-30\-mf\_inspec|score  |53        |64b       |651883         |800019065    |2020\-02\-25|64b    |
|2021\-04\-09\-multifami|score  |64b       |64        |651883         |800019065    |2020\-02\-25|64     |

With these files, discrepancies can be traced all the way back to the original downloaded resources (`origin` is the filename in the `raw/` directory).

To see all values and their origins within the output data itself (which can be handy to capture all the changes for a particular property over time), set `opt_keep_diffs=True` at the top of `hud2dlp.py`.

### Notes on the Data
- The [data/fetched folder](https://github.com/data-liberation-project/hud-inspection-scores/tree/stable/data/fetched) does not comprise the complete historical record of files uploaded by HUD to the tracked webpages. Some years do not have any associated files.
- Rows that have `pha_name` (Public Housing Authority name) are from the public housing data; rows without `pha_name` are from the multifamily data.
- The coding changed in 2020, so 80% of scores are non-numeric (like `69d*`).
- `location_quality` is from HUD; it refers to the geocoding for (lat,long) coordinates, which may be quite far from the actual site.
- Removed ~550 completely empty inspections; additional 4% have an `inspection_id` and a score of either 0 or 100, while the rest were completely empty.
- `_origins` is a list of filename prefixes that add or change data fields for a property or an inspection.

## Contributors
Many thanks to the following contributors: 
- @saulpw
- @anjakefala

## Licensing 
This repository's code is available under the MIT License terms. The raw data files (in data/fetched) and PDFs are public domain. All other data files are available under Creative Commons' CC BY-SA 4.0 license terms.

## Questions? 
File an issue in this repository. 