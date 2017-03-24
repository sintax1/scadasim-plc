init:
	pip install -r requirements.txt

test:
	py.test tests

run:
	python scadasim_plc/plc.py

.PHONY: init test run
