import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())
# Add yahoofin package path to sys.path
sys.path.append(os.path.join(os.getcwd(), 'pkgs', 'yahoofin'))

from exchanges.robinhood.robinhood import Robinhood

class TestRobinhoodLoginChallenge(unittest.TestCase):
    def setUp(self):
        self.config = {
            'products': [{'id': 'test_id', 'instrument': 'http://url'}],
            'backfill': {'enabled': False},
            'user': 'user',
            'pass': 'password',
            'mfa_key': 'mfa_secret',
            'config': '/tmp/robinhood.yml',
            'exchange': {'dummy': 'value'}
        }

    @patch('builtins.input', return_value='')
    @patch('exchanges.robinhood.robinhood.readConf')
    @patch('exchanges.robinhood.robinhood.r')
    @patch('exchanges.robinhood.robinhood.pyotp')
    def test_login_challenge_retry(self, mock_pyotp, mock_r, mock_readConf, mock_input):
        mock_readConf.return_value = self.config
        
        # Mock instruments
        mock_r.stocks.get_instruments_by_symbols.return_value = [{'simple_name': 'Test Product', 'url': 'http://url', 'id': 'test_id'}]
        
        # Mock TOTP
        mock_totp = MagicMock()
        mock_pyotp.TOTP.return_value = mock_totp
        mock_totp.now.side_effect = ['123456', '654321'] # First and second code
        
        # Mock Login: First fails with challenge, second succeeds
        challenge_exception = Exception("{'verification_workflow': {'id': '123', 'workflow_status': 'workflow_status_internal_pending'}}")
        mock_r.login.side_effect = [challenge_exception, True]
        
        rh = Robinhood(self.config, auth=True)
        
        # Verify interactions
        # 1. First login call
        self.assertEqual(mock_r.login.call_count, 2)
        mock_r.login.assert_has_calls([
            call(username='user', password='password', mfa_code='123456'),
            call(username='user', password='password', mfa_code='654321')
        ])
        
        # Verify input was called
        mock_input.assert_called_once()
        
        self.assertTrue(rh.auth)

if __name__ == '__main__':
    unittest.main()
