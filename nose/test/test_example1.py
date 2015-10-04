import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

class Test (unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_example1_func(self):
        from example1 import func1
        self.assertIsNone(func1())

        
