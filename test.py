import unittest
import sys
import os

if __name__ == '__main__':
    # Add api to path so imports work correctly
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'api')))
    
    # Discover and run all tests under tests/
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        sys.exit(1)
