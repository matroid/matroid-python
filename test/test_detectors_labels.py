import os
import time
from datetime import datetime
import pytest

from data import TEST_IMAGE_FILE, EVERYDAY_OBJECT_DETECTOR_ID

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
        zip_file=DETECTOR_TEST_ZIP, name=detector_name, detector_type='general')
      self.wait_detector_ready_for_edit(detector_id)
      label_id = self.create_label_with_images_test(
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
      self.train_detector_test(detector_id=detector_id)

      self.wait_detector_training(detector_id)

      self.detector_info_test(detector_id=detector_id)
      self.list_detectors_test()
      redo_detector_id = self.redo_detector_test(
        detector_id=EVERYDAY_OBJECT_DETECTOR_ID)
      import_detector_id = self.import_detector_test(name=import_detector_name, input_tensor=input_tensor,
                                                      output_tensor=output_tensor, detector_type='facial_recognition', file_proto=file_proto, labels=labels)
    finally:
      if detector_id:
        self.delete_detector_test(detector_id, 'main detector')
      if import_detector_id:
        self.delete_detector_test(
          import_detector_id, 'imported detector')
      if redo_detector_id:
        self.delete_detector_test(redo_detector_id, 'redo detector')

  def create_detector_test(self, zip_file, name, detector_type):
    res = self.api.create_detector(
      zip_file=zip_file, name=name, detector_type=detector_type)
    assert(res['detector_id'] != None)

    return res['detector_id']

  def create_label_with_images_test(self, name, detector_id, image_files):
    res = self.api.create_label(detector_id=detector_id,
                                name=name, image_files=image_files)
    assert('successfully uploaded 1 images to label' in res['message'])

    return res['label_id']

  def get_annotations_test(self, detector_id, label_id):
    res = self.api.get_annotations(
      detector_id=detector_id, label_id=label_id)
    assert(res['images'] != None)


  def get_label_images_test(self, detector_id, label_id):
    res = self.api.get_label_images(
      detector_id=detector_id, label_id=label_id)
    assert(res['images'] != None)

    return res['images'][0]['image_id']

  def update_annotations_test(self, detector_id, label_id, image_id, bbox):
    res = self.api.update_annotations(detector_id=detector_id, label_id=label_id, images=[
      {'id': image_id, 'bbox': bbox}])
    assert(res['message'] == 'successfully updated 1 images')


  def update_label_with_images_test(self, detector_id, label_id, image_files):
    res = self.api.update_label_with_images(
        detector_id=detector_id, label_id=label_id, image_files=image_files)
    assert('successfully uploaded 1 images to label' in res['message'])


  def delete_label_test(self, detector_id, label_id):
    res = self.api.delete_label(
        detector_id=detector_id, label_id=label_id)
    assert(res['message'] == 'Successfully deleted the label')


  def train_detector_test(self, detector_id):
    res = self.api.train_detector(detector_id=detector_id)
    assert(res['message'] == 'training began successfully')


  def detector_info_test(self, detector_id):
    res = self.api.detector_info(detector_id=detector_id)
    assert(res['id'] == detector_id)


  def list_detectors_test(self):
    res = self.api.list_detectors()
    assert(res[0]['id'] != None)


  def redo_detector_test(self, detector_id):
    res = self.api.redo_detector(detector_id=detector_id)
    redo_detector_id = res['detector_id']
    assert(redo_detector_id != None)

    return redo_detector_id

  def import_detector_test(self, name, input_tensor, output_tensor, detector_type, file_proto, labels):
    res = self.api.import_detector(name=name, input_tensor=input_tensor, output_tensor=output_tensor,
                                    detector_type=detector_type, file_proto=file_proto, labels=labels)

    assert(res['detector_id'] != None)

    return res['detector_id']

  def delete_detector_test(self, detector_id, detector_type):
    res = self.api.delete_detector(detector_id=detector_id)
    assert(res['message'] == 'Deleted detector.')


  # helpers

  def delete_pending_detectors(self):
    res = self.api.list_detectors(state='pending')
    if len(res) == 1:
      print('Info: found a pending detector, deleting it...')
      self.api.delete_detector(detector_id=res[0]['id'])
      print('Info: Deleted pending detector')

  def wait_detector_training(self, detector_id):
    res = self.api.detector_info(detector_id=detector_id)

    print ('Info: waiting for training detectors')
    indicator = ''
    while res['state'] != 'trained':
      indicator += '.'
      print(indicator)
      time.sleep(5)
      res = self.api.detector_info(detector_id=detector_id)

    print('Info: detector is ready')

  def wait_detector_ready_for_edit(self, detector_id):
    print('Info: wait for pending detector to be ready for editing')
    res = self.api.detector_info(detector_id=detector_id)

    while (res['processing']):
      res = self.api.detector_info(detector_id=detector_id)
      time.sleep(2)

    print('Info: detector is ready for editing.')