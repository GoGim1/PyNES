def format():
    with open('ac_mem', 'r') as f:
        s = f.readline()
        l = s.split()
        ret_l = [hex(int(s_num)) for s_num in l]
        with open('ac_m', 'w') as w:
            w.write(str(ret_l))


if __name__ == '__main__':
    expect_output = open('memory')
    actual_output = open('ac_m')
    expect_str = expect_output.readline()[:47]
    actual_str = actual_output.readline()[:47]
    for line in range(60):
        if expect_str != actual_str:
            print(line, '--->', expect_str)
            print(line, '--->', actual_str)
            break

    expect_output.close()
    actual_output.close()