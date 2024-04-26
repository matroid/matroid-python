import requests

from matroid import error
from matroid.src.helpers import api_call

# https://staging.app.matroid.com/docs/api/index.html#api-Temporal_Task-PostLocalizeActions
@api_call(error.InvalidQueryError)
def localize_video_actions(
    self,
    detectorId,
    labels=None,
    url=None,
    videoId=None,
    file=None,
    fps=None,
):
    """Localize actions in a provided url or file"""
    (endpoint, method) = self.endpoints["localize_video_actions"]

    if not detectorId:
        raise error.InvalidQueryError(message="Missing required parameter: detectorID")

    if not file and not url:
        raise error.InvalidQueryError(message="Missing required parameter: file or url")

    if url and file:
        raise error.InvalidQueryError(
            message="You may only specify a file or a URL, not both"
        )
    try:
        file_to_upload = None
        headers = {"Authorization": self.token.authorization_header()}
        data = {
            "detectorId": detectorId,
            "labels": labels,
            "fps": fps,
        }
        if file:
            file_to_upload = self.filereader.get_file(file)
            files = {"file": file_to_upload}

            return requests.request(
                method, endpoint, **{"headers": headers, "files": files, "data": data}
            )
        else:
            data["url"] = url
            if videoId:
                data["videoId"] = videoId

            return requests.request(
                method, endpoint, **{"headers": headers, "data": data}
            )
    except IOError as e:
        raise e
    except error.InvalidQueryError as e:
        raise e
    except Exception as e:
        raise error.APIConnectionError(message=e)
    finally:
        if file_to_upload:
            file_to_upload.close()


# https://staging.app.matroid.com/docs/api/index.html#api-Temporal_Task-PostStreamsStreamidLocalizeActions
@api_call(error.InvalidQueryError)
def localize_stream_actions(
    self,
    streamId,
    startTime,
    endTime,
    detectorId,
    labels=None,
    fps=None,
    thresholds=None,
):
    """Localize actions in a stream"""
    (endpoint, method) = self.endpoints["localize_stream_actions"]
    endpoint = endpoint.replace(":streamId", streamId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {
            "startTime": startTime,
            "endTime": endTime,
            "detectorId": detectorId,
            "labels": labels,
            "fps": fps,
            "detectionThresholds": thresholds,
        }

        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Temporal_Task-DeleteTemporalTasksTask
@api_call(error.InvalidQueryError)
def delete_temporal_task(self, taskId):
    """Delete a temporal task"""
    (endpoint, method) = self.endpoints["delete_temporal_task"]
    endpoint = endpoint.replace(":taskId", taskId)

    try:
        headers = {"Authorization": self.token.authorization_header()}

        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Temporal_Task-GetTemporalTasks
@api_call(error.InvalidQueryError)
def get_existing_temporal_tasks(self):
    """Fetch all temporal tasks for user"""
    (endpoint, method) = self.endpoints["get_existing_temporal_tasks"]
    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Temporal_Task-GetTemporalTasksTemporaltaskid
@api_call(error.InvalidQueryError)
def get_temporal_task(self, taskId):
    """Fetch a temporal task by id"""
    (endpoint, method) = self.endpoints["get_temporal_task"]
    endpoint = endpoint.replace(":taskId", taskId)

    try:
        headers = {"Authorization": self.token.authorization_header()}

        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Temporal_Task-GetStreamsStreamidTemporalTasks
@api_call(error.InvalidQueryError)
def get_stream_temporal_tasks(self, streamId):
    """Fetch all temporal tasks for a stream"""
    (endpoint, method) = self.endpoints["get_stream_temporal_tasks"]
    endpoint = endpoint.replace(":streamId", streamId)

    try:
        headers = {"Authorization": self.token.authorization_header()}

        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Temporal_Task-GetTemporalTasksTaskidPredsJson
@api_call(error.InvalidQueryError)
def get_temporal_task_preds(self, taskId):
    """Fetch a predictions JSON for given temporal task"""
    (endpoint, method) = self.endpoints["get_temporal_task_preds"]
    endpoint = endpoint.replace(":taskId", taskId)

    try:
        headers = {"Authorization": self.token.authorization_header()}

        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Temporal_Task-PostStreamsStreamidSampleStream
@api_call(error.InvalidQueryError)
def sample_stream(
    self,
    streamId,
    startTime,
    endTime,
    detectorId,
    labels=None,
    fps=None,
):
    """Localize actions in a stream"""
    (endpoint, method) = self.endpoints["sample_stream"]
    endpoint = endpoint.replace(":streamId", streamId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {
            "startTime": startTime,
            "endTime": endTime,
            "detectorId": detectorId,
            "labels": labels,
            "fps": fps,
        }

        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)
