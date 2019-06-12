import pytest


class TestAccounts(object):
  def test_accounts(self, set_up_client):
    # set up client
    self.api = set_up_client

    # start testing
    self.get_account_info_test()
    self.retrieve_token()

  # test cases
  def get_account_info_test(self):
    res = self.api.account_info()
    assert(res['account'] != None)

  def retrieve_token(self):
    res = self.api.retrieve_token()
    assert(res != None)
