from mmapf_client import MapfwBenchmarker

def test():
    pass

if __name__ == '__main__':
    benchmarker = MapfwBenchmarker(
        "<YOUR API TOKEN>",
        0, # <BENCHMARK INDEX>,
        "<YOUR ALGORITHMS NAME>",
        "<YOUR ALGORITHMS VERSION>",
        True, #<DEBUG_MODE>,
         solver=test, #<SOLVER>,
         cores=6, #<CORES>
    )
    benchmarker.run()

