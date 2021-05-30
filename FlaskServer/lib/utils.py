def get_extension(path: str, dot=True):
    ext = path.split('.')[-1]

    if dot:
        return '.' + ext
    else:
        return ext

def pretty_list(lst: list, items_per_line=5):
    s = '['
    for i, e in enumerate(lst):
        if (i+1) % items_per_line == 0:
            s += '\n'
        s += "'" + str(e) + "', "

    s += ']'
    return s

def pretty_dict(d: dict):
    s = '{\n'

    for k in d:
        s += "  '{}': {}\n".format(k, d[k])

    s += '}'
    return s
