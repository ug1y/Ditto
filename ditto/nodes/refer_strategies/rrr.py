from ditto.blockdag import BlockDAG
from referIface import ReferIface


# Test for interface, useless.

class RRR(ReferIface):

    def get_virtual_pivot_ref(self) -> BlockDAG.BlockID | None:
        pass

    def get_virtual_common_refs(self) -> set[BlockDAG.BlockID]:
        pass
