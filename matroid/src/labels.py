import requests
import json

from matroid import error
from matroid.src.helpers import api_call, batch_file_request


@api_call(error.InvalidQueryError)
def create_label(self, detector_id, name, image_files, **options):
    """Create a label. Requires processing=false. Creates label asynchronously (turn processing to true)"""
    (endpoint, method) = self.endpoints['create_label']
    endpoint = endpoint.replace(':key', detector_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        data = {
            'name': name,
            'destination': options.get('destination'),
            'bboxes': options.get('bboxes'),
        }

        if not isinstance(image_files, list):
            image_files = [image_files]

        return batch_file_request(image_files, method, endpoint, headers, data, 'image_files')
    except IOError as e:
        raise e
    except error.InvalidQueryError as e:
        raise e
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def delete_label(self, detector_id, label_id):
    """Delete a label. Requires processing=false"""
    (endpoint, method) = self.endpoints['delete_label']
    endpoint = endpoint.replace(':detector_id', detector_id)
    endpoint = endpoint.replace(':label_id', label_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        return requests.request(method, endpoint, **{'headers': headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def get_annotations(self, **options):
    """Get annotations. Requires processing=false. Note: you need to provide at least one of the three ids to query"""
    (endpoint, method) = self.endpoints['get_annotations']

    detector_id = options.get('detector_id')
    label_ids = options.get('label_ids')
    image_id = options.get('image_id')

    if not detector_id and not label_ids and not image_id:
        raise error.InvalidQueryError(
            message='Missing required parameter: detector_id or label_ids o rimage_id')

    try:
        headers = {'Authorization': self.token.authorization_header()}
        params = {
            'detector_id': detector_id,
            'label_ids': label_ids,
            'image_id': image_id,
        }
        return requests.request(method, endpoint, **{'headers': headers, 'params': params})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def get_label_images(self, detector_id, label_id):
    (endpoint, method) = self.endpoints['get_label_images']
    endpoint = endpoint.replace(':detector_id', detector_id)
    endpoint = endpoint.replace(':label_id', label_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        return requests.request(method, endpoint, **{'headers': headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def update_annotations(self, detector_id, label_id, images, **options):
    (endpoint, method) = self.endpoints['update_annotations']
    endpoint = endpoint.replace(':detector_id', detector_id)
    endpoint = endpoint.replace(':label_id', label_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        data = {
            'images': json.dumps(images),
            'destination': options.get('destination')
        }

        return requests.request(method, endpoint, **{'headers': headers, 'data': data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def update_label_with_images(self, detector_id, label_id, image_files, **options):
    """Requires processing=false. Updates label asynchronously (turn processing to true)"""
    (endpoint, method) = self.endpoints['update_label_with_images']
    endpoint = endpoint.replace(':detector_id', detector_id)
    endpoint = endpoint.replace(':label_id', label_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        data = {
            'destination': options.get('destination'),
            'bboxes': options.get('bboxes'),
        }

        if not isinstance(image_files, list):
            image_files = [image_files]

        return batch_file_request(image_files, method, endpoint, headers, data, 'image_files')
    except IOError as e:
        raise e
    except error.InvalidQueryError as e:
        raise e
    except Exception as e:
        raise error.APIConnectionError(message=e)
