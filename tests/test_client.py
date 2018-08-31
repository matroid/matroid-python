import os
import sys
import pprint
from nose.tools import assert_is_not_none, assert_true
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import matroid
from matroid.client import MatroidAPI

SAMPLE_CAT_IMAGE_URL = 'https://www.matroid.com/images/solutions/cat.jpg'
SAMPLE_CAT_IMAGE_FILE = 'tests/cat_dog.jpg'
# SAMPLE_VIDEO_URL = 'https://www.youtube.com/watch?v=N8T6AqYKRpA'
BASE_URL = 'https://www.matroid.com/api/v1'

def test_account_info():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    response = client.account_info()
    assert_is_not_none(response)

def test_list_user_detectors():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    response = client.list_detectors(**{})
    assert_is_not_none(response)
    assert_true(all(detector['owner'] == True for detector in response),
                'Expected only private detectors')

def test_list_public_detectors():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    detectors = client.list_detectors(**{'published': True})
    assert_is_not_none(detectors)
    assert_true(all(detector['permission_level'] == 'open' or detector['permission_level'] == 'readonly' for detector in detectors),
                    'Expected only publicly available detectors')

def test_list_public_detectors_by_id():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    detectors = client.list_detectors(**{'published': True})
    assert_is_not_none(detectors)
    detector = detectors[0]
    detector_from_id = client.list_detectors(**{'published': True, 'id': detector['id']})
    assert_is_not_none(detector_from_id)
    assert_true(len(detector_from_id) > 0,
               'Expected detector to be found')
    detector_from_id = detector_from_id[0]
    assert_true(detector_from_id['name'] == detector['name'],
                'Expected queried detector to have same name')
    assert_true(all(detector['permission_level'] == 'open' or detector['permission_level'] == 'readonly' for detector in detectors),
                'Expected only publicly available detectors')
def test_list_public_detectors_by_label():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    detectors = client.list_detectors(**{'published': True, 'label': 'person'})
    assert_is_not_none(detectors)
    detector = detectors[0]
    assert(any(label.startswith('person') for label in detector['labels']))

def test_list_public_detectors_by_type():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    detectors = client.list_detectors(**{'published': True, 'detector_type': 'facial_characteristics'})
    assert_is_not_none(detectors)
    detector = detectors[0]
    assert(detector['type'] == 'facial_characteristics')

def test_detector_info():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    detectors = client.list_detectors(**{'published': True, 'label': 'cat'})
    assert_is_not_none(detectors)
    detector_id = detectors[0]['id']
    detector = client.detector_info(detector_id)
    assert_is_not_none(detector)
    assert_true(detector['detector']['name'] == detectors[0]['name'])

def test_classify_cat_image():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
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
    assert_true(cat_score > .9,
                'Expected label to have appropriate score')

def test_localize_cat_image_file():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    detectors = client.list_detectors(**{'published': True, 'name': 'Yolo VOC detector'})
    assert_is_not_none(detectors)
    yolo_detector_id = detectors[0]['id']
    label = 'cat'
    results = client.localize(yolo_detector_id, label, image_file=SAMPLE_CAT_IMAGE_FILE)
    assert_is_not_none(results)
    assert_is_not_none(results['results'])
    assert_is_not_none(results['results'][0])
    predictions = results['results'][0]['predictions']
    assert_is_not_none(predictions)
    assert_true(any(p['labels'][label] > .8 for p in predictions),
                'Expected label to have appropriate score')

def test_localize_cat_image_url():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    detectors = client.list_detectors(**{'published': True, 'name': 'Yolo VOC detector'})
    assert_is_not_none(detectors)
    yolo_detector_id = detectors[0]['id']
    label = 'cat'
    results = client.localize(yolo_detector_id, label, image_url=SAMPLE_CAT_IMAGE_URL)
    assert_is_not_none(results)
    assert_is_not_none(results['results'])
    assert_is_not_none(results['results'][0])
    predictions = results['results'][0]['predictions']
    assert_is_not_none(predictions)
    assert_true(any(p['labels'][label] > .8 for p in predictions),
                'Expected label to have appropriate score')

def test_saliency_map_cat_image_file():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    detectors = client.list_detectors(**{'published': True, 'detector_type': 'general', 'name': 'general'})
    assert_is_not_none(detectors)
    general_detector_id = detectors[0]['id']
    dog_class_idx = detectors[0]['labels'].index('French bulldog')
    results = client.saliency_map(general_detector_id, dog_class_idx, image_file=SAMPLE_CAT_IMAGE_FILE)
    assert_is_not_none(results)
    assert_true(results['success'],
                'Expeted "success" in response')

