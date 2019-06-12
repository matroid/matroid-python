import pytest

from data import TEST_IMAGE_URL, EVERYDAY_OBJECT_DETECTOR_ID


class TestImages(object):
  def test_images(self, set_up_client):
    localizer_label = 'cat'

    # set up client
    self.api = set_up_client

    # start testing
    self.classify_image_test(
      detector_id=EVERYDAY_OBJECT_DETECTOR_ID, url=TEST_IMAGE_URL)
    self.localize_image_test(
      localizer=EVERYDAY_OBJECT_DETECTOR_ID, localizer_label=localizer_label, url=TEST_IMAGE_URL)

  def classify_image_test(self, detector_id, url):
    res = self.api.classify_image(detector_id=detector_id, url=url)
    assert(res['results'][0]['predictions'] != None)

  def localize_image_test(self, localizer, localizer_label, url):
    res = self.api.localize_image(
      localizer=localizer, localizer_label=localizer_label, url=url)
    assert(res['results'][0]['predictions'] != None)
