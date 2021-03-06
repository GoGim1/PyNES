def expect_data(str):
    ret = str.lower().split()[0:-2]
    if (ret[-7] == '='):
        ret.pop(-7)
        ret.pop(-6)
    ret.append(str.lower().split()[-1])
    return ret

def actual_data(str):
    return str.lower().split()

if __name__=='__main__':
    expect_output = open('tools\expect_output.txt')
    actual_output = open('tools\\actual_output.txt')
    line = 0
    actual_output.readline()
    actual_output.readline()
    for _ in range(8991):
        line += 1
        expect_str = expect_output.readline()
        actual_str = actual_output.readline()
        if (not expect_data(expect_str) == actual_data(actual_str)):
            print(line, '--->', expect_data(expect_str))
            print(line, '--->', actual_data(actual_str))
            break
    expect_output.close()
    actual_output.close()