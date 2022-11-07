from python.benchmarks.comparison.src.cbm.cbm_ctnode import CBMMakespanCTNode
from python.benchmarks.comparison.src.cbm.cbm_grid import CBMGrid
from python.benchmarks.comparison.src.cbm.cbm_high_level import CBMHighLevelSolver
from python.benchmarks.comparison.src.cbm.ssp.cbm_ssp_low_level import CBMSSPLowLevelSolver
from python.benchmarks.comparison.src.solver import Solver


class CBMSSPSolver(Solver):
    Grid = CBMGrid
    LowLevelSolver = CBMSSPLowLevelSolver
    CTNode = CBMMakespanCTNode
    HighLevelSolver = CBMHighLevelSolver

    @staticmethod
    def get_name() -> str:
        return "R.CBM.SSP"
