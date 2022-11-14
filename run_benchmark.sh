#!/bin/bash

# PYTHONPATH=$(pwd):$PYTHONPATH python3.9 python/benchmarks/comparison_75percent_3teams.py | tee benchmark_output.txt


# JESSE_DIR=/home/jesse/Documents/GitProjects/research-project
PYTHONPATH=python3.9 python/benchmarks/main.py | tee comparison_25percent_1teams.txt