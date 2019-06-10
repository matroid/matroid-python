import os

from matroid.client import Matroid

EVERYDAY_OBJECT_DETECTOR_ID = '598e23679fd1a805a5c09275'
TEST_IMAGE_URL = 'https://r.hswstatic.com/w_907/gif/tesla-cat.jpg'
TEST_VIDEO_URL = 'https://www.youtube.com/watch?v=P05wyA62W9k'
TEST_IMAGE_FILE = os.getcwd() + '/test/test_file/cat.png'
YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v=nDvh3upNJmA'


def set_up_client():
    try:
        base_url = os.environ['BASE_URL']
        client_id = os.environ['CLIENT_ID']
        client_secret = os.environ['CLIENT_SECRET']
    except:
        raise Exception('Please provide test information')

    return Matroid(base_url, client_id, client_secret)


def print_test_title(test_name):
    print ('\n=========================')
    print (test_name)
    print ('=========================\n')


def print_case_pass(test_case_name):
    print('\x1b[6;30;42m' + 'pass' + '\x1b[0m ' + test_case_name)
