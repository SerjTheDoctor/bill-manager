from lib.receipt_cpu import process

def test_dates():
    file_date_map = {
        'auchan-2.jpg': '13.03.2021',
        'carrefour-1.jpeg': '20/05/2021',
        'directClientServices-1.jpg': '03-02-2021',
        'flaviandaCrisan-1.jpg': '15-05-2021',
        'h&m-1.jpeg': '19.03.2021',
        'internationalPaper-1.jpeg': '22-04-2021',
        'lemnuVerde-1.jpg': '01-03-2021',
        'lidl-1.jpeg': '04/05/2021',
        'lidl-2.jpeg': '01/05/2021',
        'pepco-1.jpg': '24/04/2021',
        'profi-1.jpeg': '27/04/2021',
        'profi-2.jpeg': '01/04/2021',
        'profi-3.jpeg': '26/04/2021'
    }
    passed_nr = 0
    log = '\n## Testing dates ##\n'

    for filename in file_date_map:
        file = 'uploads/' + filename
        data = process(file, 'test')

        passed = data['date'] == file_date_map[filename]
        if passed:
            passed_nr += 1

        log += '[' + ('+' if passed else '-') + '] '
        log += data['date'] if data['date'] else ''
        log += ' (' + file_date_map[filename] + ') ' + filename
        log += '\n'

    log += '# Finished testing dates #\n'
    log += '\n'
    log += 'Results: {}/{}'.format(passed_nr, len(file_date_map))

    print(log)

test_dates()
