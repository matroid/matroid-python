from datetime import datetime, timedelta
import time
import os
import sys
import pytest

from unittest import mock

from urllib3.exceptions import ProtocolError

from test.data import (
    EVERYDAY_OBJECT_DETECTOR_ID,
    TEST_S3_VIDEO_URL,
    TEST_S3_VIDEO_URL_2,
    TEST_VIDEO_URL,
    RANDOM_MONGO_ID,
)
from matroid.error import InvalidQueryError, APIError
from test.helper import print_test_pass
from matroid.src.sse import _parse_sse_event as orig_parse_sse

DETECTOR_TEST_ZIP = os.getcwd() + "/test/test_file/cat-dog-lacroix.zip"
PUSH_IMAGE_TEST_IMAGE = os.getcwd() + "/test/test_file/cat.jpg"
PUSH_IMAGE_API_STREAM_URL = "api_image_push://example"
PUSH_IMAGE_API_STREAM_DEFAULT_IMAGE_SRC = (
    "https://images.pexels.com/photos/1563356/pexels-photo-1563356.jpeg"
)


class TestStreams(object):
    def test_stream(self, set_up_client):
        stream_id = None
        stream_id_2 = None
        stream_id_3 = None  # Push Image API Stream
        monitoring_id = None
        monitoring_id_2 = None

        stream_name = "py-test-stream-{}".format(datetime.now())
        stream_name_2 = "py-test-stream-2-{}".format(datetime.now())
        stream_name_3 = "py-test-stream-3-{}".format(datetime.now())
        thresholds = {"cat": 0.5, "dog": 0.6, "car": 0.1}
        task_name = "test-task"
        minDetectionInterval = 90
        # set up client
        self.api = set_up_client

        # start testing
        try:
            stream_id = self.create_stream_test(url=TEST_S3_VIDEO_URL, name=stream_name)
            self.update_stream_test(
                stream_id,
                "new-name",
                "5",
                [{"key": "i am a key", "template": "and i am a template"}],
            )
            stream_id_2 = self.register_stream_test(
                url=TEST_S3_VIDEO_URL_2, name=stream_name_2
            )

            stream_id_3 = self.create_stream_test(
                url=PUSH_IMAGE_API_STREAM_URL,
                name=stream_name_3,
                defaultImagePull={"source": PUSH_IMAGE_API_STREAM_DEFAULT_IMAGE_SRC},
            )
            monitoring_id = self.monitor_stream_test(
                stream_id=stream_id,
                detector_id=EVERYDAY_OBJECT_DETECTOR_ID,
                thresholds=thresholds,
                task_name=task_name,
                minDetectionInterval=minDetectionInterval,
            )

            monitoring_id_2 = self.monitor_stream_test(
                stream_id=stream_id_2,
                detector_id=EVERYDAY_OBJECT_DETECTOR_ID,
                thresholds=thresholds,
                task_name=task_name + "_2",
                minDetectionInterval=minDetectionInterval,
            )
            self.search_monitorings_test(
                stream_id=stream_id, monitoring_id=monitoring_id
            )
            self.search_streams_test()
            self.get_monitoring_result_test(monitoring_id=monitoring_id)
            self.get_monitoring_result_in_range_test(
                monitoring_id=monitoring_id,
                start_time="2022-05-01 00:00:00",
                end_time="2022-06-01 00:00:00",
            )
            self.watch_monitoring_result_test(
                monitoring_id=monitoring_id,
            )
            self.watch_monitoring_result_retry_test(
                monitoring_id=monitoring_id,
            )
            self.update_monitoring_test(
                monitoring_id=monitoring_id,
                thresholds={"cat": 0.98, "dog": 0.99},
                minDetectionInterval="50",
            )

            self.bulk_update_monitorings_test(
                monitoring_ids=[monitoring_id, monitoring_id_2],
                task_update={
                    "detection": {
                        "thresholds": [
                            "1",
                            "1",
                            "1",
                            "1",
                            "1",
                            "1",
                            "1",
                            "1",
                            "1",
                            "0.7",
                            "1",
                            "1",
                            "1",
                            "1",
                            "1",
                            "1",
                            "1",
                            "1",
                            "1",
                            "1",
                        ],
                        "notificationAlertSounds": [
                            "simple-ding.mp3",
                            "invalid.mp3",
                            "invalid.mp3",
                            "invalid.mp3",
                            "invalid.mp3",
                            "simple-ding.mp3",
                            "invalid.mp3",
                            "invalid.mp3",
                            "invalid.mp3",
                            "invalid.mp3",
                            "simple-ding.mp3",
                            "invalid.mp3",
                            "invalid.mp3",
                            "invalid.mp3",
                            "invalid.mp3",
                            "-",
                            "harp-strum.mp3",
                            "invalid.mp3",
                            "invalid.mp3",
                            "invalid.mp3",
                        ],
                    },
                    "registeredEndpoints": {
                        "uri": "http://example.com",
                    },
                },
            )

            self.watch_monitoring_result_stop_test(
                monitoring_id=monitoring_id,
            )

            self.sample_stream_test(
                stream_id=stream_id,
                start_time=datetime.now() - timedelta(seconds=2),
                end_time=datetime.now(),
            )

            self.push_image_test(
                stream_id=stream_id_3,
            )
        finally:
            if monitoring_id:
                self.kill_monitoring_test(monitoring_id=monitoring_id)
                self.wait_for_monitoring_stop(monitoring_id=monitoring_id)
                self.delete_monitoring_test(monitoring_id=monitoring_id)

            if monitoring_id_2:
                self.kill_monitoring_test(monitoring_id=monitoring_id_2)
                self.wait_for_monitoring_stop(monitoring_id=monitoring_id_2)
                self.delete_monitoring_test(monitoring_id=monitoring_id_2)

            if stream_id:
                self.delete_stream_test(stream_id=stream_id)
            if stream_id_2:
                self.delete_stream_test(stream_id=stream_id_2)
            if stream_id_3:
                self.delete_stream_test(stream_id=stream_id_3)

    # test cases
    def create_stream_test(self, url, name, defaultImagePull=None):
        res = self.api.create_stream(
            url=url, name=name, defaultImagePull=defaultImagePull
        )
        assert res["streamId"] != None

        with pytest.raises(APIError) as e:
            self.api.create_stream(
                url=url, name=name, defaultImagePull=defaultImagePull
            )
        assert "invalid_query_err" in str(e)

        print_test_pass()
        return res["streamId"]

    def update_stream_test(self, stream_id, name, retention_days, custom_fields):
        res = self.api.update_stream(
            streamId=stream_id,
            name=name,
            retentionDays=retention_days,
            customFields=custom_fields,
        )
        assert res["feed"] == stream_id
        assert res["name"] == name
        assert str(res["retentionDays"]) == retention_days
        assert res["customFields"] == custom_fields

        print_test_pass()

    def register_stream_test(self, url, name):
        res = self.api.register_stream(url=url, name=name)
        assert res["streamId"] != None

        with pytest.raises(APIError) as e:
            self.api.register_stream(url=url, name=name)
        assert "invalid_query_err" in str(e)

        print_test_pass()
        return res["streamId"]

    def monitor_stream_test(
        self, stream_id, detector_id, thresholds, task_name, minDetectionInterval
    ):
        end_time = "5 minutes"

        with pytest.raises(APIError) as e:
            self.api.monitor_stream(
                streamId=RANDOM_MONGO_ID,
                detectorId=detector_id,
                thresholds=thresholds,
                endTime=end_time,
                taskName=task_name,
                minDetectionInterval=minDetectionInterval,
            )
        assert "invalid_query_err" in str(e)

        res = self.api.monitor_stream(
            streamId=stream_id,
            detectorId=detector_id,
            thresholds=thresholds,
            endTime=end_time,
            taskName=task_name,
            minDetectionInterval=minDetectionInterval,
        )
        assert res["monitoringId"] != None
        assert res["minDetectionInterval"] == minDetectionInterval
        print_test_pass()
        return res["monitoringId"]

    def update_monitoring_test(self, monitoring_id, thresholds, minDetectionInterval):
        regionCoords = [
            "0.2500,0.2500",
            "0.7500,0.2500",
            "0.7500,0.7500",
            "0.2500,0.7500",
        ]
        regionEnabled = True
        res = self.api.update_monitoring(
            monitoringId=monitoring_id,
            thresholds=thresholds,
            minDetectionInterval=minDetectionInterval,
            regionEnabled=regionEnabled,
            regionCoords=regionCoords,
        )
        assert res["detection"]["minDetectionInterval"] == int(minDetectionInterval)
        # indexed thresholds for cat and dog
        assert res["detection"]["thresholds"] == [
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "0.98",
            "1",
            "1",
            "1",
            "0.99",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ]
        assert res["region"]["enabled"] == regionEnabled
        assert res["region"]["focusAreas"][0]["coords"] == [regionCoords]
        print_test_pass()

    def bulk_update_monitorings_test(self, monitoring_ids, task_update):
        res = self.api.bulk_update_monitorings(
            monitoring_ids=monitoring_ids, task_update=task_update
        )

        modified_monitorings = res["modifiedMonitorings"]
        assert len(modified_monitorings) == 2
        for monitoring in modified_monitorings:
            assert monitoring["_id"] in monitoring_ids
            assert monitoring["detection"]["thresholds"] == [
                "1",
                "1",
                "1",
                "1",
                "1",
                "1",
                "1",
                "1",
                "1",
                "0.7",
                "1",
                "1",
                "1",
                "1",
                "1",
                "1",
                "1",
                "1",
                "1",
                "1",
            ]
            assert monitoring["detection"]["notificationAlertSounds"] == [
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "-",
                "harp-strum.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
                "simple-ding.mp3",
            ]
        print_test_pass()

    def search_monitorings_test(self, stream_id, monitoring_id):
        res = self.api.search_monitorings(streamId=stream_id)
        assert res[0]["monitoringId"] == monitoring_id
        print_test_pass()

    def search_streams_test(self):
        res = self.api.search_streams(permission="private")
        assert res[0]["streamId"] != None
        print_test_pass()

    def get_monitoring_result_test(self, monitoring_id):
        res = self.api.get_monitoring_result(monitoringId=monitoring_id)
        assert res != None
        print_test_pass()

    def watch_monitoring_result_test(self, monitoring_id):
        res = self.api.watch_monitoring_result(monitoringId=monitoring_id)
        actual_res = next(iter(res))
        res.close()
        assert actual_res != None
        assert actual_res["monitoringId"] == monitoring_id
        assert len(actual_res["detections"]) >= 1
        print_test_pass()

    def watch_monitoring_result_retry_test(self, monitoring_id):
        first_call = True

        def sse_mock_impl(*args, **kwargs):
            nonlocal first_call
            if first_call:
                first_call = False
                raise ProtocolError("Fake protocol error")
            else:
                return orig_parse_sse(*args, **kwargs)

        with mock.patch("matroid.src.sse._parse_sse_event") as sse_mock:
            sse_mock.side_effect = sse_mock_impl
            res = self.api.watch_monitoring_result(monitoringId=monitoring_id)
            actual_res = next(iter(res))
            res.close()
            assert actual_res != None
            assert actual_res["monitoringId"] == monitoring_id
            assert len(actual_res["detections"]) >= 1

            assert not first_call, "Expected to throw an exception first"
            print_test_pass()

    def watch_monitoring_result_stop_test(self, monitoring_id):
        """Verifies we can stop a watch_monitoring."""
        from threading import Thread

        res = None
        exc = None

        def run():
            nonlocal res
            nonlocal exc
            try:
                res = self.api.watch_monitoring_result(monitoringId=monitoring_id)
                actual_res = next(iter(res))
                assert False, "Not expecting to reach this"
            except StopIteration as e:
                exc = e

        thread = Thread(target=run, daemon=True)
        thread.start()
        time.sleep(1)
        assert res
        res.close()
        thread.join(timeout=5)
        assert not thread.is_alive()
        assert isinstance(exc, StopIteration)
        print_test_pass()

    def get_monitoring_result_in_range_test(self, monitoring_id, start_time, end_time):
        res = self.api.get_monitoring_result(
            monitoringId=monitoring_id, startTime=start_time, endTime=end_time
        )
        assert res != None
        print_test_pass()

    def kill_monitoring_test(self, monitoring_id):
        res = self.api.kill_monitoring(monitoringId=monitoring_id)
        assert res["message"] == "Successfully killed monitoring."
        print_test_pass()

    def delete_monitoring_test(self, monitoring_id):
        res = self.api.delete_monitoring(monitoringId=monitoring_id)
        assert res["message"] == "Successfully deleted monitoring."
        print_test_pass()

    def delete_stream_test(self, stream_id):
        res = self.api.delete_stream(streamId=stream_id)
        assert res["message"] == "Successfully deleted stream."
        print_test_pass()

    def sample_stream_test(self, stream_id, start_time, end_time):
        res = self.api.create_detector(
            name="sample-stream-test",
            detectorType="general",
            file=DETECTOR_TEST_ZIP,
        )

        detector_id = res["detectorId"]

        time.sleep(5)
        res = self.api.sample_stream(
            streamId=stream_id,
            startTime=start_time,
            endTime=end_time,
            detectorId=detector_id,
            label="cat",
        )
        assert res != None
        assert res["temporal_task"] != None
        assert res["temporal_task"]["_id"] != None
        print_test_pass()

    def push_image_test(self, stream_id):
        res = self.api.push_image(
            streamId=stream_id,
            useDefaultSource=None,
            timestamp=None,
            metadata="",
            file=PUSH_IMAGE_TEST_IMAGE,
        )
        assert res["success"] == True

        res2 = self.api.push_image(streamId=stream_id, useDefaultSource=True)
        assert res["success"] == True
        print_test_pass()

    # helpers
    def wait_for_monitoring_stop(self, monitoring_id):
        print("Info: waiting for monitoring to stop")
        res = self.api.search_monitorings(monitoringId=monitoring_id)

        num_tried = 0
        max_tries = 15
        while res[0]["state"] != "failed" and res[0]["state"] != "scheduled":
            if num_tried > max_tries:
                pytest.fail("Timeout when waiting for monitoring to stop")

            res = self.api.search_monitorings(monitoringId=monitoring_id)
            time.sleep(2)

            num_tried += 1

        print("Info: monitoring stopped.")
