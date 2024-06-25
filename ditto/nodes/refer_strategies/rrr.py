from typing import Set

from ditto.blockdag import TypeAlias
from ..referIface import ReferIface


# Test for interface, useless.

class RRR(ReferIface):

    def get_virtual_new_height(self) -> TypeAlias.BlockHeight:
        pass

    def get_virtual_pivot_ref(self) -> TypeAlias.BlockID | None:
        pass

    def get_virtual_common_refs(self) -> Set[TypeAlias.BlockID]:
        pass
