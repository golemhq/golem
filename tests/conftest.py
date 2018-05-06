import os

import pytest


@pytest.fixture(scope="function")
def test_utils():    
    """A fixture that returns an instance of Test_utils"""
    yield Test_utils


# TEST UTILS   

class Test_utils:

    @staticmethod
    def create_empty_file(path, filename):
    	filepath = os.path.join(path, filename)
    	os.makedirs(path, exist_ok=True)
    	open(filepath, 'w+').close()

