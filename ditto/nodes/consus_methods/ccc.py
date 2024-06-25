from typing import Set, List

from ditto.blockdag import TypeAlias
from ..consusIface import ConsusIface, StatusType


# Test for interface, useless.

class CCC(ConsusIface):

    def get_block_status(self, bid) -> StatusType:
        pass

    def get_decided_blocks(self) -> Set[TypeAlias.BlockID]:
        pass

    def sort_finished_blocks(self, filter_decided: bool = True) -> List[TypeAlias.BlockID]:
        pass
