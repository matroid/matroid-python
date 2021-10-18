from datetime import datetime
import time
import pytest

from test.data import TEST_LOCAL_VIDEO_URL, TEST_S3_VIDEO_URL, TEST_VIDEO_URL
from matroid.error import APIError
from test.helper import print_test_pass

class TestVideoSummary(object):
  def test_video_summary(self, set_up_client):
    stream_id = None
    url_video_summary_id = None
    local_video_summary_id = None
    stream_summary_id = None
    stream_name = 'py-test-stream-{}'.format(datetime.now())
    one_day = 24 * 60 * 60

    # set up client
    self.api = set_up_client

    # start testing
    try:
      self.create_video_summary_test(url=TEST_VIDEO_URL, file=TEST_LOCAL_VIDEO_URL)
      url_video_summary_id = self.create_video_summary_test(
          url=TEST_VIDEO_URL)
      local_video_summary_id = self.create_video_summary_test(
          file=TEST_LOCAL_VIDEO_URL)
      self.get_video_summary_test(summaryId=url_video_summary_id)
      self.get_video_summary_tracks_test()
      self.get_video_summary_file_test()
      stream_id = self.create_stream_test(url=TEST_S3_VIDEO_URL, name=stream_name, dmca=True)
      self.create_stream_summary_test(
        streamId=stream_id,
        startTime=datetime.utcfromtimestamp(int(time.time()) - (one_day * 2)),
        endTime=datetime.utcfromtimestamp(int(time.time()) - (one_day))
      )
      self.get_stream_summaries_test(streamId=stream_id)
    finally:
      if url_video_summary_id:
        self.delete_video_summary_test(summaryId=url_video_summary_id)
      if local_video_summary_id:
        self.delete_video_summary_test(summaryId=local_video_summary_id)
      if stream_summary_id:
        self.delete_video_summary_test(summaryId=stream_summary_id)
      if stream_id:
        self.delete_stream_test(streamId=stream_id)

  # test cases
  def create_video_summary_test(self, url=None, videoId=None, file=None):
    if url and file:
      with pytest.raises(APIError) as e:
        self.api.create_video_summary(url=url, file=file)
      assert ('You may only specify a file or a URL, not both' in str(e))

    if url:
      with pytest.raises(APIError) as e:
        self.api.create_video_summary(url=TEST_LOCAL_VIDEO_URL)
      assert ('You provided an invalid URL' in str(e))

      res = self.api.create_video_summary(
          url=url,
      )
    if file:
      res = self.api.create_video_summary(
          file=file,
      )

    assert (res['summary'] != None)
    assert (res['summary']['video'] != None)

    print_test_pass()
    return res['summary']['_id']

  def get_video_summary_test(self, summaryId):
    with pytest.raises(APIError) as e:
      self.api.get_video_summary(summaryId='123')
    assert ('invalid_query_err' in str(e))

    res = self.api.get_video_summary(summaryId=summaryId)

    assert (res['progress'] == 0)
    assert (res['state'] == 'requested')

    print_test_pass()

  def get_video_summary_tracks_test(self):
    with pytest.raises(APIError) as e:
      self.api.get_video_summary_tracks(summaryId='123')
    assert ('invalid_query_err' in str(e))

    print_test_pass()

  def get_video_summary_file_test(self):
    with pytest.raises(APIError) as e:
      self.api.get_video_summary_file(summaryId='123')
    assert ('invalid_query_err' in str(e))

    print_test_pass()

  def create_stream_summary_test(self, streamId, startTime, endTime):
    with pytest.raises(APIError) as e:
      self.api.create_stream_summary(
        streamId=streamId,
        startTime='test',
        endTime=endTime
      )
    assert ('Invalid dates provided' in str(e))
    with pytest.raises(APIError) as e:
      self.api.create_stream_summary(
        streamId=streamId,
        startTime=datetime.utcfromtimestamp(int(time.time()) - (24 * 60 * 60 * 8)),
        endTime=endTime
      )
    assert ("Provided dates are not within your stream's retention period" in str(e))

    res = self.api.create_stream_summary(streamId, startTime, endTime)
    assert (res['summary']['feed'] == streamId)
    assert (datetime.strptime(res['summary']['startTime'], '%Y-%m-%dT%H:%M:%S.000Z') == startTime)
    assert (datetime.strptime(res['summary']['endTime'], '%Y-%m-%dT%H:%M:%S.000Z') == endTime)

    print_test_pass()

  def get_stream_summaries_test(self, streamId):
    res = self.api.get_stream_summaries(streamId)
    assert (len(res['summaries']) == 1)

    print_test_pass()

  def create_stream_test(self, url, name, dmca):
    res = self.api.create_stream(url=url, name=name, dmca=dmca)

    assert (res['streamId'] != None)

    print_test_pass()
    return res['streamId']

  def delete_stream_test(self, streamId):
    res = self.api.delete_stream(streamId=streamId)
    assert (res['message'] == 'Successfully deleted stream.')
    print_test_pass()

  def delete_video_summary_test(self, summaryId):
    with pytest.raises(APIError) as e:
      self.api.delete_video_summary(summaryId='123')
    assert ('invalid_query_err' in str(e))

    res = self.api.delete_video_summary(summaryId=summaryId)
    assert (res['summaryId'] == summaryId)
    print_test_pass()