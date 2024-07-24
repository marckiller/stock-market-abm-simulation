import unittest

def main():
    test_dir = 'test'
    suite = unittest.TestLoader().discover(start_dir=test_dir, pattern='test*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    main()