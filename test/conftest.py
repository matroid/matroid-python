import pytest

from matroid.client import Matroid


def pytest_addoption(parser):
    parser.addoption(
        "--base_url",
        action="store",
        default="",
        help="enter your base_url for the test, default: https://www.matroid.com/api/v1",
    )
    parser.addoption("--client_id", action="store", help="enter your client_id")
    parser.addoption("--client_secret", action="store", help="enter your client_secret")


@pytest.fixture(scope="module")
def set_up_client(request):
    base_url = request.config.getoption("--base_url")
    client_id = request.config.getoption("--client_id")
    client_secret = request.config.getoption("--client_secret")

    return Matroid(base_url, client_id, client_secret)


@pytest.fixture(scope="module")
def set_up_wrong_permission_client(request):
    base_url = request.config.getoption("--base_url")
    return Matroid(
        base_url=base_url, client_id="invalid-id", client_secret="invalid-secret"
    )
