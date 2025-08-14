import inspect
import time
import pytest


def print_test_pass():
    print(f"- Passed: {inspect.currentframe().f_back.f_code.co_name}")


def wait_detector_ready_for_edit(api, detector_id):
    """Wait for detector to finish processing after creation"""
    print("Info: waiting for pending detector to be ready for editing")
    res = api.get_detector_info(detectorId=detector_id)

    tried_num = 0
    max_tries = 150  # 5 minutes timeout (150 * 2 seconds)

    while res["processing"]:
        if tried_num > max_tries:
            pytest.fail("Timeout when waiting for detector to be ready for editing")

        res = api.get_detector_info(detectorId=detector_id)
        time.sleep(2)
        tried_num += 1

    print("Info: detector is ready for editing.")
