from src.analyzer.crawler import fetch_website_content
from src.analyzer.parser import parse_html
from src.analyzer.test_generator import generate_test_cases
import unittest

class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        self.url = "http://example.com"
        self.html_content = fetch_website_content(self.url)
        self.parsed_data = parse_html(self.html_content)

    def test_fetch_website_content(self):
        self.assertIsNotNone(self.html_content)
        self.assertIn("<html>", self.html_content)

    def test_parse_html(self):
        self.assertIsInstance(self.parsed_data, dict)
        self.assertIn('links', self.parsed_data)
        self.assertIn('forms', self.parsed_data)

    def test_generate_test_cases(self):
        test_cases = generate_test_cases(self.parsed_data)
        self.assertIsInstance(test_cases, list)
        self.assertGreater(len(test_cases), 0)

if __name__ == '__main__':
    unittest.main()