from ditto.blockdag import Block, BlockType, BlockDAG, DAGType

if __name__ == '__main__':
    b = Block(bid=1, type=BlockType.GENESIS, height=1)
    b2 = Block(bid=2, type=BlockType.MINED, miner="hao", crefs={hash(b)}, height=2)
    b3 = Block(bid=3, type=BlockType.MINED, miner="hao", crefs={hash(b2)}, height=3)
    g = BlockDAG(gtype=DAGType.DIVERGENCE)
    g.add_block(b)
    print(repr(g))
    g.add_block(b2)
    print(repr(g))
    g.add_block(b3)
    print(repr(g))
