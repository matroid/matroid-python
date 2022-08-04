import os
import requests
import json

from matroid import error
from matroid.src.helpers import api_call

# https://staging.app.matroid.com/docs/api/index.html#api-Collections-PostApiVersionCollectionsCollectionidCollectionTasks
@api_call(error.InvalidQueryError)
def create_collection_index(self, collectionId, detectorId, fileTypes):
    """Create an index on a collection with a detector"""
    (endpoint, method) = self.endpoints["create_collection_index"]
    endpoint = endpoint.replace(":key", collectionId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {"detectorId": detectorId, "fileTypes": fileTypes}
        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Collections-PostCollections
@api_call(error.InvalidQueryError)
def create_collection(self, name, url, sourceType, **options):
    """Creates a new collection from a web or S3 url. Automatically kick off default indexes"""
    (endpoint, method) = self.endpoints["create_collection"]

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {
            "name": name,
            "url": url,
            "sourceType": sourceType,
            "indexWithDefault": "true" if options.get("indexWithDefault") else "false",
        }

        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Collections-DeleteCollectionTasksTaskid
@api_call(error.InvalidQueryError)
def delete_collection_index(self, taskId):
    """Deletes a completed collection mananger task"""
    (endpoint, method) = self.endpoints["delete_collection_index"]
    endpoint = endpoint.replace(":key", taskId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Collections-DeleteCollectionsCollectionid
@api_call(error.InvalidQueryError)
def delete_collection(self, collectionId):
    """Deletes a collection with no active indexing tasks"""
    (endpoint, method) = self.endpoints["delete_collection"]
    endpoint = endpoint.replace(":key", collectionId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Collections-GetCollectionTasksTaskid
@api_call(error.InvalidQueryError)
def get_collection_task(self, taskId):
    """Creates a new collection from a web or S3 url"""
    (endpoint, method) = self.endpoints["get_collection_task"]
    endpoint = endpoint.replace(":key", taskId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Collections-GetCollectionsCollectionid
@api_call(error.InvalidQueryError)
def get_collection(self, collectionId):
    """Get information about a specific collection"""
    (endpoint, method) = self.endpoints["get_collection"]
    endpoint = endpoint.replace(":key", collectionId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        return requests.request(method, endpoint, **{"headers": headers})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Collections-PostCollectionTasksTaskidKill
@api_call(error.InvalidQueryError)
def kill_collection_index(self, taskId, includeCollectionInfo):
    """Kills an active collection indexing task"""
    (endpoint, method) = self.endpoints["kill_collection_index"]
    endpoint = endpoint.replace(":key", taskId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {"includeCollectionInfo": "true" if includeCollectionInfo else ""}
        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Collections-PostApiVersionCollectionTasksTaskidScoresQuery
@api_call(error.InvalidQueryError)
def query_collection_by_scores(self, taskId, thresholds, **options):
    """
    Query against a collection index using a set of labels and scores as a query.
    Takes in a map of thresholds, and returns media in the collection with detections above those thresholds
    """
    (endpoint, method) = self.endpoints["query_collection_by_scores"]
    endpoint = endpoint.replace(":key", taskId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {
            "thresholds": json.dumps(thresholds),
            "numResults": options.get("numResults"),
        }
        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)


# https://staging.app.matroid.com/docs/api/index.html#api-Collections-PostApiCollectionTasksTaskidImageQuery
@api_call(error.InvalidQueryError)
def query_collection_by_image(self, taskId, url=None, file=None, **options):
    """
    Query against a collection index (CollectionManagerTask) using an image as key.
    Takes in an image file or url and returns similar media from the collection.
    """
    (endpoint, method) = self.endpoints["query_collection_by_image"]
    endpoint = endpoint.replace(":key", taskId)

    if not file and not url:
        raise error.InvalidQueryError(message="Missing required parameter: file or url")

    try:
        file_to_upload = None
        headers = {"Authorization": self.token.authorization_header()}
        data = {
            "boundingBox": json.dumps(options.get("boundingBox")),
            "numResults": options.get("num_results"),
        }

        if file:
            file_to_upload = self.filereader.get_file(file)
            files = {"file": file_to_upload}
            return requests.request(
                method, endpoint, **{"headers": headers, "files": files, "data": data}
            )
        else:
            data["url"] = url
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


# https://staging.app.matroid.com/docs/api/index.html#api-Collections-PutApiVersionCollectionTasksTaskid
@api_call(error.InvalidQueryError)
def update_collection_index(self, taskId, updateIndex):
    """Update a collection index"""
    (endpoint, method) = self.endpoints["update_collection_index"]
    endpoint = endpoint.replace(":key", taskId)

    try:
        headers = {"Authorization": self.token.authorization_header()}
        data = {"updateIndex": "true" if updateIndex else "false"}
        return requests.request(method, endpoint, **{"headers": headers, "data": data})
    except Exception as e:
        raise error.APIConnectionError(message=e)
