import datetime
import os
import requests

from matroid import error

MAX_LOCAL_IMAGE_SIZE = 50 * 1024 * 1024
MAX_LOCAL_IMAGE_BATCH_SIZE = 50 * 1024 * 1024


def api_call(default_error):
    """setup and teardown decorator for API calls"""

    def decorator(func):
        def setup_and_teardown(self, *original_args, **original_kwargs):
            self.retrieve_token()

            response = func(self, *original_args, **original_kwargs)

            try:
                self.check_errors(response, default_error)
            except error.TokenExpirationError:
                self.retrieve_token(options={"request_from_server": True})
                return func(self, *original_args, **original_kwargs)
            else:
                return self.format_response(response)

        return setup_and_teardown

    return decorator


def bytes_to_mb(self, bytes):
    return bytes / 1024 / 1024


def check_errors(self, response=None, UserErr=None):
    """Raise specific errors depending on how the API call failed"""
    status = response.status_code
    code = None
    try:
        code = response.json().get("code")
    except:
        pass

    if status == 429 and code == "rate_err":
        raise error.RateLimitError(response)
    elif status == 402 and code == "payment_err":
        raise error.PaymentError(response)
    elif status / 100 == 4:
        if code == "token_expiration_err":
            raise error.TokenExpirationError(response)
        elif UserErr:
            raise UserErr(response)
        else:
            raise error.APIError(response)
    elif code == "media_err":
        raise error.MediaError(response)
    elif status / 100 == 5 and code == "server_err":
        raise error.ServerError(response)
    elif status / 100 != 2:
        raise error.APIError(response)


def format_response(self, response):
    """Format the output according to the options (json, print to screen)"""
    if self.print_output:
        print(response.text)
    if self.json_format:
        return response.json()
    else:
        return response.text


def save_token(self, response):
    """Extracts the access token from the API response"""
    res = response.json()

    if isinstance(res, str):
        print(response.text)
        raise error.APIError(message="Could not parse the response")

    access_token = res["access_token"]
    token_type = res["token_type"]
    expires_in = res["expires_in"]

    if not access_token or not token_type or not expires_in:
        raise error.APIError(message="Required parameters not found in the response")

    self.token = self.Token(token_type, access_token, expires_in)


def batch_file_request(
    uploaded_files, method, endpoint, headers, data, file_keyword="file"
):
    # pylint: disable = no-value-for-parameter
    filereader = FileReader()

    try:
        files = []
        total_batch_size = 0
        for file in uploaded_files:
            file_obj = filereader.get_file(file)
            file_size = check_file_size(file_obj)

            files.append((file_keyword, file_obj))
            total_batch_size += file_size

        if total_batch_size > MAX_LOCAL_IMAGE_BATCH_SIZE:
            raise error.InvalidQueryError(
                message="Max batch upload size is %d megabytes."
                % (bytes_to_mb(MAX_LOCAL_IMAGE_BATCH_SIZE))
            )

        return requests.request(
            method, endpoint, **{"headers": headers, "files": files, "data": data}
        )
    finally:
        for file_tuple in files:
            (key, file) = file_tuple
            file.close()


def check_file_size(file):
    # pylint: disable = no-value-for-parameter
    file_size = os.fstat(file.fileno()).st_size

    if file_size > MAX_LOCAL_IMAGE_SIZE:
        raise error.InvalidQueryError(
            message="File %s is larger than the limit of %d megabytes"
            % (file.name, bytes_to_mb(MAX_LOCAL_IMAGE_SIZE))
        )

    return file_size


class Token(object):
    """Represents an OAuth access token"""

    def __init__(self, token_type, token_str, expiration):
        self.token_type = token_type
        self.token_str = token_str
        self.born = datetime.datetime.now()
        self.lifetime = expiration

    def authorization_header(self):
        return self.token_type + " " + self.token_str

    def expired(self):
        return (
            self.born + datetime.timedelta(0, int(self.lifetime))
            < datetime.datetime.now()
        )


class FileReader(object):
    """Reads files for classification input"""

    def __init__(self):
        pass

    def get_file(self, file_input):
        """Extracts file from file path or returns the file if file is passed in"""
        local_file = file_input
        if isinstance(file_input, str):
            local_file = open(file_input, "rb")

        return local_file


