import pytest

from data import TEST_IMAGE_URL, EVERYDAY_OBJECT_DETECTOR_ID, YOUTUBE_VIDEO_URL


class TestVideos(object):
  def test_videos(self, set_up_client):
    threshold = 0.3

    # set up client
    self.api = set_up_client

    # start testing
    video_id = self.classify_video_test(
      detector_id=EVERYDAY_OBJECT_DETECTOR_ID, url=YOUTUBE_VIDEO_URL)
    self.get_video_results_test(video_id=video_id, threshold=threshold)

  def classify_video_test(self, detector_id, url):
    res = self.api.classify_video(
      detector_id=detector_id, url=url)
    video_id = res['video_id']
    assert(video_id != None)

    return video_id

  def get_video_results_test(self, video_id, threshold):
    res = self.api.get_video_results(
      video_id=video_id, threshold=threshold)
    assert(res != None)
