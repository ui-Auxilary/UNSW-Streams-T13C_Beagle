import pytest 

from src.other import clear_v1, check_user_exists

'''
    TESTS:
    - Right output for clear_v1
    - Check_user_exists
'''

def test_valid_output_clear():
    ## check that it returns an empty dictionary
    assert clear_v1() == {}

