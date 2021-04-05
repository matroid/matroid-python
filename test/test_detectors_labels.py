import os
import time
from datetime import datetime
import pytest

from test.data import TEST_IMAGE_FILE, RANDOM_MONGO_ID
from matroid.error import APIConnectionError, InvalidQueryError, APIError
from test.helper import print_test_pass

DETECTOR_TEST_ZIP = os.getcwd() + '/test/test_file/cat-dog-lacroix.zip'


class TestDetectorsAndLabels(object):
  def test_detector_and_labels(self, set_up_client):
    detector_id = None
    import_detector_id = None
    redo_detector_id = None

    detector_name = 'py-test-detector-{}'.format(datetime.now())
    label_name = 'py-test-label'
    bbox = {'left': 0.2, 'top': 0.1, 'width': 0.6, 'height': 0.8}

    # Info for import_detector_test
    import_detector_name = 'upload_py_gender_facial'
    detector_type = 'facial_recognition'
    input_tensor = 'input_5[128,128,3]'
    output_tensor = 'prob3[2]'
    labels = ['female', 'male']
    file_proto = os.getcwd() + '/test/test_file/gender_only_all_android.pb'

    # set up client
    self.api = set_up_client

    # start testing
    try:
      self.delete_pending_detectors()
      detector_id = self.create_detector_test(
          file=DETECTOR_TEST_ZIP, name=detector_name, detector_type='general')
      self.wait_detector_ready_for_edit(detector_id)
      label_id = self.create_label_with_images_with_images_test(
          name=label_name, detector_id=detector_id, image_files=TEST_IMAGE_FILE)
      self.get_annotations_test(
          detector_id=detector_id, label_id=label_id)
      image_id = self.get_label_images_test(
          detector_id=detector_id, label_id=label_id)
      self.update_annotations_test(
          detector_id=detector_id, label_id=label_id, image_id=image_id, bbox=bbox)
      self.update_label_with_images_test(
          detector_id=detector_id, label_id=label_id, image_files=TEST_IMAGE_FILE)
      self.delete_label_test(detector_id=detector_id, label_id=label_id)
      self.finalize_detector_test(detector_id=detector_id)

      self.wait_detector_training(detector_id)

      self.get_detector_info_test(detector_id=detector_id)
      self.search_detectors_test()
      self.list_detectors_test()
      redo_detector_id = self.redo_detector_test(
          detector_id=detector_id)
      import_detector_id = self.import_detector_test(name=import_detector_name, input_tensor=input_tensor,
                                                     output_tensor=output_tensor, detector_type='facial_recognition',
                                                     file_proto=file_proto, labels=labels)
    finally:
      if detector_id:
        self.delete_detector_test(detector_id, 'main detector')
      if import_detector_id:
        self.delete_detector_test(
            import_detector_id, 'imported detector')
      if redo_detector_id:
        self.delete_detector_test(redo_detector_id, 'redo detector')

  def create_detector_test(self, file, name, detector_type):
    with pytest.raises(APIConnectionError) as e:
      invalid_zip_path = os.getcwd() + '/test/test_file/invalid.zip'
      self.api.create_detector(
          file=invalid_zip_path, name=name, detectorType=detector_type)
    assert ('No such file or directory' in str(e))

    res = self.api.create_detector(
        file=file, name=name, detectorType=detector_type)
    assert(res['detectorId'] != None)

    print_test_pass()
    return res['detectorId']

  def create_label_with_images_with_images_test(self, name, detector_id, image_files):
    with pytest.raises(APIError) as e:
      self.api.create_label_with_images(detectorId=RANDOM_MONGO_ID,
                                        name=name, imageFiles=image_files)
    assert ('invalid_query_err' in str(e))

    res = self.api.create_label_with_images(detectorId=detector_id,
                                            name=name, imageFiles=image_files)
    assert('successfully uploaded 1 images to label' in res['message'])

    print_test_pass()
    return res['labelId']

  def get_annotations_test(self, detector_id, label_id):
    res = self.api.get_annotations(
        detectorId=detector_id, labelId=label_id)
    assert (res['images'] != None)
    print_test_pass()

  def get_label_images_test(self, detector_id, label_id):
    res = self.api.get_label_images(
        detectorId=detector_id, labelId=label_id)
    assert(res['images'] != None)

    print_test_pass()
    return res['images'][0]['imageId']

  def update_annotations_test(self, detector_id, label_id, image_id, bbox):
    with pytest.raises(APIError) as e:
      self.api.update_annotations(
          detectorId=detector_id, labelId=label_id, images=[])
    assert ('invalid_query_err' in str(e))

    res = self.api.update_annotations(detectorId=detector_id, labelId=label_id, images=[
        {'id': image_id, 'bbox': bbox}])
    assert (res['message'] == 'successfully updated 1 images')
    print_test_pass()

  def update_label_with_images_test(self, detector_id, label_id, image_files):
    res = self.api.update_label_with_images(
        detectorId=detector_id, labelId=label_id, imageFiles=image_files)
    assert ('successfully uploaded 1 images to label' in res['message'])
    print_test_pass()

  def delete_label_test(self, detector_id, label_id):
    res = self.api.delete_label(
        detectorId=detector_id, labelId=label_id)
    assert (res['message'] == 'Successfully deleted the label')
    print_test_pass()

  def finalize_detector_test(self, detector_id):
    res = self.api.finalize_detector(detectorId=detector_id)
    assert (res['message'] == 'training began successfully')
    print_test_pass()

  def get_detector_info_test(self, detector_id):
    res = self.api.get_detector_info(detectorId=detector_id)
    assert (res['id'] == detector_id)
    print_test_pass()

  def search_detectors_test(self):
    res = self.api.search_detectors()
    assert (res[0]['id'] != None)
    print_test_pass()

  def list_detectors_test(self):
    res = self.api.list_detectors()
    assert (len(res) > 0)
    print_test_pass()

  def redo_detector_test(self, detector_id):
    res = self.api.redo_detector(detectorId=detector_id)
    redo_detector_id = res['detectorId']
    assert(redo_detector_id != None)

    print_test_pass()
    return redo_detector_id

  def import_detector_test(self, name, input_tensor, output_tensor, detector_type, file_proto, labels):
    res = self.api.import_detector(name=name, inputTensor=input_tensor, outputTensor=output_tensor,
                                   detectorType=detector_type, fileProto=file_proto, labels=labels)

    assert(res['detectorId'] != None)

    print_test_pass()
    return res['detectorId']

  def delete_detector_test(self, detector_id, detector_type):
    res = self.api.delete_detector(detectorId=detector_id)
    assert (res['message'] == 'Deleted detector.')
    print_test_pass()

  # helpers
  def delete_pending_detectors(self):
    res = self.api.search_detectors(state='pending')
    if len(res) == 1:
      print('Info: found a pending detector, deleting it...')
      self.api.delete_detector(detectorId=res[0]['id'])
      print('Info: Deleted pending detector')

  def wait_detector_training(self, detector_id):
    res = self.api.get_detector_info(detectorId=detector_id)

    print ('Info: waiting for detectors training')
    indicator = '.'
    max_indicator_length = 48
    while res['state'] != 'trained' and res['state'] != 'failed':
      if len(indicator) > max_indicator_length:
        pytest.fail('Timeout when waiting for detector training')

      print(indicator)
      time.sleep(5)
      res = self.api.get_detector_info(detectorId=detector_id)

      indicator += '.'

    print('Info: detector is ready')

  def wait_detector_ready_for_edit(self, detector_id):
    print('Info: waiting for pending detector to be ready for editing')
    res = self.api.get_detector_info(detectorId=detector_id)

    tried_num = 0
    max_tries = 15

    while (res['processing']):
      if tried_num > max_tries:
        pytest.fail(
            'Timeout when waiting for detector to be ready for editing')

      res = self.api.get_detector_info(detectorId=detector_id)

      time.sleep(2)

      tried_num += 1

    print('Info: detector is ready for editing.')
