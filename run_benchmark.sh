#!/bin/bash

# PYTHONPATH=$(pwd):$PYTHONPATH python3.9 python/benchmarks/comparison_75percent_3teams.py | tee benchmark_output.txt


# JESSE_DIR=/home/jesse/Documents/GitProjects/research-project
JONA_DIR=/home/jdonszelmann/rp

PYTHONPATH=$JONA_DIR:$PYTHONPATH python3.9 $JONA_DIR/python/benchmarks/comparison/main.py | tee main.txt
# PYTHONPATH=$JESSE_DIR:$PYTHONPATH python3.9 -u $JESSE_DIR/python/benchmarks/comparison_75percent_3teams.py | tee benchmark_output_75_3.txt
# PYTHONPATH=$JONA_DIR:$PYTHONPATH python3.9 $JONA_DIR/python/benchmarks/extensions_25percent_1teams.py | tee benchmark_output.txt

#PYTHONPATH=$JONA_DIR:$PYTHONPATH python3.9 $JONA_DIR/python/benchmarks/paper/map_size_inmatch.py | tee benchmark_output.txt
