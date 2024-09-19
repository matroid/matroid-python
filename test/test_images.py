import pytest

from test.data import (
    TEST_IMAGE_URL,
    TEST_IMAGE_URL_DOG,
    TEST_IMAGE_FILE,
    TEST_IMAGE_FILE_DOG,
    EVERYDAY_OBJECT_DETECTOR_ID,
    EVERYDAY_OBJECT_SEGMENTOR_ID,
)
from matroid.error import InvalidQueryError, APIError
from test.helper import print_test_pass


class TestImages(object):
    def test_images(self, set_up_client):
        localizer_label = "cat"
        urls = [TEST_IMAGE_URL, TEST_IMAGE_URL_DOG]
        files = [TEST_IMAGE_FILE_DOG, TEST_IMAGE_FILE]

        # set up client
        self.api = set_up_client

        # start testing
        # self.classify_image_test(
        #     detector_id=EVERYDAY_OBJECT_DETECTOR_ID, url=TEST_IMAGE_URL, file=TEST_IMAGE_FILE, urls=urls, files=files)
        self.localize_image_test(
            localizer=EVERYDAY_OBJECT_DETECTOR_ID,
            localizer_label=localizer_label,
            url=TEST_IMAGE_URL,
        )

        self.segment_image_test(
            detector_id=EVERYDAY_OBJECT_SEGMENTOR_ID,
            url=TEST_IMAGE_URL,
            expected_label=localizer_label,
        )

    def classify_image_test(self, detector_id, url, urls, file, files):
        with pytest.raises(APIError) as e:
            # self.api.classify_image(detectorId=detector_id, url='invalid-url')
            self.api.classify_image(detectorId=detector_id)
        assert "invalid_query_err" in str(e)
        print("Classify invalid url test passed")

        res = self.api.classify_image(detectorId=detector_id, url=url)
        assert res["results"][0]["predictions"] != None
        print("Classify one url test passed")

        res = self.api.classify_image(detectorId=detector_id, file=file)
        assert res["results"][0]["predictions"] != None
        print("Classify one file test passed")

        res = self.api.classify_image(detectorId=detector_id, file=files)
        assert len(res["results"]) == 2
        assert res["results"][0]["predictions"] != None
        print("Classify multiple files test passed")

        res = self.api.classify_image(detectorId=detector_id, url=urls)
        assert len(res["results"]) == 2
        assert res["results"][0]["predictions"] != None
        print("Classify multiple urls test passed")

        print_test_pass()

    def localize_image_test(self, localizer, localizer_label, url):
        res = self.api.localize_image(
            localizer=localizer, localizerLabel=localizer_label, url=url
        )
        assert res["results"][0]["predictions"] != None

        print_test_pass()

    def segment_image_test(self, detector_id, url, expected_label):
        res = self.api.classify_image(detectorId=detector_id, url=url)
        preds = res["results"][0]["predictions"]
        assert len(preds) == 4, "Expected 4 predictions for Segmentation"
        predicted_labels = [
            max(pred["labels"], key=pred["labels"].get) for pred in preds
        ]
        assert expected_label in predicted_labels
        idx = predicted_labels.index(expected_label)
        assert len(preds[idx]["segments"][0]["extPoints"]) > 500

        print_test_pass()
