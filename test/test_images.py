import pytest

from data import TEST_IMAGE_URL, TEST_IMAGE_URL_DOG, TEST_IMAGE_FILE, TEST_IMAGE_FILE_DOG, EVERYDAY_OBJECT_DETECTOR_ID
from matroid.error import InvalidQueryError

class TestImages(object):
  def test_images(self, set_up_client):
    localizer_label = 'cat'
    urls = [TEST_IMAGE_URL, TEST_IMAGE_URL_DOG]
    files = [TEST_IMAGE_FILE_DOG, TEST_IMAGE_FILE]

    # set up client
    self.api = set_up_client

    # start testing
    self.classify_image_test(
      detector_id=EVERYDAY_OBJECT_DETECTOR_ID, url=TEST_IMAGE_URL, file=TEST_IMAGE_FILE, urls=urls, files=files)
    self.localize_image_test(
      localizer=EVERYDAY_OBJECT_DETECTOR_ID, localizer_label=localizer_label, url=TEST_IMAGE_URL)

  def classify_image_test(self, detector_id, url, urls, file, files):
    with pytest.raises(InvalidQueryError) as e:
      self.api.classify_image(detector_id=detector_id, url='invalid-url')
    assert ('invalid_query_err' in str(e))

    res = self.api.classify_image(detector_id=detector_id, url=url)
    assert (res['results'][0]['predictions'] != None)
    
    res = self.api.classify_image(detector_id=detector_id, file=file)
    assert(res['results'][0]['predictions'] != None)
    
    res = self.api.classify_image(detector_id=detector_id, file=files)
    assert(len(res['results']) == 2)
    assert(res['results'][0]['predictions'] != None)
    
    res = self.api.classify_image(detector_id=detector_id, url=urls)
    assert(len(res['results']) == 2)
    assert(res['results'][0]['predictions'] != None)

  def localize_image_test(self, localizer, localizer_label, url):
    res = self.api.localize_image(
      localizer=localizer, localizer_label=localizer_label, url=url)
    assert(res['results'][0]['predictions'] != None)
