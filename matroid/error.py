class APIError(Exception):
  """doc"""

  def __init__(self, response=None, message=None):
    if message:
      super(APIError, self).__init__(message)
    else:
      try:
        super(APIError, self).__init__(response.text)
      except AttributeError:
        super(APIError, self).__init__(
            'No response or error message provided')

    if response:
      self.response = response

      try:
        request = response.request
        self.res_text = response.text
        self.res_status = response.status_code
        self.req_headers = request.headers
        self.req_body = request.body
      except AttributeError:
        pass

      self.message = message

    def __str__(self):
      return unicode(self).encode('utf-8')


class APIConnectionError(APIError):
  pass


class AuthorizationError(APIError):
  pass


class InvalidQueryError(APIError):
  pass


class ServerError(APIError):
  pass


class RateLimitError(APIError):
  pass


class PaymentError(APIError):
  pass


class TokenExpirationError(APIError):
  pass


class MediaError(APIError):
  pass
