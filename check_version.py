import json, sys, urllib.request, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "matroid"))
from version import VERSION


def versions(package_name):
    """returns a list of versions of the package on pypi"""
    url = "https://pypi.org/pypi/%s/json" % (package_name,)
    data = json.load(urllib.request.urlopen(url))
    versions = list(data["releases"].keys())
    return versions


if __name__ == "__main__":
    prev_versions = versions("matroid")
    assert VERSION not in prev_versions
