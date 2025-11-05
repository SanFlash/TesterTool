from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from .language_analyzer import LanguageAnalyzer

logger = logging.getLogger(__name__)

class WebParser:
    def __init__(self, html_content, base_url):
        if not html_content:
            raise ValueError("HTML content cannot be None or empty")
        if not base_url:
            raise ValueError("Base URL cannot be None or empty")
            
        self.soup = BeautifulSoup(html_content, 'lxml')
        self.base_url = base_url
        self.language_analyzer = LanguageAnalyzer()

    def extract_links(self):
        """Extract all links from the page"""
        links = []
        base_netloc = urlparse(self.base_url).netloc
        for a_tag in self.soup.find_all('a', href=True):
            href = a_tag.get('href')
            if not href:
                # skip anchors without usable href
                continue
            text = a_tag.get_text(strip=True)
            try:
                absolute_url = urljoin(self.base_url, href)
            except Exception:
                # fallback: skip malformed URLs
                continue

            # Determine internal vs external by comparing netlocs (safer than substring checks)
            try:
                link_netloc = urlparse(absolute_url).netloc
                link_type = 'internal' if link_netloc == base_netloc else 'external'
            except Exception:
                link_type = 'external'

            links.append({
                'url': absolute_url,
                'text': text,
                'type': link_type
            })
        return links

    def extract_forms(self):
        """Extract all forms and their fields"""
        forms = []
        for form in self.soup.find_all('form'):
            fields = []
            
            # Get form attributes
            action = urljoin(self.base_url, form.get('action', ''))
            method = form.get('method', 'get').upper()
            
            # Extract form fields
            for field in form.find_all(['input', 'textarea', 'select']):
                field_type = field.get('type', 'text')
                field_name = field.get('name', '')
                field_id = field.get('id', '')
                required = field.get('required') is not None
                
                fields.append({
                    'type': field_type,
                    'name': field_name,
                    'id': field_id,
                    'required': required
                })
            
            forms.append({
                'action': action,
                'method': method,
                'fields': fields
            })
        
        return forms

    def extract_page_structure(self):
        """Extract comprehensive page structure and elements"""
        structure = {
            'title': self.soup.title.string if self.soup.title else None,
            'headings': {
                f'h{i}': [h.get_text(strip=True) for h in self.soup.find_all(f'h{i}')]
                for i in range(1, 7)
            },
            'meta': {
                'description': self.soup.find('meta', {'name': 'description'}).get('content', '') if self.soup.find('meta', {'name': 'description'}) else None,
                'keywords': self.soup.find('meta', {'name': 'keywords'}).get('content', '') if self.soup.find('meta', {'name': 'keywords'}) else None,
                'viewport': self.soup.find('meta', {'name': 'viewport'}).get('content', '') if self.soup.find('meta', {'name': 'viewport'}) else None,
                'charset': self.soup.find('meta', {'charset': True}).get('charset', '') if self.soup.find('meta', {'charset': True}) else None,
                'robots': self.soup.find('meta', {'name': 'robots'}).get('content', '') if self.soup.find('meta', {'name': 'robots'}) else None
            },
            'images': [{'src': img.get('src'), 'alt': img.get('alt', ''), 'title': img.get('title', ''), 'width': img.get('width', ''), 'height': img.get('height', '')} for img in self.soup.find_all('img')],
            'scripts': {
                'total': len(self.soup.find_all('script')),
                'external': len(self.soup.find_all('script', src=True)),
                'inline': len(self.soup.find_all('script', src=False))
            },
            'stylesheets': {
                'total': len(self.soup.find_all('link', rel='stylesheet')),
                'external': len(self.soup.find_all('link', {'rel': 'stylesheet', 'href': True})),
                'inline': len(self.soup.find_all('style'))
            },
            'language': self.soup.html.get('lang') if self.soup.html else None,
            'landmarks': self._extract_landmarks(),
            'lists': {
                'ul': len(self.soup.find_all('ul')),
                'ol': len(self.soup.find_all('ol')),
                'dl': len(self.soup.find_all('dl'))
            },
            'tables': self._analyze_tables(),
            'interactive_elements': self._extract_interactive_elements(),
            'seo_elements': self._extract_seo_elements(),
            'security_headers': self._extract_security_elements(),
            'social_meta': self._extract_social_meta()
        }
        return structure



    def _extract_landmarks(self):
        """Extract ARIA landmarks and semantic elements"""
        landmarks = []
        # Check for HTML5 semantic elements
        semantic_elements = ['header', 'nav', 'main', 'article', 'aside', 'footer', 'section']
        for element in semantic_elements:
            elements = self.soup.find_all(element)
            for el in elements:
                landmarks.append({
                    'type': element,
                    'role': el.get('role', ''),
                    'aria-label': el.get('aria-label', '')
                })
        
        # Check for ARIA roles
        roles = ['banner', 'navigation', 'main', 'complementary', 'contentinfo']
        for role in roles:
            elements = self.soup.find_all(role=role)
            for el in elements:
                landmarks.append({
                    'type': el.name,
                    'role': role,
                    'aria-label': el.get('aria-label', '')
                })
        return landmarks

    def _analyze_tables(self):
        """Analyze table structures"""
        tables = []
        for table in self.soup.find_all('table'):
            tables.append({
                'has_caption': bool(table.find('caption')),
                'has_headers': bool(table.find_all('th')),
                'rows': len(table.find_all('tr')),
                'cols': len(table.find_all('td')) // len(table.find_all('tr')) if table.find_all('tr') else 0,
                'has_scope': bool(table.find_all('th', attrs={'scope': True}))
            })
        return tables

    def _extract_interactive_elements(self):
        """Extract interactive elements"""
        return {
            'buttons': len(self.soup.find_all('button')),
            'inputs': {
                'text': len(self.soup.find_all('input', {'type': 'text'})),
                'password': len(self.soup.find_all('input', {'type': 'password'})),
                'email': len(self.soup.find_all('input', {'type': 'email'})),
                'checkbox': len(self.soup.find_all('input', {'type': 'checkbox'})),
                'radio': len(self.soup.find_all('input', {'type': 'radio'})),
                'submit': len(self.soup.find_all('input', {'type': 'submit'}))
            },
            'select': len(self.soup.find_all('select')),
            'textarea': len(self.soup.find_all('textarea')),
            'clickable': len(self.soup.find_all(['a', 'button', 'input', {'type': 'submit'}]))
        }

    def _extract_seo_elements(self):
        """Extract SEO-related elements"""
        return {
            'canonical': bool(self.soup.find('link', {'rel': 'canonical'})),
            'h1_count': len(self.soup.find_all('h1')),
            'meta_description': bool(self.soup.find('meta', {'name': 'description'})),
            'meta_keywords': bool(self.soup.find('meta', {'name': 'keywords'})),
            'img_alt_ratio': sum(1 for img in self.soup.find_all('img') if img.get('alt')) / len(self.soup.find_all('img')) if self.soup.find_all('img') else 1
        }

    def _extract_security_elements(self):
        """Extract security-related elements"""
        return {
            'csrf_token': bool(self.soup.find('input', {'name': ['csrf_token', '_token', '_csrf']})),
            'external_links': len([
                a for a in self.soup.find_all('a', href=True)
                if isinstance(a.get('href'), str)
                and a.get('href').startswith(('http', 'https'))
                and urlparse(a.get('href')).netloc != urlparse(self.base_url).netloc
            ]),
            'password_inputs': len(self.soup.find_all('input', {'type': 'password'})),
            'forms_with_csrf': len([form for form in self.soup.find_all('form') if form.find('input', {'name': ['csrf_token', '_token', '_csrf']})])
        }

    def _extract_social_meta(self):
        """Extract social media meta tags"""
        return {
            'og_tags': {tag.get('property'): tag.get('content') for tag in self.soup.find_all('meta', property=lambda x: x and x.startswith('og:'))},
            'twitter_tags': {tag.get('name'): tag.get('content') for tag in self.soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})}
        }


def parse_html(html_content: str, base_url: str = 'http://example.com') -> dict:
    """Compatibility wrapper: parse HTML and return a dict with links, forms, and structure."""
    parser = WebParser(html_content, base_url)
    return {
        'links': parser.extract_links(),
        'forms': parser.extract_forms(),
        'structure': parser.extract_page_structure()
    }