import os
import requests
import json

from matroid import error
from matroid.src.helpers import api_call

# https://staging.dev.matroid.com/docs/api/index.html#api-Collections-PostApiVersionCollectionsCollectionidCollectionTasks
@api_call(error.InvalidQueryError)
def create_collection_index(self, collection_id, detector_id, file_types):
  """Create an index on a collection with a detector"""
  (endpoint, method) = self.endpoints['create_collection_index']
  endpoint = endpoint.replace(':key', collection_id)

  try:
    headers = {'Authorization': self.token.authorization_header()}
    data = {
        'detectorId': detector_id,
        'fileTypes': file_types
    }
    return requests.request(method, endpoint, **{'headers': headers, 'data': data})
  except Exception as e:
    raise error.APIConnectionError(message=e)

# https://staging.dev.matroid.com/docs/api/index.html#api-Collections-PostCollections
@api_call(error.InvalidQueryError)
def create_collection(self, name, url, source_type):
  """Creates a new collection from a web or S3 url. Automatically kick off default indexes"""
  (endpoint, method) = self.endpoints['create_collection']

  try:
    headers = {'Authorization': self.token.authorization_header()}
    data = {
        'name': name,
        'url': url,
        'sourceType': source_type
    }
    return requests.request(method, endpoint, **{'headers': headers, 'data': data})
  except Exception as e:
    raise error.APIConnectionError(message=e)

# https://staging.dev.matroid.com/docs/api/index.html#api-Collections-DeleteCollectionTasksTaskid
@api_call(error.InvalidQueryError)
def delete_collection_index(self, task_id):
  """Deletes a completed collection mananger task"""
  (endpoint, method) = self.endpoints['delete_collection_index']
  endpoint = endpoint.replace(':key', task_id)

  try:
    headers = {'Authorization': self.token.authorization_header()}
    return requests.request(method, endpoint, **{'headers': headers})
  except Exception as e:
    raise error.APIConnectionError(message=e)

# https://staging.dev.matroid.com/docs/api/index.html#api-Collections-DeleteCollectionsCollectionid
@api_call(error.InvalidQueryError)
def delete_collection(self, collection_id):
  """Deletes a collection with no active indexing tasks"""
  (endpoint, method) = self.endpoints['delete_collection']
  endpoint = endpoint.replace(':key', collection_id)

  try:
    headers = {'Authorization': self.token.authorization_header()}
    return requests.request(method, endpoint, **{'headers': headers})
  except Exception as e:
    raise error.APIConnectionError(message=e)

# https://staging.dev.matroid.com/docs/api/index.html#api-Collections-GetCollectionTasksTaskid
@api_call(error.InvalidQueryError)
def get_collection_task(self, task_id):
  """Creates a new collection from a web or S3 url"""
  (endpoint, method) = self.endpoints['get_collection_task']
  endpoint = endpoint.replace(':key', task_id)

  try:
    headers = {'Authorization': self.token.authorization_header()}
    return requests.request(method, endpoint, **{'headers': headers})
  except Exception as e:
    raise error.APIConnectionError(message=e)

# https://staging.dev.matroid.com/docs/api/index.html#api-Collections-GetCollectionsCollectionid
@api_call(error.InvalidQueryError)
def get_collection(self, collection_id):
  """Get information about a specific collection"""
  (endpoint, method) = self.endpoints['get_collection']
  endpoint = endpoint.replace(':key', collection_id)

  try:
    headers = {'Authorization': self.token.authorization_header()}
    return requests.request(method, endpoint, **{'headers': headers})
  except Exception as e:
    raise error.APIConnectionError(message=e)

# https://staging.dev.matroid.com/docs/api/index.html#api-Collections-PostCollectionTasksTaskidKill
@api_call(error.InvalidQueryError)
def kill_collection_index(self, task_id, include_collection_info):
  """Kills an active collection indexing task"""
  (endpoint, method) = self.endpoints['kill_collection_index']
  endpoint = endpoint.replace(':key', task_id)

  try:
    headers = {'Authorization': self.token.authorization_header()}
    data = {
        'includeCollectionInfo': 'true' if include_collection_info else ''
    }
    return requests.request(method, endpoint, **{'headers': headers, 'data': data})
  except Exception as e:
    raise error.APIConnectionError(message=e)


# https://staging.dev.matroid.com/docs/api/index.html#api-Collections-PostApiVersionCollectionTasksTaskidScoresQuery
@api_call(error.InvalidQueryError)
def query_collection_by_scores(self, task_id, thresholds, num_results):
  """
  Query against a collection index using a set of labels and scores as a query.
  Takes in a map of thresholds, and returns media in the collection with detections above those thresholds
  """
  (endpoint, method) = self.endpoints['query_collection_by_scores']
  endpoint = endpoint.replace(':key', task_id)

  try:
    headers = {'Authorization': self.token.authorization_header()}
    data = {
        'thresholds': json.dumps(thresholds),
        'numResults': num_results
    }
    return requests.request(method, endpoint, **{'headers': headers, 'data': data})
  except Exception as e:
    raise error.APIConnectionError(message=e)

# https://staging.dev.matroid.com/docs/api/index.html#api-Collections-PostApiCollectionTasksTaskidImageQuery
@api_call(error.InvalidQueryError)
def query_collection_by_image(self, task_id, bounding_box=None, url=None, file=None, **options):
  """
  Query against a collection index (CollectionManagerTask) using an image as key.
  Takes in an image file or url and returns similar media from the collection.
  """
  (endpoint, method) = self.endpoints['query_collection_by_image']
  endpoint = endpoint.replace(':key', task_id)

  if not file and not url:
    raise error.InvalidQueryError(
        message='Missing required parameter: file or url')

  try:
    file_to_upload = None
    headers = {'Authorization': self.token.authorization_header()}
    data = {
        'boundingBox': json.dumps(bounding_box),
        'numResults': options.get('num_results')
    }

    if file:
      file_to_upload = self.filereader.get_file(file)
      files = {'file': file_to_upload}
      return requests.request(method, endpoint, **{'headers': headers, 'files': files, 'data': data})
    else:
      data['url'] = url
      return requests.request(method, endpoint, **{'headers': headers, 'data': data})
  except IOError as e:
    raise e
  except error.InvalidQueryError as e:
    raise e
  except Exception as e:
    raise error.APIConnectionError(message=e)
  finally:
    if file_to_upload:
      file_to_upload.close()

# https://staging.dev.matroid.com/docs/api/index.html#api-Collections-PutApiVersionCollectionTasksTaskid
@api_call(error.InvalidQueryError)
def update_collection_index(self, task_id, update_index):
  """Update a collection index"""
  (endpoint, method) = self.endpoints['update_collection_index']
  endpoint = endpoint.replace(':key', task_id)

  try:
    headers = {'Authorization': self.token.authorization_header()}
    data = {
        'updateIndex': 'true' if update_index else 'false'
    }
    return requests.request(method, endpoint, **{'headers': headers, 'data': data})
  except Exception as e:
    raise error.APIConnectionError(message=e)
