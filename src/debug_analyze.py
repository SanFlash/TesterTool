import traceback
from analyzer.crawler import WebCrawler
from analyzer.parser import WebParser
from analyzer.test_generator import TestCaseGenerator
import os

url = 'https://app.bwsala.com/'
try:
    crawler = WebCrawler(url)
    content = crawler.fetch_website_content(url)
    print('fetched content length', len(content))
    parser = WebParser(content, url)
    links = parser.extract_links()
    print('links count', len(links))
    forms = parser.extract_forms()
    print('forms count', len(forms))
    structure = parser.extract_page_structure()
    print('structure keys', list(structure.keys()))
    lang = parser.language_analyzer.analyze_language(content, url)
    print('language analysis', lang)
    # emulate app flow further
    link_checks = [crawler.check_link_accessibility(link['url']) for link in links]
    tg = TestCaseGenerator()
    tg.generate_link_test_cases(links, link_checks)
    tg.generate_form_test_cases(forms)
    tg.generate_structure_test_cases(structure)
    tg.generate_accessibility_test_cases(structure)
    tg.generate_language_test_cases(lang)
    # export
    os.makedirs('static/reports', exist_ok=True)
    fname = tg.export_to_csv('static/reports/debug_test_cases.csv')
    print('exported to', fname)
    test_cases = tg.get_test_cases_df().to_dict('records')
    print('test cases count', len(test_cases))
except Exception as e:
    print('Exception:', e)
    traceback.print_exc()
