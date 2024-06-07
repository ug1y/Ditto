from ditto.blockdag import Block, Transaction, TransactionType, BlockDAG

if __name__ == '__main__':
    b = Block(bid=1,
              miner='H1',
              pref=1,
              crefs={2, 3})

    b2 = Block()
    print(repr(b2))
    print(b2)

    t = Transaction(tid=1)
    t.type = TransactionType.CONFLICT
    print(repr(t))
    print(t)

    g = BlockDAG()
    print(repr(g))
    print(g)
    print(len(g))
