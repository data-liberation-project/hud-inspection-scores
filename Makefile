
REMS_URL=https://www.hud.gov/program_offices/housing/mfh/rems/remsinspecscores/remsphysinspscores
PIS_URL=https://www.huduser.gov/portal/datasets/pis.html
FETCHED=data/fetched
WORKING=data/converted
OUTPUT=data/output

XLS_FILES := $(wildcard ${FETCHED}/*)
JSONL_FILES := $(patsubst ${FETCHED}/%, ${WORKING}/%-1.jsonl, $(XLS_FILES))

OUTPUT_JSONL=${OUTPUT}/hud-properties.jsonl ${OUTPUT}/hud-inspections.jsonl


help:
	@echo 'These targets will run the pipeline in order:'
	@echo '  make download'
	@echo '  make parse'
	@echo '  make combined'
	@echo '  make package'

download:  # download any missing .xls/x files
	scripts/get-matching-links.py ${PIS_URL} .xls .xlsx | scripts/download-urls.py ${FETCHED}/
	scripts/get-matching-links.py ${REMS_URL} .xls .xlsx | scripts/download-urls.py ${FETCHED}/

parse: $(JSONL_FILES)

combined: ${OUTPUT_JSONL}

package: ${OUTPUT}/hud-inspections.jsonl.zip ${OUTPUT}/hud-inspections.csv.zip

${OUTPUT_JSONL}: ${JSONL_FILES}
	mkdir -p ${OUTPUT}
	scripts/hud2dlp.py $^

${OUTPUT}/hud-inspections.%.zip: ${OUTPUT}/hud-properties.% ${OUTPUT}/hud-inspections.%
	zip $@ $^

${WORKING}/%-1.jsonl: ${FETCHED}/%
	mkdir -p ${WORKING}
	scripts/xls2jsonl.py ${WORKING}/ $<

%.csv: %.jsonl
	scripts/tocsv.py $< > $@

clean:
	rm -f ${WORKING}/* ${OUTPUT}/*

.PRECIOUS: ${JSONL_FILES} ${OUTPUT_JSONL}

.PHONY: clean download
