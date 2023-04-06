import requests

from matroid import error
from matroid.src.helpers import api_call

# https://staging.app.matroid.com/docs/api/documentation#api-Video_Summary-PostSummarize
@api_call(error.InvalidQueryError)
def create_video_summary(
    self,
    detectorId,
    name=None,
    labels=None,
    url=None,
    videoId=None,
    file=None,
    fps=None,
    mc_lambda=None,
    matching_distance=None,
    n_init=None,
    nn_budget=None,
    max_iou_dist=None,
    max_age=None,
    detection_threshold=None,
):
    """Create a video summary with provided url or file"""
    (endpoint, method) = self.endpoints["create_video_summary"]

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
            "name": name,
            "detectorId": detectorId,
            "labels": labels,
            "fps": fps,
            "mc_lambda": mc_lambda,
            "matching_distance": matching_distance,
            "n_init": n_init,
            "nn_budget": nn_budget,
            "max_iou_dist": max_iou_dist,
            "max_age": max_age,
            "detection_threshold": detection_threshold,
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


# https://staging.app.matroid.com/docs/api/documentation#api-Video_Summary-GetSummariesSummaryid
@api_call(error.InvalidQueryError)
def get_video_summary(self, summaryId):
    """Fetch a video summary"""
    (endpoint, method) = self.endpoints["get_video_summary"]
    endpoint = endpoint.replace(":summaryId", summaryId)

    try:
        headers = {"Authorization": self.token.authorization_header()}

        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/documentation#api-Video_Summary-GetSummariesSummaryidTracksCsv
@api_call(error.InvalidQueryError)
def get_video_summary_tracks(self, summaryId):
    """Fetch a video summary track CSV"""
    (endpoint, method) = self.endpoints["get_video_summary_tracks"]
    endpoint = endpoint.replace(":summaryId", summaryId)

    try:
        headers = {"Authorization": self.token.authorization_header()}

        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/documentation#api-Video_Summary-GetSummariesSummaryidVideoMp4
@api_call(error.InvalidQueryError)
def get_video_summary_file(self, summaryId):
    """Fetch a video summary video file"""
    (endpoint, method) = self.endpoints["get_video_summary_file"]
    endpoint = endpoint.replace(":summaryId", summaryId)

    try:
        headers = {"Authorization": self.token.authorization_header()}

        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/documentation#api-Video_Summary-DeleteSummariesSummaryid
@api_call(error.InvalidQueryError)
def delete_video_summary(self, summaryId):
    """Delete a video summary"""
    (endpoint, method) = self.endpoints["delete_video_summary"]
    endpoint = endpoint.replace(":summaryId", summaryId)

    try:
        headers = {"Authorization": self.token.authorization_header()}

        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/documentation#api-Video_Summary-GetStreamsStreamidSummaries
@api_call(error.InvalidQueryError)
def get_stream_summaries(self, streamId):
    """Fetch all video summaries for a stream"""
    (endpoint, method) = self.endpoints["get_stream_summaries"]
    endpoint = endpoint.replace(":streamId", streamId)

    try:
        headers = {"Authorization": self.token.authorization_header()}

        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/documentation#api-Video_Summary-PostStreamsStreamidSummarize
@api_call(error.InvalidQueryError)
def create_stream_summary(
    self,
    streamId,
    startTime,
    endTime,
    detectorId,
    name=None,
    labels=None,
    fps=None,
    mc_lambda=None,
    matching_distance=None,
    n_init=None,
    nn_budget=None,
    max_iou_dist=None,
    max_age=None,
    detection_threshold=None,
):
    """Create a video summary for a stream"""
    (endpoint, method) = self.endpoints["create_stream_summary"]
    endpoint = endpoint.replace(":streamId", streamId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {
            "name": name,
            "startTime": startTime,
            "endTime": endTime,
            "detectorId": detectorId,
            "labels": labels,
            "fps": fps,
            "mc_lambda": mc_lambda,
            "matching_distance": matching_distance,
            "n_init": n_init,
            "nn_budget": nn_budget,
            "max_iou_dist": max_iou_dist,
            "max_age": max_age,
            "detection_threshold": detection_threshold,
        }

        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.dev.matroid.com/docs/api/documentation#api-Video_Summary-GetSummaries
@api_call(error.InvalidQueryError)
def get_existing_summaries(self):
    (endpoint, method) = self.endpoints["get_existing_summaries"]
    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)
