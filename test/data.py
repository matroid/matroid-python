import os

EVERYDAY_OBJECT_DETECTOR_ID = "598e23679fd1a805a5c09275"
DETECTOR_LABELS = ["person", "boat"]
RANDOM_MONGO_ID = "5d0148512563ae5e748e9a66"

TEST_IMAGE_URL = "https://matroid-web.s3.amazonaws.com/test/python-client/tesla-cat.jpg"
TEST_IMAGE_URL_DOG = "https://matroid-web.s3.amazonaws.com/test/python-client/dog.jpg"
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
