def expect_data(str):
    ret = str.lower().split()
    return ret[0:2] + ret[-11:]


def actual_data(str):
    ret = str.lower().split()
    return ret[0:2] + ret[-11:]


if __name__ == '__main__':
    expect_output = open('expect_ppu_output')
    actual_output = open('actual_ppu_output')
    actual_output.readline()
    actual_output.readline()

    line = 0
    for _ in range(100000):
        line += 1
        expect_str = expect_output.readline()
        actual_str = actual_output.readline()
        if not expect_data(expect_str) == actual_data(actual_str):
            print(line, '--->', expect_str)
            print(line, '--->', actual_str)
            break
    expect_output.close()
    actual_output.close()
