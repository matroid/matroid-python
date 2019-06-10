import unittest
import time
from datetime import datetime

from .tests_helpers import set_up_client, print_test_title, print_case_pass, EVERYDAY_OBJECT_DETECTOR_ID, TEST_IMAGE_URL

COLLECTION_NAME = 'py-test-collection-{}'.format(datetime.now())
S3_BUCKET_URL = 's3://bucket/m-test-public/'


class TestCollections(unittest.TestCase):
    def setUp(self):
        print_test_title('Collections')
        self.api = set_up_client()

    def test_collections(self):
        collection_id = None
        task_id = None

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
        res = self.api.create_collection(
            name=COLLECTION_NAME, url=S3_BUCKET_URL, source_type='s3')
        collection_id = res['collection']['_id']
        self.assertIsNotNone(collection_id)

        print_case_pass('create_collection_test')
        return collection_id

    def create_collection_index_test(self, collection_id):
        res = self.api.create_collection_index(
            collection_id=collection_id, detector_id=EVERYDAY_OBJECT_DETECTOR_ID, file_types='images')
        task_id = res['collectionTask']['_id']
        self.assertIsNotNone(task_id)

        print_case_pass('create_collection_index_test')
        return task_id

    def delete_collection_test(self, collection_id):
        res = self.api.delete_collection(collection_id=collection_id)
        self.assertEqual(res['message'], 'Successfully deleted')

        print_case_pass('delete_collection_test')

    def get_collection_test(self, collection_id):
        res = self.api.get_collection(collection_id=collection_id)
        collection = res['collection']
        self.assertEqual(collection['_id'], collection_id)
        self.assertEqual(collection['name'], COLLECTION_NAME)

        print_case_pass('get_collection_test')

    def get_collection_task_test(self, task_id):
        res = self.api.get_collection_task(task_id=task_id)
        self.assertIsNotNone(res['collectionTask'])
        collection_task_id = res['collectionTask']['_id']
        self.assertEqual(collection_task_id, task_id)

        print_case_pass('get_collection_task_test')

    def update_collection_index_test(self, task_id):
        res = self.api.update_collection_index(
            task_id=task_id, update_index=False)
        self.assertIsNotNone(res['collectionTask'])
        collection_task_id = res['collectionTask']['_id']
        self.assertEqual(collection_task_id, task_id)

        print_case_pass('update_collection_index_test')

    def query_by_detection_scores_test(self, task_id):
        print(task_id)
        res = self.api.query_by_detection_scores(
            task_id=task_id, thresholds={'cat': 0.5}, num_results=5)
        self.assertIsNotNone(res['results'])

        print_case_pass('query_by_detection_scores_test')

    def query_by_image_test(self, task_id, url):
        res = self.api.query_by_image(task_id=task_id, bounding_box={
                                      "top": 0.1, "left": 0.1, "height": 0.8, "width": 0.8},  task_type='collection', num_results=1, url=url)
        self.assertIsNotNone(res['results'])

        print_case_pass('query_by_image_test')

    def kill_collection_index_test(self, task_id):
        res = self.api.kill_collection_index(
            task_id=task_id, include_collection_info=False)
        collection_task = res['collectionTask']
        self.assertIsNotNone(collection_task)
        self.assertEqual(collection_task['_id'], task_id)

        print_case_pass('kill_collection_index_test')

    def delete_collection_task_test(self, task_id):
        res = self.api.delete_collection_task(task_id=task_id)
        self.assertEqual(res['message'], 'Successfully deleted')

        print_case_pass('delete_collection_task_test')

    def delete_collection_test(self, collection_id):
        res = self.api.delete_collection(collection_id=collection_id)
        self.assertEqual(res['message'], 'Successfully deleted')

        print_case_pass('delete_collection_test')

    # helpers

    def wait_for_collection_index_stop(self, task_id):
        print('Info: waiting for collection task to stop')
        res = self.api.get_collection_task(task_id=task_id)

        while (res['collectionTask']['state'] != 'failed'):
            res = self.api.get_collection_task(task_id=task_id)
            time.sleep(2)

        print('Info: collection task stopped.')
