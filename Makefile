.PHONY: all collect report test

all: collect report

collect:
	python3 src/report.py collect

report:
	python3 src/report.py render

test:
	python3 -m unittest discover -s tests
