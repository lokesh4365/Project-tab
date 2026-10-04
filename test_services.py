import unittest
from unittest.mock import patch
from services import send_email

class EmailBoundary(unittest.TestCase):
    @patch('services.smtplib.SMTP_SSL')
    def test_exact_preview_sent(self, smtp):
        server = smtp.return_value.__enter__.return_value
        server.send_message.return_value = {}
        send_email('sender@gmail.com', 'placeholder', 'recipient@example.com', 'A: ₹259.00\nB: ₹259.00')
        message = server.send_message.call_args.args[0]
        self.assertEqual(message['To'], 'recipient@example.com')
        self.assertIn('A: ₹259.00', message.get_content())
        server.login.assert_called_once_with('sender@gmail.com', 'placeholder')
    @patch('services.smtplib.SMTP_SSL')
    def test_invalid_recipient_never_connects(self, smtp):
        with self.assertRaises(ValueError):
            send_email('sender@gmail.com', 'placeholder', 'bad\r\nBcc:a@b.com', 'body')
        smtp.assert_not_called()
