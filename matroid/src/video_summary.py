import requests

from matroid import error
from matroid.src.helpers import api_call

# https://staging.dev.matroid.com/docs/api/index.html#api-Video_Summary-PostSummarize
@api_call(error.InvalidQueryError)
def create_video_summary(self, url=None, videoId=None, file=None):
    """Create an video summary with provided url or file"""
    (endpoint, method) = self.endpoints["create_video_summary"]

    if not file and not url:
        raise error.InvalidQueryError(message="Missing required parameter: file or url")

    if url and file:
        raise error.InvalidQueryError(
            message="You may only specify a file or a URL, not both"
        )
    try:
        file_to_upload = None
        headers = {"Authorization": self.token.authorization_header()}
        data = {}
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


# https://staging.dev.matroid.com/docs/api/index.html#api-Video_Summary-GetSummariesSummaryid
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


# https://staging.dev.matroid.com/docs/api/index.html#api-Video_Summary-GetSummariesSummaryidTracksCsv
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


# https://staging.dev.matroid.com/docs/api/index.html#api-Video_Summary-GetSummariesSummaryidVideoMp4
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


# https://staging.dev.matroid.com/docs/api/index.html#api-Video_Summary-DeleteSummariesSummaryid
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


# https://staging.dev.matroid.com/docs/api/index.html#api-Video_Summary-GetStreamsStreamidSummaries
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


# https://staging.dev.matroid.com/docs/api/index.html#api-Video_Summary-PostStreamsStreamidSummarize
@api_call(error.InvalidQueryError)
def create_stream_summary(self, streamId, startTime, endTime):
    """Create a video summary for a stream"""
    (endpoint, method) = self.endpoints["create_stream_summary"]
    endpoint = endpoint.replace(":streamId", streamId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {"startTime": startTime, "endTime": endTime}

        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)
