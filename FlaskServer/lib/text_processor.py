from datetime import datetime
import re

class TextProcessor:
    def __init__(self, environment):
        self.env = environment
        self.debug = environment == 'development'

    def process_date(self, date):
        if not date:
            return date

        new_date = re.sub('[-,|/]', '.', date)

        self.pprint("Fixed date: '{}' -> '{}'".format(date, new_date))

        return new_date

    def process_total(self, total):
        if not total:
            return total

        new_total = re.sub(',', '.', total)

        self.pprint("Fixed total: '{}' -> '{}'".format(total, new_total))

        return new_total

    def process_store(self, store):
        if not store:
            return store

        new_store = re.sub('^S[.]?C[.]? ', '', store)  # Exclude S.C.
        new_store = re.sub(' S[.]?A[.]?$', '', new_store)  # Exclude S.A.
        new_store = re.sub(' S[.]?R[.]?L[.]?$', '', new_store)  # Exclude S.R.L.
        new_store = re.sub('[^a-zA-Z ]', '', new_store)  # Exclude non-alpha characters
        new_store = re.sub(' {2,}', ' ', new_store)  # Remove multiple spaces

        self.pprint("Fixed store: '{}' -> '{}'".format(store, new_store))

        return new_store

    def pprint(self, message):
        if self.debug:
            now = datetime.now().strftime('%H:%M:%S.%f')
            print(str(now) + ' [TextProcessor] ' + str(message))
