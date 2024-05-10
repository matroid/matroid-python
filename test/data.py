import os

EVERYDAY_OBJECT_DETECTOR_ID = "598e23679fd1a805a5c09275"
EVERYDAY_OBJECT_SEGMENTOR_ID = "62bb48b7b80c90542d4e8a55"
TAL_DETECTOR_ID = "662fdc71c8630f813831c024"
TAL_DETECTOR_LABELS = ["Full Cycle"]
DETECTOR_LABELS = ["person", "boat"]
DEFAULT_DETECTION_THRESHOLD = 0.5
RANDOM_MONGO_ID = "5d0148512563ae5e748e9a66"

TEST_IMAGE_URL = (
    "https://m-test-public.s3.amazonaws.com/test/python-client/tesla-cat.jpg"
)
TEST_IMAGE_URL_DOG = "https://m-test-public.s3.amazonaws.com/test/python-client/dog.jpg"
TEST_IMAGE_FILE = os.getcwd() + "/test/test_file/cat.png"
TEST_IMAGE_FILE_DOG = os.getcwd() + "/test/test_file/dog.png"

TEST_LOCAL_VIDEO_URL = os.getcwd() + "/test/test_file/construction.mp4"
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=nDvh3upNJmA"
TEST_S3_VIDEO_URL = (
    "https://m-test-public.s3-us-west-2.amazonaws.com/videos/Multiple+cars+-+5s.mp4"
)
TEST_S3_VIDEO_URL_2 = (
    "https://m-test-public.s3.us-west-2.amazonaws.com/videos/TomCruiseInterview.mp4"
)
