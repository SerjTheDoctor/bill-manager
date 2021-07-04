from lib.receipt_cpu import process as receipt_process
from lib.utils import pretty_bill
import unittest

def process(path, extension=None):
    return receipt_process(path, ext=extension, env='test')

class TestProcessing(unittest.TestCase):
    def test_auchan2(self):
        data = process('../uploads/auchan-2.jpg')
        print(pretty_bill(data))

        self.assertEqual(data['date'], '13.03.2021')
        self.assertEqual(data['total'], '73.29')
        self.assertRegexpMatches(data['store'], 'AUCHAN ROMANIA')


if __name__ == '__main__':
    unittest.main()
