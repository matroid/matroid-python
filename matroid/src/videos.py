import os
import requests

from matroid import error
from matroid.src.helpers import api_call

# https://staging.app.matroid.com/docs/api/index.html#api-Videos-PostDetectorsDetector_idClassify_video
@api_call(error.InvalidQueryError)
def classify_video(self, detectorId, url=None, file=None, **options):
    """
    Classify a video from a url with a detector

    detectorId: a unique id for the detector
    url: internet URL for the video to classify
    """

    MAX_LOCAL_VIDEO_SIZE = 300 * 1024 * 1024

    (endpoint, method) = self.endpoints["classify_video"]

    if not url and not file:
        raise error.InvalidQueryError(message="Missing required parameter: url or file")

    if url and file:
        raise error.InvalidQueryError(
            message="Cannot classify a URL and local file in the same request"
        )

    if isinstance(file, list):
        raise error.InvalidQueryError(
            message="Only one video can be uploaded at a time"
        )

    endpoint = endpoint.replace(":key", detectorId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {"detectorId": detectorId}
        data.update(options)

        if url:
            data["url"] = url
            return requests.request(
                method, endpoint, **{"headers": headers, "data": data}
            )
        elif file:
            with self.filereader.get_file(file) as file_to_upload:
                files = {"file": file_to_upload}
                file_size = os.fstat(file_to_upload.fileno()).st_size

                if file_size > MAX_LOCAL_VIDEO_SIZE:
                    raise error.InvalidQueryError(
                        message="File %s is larger than the limit of %d megabytes"
                        % (file_to_upload.name, self.bytes_to_mb(MAX_LOCAL_VIDEO_SIZE))
                    )

                return requests.request(
                    method,
                    endpoint,
                    **{"headers": headers, "files": files, "data": data},
                )
    except error.InvalidQueryError as e:
        raise e
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Videos-GetVideosVideo_idQuery
@api_call(error.InvalidQueryError)
def get_video_results(self, videoId, **options):
    """
    Get the current classifications for a given video ID

    videoId: a unique id for the classified video
    threshold: the cutoff for confidence level in the detection at each timestamp
    format: 'csv' or 'json' for the response format
    """
    (endpoint, method) = self.endpoints["get_video_results"]

    if options.get("format") == "csv" and self.json_format:
        print(
            "cannot return csv format when json_format True is specified upon API object initialization"
        )
        print("requesting JSON format...")
        format = "json"

    endpoint = endpoint.replace(":key", videoId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        params = {
            "videoId": videoId,
        }
        params.update(options)

        return requests.request(
            method, endpoint, **{"headers": headers, "params": params}
        )
    except Exception as e:
        raise error.APIConnectionError(message=e)