def get_endpoints(base_url):
    end_points = {
        # accounts
        "token": (base_url + "/oauth/token", "POST"),
        "account_info": (base_url + "/account", "GET"),
        # detectors
        "create_detector": (base_url + "/detectors", "POST"),
        "delete_detector": (base_url + "/detectors/:key", "DELETE"),
        "finalize_detector": (base_url + "/detectors/:key/finalize", "POST"),
        "get_detector_info": (base_url + "/detectors/:key", "GET"),
        "import_detector": (base_url + "/detectors/upload", "POST"),
        "redo_detector": (base_url + "/detectors/:key/redo", "POST"),
        "detectors": (base_url + "/detectors/search", "GET"),
        "list_detectors": (base_url + "/detectors", "GET"),
        "add_feedback": (base_url + "/detectors/:detector_id/feedback", "POST"),
        "delete_feedback": (
            base_url + "/detectors/:detector_id/feedback/:feedback_id",
            "DELETE",
        ),
        # images
        "classify_image": (base_url + "/detectors/:key/classify_image", "POST"),
        "localize_image": (base_url + "/localize", "POST"),
        # videos
        "classify_video": (base_url + "/detectors/:key/classify_video", "POST"),
        "get_video_results": (base_url + "/videos/:key", "GET"),
        # streams
        "create_stream": (base_url + "/streams", "POST"),
        "delete_monitoring": (base_url + "/monitorings/:key", "DELETE"),
        "delete_stream": (base_url + "/streams/:key", "DELETE"),
        "get_monitoring_result": (base_url + "/monitorings/:key", "GET"),
        "kill_monitoring": (base_url + "/monitorings/:key/kill", "POST"),
        "monitor_stream": (base_url + "/streams/:streamId/monitor/:detectorId", "POST"),
        "search_monitorings": (base_url + "/monitorings", "GET"),
        "search_streams": (base_url + "/streams", "GET"),
        # labels
        "create_label_with_images": (base_url + "/detectors/:key/labels", "POST"),
        "delete_label": (base_url + "/detectors/:detectorId/labels/:labelId", "DELETE"),
        "get_annotations": (base_url + "/images/annotations", "GET"),
        "get_label_images": (
            base_url + "/detectors/:detectorId/labels/:labelId",
            "GET",
        ),
        "update_annotations": (
            base_url + "/detectors/:detectorId/labels/:labelId",
            "PATCH",
        ),
        "update_label_with_images": (
            base_url + "/detectors/:detectorId/labels/:labelId/images",
            "POST",
        ),
        # collections
        "create_collection_index": (
            base_url + "/collections/:key/collection-tasks",
            "POST",
        ),
        "create_collection": (base_url + "/collections", "POST"),
        "delete_collection_index": (base_url + "/collection-tasks/:key", "DELETE"),
        "delete_collection": (base_url + "/collections/:key", "DELETE"),
        "get_collection_task": (base_url + "/collection-tasks/:key", "GET"),
        "get_collection": (base_url + "/collections/:key", "GET"),
        "kill_collection_index": (base_url + "/collection-tasks/:key/kill", "POST"),
        "query_collection_by_scores": (
            base_url + "/collection-tasks/:key/scores-query",
            "POST",
        ),
        "query_collection_by_image": (
            base_url + "/collection-tasks/:key/image-query",
            "POST",
        ),
        "update_collection_index": (base_url + "/collection-tasks/:key", "PUT"),
        # video summary
        "create_video_summary": (base_url + "/summarize", "POST"),
        "get_video_summary": (base_url + "/summaries/:summaryId", "GET"),
        "get_video_summary_tracks": (
            base_url + "/summaries/:summaryId/tracks.csv",
            "GET",
        ),
        "get_video_summary_file": (base_url + "/summaries/:summaryId/video.mp4", "GET"),
        "delete_video_summary": (base_url + "/summaries/:summaryId", "DELETE"),
        "create_stream_summary": (base_url + "/streams/:streamId/summarize", "POST"),
        "get_stream_summaries": (base_url + "/streams/:streamId/summaries", "GET"),
        "get_existing_summaries": (base_url + "/summaries", "GET"),
    }

    return end_points
