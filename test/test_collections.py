import time
from datetime import datetime
import pytest

from test.data import EVERYDAY_OBJECT_DETECTOR_ID, TEST_IMAGE_URL, RANDOM_MONGO_ID
from matroid.error import InvalidQueryError, APIError
from test.helper import print_test_pass

COLLECTION_NAME = 'py-test-collection-{}'.format(datetime.now())
S3_BUCKET_URL = 's3://bucket/m-test-public/'


class TestCollections(object):

  def test_collections(self, set_up_client):
    collection_id = None
    task_id = None

    # set up client
    self.api = set_up_client
    task_killed = False

    # start testing
    try:
      collection_id = self.create_collection_test()
      task_id = self.create_collection_index_test(collection_id)
      self.get_collection_test(collection_id)
      self.get_collection_task_test(task_id)
      self.kill_collection_index_test(task_id)
      task_killed = True
      self.wait_for_collection_index_stop(task_id)
      self.update_collection_index_test(task_id)
      task_killed = False
    finally:
      if task_id:
        if not task_killed:
          self.kill_collection_index_test(task_id)
        self.wait_for_collection_index_stop(task_id)
        self.delete_collection_index_test(task_id)
      if collection_id:
        self.delete_collection_test(collection_id)

  # test cases
  def create_collection_test(self):
    with pytest.raises(APIError) as e:
      self.api.create_collection(
          name='invalid-collection', url='invalid-url', sourceType='s3')
    assert ('invalid_query_err' in str(e))

    # should create collection with correct params
    sourceType = 's3'
    res = self.api.create_collection(
        name=COLLECTION_NAME, url=S3_BUCKET_URL, sourceType=sourceType)
    collection_id = res['collection']['_id']
    assert(collection_id != None)
    assert (res['collection']['name'] == COLLECTION_NAME)
    assert (res['collection']['url'] == S3_BUCKET_URL)
    assert (res['collection']['sourceType'] == sourceType)
    assert (len(res['collection']['detectingTasks']) == 0)

    print_test_pass()
    return collection_id

  def create_collection_index_test(self, collection_id):
    with pytest.raises(APIError) as e:
      self.api.create_collection_index(
          collectionId=collection_id, detectorId=RANDOM_MONGO_ID, fileTypes='images')
    assert ('invalid_query_err' in str(e))

    res = self.api.create_collection_index(
        collectionId=collection_id, detectorId=EVERYDAY_OBJECT_DETECTOR_ID, fileTypes='images')
    task_id = res['collectionTask']['_id']
    assert (task_id != None)

    print_test_pass()
    return task_id

  def get_collection_test(self, collection_id):
    res = self.api.get_collection(collectionId=collection_id)
    collection = res['collection']
    assert(collection['_id'] == collection_id)
    assert (collection['name'] == COLLECTION_NAME)
    print_test_pass()

  def get_collection_task_test(self, task_id):
    res = self.api.get_collection_task(taskId=task_id)
    assert(res['collectionTask'] != None)
    collection_task_id = res['collectionTask']['_id']
    assert (collection_task_id == task_id)
    print_test_pass()

  def update_collection_index_test(self, task_id):
    res = self.api.update_collection_index(
        taskId=task_id, updateIndex=False)
    assert(res['collectionTask'] != None)
    collection_task_id = res['collectionTask']['_id']
    assert (collection_task_id == task_id)
    print_test_pass()

  def query_collection_by_scores_test(self, task_id):
    print(task_id)
    res = self.api.query_collection_by_scores(
        taskId=task_id, thresholds={'cat': 0.5}, numResults=5)
    assert (res['results'] != None)
    print_test_pass()

  def query_collection_by_image_test(self, task_id, url):
    res = self.api.query_collection_by_image(taskId=task_id, numResults=1, url=url, boundingBox={
        "top": 0.1, "left": 0.1, "height": 0.8, "width": 0.8})
    assert (res['results'] != None)
    print_test_pass()

  def kill_collection_index_test(self, task_id):
    res = self.api.kill_collection_index(
        taskId=task_id, includeCollectionInfo=False)
    collection_task = res['collectionTask']
    assert(collection_task != None)
    assert (collection_task['_id'] == task_id)
    print_test_pass()

  def delete_collection_index_test(self, task_id):
    res = self.api.delete_collection_index(taskId=task_id)
    assert (res['message'] == 'Successfully deleted')
    print_test_pass()

  def delete_collection_test(self, collection_id):
    res = self.api.delete_collection(collectionId=collection_id)
    assert (res['message'] == 'Successfully deleted')
    print_test_pass()

  # helpers
  def wait_for_collection_index_stop(self, task_id):
    print('Info: waiting for collection task to stop')
    res = self.api.get_collection_task(taskId=task_id)

    tried_num = 0
    max_tries = 15
    while (res['collectionTask']['state'] != 'failed'):
      if tried_num > max_tries:
        pytest.fail('Timeout when waiting for collection index to stop')

      res = self.api.get_collection_task(taskId=task_id)
      time.sleep(2)

      tried_num += 1

    print('Info: collection task stopped.')
