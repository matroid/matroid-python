import os
import sys
import pprint
from unittest.mock import Mock, patch
from nose.tools import assert_is_not_none
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import matroid
from matroid.client import MatroidAPI

SAMPLE_CAT_IMAGE_URL = 'https://www.matroid.com/images/solutions/cat.jpg'
# SAMPLE_VIDEO_URL = 'https://www.youtube.com/watch?v=N8T6AqYKRpA'

# @patch('matroid.client.requests.get')
# def test_account_info(mock_get):
def test_account_info():
    # mock_get.return_value.ok = True
    client = MatroidAPI(options={'json_format': True})
    response = client.account_info()
    assert_is_not_none(response)

# @patch('matroid.client.requests.get')
# def test_list_user_detectors(mock_get):
def test_list_user_detectors():
    # mock_get.return_value.ok = True
    client = MatroidAPI(options={'json_format': True})
    response = client.list_detectors(**{})
    assert_is_not_none(response)
    assert(all(detector['owner'] == True  for detector in response))

# @patch('matroid.client.requests.get')
# def test_list_public_detectors(mock_get):
def test_list_public_detectors():
    # mock_get.return_value.ok = True
    client = MatroidAPI(options={'json_format': True})
    detectors = client.list_detectors(**{'published': True})
    assert_is_not_none(detectors)
    assert(all(detector['permission_level'] == 'open' or detector['permission_level'] == 'readonly' for detector in detectors))

# @patch('matroid.client.requests.get')
# def test_list_public_detectors_by_id(mock_get):
def test_list_public_detectors_by_id():
    # mock_get.return_value.ok = True
    client = MatroidAPI(options={'json_format': True})
    detectors = client.list_detectors(**{'published': True})
    assert_is_not_none(detectors)
    detector = detectors[0]
    detector_from_id = client.list_detectors(**{'published': True, 'id': detector['id']})
    assert_is_not_none(detector_from_id)
    assert(len(detector_from_id) > 0)
    detector_from_id = detector_from_id[0]
    assert(detector_from_id['name'] == detector['name'])

# @patch('matroid.client.requests.get')
# def test_list_public_detectors_by_label(mock_get):
def test_list_public_detectors_by_label():
    # mock_get.return_value.ok = True
    client = MatroidAPI(options={'json_format': True})
    detectors = client.list_detectors(**{'published': True, 'label': 'person'})
    assert_is_not_none(detectors)
    detector = detectors[0]
    assert(any(label.startswith('person') for label in detector['labels']))

# @patch('matroid.client.requests.get')
# def test_list_public_detectors_by_type(mock_get):
def test_list_public_detectors_by_type():
    # mock_get.return_value.ok = True
    client = MatroidAPI(options={'json_format': True})
    detectors = client.list_detectors(**{'published': True, 'detector_type': 'facial_characteristics'})
    assert_is_not_none(detectors)
    detector = detectors[0]
    assert(detector['type'] == 'facial_characteristics')

# @patch('matroid.client.requests.get')
# def test_detector_info(mock_get):
def test_detector_info():
    # mock_get.return_value.ok = True
    client = MatroidAPI(options={'json_format': True})
    detectors = client.list_detectors(**{'published': True, 'label': 'cat'})
    assert_is_not_none(detectors)
    detector_id = detectors[0]['id']
    detector = client.detector_info(detector_id)
    assert_is_not_none(detector)
    assert(detector['detector']['name'] == detectors[0]['name'])

# @patch('matroid.client.requests.get')
# @patch('matroid.client.requests.post')
# def test_classify_cat_image(mock_get, mock_post):
def test_classify_cat_image():
    # mock_get.return_value.ok = True
    # mock_post.return_value.ok = True
    client = MatroidAPI(options={'json_format': True})
    detectors = client.list_detectors(**{'published': True, 'name': 'Yolo VOC detector'})
    assert_is_not_none(detectors)
    yolo_detector_id = detectors[0]['id']
    results = client.classify_image(yolo_detector_id, image_url=SAMPLE_CAT_IMAGE_URL)
    assert_is_not_none(results)
    results = results['results'][0]
    assert_is_not_none(results)
    predictions = results['predictions']
    assert_is_not_none(predictions)
    first_prediction = predictions[0]
    assert_is_not_none(first_prediction)
    cat_score = first_prediction['labels']['cat']
    assert(cat_score > .9)
