import unittest
from core import allocate, cents, split_bill, valid_email

class MoneyTests(unittest.TestCase):
    def test_remainders(self):
        self.assertEqual(allocate(100, [1, 1, 1]), [34, 33, 33])
        for total in range(1000):
            self.assertEqual(sum(allocate(total, [1, 2, 7])), total)
    def test_round_half_up(self):
        self.assertEqual(cents('1.005'), 101)
        for bad in ['nan', 'inf', None]:
            with self.assertRaises(ValueError): cents(bad)
    def test_sample(self):
        rows = [{'item': 'Food', 'amount': 740}]
        self.assertEqual(split_bill(rows, ['A','B','C'], 3700), {'A':25900,'B':25900,'C':25900})
    def test_unequal_items_and_tax(self):
        rows = [{'item':'A meal','amount':100,'owners':['A']}, {'item':'B meal','amount':200,'owners':['B']}]
        self.assertEqual(split_bill(rows, ['A','B'], 3000, True), {'A':11000,'B':22000})
    def test_discount(self):
        rows = [{'item':'Food','amount':100}]
        self.assertEqual(sum(split_bill(rows, ['A','B','C'], -9999).values()), 1)
    def test_empty_owner_and_duplicate(self):
        with self.assertRaises(ValueError): split_bill([{'item':'Food','amount':1,'owners':[]}], ['A'], by_item=True)
        with self.assertRaises(ValueError): split_bill([{'item':'Food','amount':1}], ['A','A'])
    def test_email_injection(self):
        self.assertFalse(valid_email('a@b.com\r\nBcc:x@y.com'))
        self.assertFalse(valid_email('a@b.com,c@d.com'))
        self.assertTrue(valid_email('first.last+test@gmail.com'))

if __name__ == '__main__': unittest.main()
