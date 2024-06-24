from ditto.blockdag import Block, BlockDAG, DAGType
from ..referIface import ReferIface


class SimpleRef(ReferIface):
    """
    Reference all leaves of the blockDAG.

    Only for divergence blockDAG.
    """

    def __init__(self, blockdag: BlockDAG):
        super().__init__(blockdag)
        if self.blockdag.get_graph_type() != DAGType.DIVERGENCE:
            raise ValueError("Only for divergence blockDAG.")

    def get_virtual_pivot_ref(self) -> Block.BlockID | None:
        return None

    def get_virtual_common_refs(self) -> set[Block.BlockID]:
        return self.blockdag.get_leaves_blocks().copy()

    def get_virtual_new_height(self) -> Block.BlockHeight:
        leaves = self.blockdag.get_leaves_blocks()
        return max(self.blockdag[lid].height for lid in leaves) + 1
