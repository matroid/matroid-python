import inspect


def print_test_pass():
    print("- Passed: {}".format(inspect.currentframe().f_back.f_code.co_name))
