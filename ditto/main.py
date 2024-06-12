from ditto.blockdag import Block, BlockType, BlockDAG, DAGType

if __name__ == '__main__':
    b1 = Block(bid=1, type=BlockType.GENESIS, height=1)
    b2 = Block(bid=2, type=BlockType.MINED, miner="hao", pref=hash(b1), crefs=set(), height=2)
    b3 = Block(bid=3, type=BlockType.MINED, miner="hao", pref=hash(b1), crefs=set(), height=2)
    b4 = Block(bid=4, type=BlockType.MINED, miner="hao", pref=hash(b2), crefs={hash(b3)}, height=3)

    g = BlockDAG(gtype=DAGType.PARALLEL)
    print(g.add_block(b1), repr(g))
    print(g.add_block(b2), repr(g))
    print(g.add_block(b3), repr(g))
    print(g.add_block(b4), repr(g))

    print(g.get_graph_type())
    print(g.get_virtual_parents())
    print(g.get_column_blocks())
    print(g.get_pivot_chain(4))
