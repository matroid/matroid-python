from datetime import datetime
import time
import os
import sys
import pytest

from test.data import EVERYDAY_OBJECT_DETECTOR_ID, TEST_S3_VIDEO_URL, TEST_S3_VIDEO_URL_2, TEST_VIDEO_URL, RANDOM_MONGO_ID
from matroid.error import InvalidQueryError, APIError
from test.helper import print_test_pass


class TestStreams(object):
  def test_stream(self, set_up_client):
    stream_id = None
    stream_id_2 = None
    monitoring_id = None

    stream_name = 'py-test-stream-{}'.format(datetime.now())
    stream_name_2 = 'py-test-stream-2-{}'.format(datetime.now())
    thresholds = {'cat': 0.5, 'dog': 0.6}
    task_name = 'test-task'

    # set up client
    self.api = set_up_client

    # start testing
    try:
      stream_id = self.create_stream_test(
          url=TEST_S3_VIDEO_URL, name=stream_name)
      stream_id_2 = self.register_stream_test(
          url=TEST_S3_VIDEO_URL_2, name=stream_name_2)
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
      if stream_id_2:
        self.delete_stream_test(stream_id=stream_id_2)

  # test cases
  def create_stream_test(self, url, name):
    res = self.api.create_stream(
        url=url,
        name=name
    )
    assert (res['streamId'] != None)

    with pytest.raises(APIError) as e:
      self.api.create_stream(url=url, name=name)
    assert ('invalid_query_err' in str(e))

    print_test_pass()
    return res['streamId']

  def register_stream_test(self, url, name):
    res = self.api.register_stream(
      url=url,
      name=name
    )
    assert (res['streamId'] != None)

    with pytest.raises(APIError) as e:
      self.api.register_stream(url=url, name=name)
    assert ('invalid_query_err' in str(e))

    print_test_pass()
    return res['streamId']

  def monitor_stream_test(self, stream_id, detector_id, thresholds, task_name):
    end_time = '5 minutes'

    with pytest.raises(APIError) as e:
      self.api.monitor_stream(streamId=RANDOM_MONGO_ID, detectorId=detector_id,
                              thresholds=thresholds, endTime=end_time, taskName=task_name)
    assert ('invalid_query_err' in str(e))

    res = self.api.monitor_stream(streamId=stream_id, detectorId=detector_id,
                                  thresholds=thresholds, endTime=end_time, taskName=task_name)
    assert(res['monitoringId'] != None)

    print_test_pass()
    return res['monitoringId']

  def search_monitorings_test(self, stream_id, monitoring_id):
    res = self.api.search_monitorings(streamId=stream_id)
    assert (res[0]['monitoringId'] == monitoring_id)
    print_test_pass()

  def search_streams_test(self):
    res = self.api.search_streams(permission='private')
    assert (res[0]['streamId'] != None)
    print_test_pass()

  def get_monitoring_result_test(self, monitoring_id):
    res = self.api.get_monitoring_result(monitoringId=monitoring_id)
    assert (res != None)
    print_test_pass()

  def kill_monitoring_test(self, monitoring_id):
    res = self.api.kill_monitoring(monitoringId=monitoring_id)
    assert (res['message'] == 'Successfully killed monitoring.')
    print_test_pass()

  def delete_monitoring_test(self, monitoring_id):
    res = self.api.delete_monitoring(monitoringId=monitoring_id)
    assert (res['message'] == 'Successfully deleted monitoring.')
    print_test_pass()

  def delete_stream_test(self, stream_id):
    res = self.api.delete_stream(streamId=stream_id)
    assert (res['message'] == 'Successfully deleted stream.')
    print_test_pass()

  # helpers
  def wait_for_monitoring_stop(self, monitoring_id):
    print('Info: waiting for monitoring to stop')
    res = self.api.search_monitorings(monitoringId=monitoring_id)

    num_tried = 0
    max_tries = 15
    while (res[0]['state'] != 'failed' and res[0]['state'] != 'scheduled'):
      if num_tried > max_tries:
        pytest.fail('Timeout when waiting for monitoring to stop')

      res = self.api.search_monitorings(monitoringId=monitoring_id)
      time.sleep(2)

      num_tried += 1

    print('Info: monitoring stopped.')
