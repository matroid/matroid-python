import unittest

from .tests_helpers import set_up_client, print_test_title, print_case_pass, TEST_IMAGE_URL, EVERYDAY_OBJECT_DETECTOR_ID, YOUTUBE_VIDEO_URL


class TestVideos(unittest.TestCase):
    def setUp(self):
        print_test_title('TestVideos')
        self.api = set_up_client()

    def test_videos(self):
        threshold = 0.3

        video_id = self.classify_video_test(
            detector_id=EVERYDAY_OBJECT_DETECTOR_ID, url=YOUTUBE_VIDEO_URL)
        self.get_video_results_test(video_id=video_id, threshold=threshold)

    def classify_video_test(self, detector_id, url):
        res = self.api.classify_video(
            detector_id=detector_id, url=url)
        video_id = res['video_id']
        self.assertIsNotNone(video_id)

        print_case_pass('classify_video_test')
        return video_id

    def get_video_results_test(self, video_id, threshold):
        res = self.api.get_video_results(
            video_id=video_id, threshold=threshold)
        self.assertIsNotNone(res)

        print_case_pass('get_video_results_test')
