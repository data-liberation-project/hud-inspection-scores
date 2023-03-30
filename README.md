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

    make download   # download new raw .xls files, if any
    make commit     # commit raw data
    make parse      # parse from .xls/x to .jsonl
    make combine    # combine all .jsonl into toplevel hud-properties.jsonl and hud-inspections.jsonl
    make package    # generate .jsonl.zip and .csv.zip
