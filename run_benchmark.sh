#!/bin/bash

# PYTHONPATH=$(pwd):$PYTHONPATH python3.9 python/benchmarks/comparison_75percent_3teams.py | tee benchmark_output.txt


# JESSE_DIR=/home/jesse/Documents/GitProjects/research-project
JONA_DIR=/data/BCP-paper
PYTHONPATH=$JONA_DIR:$PYTHONPATH python3.9 $JONA_DIR/python/benchmarks/main.py | tee comparison_25percent_1teams.txt
