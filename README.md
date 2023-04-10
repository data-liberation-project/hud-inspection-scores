# HUD inspection scores

HUD publishes:

- [public housing inspection scores in a .xls file (Excel spreadsheet)]([https://www.hud.gov/program_offices/housing/mfh/rems/remsinspecscores/remsphysinspscores).
- [Historical Physical Inspection Scores (w/ Location Info)](https://www.huduser.gov/portal/datasets/pis.html)
- [Assorted HUD Multifamily Data](https://www.hud.gov/program_offices/housing/mfh/mfdata)

This script parses these files and generates JSONL, structured as a single table, such that multiple overlapping datasets can be concatenated and deduped with simple text tools.

## Requirements

- Python 3.7, and these external modules:
    - python-dateutil
    - BeautifulSoup
    - xlrd
    - openpyxl

## Usage

To download new data files from HUD:

    make download    # download new raw .xls files, if any (20s)
    make parse       # parse from .xls/x to .jsonl (100s)
    make combined    # combine all .jsonl into toplevel jsonl (200s)
    make package     # generate .jsonl.zip and .csv.zip

## Notes on the data

The data has all been combined and normalized into two tables:

- `properties` with a unique key `property_id`
- `inspections`, such that (`property_id`, `date`) identifies a unique inspection row

so it's easy to take any slice of the unified data over time and/or geography and plug it directly into your favorite analysis tool.

But in reality, data is never that simple.
The recorded attributes of these public house and multifamily properties fluctuate over time, and in fact the scores for inspections *in the past* sometimes change from release to release, in ways both major and minor.
Where the values are different, we always use the most recent value, assuming good faith from the data providers and an overall tendency towards greater accuracy.

## Investigating changes

To facilitate direct investigation of these discrepancies, `make combine` also generates two `diffs` jsonl files, for example:

|origin                |attr   |oldvalue  |newvalue  |inspection\_id |property\_id |date        |score  |
|----------------------|-------|----------|----------|---------------|-------------|------------|-------|
|2020\-09\-18\-multifami|score  |53b       |53        |651883         |800019065    |2020\-02\-25|53     |
|2020\-09\-30\-mf\_inspec|score  |53        |64b       |651883         |800019065    |2020\-02\-25|64b    |
|2021\-04\-09\-multifami|score  |64b       |64        |651883         |800019065    |2020\-02\-25|64     |

These discrepancies can be traced all the way back to the original downloaded resources (`origin` is the filename in the `raw/` directory).

To see all values and their origins within the output data itself (which can be handy to capture all the changes for a particular property over time), set `opt_keep_diffs=True` at the top of `hud2dlp.py`.

## Other notes

- rows that have `pha_name` (Public Housing Authority name) are from the public housing data; rows without `pha_name` are from the multifamily data.
- the coding changed in 2020, so 80% of scores are non-numeric (like `69d*`).
- `location_quality` refers to the geocoding for (lat,long) coordinates, which may be quite far from the actual site.
- removed ~550 completely empty inspections; additional 4% have an `inspection_id` and a score of either 0 or 100, while the rest were completely empty.

## About the Pipeline

- the saved filenames start with the reported last-modified date from the http response headers
