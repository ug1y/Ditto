from ditto.blockdag import Block, BlockType, BlockDAG, DAGType

if __name__ == '__main__':
    g = BlockDAG(gtype=DAGType.CONVERGENCE)
    b1 = Block(bid=1, type=BlockType.GENESIS, height=1)
    g.add_block(b1)

    g.add_block(b1)
    b11 = Block(bid=11, type=BlockType.GENESIS, height=1)
    g.add_block(b11)
