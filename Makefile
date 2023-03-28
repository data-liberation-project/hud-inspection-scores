
REMS_URL=https://www.hud.gov/program_offices/housing/mfh/rems/remsinspecscores/remsphysinspscores
PIS_URL=https://www.huduser.gov/portal/datasets/pis.html
RAWDATADIR=raw/

XLS_FILES := $(wildcard raw/*.xls)
XLSX_FILES := $(wildcard raw/*.xlsx)
JSONL_FILES := $(patsubst %.xls, %.jsonl, $(XLS_FILES))
JSONL_FILES += $(patsubst %.xlsx, %.jsonl, $(XLSX_FILES))

all: download commit parse transform

download:  # download any missing .xls/x files
	scripts/get-matching-links.py ${PIS_URL} .xls .xlsx | scripts/download-urls.py ${RAWDATADIR}/
	scripts/get-matching-links.py ${REMS_URL} .xls .xlsx | scripts/download-urls.py ${RAWDATADIR}/

parse: $(JSONL_FILES)

transform:
	scripts/hud2dlp.py raw/*.jsonl

commit:
	git add ${RAWDATADIR}/*.xls*
	git commit -m 'new downloads'


%.jsonl: %.xls
	scripts/xls2jsonl.py $<

%.jsonl: %.xlsx
	scripts/xls2jsonl.py $<

clean:
	rm -f raw/*.jsonl raw/*.jsonl hud-*.jsonl
