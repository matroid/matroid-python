import time
from datetime import datetime
import pytest

from data import EVERYDAY_OBJECT_DETECTOR_ID, TEST_IMAGE_URL, RAMDOM_MONGO_ID
from matroid.error import InvalidQueryError

COLLECTION_NAME = 'py-test-collection-{}'.format(datetime.now())
S3_BUCKET_URL = 's3://bucket/m-test-public/'

class TestCollections(object):
  def test_collections(self, set_up_client):
    collection_id = None
    task_id = None

    # set up client
    self.api = set_up_client

    # start testing
    try:
      collection_id = self.create_collection_test()
      task_id = self.create_collection_index_test(collection_id)
      self.get_collection_test(collection_id)
      self.get_collection_task_test(task_id)
      self.kill_collection_index_test(task_id)
      self.wait_for_collection_index_stop(task_id)
      self.update_collection_index_test(task_id)
    finally:
      if task_id:
        self.kill_collection_index_test(task_id)
        self.wait_for_collection_index_stop(task_id)
        self.delete_collection_task_test(task_id)
      if collection_id:
        self.delete_collection_test(collection_id)

  # test cases
  def create_collection_test(self):
    with pytest.raises(InvalidQueryError) as e:
      self.api.create_collection(name='invalid-collection', url='invalid-url', source_type='s3')
    assert ('invalid_query_err' in str(e))

    res = self.api.create_collection(
      name=COLLECTION_NAME, url=S3_BUCKET_URL, source_type='s3')
    collection_id = res['collection']['_id']
    assert(collection_id != None)

    return collection_id

  def create_collection_index_test(self, collection_id):
    with pytest.raises(InvalidQueryError) as e:
      self.api.create_collection_index(
        collection_id=collection_id, detector_id=RAMDOM_MONGO_ID, file_types='images')
    assert ('invalid_query_err' in str(e))

    res = self.api.create_collection_index(
      collection_id=collection_id, detector_id=EVERYDAY_OBJECT_DETECTOR_ID, file_types='images')
    task_id = res['collectionTask']['_id']
    assert(task_id != None)

    return task_id

  def delete_collection_test(self, collection_id):
    res = self.api.delete_collection(collection_id=collection_id)
    assert(res['message'] == 'Successfully deleted')

  def get_collection_test(self, collection_id):
    res = self.api.get_collection(collection_id=collection_id)
    collection = res['collection']
    assert(collection['_id'] == collection_id)
    assert(collection['name'] == COLLECTION_NAME)

  def get_collection_task_test(self, task_id):
    res = self.api.get_collection_task(task_id=task_id)
    assert(res['collectionTask'] != None)
    collection_task_id = res['collectionTask']['_id']
    assert(collection_task_id == task_id)

  def update_collection_index_test(self, task_id):
    res = self.api.update_collection_index(
      task_id=task_id, update_index=False)
    assert(res['collectionTask'] != None)
    collection_task_id = res['collectionTask']['_id']
    assert(collection_task_id == task_id)

  def query_by_detection_scores_test(self, task_id):
    print(task_id)
    res = self.api.query_by_detection_scores(
        task_id=task_id, thresholds={'cat': 0.5}, num_results=5)
    assert(res['results'] != None)

  def query_by_image_test(self, task_id, url):
    res = self.api.query_by_image(task_id=task_id, bounding_box={
                                  "top": 0.1, "left": 0.1, "height": 0.8, "width": 0.8},  task_type='collection', num_results=1, url=url)
    assert(res['results'] != None)

  def kill_collection_index_test(self, task_id):
    res = self.api.kill_collection_index(
      task_id=task_id, include_collection_info=False)
    collection_task = res['collectionTask']
    assert(collection_task != None)
    assert(collection_task['_id'] == task_id)

  def delete_collection_task_test(self, task_id):
    res = self.api.delete_collection_task(task_id=task_id)
    assert(res['message'] == 'Successfully deleted')

  def delete_collection_test(self, collection_id):
    res = self.api.delete_collection(collection_id=collection_id)
    assert(res['message'] == 'Successfully deleted')

  # helpers
  def wait_for_collection_index_stop(self, task_id):
    print('Info: waiting for collection task to stop')
    res = self.api.get_collection_task(task_id=task_id)

    tried_num = 0
    max_tries = 15
    while (res['collectionTask']['state'] != 'failed'):
      if tried_num > max_tries:
        pytest.fail('Timeout when waiting for collection index to stop')

      res = self.api.get_collection_task(task_id=task_id)
      time.sleep(2)

      tried_num += 1

    print('Info: collection task stopped.')
