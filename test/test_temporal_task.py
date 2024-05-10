from datetime import datetime
import time
import pytest
import random

from test.data import (
    TEST_LOCAL_VIDEO_URL,
    TEST_S3_VIDEO_URL,
    TEST_VIDEO_URL,
    EVERYDAY_OBJECT_DETECTOR_ID,
    TAL_DETECTOR_ID,
    DETECTOR_LABELS,
    TAL_DETECTOR_LABELS,
    DEFAULT_DETECTION_THRESHOLD,
)
from matroid.error import APIError
from test.helper import print_test_pass


class TestTemporalTask(object):
    def test_temporal_task(self, set_up_client):
        stream_id = None
        url_temporal_task_id = None
        local_temporal_task_id = None
        stream_temporal_task_id = None
        stream_name = "py-test-stream-{}".format(datetime.now())

        # set up client
        self.api = set_up_client

        # start testing
        try:
            self.create_temporal_task_test(
                url=TEST_VIDEO_URL, file=TEST_LOCAL_VIDEO_URL
            )
            url_temporal_task_id = self.create_temporal_task_test(url=TEST_VIDEO_URL)
            local_temporal_task_id = self.create_temporal_task_test(
                file=TEST_LOCAL_VIDEO_URL
            )
            self.get_temporal_task_test(taskId=url_temporal_task_id)
            self.get_temporal_task_preds_test()

            stream_id = self.create_stream_test(
                url=TEST_S3_VIDEO_URL, name=stream_name, dmca=True
            )
            time.sleep(90)
            stream_temporal_task_id = self.create_stream_temporal_task_test(
                streamId=stream_id,
                startTime=datetime.utcfromtimestamp(int(time.time()) - (60)),
                endTime=datetime.utcfromtimestamp(int(time.time()) - (30)),
            )
            self.get_stream_temporal_tasks_test(streamId=stream_id)

        finally:
            self.get_existing_temporal_tasks_test(
                url_temporal_task_id,
                local_temporal_task_id,
            )
            if url_temporal_task_id:
                self.delete_temporal_task_test(taskId=url_temporal_task_id)
            if local_temporal_task_id:
                self.delete_temporal_task_test(taskId=local_temporal_task_id)
            if stream_temporal_task_id:
                self.delete_temporal_task_test(taskId=stream_temporal_task_id)
            if stream_id:
                self.delete_stream_test(streamId=stream_id)

    # test cases
    def create_temporal_task_test(
        self,
        url=None,
        videoId=None,
        file=None,
    ):
        if url and file:
            with pytest.raises(APIError) as e:
                self.api.localize_video_actions(
                    detectorId=TAL_DETECTOR_ID,
                    url=url,
                    file=file,
                    labels=TAL_DETECTOR_LABELS,
                )
            assert "You may only specify a file or a URL, not both" in str(e)

        if url:
            with pytest.raises(APIError) as e:
                self.api.localize_video_actions(
                    detectorId=TAL_DETECTOR_ID,
                    url=TEST_LOCAL_VIDEO_URL,
                    labels=TAL_DETECTOR_LABELS,
                )
            assert "You provided an invalid URL" in str(e)

            with pytest.raises(APIError) as e:
                self.api.localize_video_actions(
                    detectorId=EVERYDAY_OBJECT_DETECTOR_ID,
                    url=TEST_LOCAL_VIDEO_URL,
                    labels=DETECTOR_LABELS,
                )
            assert "This detector does not support TAL" in str(e)

            res = self.api.localize_video_actions(
                detectorId=TAL_DETECTOR_ID,
                url=url,
                labels=TAL_DETECTOR_LABELS,
            )

        if file:
            res = self.api.localize_video_actions(
                detectorId=TAL_DETECTOR_ID,
                file=file,
                labels=TAL_DETECTOR_LABELS,
            )

        assert res["temporal_task"]["network"] == TAL_DETECTOR_ID

        print_test_pass()
        return res["temporal_task"]["_id"]

    def get_temporal_task_test(self, taskId):
        with pytest.raises(APIError) as e:
            self.api.get_temporal_task(taskId="123")
        assert "invalid_query_err" in str(e)

        res = self.api.get_temporal_task(taskId=taskId)

        assert res["progress"] >= 0 and res["progress"] <= 1
        assert res["state"] in [
            "requested",
            "preparing",
            "toprepare",
            "ready",
            "success",
        ]

        print_test_pass()

    def get_temporal_task_preds_test(self):
        with pytest.raises(APIError) as e:
            self.api.get_temporal_task_preds(taskId="123")
        assert "invalid_query_err" in str(e)

        print_test_pass()

    def get_existing_temporal_tasks_test(self, *task_ids):
        res = self.api.get_existing_temporal_tasks()
        res_task_ids = [task["_id"] for task in res["temporal_tasks"]]

        for task_id in task_ids:
            assert (
                task_id in res_task_ids
            ), f"Summary ID {task_id} was not found in existing user summaries."

        assert res["temporal_tasks"] is not None
        print_test_pass()

    def delete_temporal_task_test(self, taskId):
        with pytest.raises(APIError) as e:
            self.api.delete_temporal_task(taskId="123")
        assert "invalid_query_err" in str(e)

        res = self.api.delete_temporal_task(taskId=taskId)
        assert res["taskId"] == taskId
        print_test_pass()

    def create_stream_test(self, url, name, dmca):
        res = self.api.create_stream(url=url, name=name, dmca=dmca)

        assert res["streamId"] != None

        print_test_pass()
        return res["streamId"]

    def create_stream_temporal_task_test(self, streamId, startTime, endTime):
        with pytest.raises(APIError) as e:
            self.api.localize_stream_actions(
                streamId=streamId,
                startTime="test",
                endTime=endTime,
                detectorId=TAL_DETECTOR_ID,
                labels=TAL_DETECTOR_LABELS,
                thresholds=[DEFAULT_DETECTION_THRESHOLD] * len(TAL_DETECTOR_LABELS),
            )
        assert "Invalid dates provided" in str(e)
        with pytest.raises(APIError) as e:
            self.api.localize_stream_actions(
                detectorId=TAL_DETECTOR_ID,
                labels=TAL_DETECTOR_LABELS,
                streamId=streamId,
                startTime=datetime.utcfromtimestamp(
                    int(time.time()) - (24 * 60 * 60 * 8)
                ),
                endTime=endTime,
                thresholds=[DEFAULT_DETECTION_THRESHOLD] * len(TAL_DETECTOR_LABELS),
            )
        assert "Provided dates are not within your stream" in str(e)

        with pytest.raises(APIError) as e:
            self.api.localize_stream_actions(
                detectorId=EVERYDAY_OBJECT_DETECTOR_ID,
                labels=DETECTOR_LABELS,
                streamId=streamId,
                startTime=datetime.utcfromtimestamp(
                    int(time.time()) - (24 * 60 * 60 * 8)
                ),
                endTime=endTime,
                thresholds=[DEFAULT_DETECTION_THRESHOLD] * len(DETECTOR_LABELS),
            )
        assert "This detector does not support TAL" in str(e)

        res = self.api.localize_stream_actions(
            streamId,
            startTime,
            endTime,
            detectorId=TAL_DETECTOR_ID,
            labels=TAL_DETECTOR_LABELS,
            thresholds=[DEFAULT_DETECTION_THRESHOLD] * len(TAL_DETECTOR_LABELS),
        )
        assert res["temporal_task"]["feed"] == streamId
        assert (
            datetime.strptime(
                res["temporal_task"]["startTime"], "%Y-%m-%dT%H:%M:%S.000Z"
            )
            == startTime
        )
        assert (
            datetime.strptime(res["temporal_task"]["endTime"], "%Y-%m-%dT%H:%M:%S.000Z")
            == endTime
        )
        assert res["temporal_task"]["network"] == TAL_DETECTOR_ID

        print_test_pass()
        return res["temporal_task"]["_id"]

    def get_stream_temporal_tasks_test(self, streamId):
        res = self.api.get_stream_temporal_tasks(streamId)
        assert len(res["temporal_tasks"]) == 1

        print_test_pass()

    def delete_stream_test(self, streamId):
        res = self.api.delete_stream(streamId=streamId)
        assert res["message"] == "Successfully deleted stream."
        print_test_pass()
