import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

def test_simple_example1_func():
    from example1 import func1
    func1()
