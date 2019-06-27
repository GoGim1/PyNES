def list_to_hex_str(l):
    ret = ''
    for n in l:
        ret += fromat(n) + ' '
    return ret


def fromat(n):
    no_prefix = hex(n)[2:]
    if len(no_prefix) == 1 or len(no_prefix) == 3:
        return '0' + no_prefix
    else:
        return no_prefix

