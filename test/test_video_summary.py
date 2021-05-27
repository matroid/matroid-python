from datetime import datetime
import time
import os
import sys
import pytest

from test.data import EVERYDAY_OBJECT_DETECTOR_ID, TEST_LOCAL_VIDEO_URL, TEST_S3_VIDEO_URL, TEST_S3_VIDEO_URL_2, TEST_VIDEO_URL, RANDOM_MONGO_ID
from matroid.error import InvalidQueryError, APIError
from test.helper import print_test_pass


class TestVideoSummary(object):
  def test_video_summary(self, set_up_client):
    stream_id = None
    url_video_summary_id = None
    local_video_summary_id = None
    stream_summary_id = None

    stream_name = 'py-test-stream-{}'.format(datetime.now())

    # set up client
    self.api = set_up_client

    # start testing
    try:
      url_video_summary_id = self.create_video_summary_test(
          url=TEST_VIDEO_URL)
      local_video_summary_id = self.create_video_summary_test(
          file=TEST_LOCAL_VIDEO_URL)
      self.get_video_summary(url_video_summary_id)
      self.get_video_summary_tracks(url_video_summary_id)
      self.get_video_summary_file(url_video_summary_id)

