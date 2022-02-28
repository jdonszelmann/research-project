#!/bin/bash

# PYTHONPATH=$(pwd):$PYTHONPATH python3.9 python/benchmarks/comparison_75percent_3teams.py | tee benchmark_output.txt


JESSE_DIR=/home/jesse/Documents/GitProjects/research-project

# PYTHONPATH=$JONA_DIR:$PYTHONPATH python3.9 $JONA_DIR/python/benchmarks/comparison_25percent_3teams.py | tee benchmark_output_25_3.txt
PYTHONPATH=$JESSE_DIR:$PYTHONPATH python3.9 $JESSE_DIR/python/benchmarks/comparison_75percent_3teams.py | tee benchmark_output_75_3.txt
# PYTHONPATH=$JONA_DIR:$PYTHONPATH python3.9 $JONA_DIR/python/benchmarks/extensions_25percent_1teams.py | tee benchmark_output.txt

#PYTHONPATH=$JONA_DIR:$PYTHONPATH python3.9 $JONA_DIR/python/benchmarks/paper/map_size_inmatch.py | tee benchmark_output.txt
