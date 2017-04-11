import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import matroid
from matroid.client import MatroidAPI

SAMPLE_IMAGE_URL = 'https://www.matroid.com/images/logo2.png'
SAMPLE_VIDEO_URL = 'https://www.youtube.com/watch?v=N8T6AqYKRpA'


class APIFunctionalTest(unittest.TestCase):

  def test_list_detectors(self):
    client = MatroidAPI(options={'json_format': True})
    result = client.list_detectors()
    self.assertTrue(result[0]['detector_id'])

if __name__ == '__main__':
  unittest.main()
