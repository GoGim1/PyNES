class Memory(object):
    def __init__(self, size):
        self.memory = [0 for _ in range(size)]

    def read(self, addr):
        return self.memory[addr]

    def write(self, addr, data):
        self.memory[addr] = data
