import os
import requests

from matroid import error
from matroid.src.helpers import api_call


@api_call(error.InvalidQueryError)
def create_detector(self, zip_file, name, detector_type):
    """
    Create a new detector with the contents of the zip file

    detector_type: general, facial_recognition, or facial_characteristics
    name: the detector's display name
    zip_file: a zip file containing the images to be used in the detector creation
              the root folder should contain only directories which will become the labels for detection
              each of these directories should contain only images corresponding to that label.

              However, there is an exception if you want to add negative examples to a label.
              In that case, put the negative images for the label in a folder called "negative" inside the corresponding label.

              To include bounding boxes, include one file called bbox.csv in the top level directory.
              Each line of this file should be formatted as follows:
                0.25, 0.3, 0.75, 0.8, cat, positive, image.jpg
                0.25, 0.4, 0.55, 0.7, dog, positive, picture.jpg
                0.0, 0.1, 0.2, 0.3, cat, negative, raccoon.jpg

              Column definitions:
                top left X coordinate, top left Y coordinate, bottom right X coordinate, bottom right Y coordinate, label, positive or negative example, file name

              Max 300 MB zip file upload

      structure example:
        cat/
          garfield.jpg
          nermal.png
        dog/
          odie.TIFF
          negative/
            lobo.jpg
        bbox.csv
    """
    MAX_LOCAL_ZIP_SIZE = 300 * 1024 * 1024

    (endpoint, method) = self.endpoints['create_detector']

    try:
        headers = {'Authorization': self.token.authorization_header()}
        data = {'name': name, 'detector_type': detector_type}
        with self.filereader.get_file(zip_file) as file_to_upload:
            files = {'file': file_to_upload}
            file_size = os.fstat(file_to_upload.fileno()).st_size

            if file_size > MAX_LOCAL_ZIP_SIZE:
                raise error.InvalidQueryError(message='File %s is larger than the limit of %d megabytes' % (
                    file_to_upload.name, self.bytes_to_mb(MAX_LOCAL_ZIP_SIZE)))

            return requests.request(method, endpoint, **{'headers': headers, 'files': files, 'data': data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def delete_detector(self, detector_id):
    """
    Requires processing=false. 
    Note: Users can only delete pending detectors; once finalized, the only way to delete is via the Web UI.
    """
    (endpoint, method) = self.endpoints['delete_detector']

    endpoint = endpoint.replace(':key', detector_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        return requests.request(method, endpoint, **{'headers': headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def detector_info(self, detector_id):
    """Get information about detector"""
    (endpoint, method) = self.endpoints['detector_info']

    endpoint = endpoint.replace(':key', detector_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        return requests.request(method, endpoint, **{'headers': headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def train_detector(self, detector_id, name=None, detector_type=None):
    """Begin training the detector"""
    (endpoint, method) = self.endpoints['train_detector']

    endpoint = endpoint.replace(':key', detector_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        data = {}
        if name:
            data['name'] = name
        if detector_type:
            data['detector_type'] = detector_type

        return requests.request(method, endpoint, **{'headers': headers, 'data': data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def import_detector(self, name, **options):
    """
    Note: certain combination of parameters can be supplied: file_detector, file_proto + file_label (+ file_label_ind), or file_proto + labels (+ label_inds). Parentheses part can be optionally supplied for object detection.
    """
    (endpoint, method) = self.endpoints['import_detector']

    data = {
        'name': name,
    }

    def get_data_info():
        data['input_tensor'] = options.get('input_tensor'),
        data['output_tensor'] = options.get('output_tensor'),
        data['detector_type'] = options.get('detector_type'),

    if options.get('file_detector'):
        file_paths = {'file_detector': options.get('file_detector')}
    elif options.get('file_proto') and options.get('file_label'):
        file_paths = {
            'file_proto': options.get('file_proto'),
            'file_label': options.get('file_label'),
            'file_label_ind': options.get('file_label_ind')
        }
        get_data_info()
    elif options.get('file_proto') and options.get('labels'):
        file_paths = {
            'file_proto': options.get('file_proto'),
        }
        data['labels'] = options.get('labels')
        data['label_inds'] = options.get('label_inds')
        get_data_info()
    else:
        raise error.InvalidQueryError(
            message='Invalid parameter combination')

    file_objs = {}
    for file_keyword, file_path in file_paths.items():
        file_obj = self.filereader.get_file(file_path)
        file_objs[file_keyword] = file_obj

    try:
        headers = {'Authorization': self.token.authorization_header()}
        return requests.request(method, endpoint, **{'headers': headers, 'files': file_objs, 'data': data})
    except IOError as e:
        raise e
    except error.InvalidQueryError as e:
        raise e
    except Exception as e:
        raise error.APIConnectionError(message=e)
    finally:
        for file_keyword, file_obj in file_objs.items():
            if isinstance(file_obj, file):
                file_obj.close()


@api_call(error.InvalidQueryError)
def redo_detector(self, detector_id):
    """
    Redo a detector
    Note: a deep copy of the trained detector with different detector_id will be made
    """
    (endpoint, method) = self.endpoints['redo_detector']

    endpoint = endpoint.replace(':key', detector_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        return requests.request(method, endpoint, **{'headers': headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def list_detectors(self, **query):
    """Lists the available detectors"""
    (endpoint, method) = self.endpoints['detectors']

    try:
        headers = {'Authorization': self.token.authorization_header()}
        params = {x: str(query[x]).lower() for x in query}
        return requests.request(method, endpoint, **{'headers': headers, 'params': params})
    except Exception as e:
        raise error.APIConnectionError(message=e)
