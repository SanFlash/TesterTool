import sys
import os
# Ensure project root is on sys.path so we can import analyzer package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analyzer.parser import WebParser
html='''<html><head><title>Test</title></head><body>
<a href="/about">About</a>
<a href="http://external.example.com/page">External</a>
<a>EmptyAnchor</a>
<a href="javascript:void(0)">JS</a>
</body></html>'''
parser=WebParser(html,'http://example.com')
print('links:', parser.extract_links())
print('security:', parser._extract_security_elements())
