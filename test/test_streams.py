from datetime import datetime
import time
import os
import unittest

from .tests_helpers import set_up_client, print_test_title, print_case_pass, EVERYDAY_OBJECT_DETECTOR_ID, TEST_VIDEO_URL


class TestStreams(unittest.TestCase):
    def setUp(self):
        print_test_title('Streams')
        self.api = set_up_client()

    def test_stream(self):
        stream_id = None
        monitoring_id = None

        stream_name = 'py-test-stream-{}'.format(datetime.now())
        thresholds = {'cat': 0.5, 'dog': 0.6}
        task_name = 'test-task'

        try:
            stream_id = self.create_stream_test(
                stream_url=TEST_VIDEO_URL, stream_name=stream_name)
            monitoring_id = self.monitor_stream_test(
                stream_id=stream_id, detector_id=EVERYDAY_OBJECT_DETECTOR_ID, thresholds=thresholds, task_name=task_name)
            self.search_monitorings_test(
                stream_id=stream_id, monitoring_id=monitoring_id)
            self.search_streams_test()
            self.get_monitoring_result_test(monitoring_id=monitoring_id)
        finally:
            if monitoring_id:
                self.kill_monitoring_test(monitoring_id=monitoring_id)
                self.wait_for_monitoring_stop(monitoring_id=monitoring_id)
                self.delete_monitoring_test(monitoring_id=monitoring_id)
            if stream_id:
                self.delete_stream_test(stream_id=stream_id)

    # test cases

    def create_stream_test(self, stream_url, stream_name):
        res = self.api.create_stream(
            stream_url=stream_url,
            stream_name=stream_name
        )
        self.assertIsNotNone(res['stream_id'])

        print_case_pass('create_stream_test')
        return res['stream_id']

    def monitor_stream_test(self, stream_id, detector_id, thresholds, task_name):
        end_time = '5 minutes'
        res = self.api.monitor_stream(stream_id=stream_id, detector_id=detector_id,
                                      thresholds=thresholds, end_time=end_time, task_name=task_name)
        self.assertIsNotNone(res['monitoring_id'])

        print_case_pass('monitor_stream_test')
        return res['monitoring_id']

    def search_monitorings_test(self, stream_id, monitoring_id):
        res = self.api.search_monitorings(stream_id=stream_id)
        self.assertEqual(res[0]['monitoring_id'], monitoring_id)

        print_case_pass('search_monitorings_test')

    def search_streams_test(self):
        res = self.api.search_streams(permission='private')
        self.assertIsNotNone(res[0]['stream_id'])

        print_case_pass('search_streams_test')

    def get_monitoring_result_test(self, monitoring_id):
        res = self.api.get_monitoring_result(monitoring_id=monitoring_id)
        self.assertIsNotNone(res)

        print_case_pass('get_monitoring_result_test')

    def kill_monitoring_test(self, monitoring_id):
        res = self.api.kill_monitoring(monitoring_id=monitoring_id)
        self.assertEqual(res['message'], 'Successfully killed monitoring.')

        print_case_pass('kill_monitoring_test')

    def delete_monitoring_test(self, monitoring_id):
        res = self.api.delete_monitoring(monitoring_id=monitoring_id)
        self.assertEqual(res['message'], 'Successfully deleted monitoring.')

        print_case_pass('delete_monitoring_test')

    def delete_stream_test(self, stream_id):
        res = self.api.delete_stream(stream_id=stream_id)
        self.assertEqual(res['message'], 'Successfully deleted stream.')

        print_case_pass('delete_stream_test')

    # Helpers
    def wait_for_monitoring_stop(self, monitoring_id):
        print('Info: waiting for monitoring to stop')
        res = self.api.search_monitorings(monitoring_id=monitoring_id)

        while (res[0]['state'] != 'failed' and res[0]['state'] != 'scheduled'):
            res = self.api.search_monitorings(monitoring_id=monitoring_id)
            time.sleep(2)

        print('Info: monitoring stopped.')
