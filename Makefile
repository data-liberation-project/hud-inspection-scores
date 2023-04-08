
REMS_URL=https://www.hud.gov/program_offices/housing/mfh/rems/remsinspecscores/remsphysinspscores
PIS_URL=https://www.huduser.gov/portal/datasets/pis.html
FETCHED=data/fetched
CONVERTED=data/converted
OUTPUT=data/output

XLS_FILES := $(wildcard ${FETCHED}/*)
JSONL_FILES := $(patsubst ${FETCHED}/%, ${CONVERTED}/%-1.jsonl, $(XLS_FILES))

OUTPUT_JSONL=${OUTPUT}/hud-properties.jsonl ${OUTPUT}/hud-inspections.jsonl


help:
	@echo 'Run these commands separately and in order:'
	@echo '  make download'
	@echo '  make parse'
	@echo '  make combine'
	@echo '  make package'

download:  # download any missing .xls/x files
	PYTHONPATH=. scripts/get-matching-links.py ${PIS_URL} .xls .xlsx | PYTHONPATH=. scripts/download-urls.py ${FETCHED}/
	PYTHONPATH=. scripts/get-matching-links.py ${REMS_URL} .xls .xlsx | PYTHONPATH=. scripts/download-urls.py ${FETCHED}/

parse: $(JSONL_FILES)

combine: ${OUTPUT_JSONL}

package: ${OUTPUT}/hud-inspections.jsonl.zip ${OUTPUT}/hud-inspections.csv.zip

${OUTPUT_JSONL}: ${JSONL_FILES}
	PYTHONPATH=. scripts/hud2dlp.py ${CONVERTED}/*.jsonl

${OUTPUT}/hud-inspections.%.zip: ${OUTPUT}/hud-properties.% ${OUTPUT}/hud-inspections.%
	zip $@ $^

${CONVERTED}/%-1.jsonl: ${FETCHED}/%
	PYTHONPATH=. scripts/xls2jsonl.py $<

%.csv: %.jsonl
	PYTHONPATH=. scripts/tocsv.py $< > $@

clean:
	rm -f ${CONVERTED}/* ${OUTPUT}/* data/aux/*

.PRECIOUS: ${JSONL_FILES} ${OUTPUT_JSONL}

.PHONY: clean download
