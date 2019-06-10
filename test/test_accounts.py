import unittest

from .tests_helpers import set_up_client, print_test_title, print_case_pass


class TestAccounts(unittest.TestCase):
    def setUp(self):
        print_test_title('Accounts')
        self.api = set_up_client()

    def test_accounts(self):
        self.get_account_info_test()
        self.retrieve_token()

    # test cases
    def get_account_info_test(self):
        res = self.api.account_info()
        self.assertIsNotNone(res['account'])

        print_case_pass('get_account_info_test')

    def retrieve_token(self):
        res = self.api.retrieve_token()
        self.assertIsNotNone(res)

        print_case_pass('retrieve_token')
