import requests
import json

from matroid import error
from matroid.src.helpers import api_call
from matroid.src.sse import stream_sse_events
import time

INITIAL_BACKOFF_SECS = 1
MAX_BACKOFF_SECS = 60


# https://staging.app.matroid.com/docs/api/documentation#api-Streams-PostStreams
@api_call(error.InvalidQueryError)
def create_stream(self, url, name, **options):
    (endpoint, method) = self.endpoints["create_stream"]

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {"name": name, "url": url}
        data.update(options)

        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# register_stream is now DEPRECATED in favor of create_stream (kept for backwards-compatibility)
register_stream = create_stream


# https://staging.app.matroid.com/docs/api/documentation#api-Streams-DeleteMonitoringsMonitoring_id
@api_call(error.InvalidQueryError)
def delete_monitoring(self, monitoringId):
    (endpoint, method) = self.endpoints["delete_monitoring"]
    endpoint = endpoint.replace(":key", monitoringId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/documentation#api-Streams-DeleteStreamsStream_id
@api_call(error.InvalidQueryError)
def delete_stream(self, streamId):
    (endpoint, method) = self.endpoints["delete_stream"]
    endpoint = endpoint.replace(":key", streamId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


def watch_monitoring_result(self, monitoringId, **options):
    self.retrieve_token()
    (endpoint, method) = self.endpoints["watch_monitoring_result"]
    endpoint = endpoint.replace(":key", monitoringId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        params = {}

        backoff = INITIAL_BACKOFF_SECS
        while True:
            try:
                with requests.request(
                    method, endpoint, headers=headers, params=params, stream=True
                ) as req:
                    if req.status_code >= 400 and req.status_code < 500:
                        self.check_errors(req, error.InvalidQueryError)
                    backoff = INITIAL_BACKOFF_SECS
                    yield from stream_sse_events(req.raw)
            except error.TokenExpirationError:
                self.retrieve_token(options={"request_from_server": True})
            except requests.RequestException as e:
                print("Detections connection interrupted, will retry", e)
                time.sleep(backoff)
                backoff = min(MAX_BACKOFF_SECS, backoff * 2)
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/documentation#api-Streams-GetMonitoringsMonitoring_idQuery
@api_call(error.InvalidQueryError)
def get_monitoring_result(self, monitoringId, **options):
    (endpoint, method) = self.endpoints["get_monitoring_result"]
    endpoint = endpoint.replace(":key", monitoringId)

    if options.get("format") == "csv" and self.json_format:
        print(
            "cannot return csv format when json_format True is specified upon API object initialization"
        )
        print("requesting JSON format...")
        options["format"] = "json"

    try:
        headers = {"Authorization": self.token.authorization_header()}
        params = {
            "format": options.get("format"),
            "statusOnly": "true" if options.get("statusOnly") else "false",
            "startTime": options.get("startTime"),
            "endTime": options.get("endTime"),
        }

        return requests.request(
            method, endpoint, **{"headers": headers, "params": params}
        )
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/documentation#api-Streams-PostMonitoringsMonitoring_idKill
@api_call(error.InvalidQueryError)
def kill_monitoring(self, monitoringId):
    (endpoint, method) = self.endpoints["kill_monitoring"]
    endpoint = endpoint.replace(":key", monitoringId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/documentation#api-Streams-PostStreamsStream_idMonitorDetector_id
@api_call(error.InvalidQueryError)
def monitor_stream(self, streamId, detectorId, thresholds, **options):
    (endpoint, method) = self.endpoints["monitor_stream"]
    endpoint = endpoint.replace(":detectorId", detectorId)
    endpoint = endpoint.replace(":streamId", streamId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {
            "thresholds": json.dumps(thresholds),
            "sendEmailNotifications": "true"
            if options.get("sendEmailNotifications")
            else "false",
            "regionEnabled": "true" if options.get("regionEnabled") else "false",
        }

        if options.get("minDetectionInterval"):
            try:
                data["minDetectionInterval"] = int(options.get("minDetectionInterval"))
            except ValueError:
                pass  # doesnt parse to int

        data.update(options)

        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def update_monitoring(self, monitoringId, **options):
    (endpoint, method) = self.endpoints["update_monitoring"]
    endpoint = endpoint.replace(":monitoringId", monitoringId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {
            "detection": options.get("detection") if options.get("detection") else {},
            "schedule": options.get("schedule") if options.get("schedule") else {},
            "registeredEndpoint": options.get("registeredEndpoint")
            if options.get("registeredEndpoint")
            else {},
            "region": options.get("region") if options.get("region") else {},
        }

        data.update(options)
        return requests.request(method, endpoint, **{"headers": headers, "json": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/documentation#api-Streams-GetMonitoringsQuery
@api_call(error.InvalidQueryError)
def search_monitorings(self, **options):
    (endpoint, method) = self.endpoints["search_monitorings"]

    try:
        headers = {"Authorization": self.token.authorization_header()}
        params = {}
        params.update(options)

        return requests.request(
            method, endpoint, **{"headers": headers, "params": params}
        )
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/documentation#api-Streams-GetStreamsQuery
@api_call(error.InvalidQueryError)
def search_streams(self, **options):
    (endpoint, method) = self.endpoints["search_streams"]

    try:
        headers = {"Authorization": self.token.authorization_header()}
        params = {
            "streamId": options.get("streamId"),
            "name": options.get("name"),
            "permission": options.get("permission"),
        }
        return requests.request(
            method, endpoint, **{"headers": headers, "params": params}
        )
    except Exception as e:
        raise error.APIConnectionError(message=e)
