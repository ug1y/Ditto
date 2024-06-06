from ditto.blockdag import Block

if __name__ == '__main__':
    b = Block(block_id=1,
              miner_name='H1',
              pivot_reference=1,
              common_references={2, 3})

    b2 = Block()

    print(b2)
