import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

class AppFlow(unittest.TestCase):
    def test_sample_and_edit(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=20).run()
        self.assertFalse(app.exception)
        app.text_input[0].set_value('Lokesh')
        app.button[0].click().run()
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label == 'Load sample table →').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, '₹777.00')
        self.assertEqual(app.metric[2].value, '₹259.00')
        app.radio[0].set_value('By what we ordered').run()
        self.assertFalse(app.exception)
        app.multiselect[0].set_value(['Lokesh']).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, '₹777.00')
        app.checkbox[0].check().run()
        self.assertTrue(app.checkbox[0].value)
        app.number_input[1].set_value(30.0).run()
        self.assertFalse(app.checkbox[0].value)
        self.assertEqual(app.metric[0].value, '₹807.00')

if __name__ == '__main__': unittest.main()
