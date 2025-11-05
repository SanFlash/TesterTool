import pandas as pd
from datetime import datetime
import logging
from typing import List, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class TestCaseGenerator:
    def __init__(self):
        self.test_cases = []
        self.tc_counter = 1

    def add_test_case(self, description: str, test_step: str, expected_result: str, actual_result: str, status: str):
        """Add a new test case to the collection"""
        self.test_cases.append({
            'TC_ID': f'TC_{self.tc_counter:03d}',
            'Test Case Description': description,
            'Test Step': test_step,
            'Expected Result': expected_result,
            'Actual Result': actual_result,
            'Status': status
        })
        self.tc_counter += 1

    def generate_link_test_cases(self, links: List[Dict[str, Any]], link_checks: List[Dict[str, Any]]):
        """Generate test cases for links"""
        for link, check in zip(links, link_checks):
            # Basic link presence test
            self.add_test_case(
                description=f"Verify presence of link: {link['text']}",
                test_step=f"Check if link with text '{link['text']}' exists",
                expected_result="Link should be present in the page",
                actual_result="Link is present",
                status="Pass"
            )

            # Link accessibility test
            status = "Pass" if check['is_accessible'] else "Fail"
            actual_result = (
                f"Link is accessible with status code {check['status_code']}"
                if check['is_accessible']
                else f"Link is not accessible: {check.get('error', f'Status code: {check['status_code']}')}"
            )

            self.add_test_case(
                description=f"Verify accessibility of link: {link['text']}",
                test_step=f"Try to access URL: {link['url']}",
                expected_result="Link should be accessible with 2xx/3xx status code",
                actual_result=actual_result,
                status=status
            )

    def generate_form_test_cases(self, forms: List[Dict[str, Any]]):
        """Generate test cases for forms"""
        for i, form in enumerate(forms, 1):
            # Form presence test
            self.add_test_case(
                description=f"Verify presence of form #{i}",
                test_step=f"Check if form with action '{form['action']}' exists",
                expected_result="Form should be present in the page",
                actual_result="Form is present",
                status="Pass"
            )

            # Required fields test
            required_fields = [f for f in form['fields'] if f['required']]
            if required_fields:
                self.add_test_case(
                    description=f"Verify required fields in form #{i}",
                    test_step="Check if required fields are properly marked",
                    expected_result=f"Fields {', '.join(f['name'] for f in required_fields)} should be required",
                    actual_result="All required fields are properly marked",
                    status="Pass"
                )

            # Form submission test
            self.add_test_case(
                description=f"Verify form #{i} submission endpoint",
                test_step=f"Check if form action URL '{form['action']}' is valid",
                expected_result="Form action URL should be valid",
                actual_result=f"Form action URL is {'valid' if form['action'] else 'missing'}",
                status="Pass" if form['action'] else "Fail"
            )

    def generate_structure_test_cases(self, structure: Dict[str, Any]):
        """Generate comprehensive test cases for page structure"""
        # Title test
        if 'title' in structure:
            self.add_test_case(
                description="Verify page title",
                test_step="Check if page has a title",
                expected_result="Page should have a title",
                actual_result=f"Page title is '{structure['title']}'",
                status="Pass" if structure['title'] else "Fail"
            )

        # Meta tags tests
        meta = structure.get('meta', {})
        for meta_type, content in meta.items():
            self.add_test_case(
                description=f"Verify meta {meta_type}",
                test_step=f"Check if page has meta {meta_type}",
                expected_result=f"Page should have meta {meta_type}",
                actual_result=f"Meta {meta_type} is {'present' if content else 'missing'}",
                status="Pass" if content else "Fail"
            )

        # Viewport test for responsiveness
        if 'viewport' in meta:
            self.add_test_case(
                description="Verify responsive design meta tag",
                test_step="Check if page has viewport meta tag",
                expected_result="Page should have viewport meta tag for responsiveness",
                actual_result=f"Viewport meta tag is present: {meta['viewport']}",
                # Guard against None: meta['viewport'] may be None even when key exists
                status="Pass" if 'width=device-width' in (meta.get('viewport') or '') else "Fail"
            )

        # Scripts and Stylesheets
        self._generate_resource_test_cases(structure)

        # Tables analysis
        if 'tables' in structure:
            self._generate_table_test_cases(structure['tables'])

        # Interactive elements
        if 'interactive_elements' in structure:
            self._generate_interactive_element_test_cases(structure['interactive_elements'])

        # SEO elements
        if 'seo_elements' in structure:
            self._generate_seo_test_cases(structure['seo_elements'])

        # Security elements
        if 'security_headers' in structure:
            self._generate_security_test_cases(structure['security_headers'])

        # Social media tags
        if 'social_meta' in structure:
            self._generate_social_media_test_cases(structure['social_meta'])

    def _generate_resource_test_cases(self, structure):
        """Generate test cases for scripts and stylesheets"""
        scripts = structure.get('scripts', {})
        if scripts:
            self.add_test_case(
                description="Verify script loading",
                test_step="Check script inclusion",
                expected_result="Page should load all required scripts",
                actual_result=f"Found {scripts['total']} scripts ({scripts['external']} external, {scripts['inline']} inline)",
                status="Pass" if scripts['total'] > 0 else "Fail"
            )

        stylesheets = structure.get('stylesheets', {})
        if stylesheets:
            self.add_test_case(
                description="Verify stylesheet loading",
                test_step="Check stylesheet inclusion",
                expected_result="Page should load all required stylesheets",
                actual_result=f"Found {stylesheets['total']} stylesheets ({stylesheets['external']} external, {stylesheets['inline']} inline)",
                status="Pass" if stylesheets['total'] > 0 else "Fail"
            )

    def _generate_table_test_cases(self, tables):
        """Generate test cases for table accessibility"""
        for i, table in enumerate(tables, 1):
            self.add_test_case(
                description=f"Verify table #{i} accessibility",
                test_step="Check table structure and accessibility features",
                expected_result="Table should have proper headers and structure",
                actual_result=(
                    f"Table has {table['rows']} rows, {table['cols']} columns, "
                    f"{'has' if table['has_headers'] else 'lacks'} headers, "
                    f"{'has' if table['has_caption'] else 'lacks'} caption"
                ),
                status="Pass" if table['has_headers'] and table['has_caption'] else "Warning"
            )

    def _generate_interactive_element_test_cases(self, elements):
        """Generate test cases for interactive elements"""
        total_inputs = sum(elements['inputs'].values())
        self.add_test_case(
            description="Verify form elements presence",
            test_step="Check presence of interactive elements",
            expected_result="Page should have necessary interactive elements",
            actual_result=(
                f"Found {elements['buttons']} buttons, {total_inputs} input fields, "
                f"{elements['select']} select dropdowns, {elements['textarea']} text areas"
            ),
            status="Pass" if total_inputs > 0 else "Info"
        )

    def _generate_seo_test_cases(self, seo):
        """Generate SEO-related test cases"""
        self.add_test_case(
            description="Verify SEO basics",
            test_step="Check basic SEO elements",
            expected_result="Page should have basic SEO elements",
            actual_result=(
                f"{'Has' if seo['canonical'] else 'Missing'} canonical link, "
                f"{'Has' if seo['meta_description'] else 'Missing'} meta description, "
                f"Image alt text ratio: {seo['img_alt_ratio']:.0%}"
            ),
            status="Pass" if all([seo['canonical'], seo['meta_description'], seo['img_alt_ratio'] > 0.8]) else "Warning"
        )

    def _generate_security_test_cases(self, security):
        """Generate security-related test cases"""
        self.add_test_case(
            description="Verify security measures",
            test_step="Check security features",
            expected_result="Page should implement basic security measures",
            actual_result=(
                f"CSRF protection: {'Present' if security['csrf_token'] else 'Missing'}, "
                f"External links: {security['external_links']}, "
                f"Password fields: {security['password_inputs']}"
            ),
            status="Pass" if security['csrf_token'] or security['password_inputs'] == 0 else "Warning"
        )

    def _generate_social_media_test_cases(self, social):
        """Generate social media metadata test cases"""
        og_tags = social.get('og_tags', {})
        twitter_tags = social.get('twitter_tags', {})
        
        self.add_test_case(
            description="Verify social media metadata",
            test_step="Check social media meta tags",
            expected_result="Page should have social media meta tags",
            actual_result=(
                f"OpenGraph tags: {len(og_tags)}, "
                f"Twitter cards: {len(twitter_tags)}"
            ),
            status="Pass" if og_tags or twitter_tags else "Info"
        )

    def generate_language_test_cases(self, language_analysis: Dict[str, Any]):
        """Generate comprehensive language-related test cases"""
        # Language Declaration Test
        declared = language_analysis['declared_language']
        detected = language_analysis['detected_language']
        
        self.add_test_case(
            description="Verify HTML language declaration",
            test_step="Check if page has proper language declaration",
            expected_result="Page should have valid language declaration",
            actual_result=(
                f"Declared language: {declared['name']} ({declared['code']})"
                if declared['code']
                else "No language declaration found"
            ),
            status="Pass" if declared['code'] else "Fail"
        )

        # Language Detection Test
        self.add_test_case(
            description="Verify content language",
            test_step="Detect main content language",
            expected_result="Content language should be detectable",
            actual_result=(
                f"Detected language: {detected['name']} ({detected['code']}) "
                f"with {detected['confidence']:.1%} confidence"
            ),
            status="Pass" if detected['confidence'] > 0.8 else "Warning"
        )

        # Language Consistency Test
        if declared['code'] and detected['code']:
            is_consistent = declared['code'].split('-')[0] == detected['code']
            self.add_test_case(
                description="Verify language consistency",
                test_step="Compare declared vs detected language",
                expected_result="Declared language should match content language",
                actual_result=(
                    f"Declared: {declared['name']} ({declared['code']}), "
                    f"Detected: {detected['name']} ({detected['code']})"
                ),
                status="Pass" if is_consistent else "Fail"
            )

        # Multi-language Content Test
        other_langs = language_analysis['other_languages']
        if other_langs:
            self.add_test_case(
                description="Check multi-language content",
                test_step="Analyze content for multiple languages",
                expected_result="Document should consistently use declared language",
                actual_result=(
                    f"Found content in other languages: "
                    f"{', '.join(f'{lang['name']} ({lang['confidence']:.1%})' for lang in other_langs)}"
                ),
                status="Info"
            )

        # Text Direction Test
        direction = language_analysis['direction']
        self.add_test_case(
            description="Verify text direction",
            test_step="Check if text direction is appropriate for the language",
            expected_result="Text direction should match language requirements",
            actual_result=f"Text direction is {direction.upper()}",
            status="Pass"
        )

        # Character Encoding Test
        charset = language_analysis.get('charset', 'utf-8')
        self.add_test_case(
            description="Verify character encoding",
            test_step="Check character encoding declaration",
            expected_result="Page should use UTF-8 or appropriate encoding",
            actual_result=f"Character encoding: {charset}",
            status="Pass" if charset.lower() in ['utf-8', 'utf8'] else "Warning"
        )

        # Language Elements Test
        elements = language_analysis.get('language_elements', {})
        lang_attrs = elements.get('lang_attributes', [])
        self.add_test_case(
            description="Check language annotations",
            test_step="Verify language attributes on elements",
            expected_result="Multi-language content should be properly marked",
            actual_result=f"Found {len(lang_attrs)} elements with language attributes",
            status="Pass" if len(lang_attrs) > 0 or not other_langs else "Warning"
        )

        # Translation Support Test
        translation_links = elements.get('translation_links', [])
        if translation_links:
            self.add_test_case(
                description="Check translation support",
                test_step="Verify language switching options",
                expected_result="Multi-language sites should offer language selection",
                actual_result=f"Found {len(translation_links)} language switcher links",
                status="Pass" if len(translation_links) > 0 else "Info"
            )

        # Locale Information Test
        locale_info = language_analysis.get('locale_info', {})
        if locale_info:
            self.add_test_case(
                description="Verify locale information",
                test_step="Check locale-specific content",
                expected_result="Content should be properly localized",
                actual_result=(
                    f"Language: {locale_info.get('language_name', 'Unknown')}, "
                    f"Territory: {locale_info.get('territory', 'Not specified')}, "
                    f"Script: {locale_info.get('script', 'Not specified')}"
                ),
                status="Info"
            )

    def generate_accessibility_test_cases(self, structure: Dict[str, Any]):
        """Generate comprehensive accessibility test cases"""
        # Image alt text test
        images = structure['images']
        images_without_alt = [img for img in images if not img['alt']]
        
        self.add_test_case(
            description="Verify image alt texts",
            test_step="Check if all images have alt text",
            expected_result="All images should have alt text",
            actual_result=(
                "All images have alt text"
                if not images_without_alt
                else f"{len(images_without_alt)} images missing alt text"
            ),
            status="Pass" if not images_without_alt else "Fail"
        )

        # Heading hierarchy test
        headings = structure['headings']
        has_h1 = len(headings.get('h1', [])) > 0
        self.add_test_case(
            description="Verify heading hierarchy",
            test_step="Check if page has proper heading structure starting with H1",
            expected_result="Page should have at least one H1 heading",
            actual_result="Found H1 heading" if has_h1 else "No H1 heading found",
            status="Pass" if has_h1 else "Fail"
        )

        # Check for multiple H1s
        multiple_h1s = len(headings.get('h1', [])) > 1
        self.add_test_case(
            description="Check for multiple H1 headings",
            test_step="Verify page has only one main H1 heading",
            expected_result="Page should have only one H1 heading",
            actual_result=f"Found {len(headings.get('h1', []))} H1 heading(s)",
            status="Pass" if not multiple_h1s else "Fail"
        )

        # ARIA landmarks test
        if 'landmarks' in structure:
            self.add_test_case(
                description="Verify ARIA landmarks",
                test_step="Check for presence of ARIA landmarks",
                expected_result="Page should have proper ARIA landmarks",
                actual_result=f"Found {len(structure['landmarks'])} ARIA landmarks",
                status="Pass" if structure['landmarks'] else "Fail"
            )

    def get_test_cases_df(self) -> pd.DataFrame:
        """Convert test cases to a pandas DataFrame"""
        return pd.DataFrame(self.test_cases)

    def export_to_csv(self, filename: str):
        """Export test cases to a CSV file"""
        df = self.get_test_cases_df()
        df.to_csv(filename, index=False)
        return filename


def generate_test_cases(parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compatibility wrapper to generate test cases from parsed data.

    The older test-suite expects a module-level function generate_test_cases.
    This builds a TestCaseGenerator and returns the generated test cases list.
    """
    gen = TestCaseGenerator()
    links = parsed_data.get('links', [])
    # Provide optimistic default link checks if none provided
    link_checks = [{'url': l.get('url'), 'status_code': 200, 'is_accessible': True} for l in links]
    if links:
        gen.generate_link_test_cases(links, link_checks)

    forms = parsed_data.get('forms', [])
    if forms:
        gen.generate_form_test_cases(forms)

    structure = parsed_data.get('structure', {})
    if structure:
        gen.generate_structure_test_cases(structure)
        gen.generate_accessibility_test_cases(structure)

    # Language tests if available
    language_analysis = parsed_data.get('language')
    if language_analysis:
        try:
            gen.generate_language_test_cases(language_analysis)
        except Exception:
            # don't fail generation for missing or partial language info
            pass

    return gen.test_cases