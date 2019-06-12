import pytest

from matroid.error import AuthorizationError


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
    assert (res != None)

  def test_with_wrong_permission(self, set_up_wrong_permission_client):
    with pytest.raises(AuthorizationError) as e:
      api = set_up_wrong_permission_client
      api.retrieve_token()
    assert ('authorization_err' in str(e))
