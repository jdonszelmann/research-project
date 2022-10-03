from src.ctnode import CTNode


class CBMMakespanCTNode(CTNode):
    def update_costs(self) -> None:
        self.cost = max(self.cost, self.full_solution.get_cost())
