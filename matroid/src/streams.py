import requests
import json

from matroid import error
from matroid.src.helpers import api_call


@api_call(error.InvalidQueryError)
def create_stream(self, stream_url, stream_name):
    (endpoint, method) = self.endpoints['create_stream']

    try:
        headers = {'Authorization': self.token.authorization_header()}
        data = {
            'name': stream_name,
            'url': stream_url
        }
        return requests.request(method, endpoint, **{'headers': headers, 'data': data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def delete_monitoring(self, monitoring_id):
    (endpoint, method) = self.endpoints['delete_monitoring']
    endpoint = endpoint.replace(':key', monitoring_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        return requests.request(method, endpoint, **{'headers': headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def delete_stream(self, stream_id):
    (endpoint, method) = self.endpoints['delete_stream']
    endpoint = endpoint.replace(':key', stream_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        return requests.request(method, endpoint, **{'headers': headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def get_monitoring_result(self, monitoring_id, **options):
    (endpoint, method) = self.endpoints['get_monitoring_result']
    endpoint = endpoint.replace(':key', monitoring_id)

    if options.get('format') == 'csv' and self.json_format:
        print('cannot return csv format when json_format True is specified upon API object initialization')
        print ('requesting JSON format...')
        options['format'] = 'json'

    try:
        headers = {'Authorization': self.token.authorization_header()}
        params = {
            'format': options.get('format'),
            'status_only': 'true' if options.get('status_only') else 'false'
        }

        return requests.request(method, endpoint, **{'headers': headers, 'params': params})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def kill_monitoring(self, monitoring_id):
    (endpoint, method) = self.endpoints['kill_monitoring']
    endpoint = endpoint.replace(':key', monitoring_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        return requests.request(method, endpoint, **{'headers': headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def monitor_stream(self, stream_id, detector_id, **options):
    (endpoint, method) = self.endpoints['monitor_stream']
    endpoint = endpoint.replace(':detector_id', detector_id)
    endpoint = endpoint.replace(':stream_id', stream_id)

    try:
        headers = {'Authorization': self.token.authorization_header()}
        data = {
            'thresholds': json.dumps(options.get('thresholds')),
            'startTime': options.get('start_time'),
            'endTime': options.get('end_time'),
            'endpoint': options.get('endpoint'),
            'taskName': options.get('task_name')
        }
        return requests.request(method, endpoint, **{'headers': headers, 'data': data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def search_monitorings(self, **options):
    (endpoint, method) = self.endpoints['search_monitorings']

    try:
        headers = {'Authorization': self.token.authorization_header()}
        params = {
            'stream_id': options.get('stream_id'),
            'monitoring_id': options.get('monitoring_id'),
            'detector_id': options.get('detector_id'),
            'name': options.get('name'),
            'start_time': options.get('start_time'),
            'end_time': options.get('end_time'),
            'state': options.get('state'),
        }
        return requests.request(method, endpoint, **{'headers': headers, 'params': params})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def search_streams(self, **options):
    (endpoint, method) = self.endpoints['search_streams']

    try:
        headers = {'Authorization': self.token.authorization_header()}
        params = {
            'stream_id': options.get('stream_id'),
            'name': options.get('name'),
            'permission': options.get('permission')
        }
        return requests.request(method, endpoint, **{'headers': headers, 'params': params})
    except Exception as e:
        raise error.APIConnectionError(message=e)
