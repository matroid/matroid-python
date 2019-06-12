from datetime import datetime
import time
import os
import sys
import pytest

from data import EVERYDAY_OBJECT_DETECTOR_ID, TEST_VIDEO_URL, RAMDOM_MONGO_ID
from matroid.error import InvalidQueryError


class TestStreams(object):
  def test_stream(self, set_up_client):
    stream_id = None
    monitoring_id = None

    stream_name = 'py-test-stream-{}'.format(datetime.now())
    thresholds = {'cat': 0.5, 'dog': 0.6}
    task_name = 'test-task'

    # set up client
    self.api = set_up_client

    # start testing
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
    assert (res['stream_id'] != None)

    with pytest.raises(InvalidQueryError) as e:
      self.api.create_stream(stream_url=stream_url, stream_name=stream_name)
    assert ('invalid_query_err' in str(e))

    return res['stream_id']

  def monitor_stream_test(self, stream_id, detector_id, thresholds, task_name):
    end_time = '5 minutes'

    with pytest.raises(InvalidQueryError) as e:
      self.api.monitor_stream(stream_id=RAMDOM_MONGO_ID, detector_id=detector_id,
                              thresholds=thresholds, end_time=end_time, task_name=task_name)
    assert ('invalid_query_err' in str(e))

    res = self.api.monitor_stream(stream_id=stream_id, detector_id=detector_id,
                                  thresholds=thresholds, end_time=end_time, task_name=task_name)
    assert(res['monitoring_id'] != None)

    return res['monitoring_id']

  def search_monitorings_test(self, stream_id, monitoring_id):
    res = self.api.search_monitorings(stream_id=stream_id)
    assert(res[0]['monitoring_id'] == monitoring_id)

  def search_streams_test(self):
    res = self.api.search_streams(permission='private')
    assert(res[0]['stream_id'] != None)

  def get_monitoring_result_test(self, monitoring_id):
    res = self.api.get_monitoring_result(monitoring_id=monitoring_id)
    assert(res != None)

  def kill_monitoring_test(self, monitoring_id):
    res = self.api.kill_monitoring(monitoring_id=monitoring_id)
    assert(res['message'] == 'Successfully killed monitoring.')

  def delete_monitoring_test(self, monitoring_id):
    res = self.api.delete_monitoring(monitoring_id=monitoring_id)
    assert(res['message'] == 'Successfully deleted monitoring.')

  def delete_stream_test(self, stream_id):
    res = self.api.delete_stream(stream_id=stream_id)
    assert(res['message'] == 'Successfully deleted stream.')

  # helpers
  def wait_for_monitoring_stop(self, monitoring_id):
    print('Info: waiting for monitoring to stop')
    res = self.api.search_monitorings(monitoring_id=monitoring_id)

    num_tried = 0
    max_tries = 15
    while (res[0]['state'] != 'failed' and res[0]['state'] != 'scheduled'):
      if num_tried > max_tries:
        pytest.fail('Timeout when waiting for monitoring to stop')

      res = self.api.search_monitorings(monitoring_id=monitoring_id)
      time.sleep(2)

      num_tried += 1

    print('Info: monitoring stopped.')
