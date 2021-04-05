import os
import re
import sys

from matroid import error
from matroid.src.helpers import api_call

BASE_URL = 'https://www.matroid.com/api/v1'
DEFAULT_GRANT_TYPE = 'client_credentials'


class MatroidAPI(object):
  from matroid.src.helpers import bytes_to_mb, check_errors, format_response, save_token, Token, FileReader
  from matroid.src.accounts import get_account_info, account_info, retrieve_token
  from matroid.src.detectors import create_detector, delete_detector, finalize_detector, train_detector, get_detector_info, detector_info, import_detector, redo_detector, search_detectors, list_detectors
  from matroid.src.images import classify_image, localize_image
  from matroid.src.videos import classify_video, get_video_results
  from matroid.src.streams import create_stream, register_stream, delete_monitoring, delete_stream, get_monitoring_result, kill_monitoring, monitor_stream, search_monitorings, search_streams
  from matroid.src.labels import create_label_with_images, delete_label, get_annotations, get_label_images, update_annotations, update_label_with_images
  from matroid.src.collections import create_collection_index, create_collection, delete_collection_index, delete_collection, get_collection_task, get_collection, kill_collection_index, query_collection_by_scores, query_collection_by_image, update_collection_index

  def __init__(self, base_url=BASE_URL, client_id=None, client_secret=None, options={}):
    """
    base_url: the API endpoint
    client_id: OAuth public API key
    client_secret: OAuth private API key
    options (dict):
      set json_format to False to return API results as strings instead of objects
      set print_output to True to print the API results to the screen in addition to returning them
      set access_token with your auth token e.g., 43174a480adebf5b8e2bf39c0dcb53f1, to preload the token instead of requesting it from the server
    """

    from matroid.src.helpers import get_endpoints

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

    token = options.get('access_token')

    if token:
      token_type = 'Bearer'
      # if the token's lifetime is shorter than this, the client will request a refresh automatically
      lifetime_in_seconds = 7 * 24 * 60 * 60
      self.token = self.Token(token_type, token, lifetime_in_seconds)

    self.endpoints = get_endpoints(self.base_url)


Matroid = MatroidAPI
