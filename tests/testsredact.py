import pytest
from redactor import main

def test_main_function():
    # Test case 1
    args = argparse.Namespace(input=['./test_input.txt'], names=True, dates=False, phones=False, genders=False, address=False, output='./test_output', stats=None)
    main(args)
    # Verify that output file was created
    assert os.path.exists('./test_output/test_input.txt')

    # Test case 2
    args = argparse.Namespace(input=['./test_input.txt'], names=True, dates=True, phones=True, genders=True, address=True, output='./test_output', stats=None)
    main(args)
    # Verify that output file was created
    assert os.path.exists('./test_output/test_input.txt')
