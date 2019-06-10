import unittest

from .helpers import set_up_client, print_test_title, print_case_pass, TEST_IMAGE_URL, EVERYDAY_OBJECT_DETECTOR_ID


class TestImages(unittest.TestCase):
    def setUp(self):
        print_test_title('TestImages')
        self.api = set_up_client()

    def test_images(self):
        localizer_label = 'cat'

        self.classify_image_test(
            detector_id=EVERYDAY_OBJECT_DETECTOR_ID, url=TEST_IMAGE_URL)
        self.localize_image_test(
            localizer=EVERYDAY_OBJECT_DETECTOR_ID, localizer_label=localizer_label, url=TEST_IMAGE_URL)

    def classify_image_test(self, detector_id, url):
        res = self.api.classify_image(detector_id=detector_id, url=url)
        self.assertIsNotNone(res['results'])

        print_case_pass('classify_image_test')

    def localize_image_test(self, localizer, localizer_label, url):
        res = self.api.localize_image(
            localizer=localizer, localizer_label=localizer_label, url=url)
        self.assertIsNotNone(res['results'])

        print_case_pass('localize_image_test')
