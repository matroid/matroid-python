import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import matroid
from matroid.client import MatroidAPI

SAMPLE_IMAGE_URL = 'https://www.matroid.com/images/logo2.png'
SAMPLE_VIDEO_URL = 'https://www.youtube.com/watch?v=N8T6AqYKRpA'
SAMPLE_DETECTOR = 'test'  # will not charge for the API call
SAMPLE_VIDEO_ID = 'test'  # will not charge for the API call


class APIFunctionalTest(unittest.TestCase):

  def test_list_detectors(self):
    client = MatroidAPI(options={'json_format': True})
    result = client.list_detectors()
    self.assertTrue(result[0]['detector_id'])

  def test_classify_image(self):
    client = MatroidAPI(options={'json_format': True})
    result = client.classify_image(
        detector_id=SAMPLE_DETECTOR, image_url=SAMPLE_IMAGE_URL)
    self.assertTrue(result['results'][0]['predictions'])
    predictions = result['results'][0]['predictions']
    cat_score = predictions[0]['labels']['cat']
    self.assertEqual(cat_score, 0.71)
    dog_score = predictions[0]['labels']['dog']
    self.assertEqual(dog_score, 0.29)

  def test_classify_video(self):
    client = MatroidAPI(options={'json_format': True})
    result = client.classify_video(
        detector_id=SAMPLE_DETECTOR, video_url=SAMPLE_VIDEO_URL)
    self.assertTrue(result['video_id'])

  def test_get_video_results(self):
    client = MatroidAPI(options={'json_format': True})
    result = client.get_video_results(video_id=SAMPLE_VIDEO_ID)
    self.assertTrue(result['detections'])
    detections = result['detections']
    self.assertEqual(detections['3']['0'], 88)

if __name__ == '__main__':
  unittest.main()
