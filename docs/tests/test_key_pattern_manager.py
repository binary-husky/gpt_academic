import unittest

def validate_path():
    import os, sys

    os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) + "/..")
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)


validate_path()  # validate path so you can run from base directory

from shared_utils.key_pattern_manager import is_openai_api_key

class TestKeyPatternManager(unittest.TestCase):
    def test_is_openai_api_key_with_valid_key(self):
        key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        self.assertTrue(is_openai_api_key(key))

        key = "sx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        self.assertFalse(is_openai_api_key(key))

        key = "sess-wg61ZafYHpNz7FFwIH7HGZlbVqUVaeV5tatHCWpl"
        self.assertTrue(is_openai_api_key(key))

        key = "sess-wg61ZafYHpNz7FFwIH7HGZlbVqUVa5tatHCWpl"
        self.assertFalse(is_openai_api_key(key))


    def test_is_openai_api_key_with_invalid_key(self):
        key = "invalid_key"
        self.assertFalse(is_openai_api_key(key))

    def test_is_openai_api_key_with_custom_pattern(self):
        # Assuming you have set a custom pattern in your configuration
        key = "custom-pattern-key"
        self.assertFalse(is_openai_api_key(key))

if __name__ == '__main__':
    unittest.main()