import pytest
import inspect

from matroid.error import APIError
from test.helper import print_test_pass


class TestAccounts(object):
  def test_accounts(self, set_up_client):
    # set up client
    self.api = set_up_client

    # start testing
    self.get_account_info_test()
    self.account_info_test()
    self.retrieve_token()

  # test cases
  def get_account_info_test(self):
    res = self.api.get_account_info()
    assert (res['account'] != None)
    assert (res['account']['name'] != None)
    assert (res['account']['email'] != None)
    print_test_pass()

  # test deprecated method name (account_info, now get_account_info)
  def account_info_test(self):
      res = self.api.account_info()
      assert (res['account'] != None)
      assert (res['account']['name'] != None)
      assert (res['account']['email'] != None)
      print_test_pass()

  def retrieve_token(self):
    res = self.api.retrieve_token()
    assert (res != None)
    assert (res.token_type != None)
    assert (res.token_str != None)
    print_test_pass()

  def test_with_wrong_permission(self, set_up_wrong_permission_client):
    with pytest.raises(APIError) as e:
      api = set_up_wrong_permission_client
      api.retrieve_token()
    assert ('authorization_err' in str(e))
    print_test_pass()
