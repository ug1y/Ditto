from ditto.blockdag import BlockDAG, DAGType, Block, BlockType


class TestBlockDAG:

    def test_init(self):
        g = BlockDAG()
        assert len(g._G.nodes()) == 0
        assert len(g._G.edges()) == 0
        assert g._gtype == DAGType.DIVERGENCE
        assert g._leaves == set()
        assert g._column == list()
        assert g._logger is not None

    def test_divergence_dag(self):
        """
        Example:
            1 <- 2, 1 <- 3, 1 <- 4

            2 <- 5, 3 <- 5

            2 <- 6, 3 <- 6, 4 <- 6
        """
        g = BlockDAG(gtype=DAGType.DIVERGENCE)
        b1 = Block(bid=1, type=BlockType.GENESIS, height=1)
        g.add_block(b1)
        b2 = Block(bid=2, type=BlockType.MINED, miner="ug1y", crefs={hash(b1)}, height=2)
        g.add_block(b2)
        b3 = Block(bid=3, type=BlockType.MINED, miner="ug1y", crefs={hash(b1)}, height=2)
        g.add_block(b3)
        b4 = Block(bid=4, type=BlockType.MINED, miner="ug1y", crefs={hash(b1)}, height=2)
        g.add_block(b4)
        b5 = Block(bid=5, type=BlockType.MINED, miner="ug1y", crefs={hash(b2), hash(b3)}, height=3)
        g.add_block(b5)
        b6 = Block(bid=6, type=BlockType.MINED, miner="ug1y", crefs={hash(b2), hash(b3), hash(b4)}, height=3)
        g.add_block(b6)

        assert g.add_block(b1) is False
        b11 = Block(bid=11, type=BlockType.GENESIS, height=1)
        assert g.add_block(b11) is False

        assert set(g.get_virtual_parents()) == {5, 6}
        assert set(g.get_column_blocks(1)) == {1}
        assert set(g.get_column_blocks(2)) == {2, 3, 4}
        assert set(g.get_column_blocks(3)) == {5, 6}
        assert set(g.get_column_blocks(4)) == set()
        assert set(g.get_pivot_chain(hash(b5))) == set()

        assert set(g.ask_block(hash(b6)).get_parents()) == set(g.successors(hash(b6)))
        assert set(g.predecessors(hash(b3))) == {5, 6}
        assert g.has_path(hash(b6), hash(b3)) is True
        assert g.has_path(hash(b6), hash(b5)) is False

        assert g.cut_block(hash(b6)) is True
        assert set(g.get_virtual_parents()) == {4, 5}
        assert len(g.graph().nodes()) == 5
        assert len(g.graph().edges()) == 5
        assert g.subgraph(hash(b6)) is None
        assert set(g.subgraph(hash(b4)).nodes()) == {1, 4}
        assert set(g.subgraph(hash(b4)).edges()) == {(4, 1)}

    def test_parallel_dag(self):
        """
        Example:
            1 <= 4, 4 <= 6

            2 <= 5, 2 <- 4

            3 <- 5, 5 <- 6
        """
        g = BlockDAG(gtype=DAGType.PARALLEL)
        b1 = Block(bid=1, type=BlockType.GENESIS, height=1)
        g.add_block(b1)
        b2 = Block(bid=2, type=BlockType.GENESIS, height=1)
        g.add_block(b2)
        b3 = Block(bid=3, type=BlockType.GENESIS, height=1)
        g.add_block(b3)
        b4 = Block(bid=4, type=BlockType.MINED, miner="ug1y", pref=hash(b1), crefs={hash(b2)}, height=2)
        g.add_block(b4)
        b5 = Block(bid=5, type=BlockType.MINED, miner="ug1y", pref=hash(b2), crefs={hash(b3)}, height=2)
        g.add_block(b5)
        b6 = Block(bid=6, type=BlockType.MINED, miner="ug1y", pref=hash(b4), crefs={hash(b5)}, height=3)
        g.add_block(b6)

        assert g.add_block(b1) is False
        b11 = Block(bid=11, type=BlockType.MINED, miner="ug1y", pref=hash(b3), crefs={hash(b6)}, height=2)
        assert g.add_block(b11) is False
        b12 = Block(bid=12, type=BlockType.MINED, miner="ug1y", pref=hash(b3), crefs={hash(b6)}, height=4)
        assert g.add_block(b12) is True
        g.cut_block(hash(b12))

        assert set(g.get_virtual_parents()) == {6}
        assert set(g.get_column_blocks(1)) == {1, 2, 3}
        assert set(g.get_column_blocks(2)) == {4, 5}
        assert set(g.get_column_blocks(3)) == {6}
        assert set(g.get_column_blocks(4)) == set()
        assert set(g.get_pivot_chain(hash(b6))) == {1, 4, 6}
        assert set(g.get_pivot_chain(hash(b5))) == {2, 5}

        assert set(g.ask_block(hash(b5)).get_parents()) == set(g.successors(hash(b5)))
        assert set(g.predecessors(hash(b2))) == {4, 5}
        assert g.has_path(hash(b6), hash(b3)) is True
        assert g.has_path(hash(b4), hash(b5)) is False

        assert g.cut_block(hash(b5)) is True
        assert set(g.get_virtual_parents()) == {4, 3}
        assert len(g.graph().nodes()) == 4
        assert len(g.graph().edges()) == 2
        assert g.subgraph(hash(b6)) is None
        assert set(g.subgraph(hash(b4)).nodes()) == {1, 2, 4}
        assert set(g.subgraph(hash(b4)).edges()) == {(4, 1), (4, 2)}

    def test_convergence_dag(self):
        """
        Example:
            1 <= 2, 1 <= 3, 1 <= 4

            4 <= 5, 3 <- 5

            3 <= 6, 2 <- 6, 4 <- 6
        """
        g = BlockDAG(gtype=DAGType.CONVERGENCE)
        b1 = Block(bid=1, type=BlockType.GENESIS, height=1)
        g.add_block(b1)
        b2 = Block(bid=2, type=BlockType.MINED, miner="ug1y", pref=hash(b1), height=2)
        g.add_block(b2)
        b3 = Block(bid=3, type=BlockType.MINED, miner="ug1y", pref=hash(b1), height=2)
        g.add_block(b3)
        b4 = Block(bid=4, type=BlockType.MINED, miner="ug1y", pref=hash(b1), height=2)
        g.add_block(b4)
        b5 = Block(bid=5, type=BlockType.MINED, miner="ug1y", pref=hash(b4), crefs={hash(b3)}, height=3)
        g.add_block(b5)
        b6 = Block(bid=6, type=BlockType.MINED, miner="ug1y", pref=hash(b3), crefs={hash(b2), hash(b4)}, height=3)
        g.add_block(b6)

        assert g.add_block(b1) is False
        b11 = Block(bid=11, type=BlockType.GENESIS, height=1)
        assert g.add_block(b11) is False
        b12 = Block(bid=12, type=BlockType.MINED, miner="ug1y", pref=hash(b3), crefs={hash(b6)}, height=3)
        assert g.add_block(b12) is False

        assert set(g.get_virtual_parents()) == {5, 6}
        assert set(g.get_column_blocks(1)) == {1}
        assert set(g.get_column_blocks(2)) == {2, 3, 4}
        assert set(g.get_column_blocks(3)) == {5, 6}
        assert set(g.get_column_blocks(4)) == set()
        assert set(g.get_pivot_chain(hash(b6))) == {1, 3, 6}
        assert set(g.get_pivot_chain(hash(b5))) == {1, 4, 5}

        assert set(g.ask_block(hash(b5)).get_parents()) == set(g.successors(hash(b5)))
        assert set(g.predecessors(hash(b3))) == {5, 6}
        assert g.has_path(hash(b6), hash(b3)) is True
        assert g.has_path(hash(b4), hash(b3)) is False

        assert g.cut_block(hash(b6)) is True
        assert set(g.get_virtual_parents()) == {2, 5}
        assert len(g.graph().nodes()) == 5
        assert len(g.graph().edges()) == 5
        assert g.subgraph(hash(b6)) is None
        assert set(g.subgraph(hash(b4)).nodes()) == {1, 4}
        assert set(g.subgraph(hash(b4)).edges()) == {(4, 1)}