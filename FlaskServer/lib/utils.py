def get_extension(path: str, dot=True):
    ext = path.split('.')[-1]

    if dot:
        return '.' + ext
    else:
        return ext

def string2float(s: str):
    s = s.replace(',', '.').strip()

    try:
        return float(s)
    except ValueError:
        return None

def pretty_list(lst: list, items_per_line=5):
    s = '['
    for i, e in enumerate(lst):
        if (i+1) % items_per_line == 0:
            s += '\n'
        s += "'" + str(e) + "', "

    s += '\n]'
    return s

def pretty_dict(d: dict):
    s = '{\n'

    for k in d:
        s += "  '{}': {}\n".format(k, d[k])

    s += '}'
    return s

def pretty_bill(b):
    s = 'Merchant: {}\n'.format(b['store'])
    s += 'Date: {}\n'.format(b['date'])

    for item in reversed(b['items']):
        s += '  {} - {} {} x {} = {}\n'.format(
            item['name'], item['quantity'], item['unit'], item['unit_price'], item['total_price']
        )

    s += 'Total: {}\n'.format(b['total'])
    return s
