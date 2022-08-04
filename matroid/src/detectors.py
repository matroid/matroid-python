import io
import os
import requests
import json

from matroid import error
from matroid.src.helpers import api_call

# https://staging.app.matroid.com/docs/api/index.html#api-Detectors-PostDetectors
@api_call(error.InvalidQueryError)
def create_detector(self, file, name, detectorType, **options):
    """
    Create a new detector with the contents of the zip file

    detector_type: general, facial_recognition, or facial_characteristics
    name: the detector's display name
    file: a zip file containing the images to be used in the detector creation
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

    (endpoint, method) = self.endpoints["create_detector"]

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {"name": name, "detectorType": detectorType}
        data.update(options)

        with self.filereader.get_file(file) as file_to_upload:
            # files = {'file': file_to_upload}
            files = {"file": (file, file_to_upload, "application/zip")}
            file_size = os.fstat(file_to_upload.fileno()).st_size

            if file_size > MAX_LOCAL_ZIP_SIZE:
                raise error.InvalidQueryError(
                    message="File %s is larger than the limit of %d megabytes"
                    % (file_to_upload.name, self.bytes_to_mb(MAX_LOCAL_ZIP_SIZE))
                )
            return requests.request(
                method, endpoint, **{"headers": headers, "files": files, "data": data}
            )
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Detectors-DeleteDetectorsDetector_id
@api_call(error.InvalidQueryError)
def delete_detector(self, detectorId):
    """
    Requires processing=false.
    Note: Users can only delete pending detectors; once finalized, the only way to delete is via the Web UI.
    """
    (endpoint, method) = self.endpoints["delete_detector"]

    endpoint = endpoint.replace(":key", detectorId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Detectors-PostDetectorsDetector_idFinalize
@api_call(error.InvalidQueryError)
def finalize_detector(self, detectorId):
    """Begin training the detector"""
    (endpoint, method) = self.endpoints["finalize_detector"]

    endpoint = endpoint.replace(":key", detectorId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {}

        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


train_detector = finalize_detector

# https://staging.app.matroid.com/docs/api/index.html#api-Detectors-GetDetectorsDetector_id
@api_call(error.InvalidQueryError)
def get_detector_info(self, detectorId):
    """Get information about detector"""
    (endpoint, method) = self.endpoints["get_detector_info"]

    endpoint = endpoint.replace(":key", detectorId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


detector_info = get_detector_info

# https://staging.app.matroid.com/docs/api/index.html#api-Detectors-PostDetectorsUpload
@api_call(error.InvalidQueryError)
def import_detector(self, name, **options):
    """
    Note: certain combination of parameters can be supplied: file_detector, file_proto + file_label (+ file_label_ind), or file_proto + labels (+ label_inds). Parentheses part can be optionally supplied for object detection.
    """
    (endpoint, method) = self.endpoints["import_detector"]

    data = {
        "name": name,
    }

    def get_data_info():
        data["inputTensor"] = (options.get("inputTensor"),)
        data["outputTensor"] = (options.get("outputTensor"),)
        data["detectorType"] = (options.get("detectorType"),)

    if options.get("fileDetector"):
        file_paths = {"fileDetector": options.get("fileDetector")}
    elif options.get("fileProto") and options.get("fileLabel"):
        file_paths = {
            "fileProto": options.get("fileProto"),
            "fileLabel": options.get("fileLabel"),
            "fileLabelInd": options.get("fileLabelInd"),
        }
        get_data_info()
    elif options.get("fileProto") and options.get("labels"):
        file_paths = {
            "fileProto": options.get("fileProto"),
        }
        data["labels"] = options.get("labels")
        data["labelInds"] = options.get("labelInds")
        get_data_info()
    else:
        raise error.InvalidQueryError(message="Invalid parameter combination")

    file_objs = {}
    for file_keyword, file_path in file_paths.items():
        file_obj = self.filereader.get_file(file_path)
        file_objs[file_keyword] = file_obj

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(
            method, endpoint, **{"headers": headers, "files": file_objs, "data": data}
        )
    except IOError as e:
        raise e
    except error.InvalidQueryError as e:
        raise e
    except Exception as e:
        raise error.APIConnectionError(message=e)
    finally:
        for file_keyword, file_obj in file_objs.items():
            if isinstance(file_obj, io.IOBase):
                file_obj.close()


# https://staging.app.matroid.com/docs/api/index.html#api-Detectors-PostDetectorsDetector_idRedo
@api_call(error.InvalidQueryError)
def redo_detector(self, detectorId, **options):
    """
    Redo a detector
    Note: a deep copy of the trained detector with different detector_id will be made
    """
    (endpoint, method) = self.endpoints["redo_detector"]

    endpoint = endpoint.replace(":key", detectorId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {"feedbackOnly": "true" if options.get("feedbackOnly") else "false"}
        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Detectors-Search
@api_call(error.InvalidQueryError)
def search_detectors(self, **query):
    """Lists the available detectors"""
    (endpoint, method) = self.endpoints["detectors"]

    try:
        headers = {"Authorization": self.token.authorization_header()}
        params = {x: str(query[x]).lower() for x in query}
        params["published"] = "true" if query.get("published") else "false"

        return requests.request(
            method, endpoint, **{"headers": headers, "params": params}
        )
    except Exception as e:
        raise error.APIConnectionError(message=e)


# DEPRECATED in favor of search_detectors
@api_call(error.InvalidQueryError)
def list_detectors(self):
    """Lists the available detectors"""
    (endpoint, method) = self.endpoints["list_detectors"]

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


@api_call(error.InvalidQueryError)
def add_feedback(self, detectorId, feedback, file=None, url=None):
    """
    Add feedback to a detector using a local file or image URL
    """
    (endpoint, method) = self.endpoints["add_feedback"]
    endpoint = endpoint.replace(":detector_id", detectorId)

    if not url and not file:
        raise error.InvalidQueryError(message="Missing required parameter: file or URL")

    if url and file:
        raise error.InvalidQueryError(
            message="You may only specify a file or a URL, not both"
        )

    data = {"feedback": format_feedback(feedback)}

    image_file = None
    files = None

    try:
        if url:
            data["url"] = url
        else:
            image_file = self.filereader.get_file(file)
            files = {"file": image_file}

        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(
            method, endpoint, **{"headers": headers, "files": files, "data": data}
        )
    except IOError as e:
        raise e
    except error.InvalidQueryError as e:
        raise e
    except Exception as e:
        raise error.APIConnectionError(message=e)
    finally:
        if isinstance(image_file, io.IOBase):
            image_file.close()


@api_call(error.InvalidQueryError)
def delete_feedback(self, feedbackId, detectorId):
    """Delete previously given feedback"""
    (endpoint, method) = self.endpoints["delete_feedback"]
    endpoint = endpoint.replace(":detector_id", detectorId)
    endpoint = endpoint.replace(":feedback_id", feedbackId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except error.InvalidQueryError as e:
        raise e
    except Exception as e:
        raise error.APIConnectionError(message=e)


def format_feedback(feedback):
    if not isinstance(feedback, list):
        feedback = [feedback]

    if len(feedback) == 1:
        return json.dumps(feedback[0])

    return [json.dumps(item) for item in feedback]
