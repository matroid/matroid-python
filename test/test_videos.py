import pytest

from data import TEST_IMAGE_URL, EVERYDAY_OBJECT_DETECTOR_ID, TEST_VIDEO_URL, RAMDOM_MONGO_ID
from matroid.error import InvalidQueryError
from test.helper import print_test_pass


class TestVideos(object):
  def test_videos(self, set_up_client):
    threshold = 0.3

    # set up client
    self.api = set_up_client

    # start testing
    video_id = self.classify_video_test(
        detector_id=EVERYDAY_OBJECT_DETECTOR_ID, url=TEST_VIDEO_URL)
    self.get_video_results_test(video_id=video_id, threshold=threshold)

  def classify_video_test(self, detector_id, url):
    with pytest.raises(InvalidQueryError) as e:
      self.api.classify_video(detectorId=detector_id, url='invlid-url')
    assert ('invalid_query_err' in str(e))

    res = self.api.classify_video(
        detectorId=detector_id, url=url)
    video_id = res['videoId']
    assert(video_id != None)

    print_test_pass()
    return video_id

  def get_video_results_test(self, video_id, threshold):
    with pytest.raises(InvalidQueryError) as e:
      self.api.classify_video(detectorId=RAMDOM_MONGO_ID, url='invlid-url')
    assert ('invalid_query_err' in str(e))

    res = self.api.get_video_results(
        videoId=video_id, threshold=threshold)
    assert (res != None)

    print_test_pass()
