from ditto.blockdag import Block

if __name__ == '__main__':
    b = Block(bid=1,
              miner='H1',
              pref=1,
              crefs={2, 3})

    b2 = Block()
    print(repr(b2))
    print(b2)
