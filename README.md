# HUD inspection scores

HUD publishes [public housing inspection scores in a .xls file (Excel spreadsheet)]([https://www.hud.gov/program_offices/housing/mfh/rems/remsinspecscores/remsphysinspscores).

This script parses one of these files and generates JSONL, structured as a single table, such that multiple overlapping datasets can be concatenated and deduped with simple text tools.

## Usage

```
    ./hud2jsonl.py MF_InspectionReport.xls
```
