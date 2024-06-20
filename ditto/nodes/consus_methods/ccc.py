from consusIface import ConsusIface, StatusType
from ditto.blockdag import BlockDAG


# Test for interface, useless.

class CCC(ConsusIface):

    def get_block_status(self, bid) -> StatusType:
        pass

    def get_decided_blocks(self) -> set[BlockDAG.BlockID]:
        pass

    def sort_finished_blocks(self, filter_decided: bool = True) -> list[BlockDAG.BlockID]:
        pass
