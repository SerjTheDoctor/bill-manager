def print_list(lst: list):
    items_per_line = 10

    s = '['
    for i, e in enumerate(lst):
        if (i+1) % items_per_line == 0:
            s += '\n'
        s += "'" + str(e) + "', "

    s += ']'
    print(s)
