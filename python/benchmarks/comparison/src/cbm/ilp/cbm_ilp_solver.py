from python.benchmarks.comparison.src.cbm.cbm_ctnode import CBMMakespanCTNode
from python.benchmarks.comparison.src.cbm.cbm_grid import CBMGrid
from python.benchmarks.comparison.src.cbm.cbm_high_level import CBMHighLevelSolver
from python.benchmarks.comparison.src.cbm.ilp.cbm_ilp_low_level import CBMILPLowLevelSolver
from python.benchmarks.comparison.src.solver import Solver


class CBMILPSolver(Solver):
    Grid = CBMGrid
    LowLevelSolver = CBMILPLowLevelSolver
    CTNode = CBMMakespanCTNode
    HighLevelSolver = CBMHighLevelSolver

    @staticmethod
    def get_name() -> str:
        return "R.CBM.ILP"
