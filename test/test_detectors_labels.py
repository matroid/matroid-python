from datetime import datetime
import time
import unittest
import os

from .helpers import set_up_client, print_test_title, print_case_pass, TEST_IMAGE_FILE, EVERYDAY_OBJECT_DETECTOR_ID

DETECTOR_TEST_ZIP = os.getcwd() + '/test/test_file/cat-dog-lacroix.zip'


class TestDetectorsAndLabels(unittest.TestCase):
    def setUp(self):
        print_test_title('Detectors')
        self.api = set_up_client()
        self.delete_pending_detectors()

    def test_detector_and_labels(self):
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

        try:
            detector_id = self.create_detector_test(
                zip_file=DETECTOR_TEST_ZIP, name=detector_name, detector_type='general')
            time.sleep(3)
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

    def delete_pending_detectors(self):
        res = self.api.list_detectors(state='pending')
        if len(res) == 1:
            print('Info: found a pending detector, deleting it...')
            self.api.delete_detector(detector_id=res[0]['id'])
            print('Info: Deleted pending detector')

    def create_detector_test(self, zip_file, name, detector_type):
        res = self.api.create_detector(
            zip_file=zip_file, name=name, detector_type=detector_type)

        print_case_pass('create_detector_test')
        return res['detector_id']

    def create_label_with_images_test(self, name, detector_id, image_files):
        res = self.api.create_label(detector_id=detector_id,
                                    name=name, image_files=image_files)
        assert('successfully uploaded 1 images to label' in res['message'])

        print_case_pass('create_label_with_images_test')
        return res['label_id']

    def get_annotations_test(self, detector_id, label_id):
        res = self.api.get_annotations(
            detector_id=detector_id, label_id=label_id)
        self.assertIsNotNone(res)

        print_case_pass('get_annotations_test')

    def get_label_images_test(self, detector_id, label_id):
        res = self.api.get_label_images(
            detector_id=detector_id, label_id=label_id)
        self.assertIsNotNone(res['images'])

        print_case_pass('get_label_images_test')
        return res['images'][0]['image_id']

    def update_annotations_test(self, detector_id, label_id, image_id, bbox):
        res = self.api.update_annotations(detector_id=detector_id, label_id=label_id, images=[
            {'id': image_id, 'bbox': bbox}])
        self.assertEqual(res['message'], 'successfully updated 1 images')

        print_case_pass('update_annotations_test')

    def update_label_with_images_test(self, detector_id, label_id, image_files):
        res = self.api.update_label_with_images(
            detector_id=detector_id, label_id=label_id, image_files=image_files)
        assert ('successfully uploaded 1 images to label' in res['message'])

        print_case_pass('update_label_with_images_test')

    def delete_label_test(self, detector_id, label_id):
        res = self.api.delete_label(
            detector_id=detector_id, label_id=label_id)
        self.assertEqual(res['message'], 'Successfully deleted the label')

        print_case_pass('delete_label_test')

    def train_detector_test(self, detector_id):
        res = self.api.train_detector(detector_id=detector_id)
        self.assertEqual(res['message'], 'training began successfully')

        print_case_pass('train_detector_test')

    def detector_info_test(self, detector_id):
        res = self.api.detector_info(detector_id=detector_id)
        self.assertIsNotNone(res)

        print_case_pass('detector_info_test')

    def list_detectors_test(self):
        res = self.api.list_detectors()
        self.assertIsNotNone(res)

        print_case_pass('list_detectors_test')

    def redo_detector_test(self, detector_id):
        res = self.api.redo_detector(detector_id=detector_id)
        redo_detector_id = res['detector_id']
        self.assertIsNotNone(redo_detector_id)

        print_case_pass('redo_detector_test')
        return redo_detector_id

    def import_detector_test(self, name, input_tensor, output_tensor, detector_type, file_proto, labels):
        res = self.api.import_detector(name=name, input_tensor=input_tensor, output_tensor=output_tensor,
                                       detector_type=detector_type, file_proto=file_proto, labels=labels)

        self.assertIsNotNone(res)

        print_case_pass('import_detector_test')
        return res['detector_id']

    def delete_detector_test(self, detector_id, detector_type):
        res = self.api.delete_detector(detector_id=detector_id)
        self.assertEqual(res['message'], 'Deleted detector.')

        print_case_pass('delete_detector_test - {}'.format(detector_type))

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
