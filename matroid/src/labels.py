import requests
import json

from matroid import error
from matroid.src.helpers import api_call, batch_file_request

# https://staging.app.matroid.com/docs/api/index.html#api-Labels-PostDetectorsDetector_idLabels
@api_call(error.InvalidQueryError)
def create_label_with_images(self, detectorId, name, imageFiles, **options):
    """Create a label. Requires processing=false. Creates label asynchronously (turn processing to true)"""
    (endpoint, method) = self.endpoints["create_label_with_images"]
    endpoint = endpoint.replace(":key", detectorId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {
            "name": name,
            "destination": options.get("destination"),
        }

        if options.get("bboxes"):
            data["bboxes"] = json.dumps(options.get("bboxes"))

        if not isinstance(imageFiles, list):
            imageFiles = [imageFiles]

        return batch_file_request(
            imageFiles, method, endpoint, headers, data, "imageFiles"
        )
    except IOError as e:
        raise e
    except error.InvalidQueryError as e:
        raise e
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Labels-DeleteDetectorsDetector_idLabelsLabel_id
@api_call(error.InvalidQueryError)
def delete_label(self, detectorId, labelId):
    """Delete a label. Requires processing=false"""
    (endpoint, method) = self.endpoints["delete_label"]
    endpoint = endpoint.replace(":detectorId", detectorId)
    endpoint = endpoint.replace(":labelId", labelId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Labels-GetImagesAnnotationsQuery
@api_call(error.InvalidQueryError)
def get_annotations(self, **options):
    """Get annotations. Requires processing=false. Note: you need to provide at least one of the three ids to query"""
    (endpoint, method) = self.endpoints["get_annotations"]

    detector_id = options.get("detectorId")
    label_ids = options.get("labelIds")
    image_id = options.get("imageId")

    if not detector_id and not label_ids and not image_id:
        raise error.InvalidQueryError(
            message="Missing required parameter: detectorId, labelIds or imageId"
        )

    try:
        headers = {"Authorization": self.token.authorization_header()}
        params = {
            "detectorId": detector_id,
            "labelIds": label_ids,
            "imageId": image_id,
        }
        return requests.request(
            method, endpoint, **{"headers": headers, "params": params}
        )
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Labels-GetDetectorsDetector_idLabelsLabel_id
@api_call(error.InvalidQueryError)
def get_label_images(self, detectorId, labelId):
    (endpoint, method) = self.endpoints["get_label_images"]
    endpoint = endpoint.replace(":detectorId", detectorId)
    endpoint = endpoint.replace(":labelId", labelId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Labels-UpdateAnnotations
@api_call(error.InvalidQueryError)
def update_annotations(self, detectorId, labelId, images, **options):
    (endpoint, method) = self.endpoints["update_annotations"]
    endpoint = endpoint.replace(":detectorId", detectorId)
    endpoint = endpoint.replace(":labelId", labelId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {
            "images": json.dumps(images),
        }
        data.update(options)

        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Labels-PostDetectorsDetector_idLabelsLabel_idImages
@api_call(error.InvalidQueryError)
def update_label_with_images(self, detectorId, labelId, imageFiles, **options):
    """Requires processing=false. Updates label asynchronously (turn processing to true)"""
    (endpoint, method) = self.endpoints["update_label_with_images"]
    endpoint = endpoint.replace(":detectorId", detectorId)
    endpoint = endpoint.replace(":labelId", labelId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {}
        data.update(options)

        if not isinstance(imageFiles, list):
            imageFiles = [imageFiles]

        return batch_file_request(
            imageFiles, method, endpoint, headers, data, "imageFiles"
        )
    except IOError as e:
        raise e
    except error.InvalidQueryError as e:
        raise e
    except Exception as e:
        raise error.APIConnectionError(message=e)
