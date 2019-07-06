class Memory(object):
    def __init__(self, size):
        self.size = size
        self.memory = [0 for _ in range(size)]

    def read(self, addr):
        return self.memory[addr]

    def write(self, addr, data):
        self.memory[addr] = data

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.read(item)
        if isinstance(item, slice):
            start, end = item.start, item.stop
            ret = []
            for i in range(start, end):
                ret.append(self.read(i))
            return ret

    def __setitem__(self, key, value):
        self.write(key, value)

    def set(self, l):
        assert len(l) == self.size
        self.memory = l


if __name__ == '__main__':
    a = Memory(3)
    b = a[1:3]
    print(b)