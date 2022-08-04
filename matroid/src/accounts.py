import requests

from matroid import error
from matroid.src.helpers import api_call

# https://staging.app.matroid.com/docs/api/index.html#api-Accounts-RefreshToken


def retrieve_token(self, options={}):
    """
    Generates an OAuth token. The API client will intelligently refresh the Access Token for you
    However, if you would like to manually expire an existing token and create a new token,
    call this method manually and pass in 'expire_token': True in the options argument.

    In addition, you would have to refresh manually if another client has expired your access token.

    You can pass the 'refresh': True option to make a request
    to the server for the access token without invalidating it. This is useful if you are running
    multiple clients with the same token so they don't endlessly refresh each others' tokens
    """

    (endpoint, method) = self.endpoints["token"]

    if not options.get("expire_token") and not options.get("refresh"):
        if self.token and not self.token.expired():
            return self.token

    try:
        query_data = {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if options.get("refresh"):
            query_data["refresh"] = "true"
        response = requests.request(method, endpoint, data=query_data)
    except Exception as e:
        raise error.APIConnectionError(message=e)

    self.check_errors(response, error.AuthorizationError)

    self.save_token(response)

    return response.json()


# https://staging.app.matroid.com/docs/api/index.html#api-Accounts-GetAccount
@api_call(error.InvalidQueryError)
def account_info(self):
    """Get user account and credits information"""
    (endpoint, method) = self.endpoints["account_info"]

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# account_info is now DEPRECATED in favor of get_account_info (kept for backwards-compatibility)
get_account_info = account_info
