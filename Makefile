.PHONY: test benchmark-index benchmark-showcase benchmark-all

test:
	python3 tools/run_tests.py

benchmark-index:
	python3 tools/benchmark_rdt_index.py

benchmark-showcase:
	python3 tools/run_showcase.py

benchmark-all:
	python3 tools/run_showcase.py
	python3 tools/benchmark_rdt_index.py
