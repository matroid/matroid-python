import os
import re
import sys
import datetime

import requests

from matroid import error

BASE_URL = 'https://www.matroid.com/api/0.1'
DEFAULT_GRANT_TYPE = 'client_credentials'

def api_call(default_error):
  """setup and teardown decorator for API calls"""
  def decorator(func):
    def setup_and_teardown(self, *original_args, **original_kwargs):
      self.retrieve_token()

      response = func(self, *original_args, **original_kwargs)

      try:
        self.check_errors(response, default_error)
      except error.TokenExpirationError:
        self.retrieve_token(options={'request_from_server': True})
        return func(self, *original_args, **original_kwargs)
      else:
        return self.format_response(response)
    return setup_and_teardown
  return decorator


class MatroidAPI(object):
  def __init__(self, base_url=BASE_URL, client_id=None, client_secret=None, options={}):
    """
    base_url: the API endpoint
    client_id: OAuth public API key
    client_secret: OAuth private API key
    options (dict):
      set json_format to False to return API results as strings instead of objects
      set print_output to True to print the API results to the screen in addition to returning them
    """

    if not client_id:
      client_id = os.environ.get('MATROID_CLIENT_ID', None)

    if not client_secret:
      client_secret = os.environ.get('MATROID_CLIENT_SECRET', None)

    if not client_id or not client_secret:
      raise error.AuthorizationError(
          message='Both client_id and client_secret parameters are required')

    self.client_id = client_id
    self.client_secret = client_secret
    self.base_url = base_url
    self.token = None
    self.grant_type = DEFAULT_GRANT_TYPE
    self.json_format = options.get('json_format', True)
    self.print_output = options.get('print_output', False)
    self.filereader = self.FileReader()

    self.endpoints = {
        'token': (self.base_url + '/oauth/token', 'POST'),
        'detectors': (self.base_url + '/detectors', 'GET'),
        'create_detector': (self.base_url + '/detectors', 'POST'),
        'classify_image': (self.base_url + '/detectors/:key/classify_image', 'POST'),
        'classify_video': (self.base_url + '/detectors/:key/classify_video', 'POST'),
        'get_video_results': (self.base_url + '/videos/:key', 'GET'),
        'train_detector': (self.base_url + '/detectors/:key/finalize', 'POST'),
        'detector_info': (self.base_url + '/detectors/:key', 'GET'),
        'account_info': (self.base_url + '/account', 'GET')
    }

  @api_call(error.InvalidQueryError)
  def list_detectors(self):
    """Lists the available detectors"""
    (endpoint, method) = self.endpoints['detectors']

    try:
      headers = {'Authorization': self.token.authorization_header()}
      return requests.request(method, endpoint, **{'headers': headers})
    except Exception as e:
      raise error.APIConnectionError(message=e)

  @api_call(error.InvalidQueryError)
  def classify_image(self, detector_id, image_file=None, image_url=None):
    """
    Classify an image with a detector

    detector_id: a unique id for the detector
    image_file: path to local image file to classify
    image_url: internet URL for the image to classify
    """

    MAX_LOCAL_IMAGE_SIZE = 50 * 1024 * 1024
    MAX_LOCAL_IMAGE_BATCH_SIZE = 50 * 1024 * 1024

    def batch_file_classify(image_file):
      try:
        files = []
        total_batch_size = 0
        for file in image_file:
          file_obj = self.filereader.get_file(file)
          file_size = os.fstat(file_obj.fileno()).st_size

          if file_size > MAX_LOCAL_IMAGE_SIZE:
            raise error.InvalidQueryError(message='File %s is larger than the limit of %d megabytes' % (file_obj.name, self.bytes_to_mb(MAX_LOCAL_IMAGE_BATCH_SIZE)))

          files.append(('file', file_obj))
          total_batch_size += file_size

        if total_batch_size > MAX_LOCAL_IMAGE_BATCH_SIZE:
          raise error.InvalidQueryError(message='Max batch upload size is %d megabytes.' % (self.bytes_to_mb(MAX_LOCAL_IMAGE_BATCH_SIZE)))

        return requests.request(method, endpoint, **{'headers': headers, 'files': files, 'data': data})
      finally:
        for file_tuple in files:
          (key, file) = file_tuple
          file.close()

    (endpoint, method) = self.endpoints['classify_image']

    if image_url and image_file:
      raise error.InvalidQueryError(
          message='Cannot classify a URL and local file in the same request')

    if not image_url and not image_file:
      raise error.InvalidQueryError(
          message='Missing required parameter: image_file or image_url')

    endpoint = endpoint.replace(':key', detector_id)

    try:
      headers = {'Authorization': self.token.authorization_header()}
      data = {'detector_id': detector_id}
      if image_file:
        if isinstance(image_file, list):
          return batch_file_classify(image_file)
        else:
          with self.filereader.get_file(image_file) as file_to_upload:
            files = {'file': file_to_upload}
            file_size = os.fstat(file_to_upload.fileno()).st_size

            if file_size > MAX_LOCAL_IMAGE_SIZE:
              raise error.InvalidQueryError(message='File %s is larger than the limit of %d megabytes' % (file_to_upload.name, self.bytes_to_mb(MAX_LOCAL_IMAGE_SIZE)))

            return requests.request(method, endpoint, **{'headers': headers, 'files': files, 'data': data})
      elif image_url:
        data['url'] = image_url
        return requests.request(method, endpoint, **{'headers': headers, 'data': data})
    except IOError as e:
      raise e
    except error.InvalidQueryError as e:
      raise e
    except Exception as e:
      raise error.APIConnectionError(message=e)

  def retrieve_token(self, options={}):
    """
    Generates an OAuth token. The API client will intelligently refresh the Access Token for you
    However, if you would like to manually expire an existing token and create a new token,
    call this method manually and pass in 'expire_token': True in the options argument.

    In addition, you would have to refresh manually if another client has expired your access token.

    You can pass the 'request_from_server': True option to make a request
    to the server for the access token without invalidating it. This is useful if you are running
    multiple clients with the same token so they don't endlessly refresh each others' tokens
    """

    (endpoint, method) = self.endpoints['token']

    if not options.get('expire_token') and not options.get('request_from_server'):
      if self.token and not self.token.expired():
        return self.token

    try:
      query_data = {'grant_type': self.grant_type,
                    'client_id': self.client_id, 'client_secret': self.client_secret}
      if options.get('expire_token'):
        query_data['refresh'] = 'true'
      response = requests.request(method, endpoint, data=query_data)
    except Exception as e:
      raise error.APIConnectionError(message=e)

    self.check_errors(response, error.AuthorizationError)

    self.save_token(response)

  @api_call(error.InvalidQueryError)
  def classify_video(self, detector_id, video_url=None, video_file=None):
    """
    Classify a video from a url with a detector

    detector_id: a unique id for the detector
    video_url: internet URL for the video to classify
    """

    MAX_LOCAL_VIDEO_SIZE = 300 * 1024 * 1024

    (endpoint, method) = self.endpoints['classify_video']

    if not video_url and not video_file:
      raise error.InvalidQueryError(
          message='Missing required parameter: video_url or video_file')

    if video_url and video_file:
      raise error.InvalidQueryError(
          message='Cannot classify a URL and local file in the same request')

    if isinstance(video_file, list):
      raise error.InvalidQueryError(
          message='Only one video can be uploaded at a time')

    endpoint = endpoint.replace(':key', detector_id)

    try:
      headers = {'Authorization': self.token.authorization_header()}
      data = {'detector_id': detector_id}
      if video_url:
        data['url'] = video_url
        return requests.request(method, endpoint, **{'headers': headers, 'data': data})
      elif video_file:
        with self.filereader.get_file(video_file) as file_to_upload:
          files = {'file': file_to_upload}
          file_size = os.fstat(file_to_upload.fileno()).st_size

          if file_size > MAX_LOCAL_VIDEO_SIZE:
            raise error.InvalidQueryError(message='File %s is larger than the limit of %d megabytes' % (file_to_upload.name, self.bytes_to_mb(MAX_LOCAL_VIDEO_SIZE)))

          return requests.request(method, endpoint, **{'headers': headers, 'files': files, 'data': data})
    except error.InvalidQueryError as e:
      raise e
    except Exception as e:
      raise error.APIConnectionError(message=e)

  @api_call(error.InvalidQueryError)
  def get_video_results(self, video_id, threshold=1, response_format='json'):
    """
    Get the current classifications for a given video ID

    video_id: a unique id for the classified video
    threshold: the cutoff for confidence level in the detection at each timestamp
    response_format: 'csv' or 'json' for the response format
    """
    (endpoint, method) = self.endpoints['get_video_results']

    if response_format == 'csv' and self.json_format:
      print('cannot return csv format when json_format True is specified upon API object initialization')
      print('requesting JSON format...')
      response_format = 'json'

    endpoint = endpoint.replace(':key', video_id)

    try:
      headers = {'Authorization': self.token.authorization_header()}
      params = {'videoId': video_id, 'threshold': threshold, 'format': response_format}
      return requests.request(method, endpoint, **{'headers': headers, 'params': params})
    except Exception as e:
      raise error.APIConnectionError(message=e)

  @api_call(error.InvalidQueryError)
  def create_detector(self, zip_file, name, detector_type):
    """
    Create a new detector with the contents of the zip file

    detector_type: general, facial_recognition, or facial_characteristics
    name: the detector's display name
    zip_file: a zip file containing the images to be used in the detector creation
              the root folder should contain only directories which will become the labels for detection
              each of these directories should contain only images corresponding to that label.

              However, there is an exception if you want to add negative examples to a label.
              In that case, put the negative images for the label in a folder called "negative" inside the corresponding label.

              To include bounding boxes, include one file called bbox.csv in the top level directory.
              Each line of this file should be formatted as follows:
                0.25, 0.3, 0.75, 0.8, cat, positive, image.jpg
                0.25, 0.4, 0.55, 0.7, dog, positive, picture.jpg
                0.0, 0.1, 0.2, 0.3, cat, negative, raccoon.jpg

              Column definitions:
                top left X coordinate, top left Y coordinate, bottom right X coordinate, bottom right Y coordinate, label, positive or negative example, file name

              Max 300 MB zip file upload

      structure example:
        cat/
          garfield.jpg
          nermal.png
        dog/
          odie.TIFF
          negative/
            lobo.jpg
        bbox.csv
    """
    MAX_LOCAL_ZIP_SIZE = 300 * 1024 * 1024

    (endpoint, method) = self.endpoints['create_detector']

    try:
      headers = {'Authorization': self.token.authorization_header()}
      data = {'name': name, 'detector_type': detector_type}
      with self.filereader.get_file(zip_file) as file_to_upload:
        files = {'file': file_to_upload}
        file_size = os.fstat(file_to_upload.fileno()).st_size

        if file_size > MAX_LOCAL_ZIP_SIZE:
          raise error.InvalidQueryError(message='File %s is larger than the limit of %d megabytes' % (file_to_upload.name, self.bytes_to_mb(MAX_LOCAL_ZIP_SIZE)))

        return requests.request(method, endpoint, **{'headers': headers, 'files': files, 'data': data})
    except Exception as e:
      raise error.APIConnectionError(message=e)

  @api_call(error.InvalidQueryError)
  def train_detector(self, detector_id, name=None, detector_type=None):
    """Begin training the detector"""
    (endpoint, method) = self.endpoints['train_detector']

    endpoint = endpoint.replace(':key', detector_id)

    try:
      headers = {'Authorization': self.token.authorization_header()}
      data = {}
      if name:
        data['name'] = name
      if detector_type:
        data['detector_type'] = detector_type

      return requests.request(method, endpoint, **{'headers': headers, 'data': data})
    except Exception as e:
      raise error.APIConnectionError(message=e)

  @api_call(error.InvalidQueryError)
  def detector_info(self, detector_id):
    """Get information about detector"""
    (endpoint, method) = self.endpoints['detector_info']

    endpoint = endpoint.replace(':key', detector_id)

    try:
      headers = {'Authorization': self.token.authorization_header()}
      return requests.request(method, endpoint, **{'headers': headers})
    except Exception as e:
      raise error.APIConnectionError(message=e)

  @api_call(error.InvalidQueryError)
  def account_info(self):
    """Get user account and credits information"""
    (endpoint, method) = self.endpoints['account_info']

    try:
      headers = {'Authorization': self.token.authorization_header()}
      return requests.request(method, endpoint, **{'headers': headers})
    except Exception as e:
      raise error.APIConnectionError(message=e)

  # -----------------------------------------------------------------
  # Helper methods and helper classes
  # -----------------------------------------------------------------

  def bytes_to_mb(self, bytes):
    return bytes / 1024 / 1024

  def check_errors(self, response=None, UserErr=None):
    """Raise specific errors depending on how the API call failed"""
    status = response.status_code
    code = None
    try:
      code = response.json().get('code')
    except:
      pass

    if status == 429 and code == 'rate_err':
      raise error.RateLimitError(response)
    elif status == 402 and code == 'payment_err':
      raise error.PaymentError(response)
    elif status / 100 == 4:
      if code == 'token_expiration_err':
        raise TokenExpirationError(response)
      elif UserErr:
        raise UserErr(response)
      else:
        raise error.APIError(response)
    elif code == 'media_err':
      raise error.MediaError(response)
    elif status / 100 == 5 and code == 'server_err':
      raise error.ServerError(response)
    elif status / 100 != 2:
      raise error.APIError(response)

  def format_response(self, response):
    """Format the output according to the options (json, print to screen)"""
    if self.print_output:
      print(response.text)
    if self.json_format:
      return response.json()
    else:
      return response.text

  def save_token(self, response):
    """Extracts the access token from the API response"""
    res = response.json()

    if isinstance(res, str):
      print(response.text)
      raise error.APIError(message='Could not parse the response')

    access_token = res['access_token']
    token_type = res['token_type']
    expires_in = res['expires_in']

    if not access_token or not token_type or not expires_in:
      raise error.APIError(
          message='Required parameters not found in the response')

    self.token = self.Token(token_type, access_token, expires_in)

  class Token(object):
    """Represents an OAuth access token"""

    def __init__(self, token_type, token_str, expiration):
      self.token_type = token_type
      self.token_str = token_str
      self.born = datetime.datetime.now()
      self.lifetime = expiration

    def authorization_header(self):
      return self.token_type + " " + self.token_str

    def expired(self):
      return self.born + datetime.timedelta(0, int(self.lifetime)) < datetime.datetime.now()

  class FileReader(object):
    """Reads files for classification input"""

    def __init__(self):
      pass

    def get_file(self, file_input):
      """Extracts file from file path or returns the file if file is passed in"""
      if isinstance(file_input, str):
        # try to read the file
        local_file = open(file_input, 'rb')
        return local_file
      else:
        return local_file

Matroid = MatroidAPI
