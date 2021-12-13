import os


def pytest_generate_tests(metafunc):
    os.environ["FOO"] = "foo"
    os.environ["REDSHIFT_PASSWORD"] = "verySECRETpassword"