def test_saliency_map_cat_image_url():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    detectors = client.list_detectors(**{'published': True, 'detector_type': 'general', 'name': 'general'})
    assert_is_not_none(detectors)
    general_detector_id = detectors[0]['id']
    dog_class_idx = detectors[0]['labels'].index('French bulldog')
    results = client.saliency_map(general_detector_id, dog_class_idx, image_url=SAMPLE_CAT_IMAGE_URL)
    assert_is_not_none(results)
    assert_true(results['success'],
                'Expeted "success" in response')

def test_list_streams():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    streams = client.list_streams()
    assert_is_not_none(streams)

def test_list_monitors():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    monitorings = client.list_monitors()
    assert_is_not_none(monitorings)


def test_list_monitors_by_state():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    monitorings = client.list_monitors(state='scheduled')
    assert_is_not_none(monitorings)
    assert_true(all(monitor['state'] == 'scheduled' for monitor in monitorings),
                'Expected to find only "scheduled" states')
    monitorings = client.list_monitors(state='ready')
    assert_is_not_none(monitorings)
    assert_true(all(monitor['state'] == 'ready' for monitor in monitorings),
                'Expected to find only "ready" states')
    monitorings = client.list_monitors(state='failed')
    assert_is_not_none(monitorings)
    assert_true(all(monitor['state'] == 'failed' for monitor in monitorings),
                'Expected to find only "failed" states')

def test_list_monitors_by_id():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    monitorings = client.list_monitors()
    assert_is_not_none(monitorings)
    a_monitor = monitorings[0]
    assert_is_not_none(a_monitor)

    monitorings_by_monitoring_id = client.list_monitors(monitoring_id=a_monitor['monitoring_id'])
    assert_true(all(monitor['monitoring_id'] == a_monitor['monitoring_id'] for monitor in monitorings_by_monitoring_id),
                'Expected to find monitoring by monitoring_id')

    monitorings_by_stream_id = client.list_monitors(stream_id=a_monitor['stream_id'])
    assert_true(all(monitor['stream_id'] == a_monitor['stream_id'] for monitor in monitorings_by_stream_id),
                'Expected to find monitoring by stream_id')

def test_create_monitor():
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    detectors = client.list_detectors(name='Matroid Everyday Objects 545', published=True)
    streams = client.list_streams()
    assert_is_not_none(detectors)
    assert_is_not_none(streams)
    everyday_detector = detectors[0]
    stream = streams[0]
    assert_is_not_none(everyday_detector)
    assert_is_not_none(stream)
    detector_id = everyday_detector['id']
    stream_id = stream['stream_id']
    thresholds = {'dog': 0.5, 'cat': 0.5}
    new_monitor = client.create_monitor(stream_id, detector_id, thresholds, name="MY_COOL_NEW_DOG_MONITOR")
    new_monitoring_list = client.list_monitors(monitoring_id=new_monitor['monitoring_id'])
    assert_true(new_monitor['stream_id'] == stream_id,
                'Expected new montior to have correct stream id')
    assert_true(len(new_monitoring_list) == 1,
                'Expected new stream list to contain new monitor')
    assert_true(new_monitoring_list[0]['monitoring_id'] == new_monitor['monitoring_id'],
                'Expected new monitorings list to contain new monitor')

def test_kill_monitor():
    """Depends on the above test to pass!"""
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    monitoring_list = client.list_monitors(name="MY_COOL_NEW_DOG_MONITOR")
    monitor = monitoring_list[0]
    monitoring_id = monitor['monitoring_id']
    result = client.kill_monitor(monitoring_id)
    assert_true(result['message']) == 'Successfully killed monitoring.',
                'Expected success response')

def test_delete_monitor():
    """Depends on the above test to pass!"""
    client = MatroidAPI(options={'json_format': True}, base_url=BASE_URL)
    monitoring_list = client.list_monitors(name="MY_COOL_NEW_DOG_MONITOR")
    monitor = monitoring_list[0]
    monitoring_id = monitor['monitoring_id']
    result = client.delete_monitor(monitoring_id)
    assert_true(result['message']) == 'Successfully deleted monitoring.',
                'Expected success response')
