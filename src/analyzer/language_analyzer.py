from typing import Dict, Any, List
import logging
import re
from bs4 import BeautifulSoup
import langid
from deep_translator import GoogleTranslator
from charset_normalizer import detect as detect_charset
import html5lib

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    'en': {'name': 'English', 'native': 'English'},
    'es': {'name': 'Spanish', 'native': 'Español'},
    'fr': {'name': 'French', 'native': 'Français'},
    'de': {'name': 'German', 'native': 'Deutsch'},
    'it': {'name': 'Italian', 'native': 'Italiano'},
    'pt': {'name': 'Portuguese', 'native': 'Português'},
    'ru': {'name': 'Russian', 'native': 'Русский'},
    'ja': {'name': 'Japanese', 'native': '日本語'},
    'ko': {'name': 'Korean', 'native': '한국어'},
    'zh': {'name': 'Chinese', 'native': '中文'},
    'ar': {'name': 'Arabic', 'native': 'العربية'},
    'hi': {'name': 'Hindi', 'native': 'हिन्दी'},
    'nl': {'name': 'Dutch', 'native': 'Nederlands'},
    'pl': {'name': 'Polish', 'native': 'Polski'},
    'tr': {'name': 'Turkish', 'native': 'Türkçe'},
    'vi': {'name': 'Vietnamese', 'native': 'Tiếng Việt'},
    'th': {'name': 'Thai', 'native': 'ไทย'},
    'sv': {'name': 'Swedish', 'native': 'Svenska'},
    'da': {'name': 'Danish', 'native': 'Dansk'},
    'fi': {'name': 'Finnish', 'native': 'Suomi'}
}

class LanguageAnalyzer:
    def __init__(self):
        langid.set_languages(list(LANGUAGE_NAMES.keys()))
        
    def analyze_language(self, html_content: str, url: str) -> Dict[str, Any]:
        """Analyze the language characteristics of the webpage"""
        if html_content is None:
            raise ValueError("HTML content cannot be None")
        if not isinstance(html_content, str):
            raise ValueError("HTML content must be a string")

        soup = BeautifulSoup(html_content, 'lxml')
        
        # Get declared language
        html_tag = soup.find('html')
        declared_lang = html_tag.get('lang', '') if html_tag else ''
        
        # Extract text content
        text_content = self._extract_text_content(soup)
        
        # Handle empty text content
        if not text_content or len(text_content.strip()) < 10:  # Require at least 10 chars for analysis
            return {
                'error': 'Insufficient text content for language analysis',
                'declared_language': {'code': declared_lang} if declared_lang else None,
                'detected_language': None,
                'other_languages': [],
                'direction': 'ltr',  # default
                'language_elements': self._analyze_language_elements(soup),
                'charset': self._detect_charset(html_content)
            }
        
        try:
            # Detect primary language using langid
            detected_lang, confidence = langid.classify(text_content)

            # Get language details from our mapping
            lang_info = LANGUAGE_NAMES.get(detected_lang, {
                'name': 'Unknown',
                'native': 'Unknown'
            })

            # Analyze language consistency
            other_langs = self._detect_other_languages(text_content, detected_lang)

            lang_analysis = {
                'declared_language': {
                    'code': declared_lang,
                    'name': LANGUAGE_NAMES.get(declared_lang.split('-')[0], {}).get('name', 'Not declared') if declared_lang else 'Not declared',
                    'native_name': LANGUAGE_NAMES.get(declared_lang.split('-')[0], {}).get('native', 'Not declared') if declared_lang else 'Not declared'
                },
                'detected_language': {
                    'code': detected_lang,
                    'name': lang_info['name'],
                    'native_name': lang_info['native'],
                    'confidence': confidence
                },
                'other_languages': other_langs,
                'direction': 'rtl' if self._is_rtl_language(detected_lang) else 'ltr',
                'language_elements': self._analyze_language_elements(soup),
                'charset': self._detect_charset(html_content)
            }

            return lang_analysis

        except Exception as e:
            logger.error(f"Error analyzing language for {url}: {str(e)}")
            return {
                'error': f"Language detection failed: {str(e)}",
                'declared_language': {'code': declared_lang} if declared_lang else None
            }

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract meaningful text content from the webpage"""
        # Remove scripts and styles
        for script in soup(['script', 'style', 'code', 'pre']):
            script.decompose()
        
        # Get text and normalize whitespace
        text = ' '.join(soup.stripped_strings)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _detect_other_languages(self, text: str, primary_lang: str, chunks: int = 8) -> List[Dict[str, Any]]:
        """Detect other languages present in the text by sampling chunks.

        Returns a list of dicts with keys: code, name, native, count, avg_confidence
        """
        if not text or len(text) < 50:
            return []

        # Break text into roughly equal chunks
        length = len(text)
        step = max(1, length // chunks)
        counts: Dict[str, List[float]] = {}

        for i in range(0, length, step):
            sample = text[i:i+step].strip()
            if not sample:
                continue
            try:
                lang, conf = langid.classify(sample)
            except Exception:
                continue
            if lang == primary_lang:
                continue
            counts.setdefault(lang, []).append(conf)

        results: List[Dict[str, Any]] = []
        for lang, confs in counts.items():
            avg_conf = sum(confs) / len(confs) if confs else 0
            info = LANGUAGE_NAMES.get(lang, {'name': 'Unknown', 'native': 'Unknown'})
            results.append({
                'code': lang,
                'name': info.get('name', 'Unknown'),
                'native': info.get('native', 'Unknown'),
                'count': len(confs),
                'confidence': avg_conf
            })

        # Sort by count then confidence
        results.sort(key=lambda r: (r['count'], r['confidence']), reverse=True)
        return results

    def _is_rtl_language(self, lang_code: str) -> bool:
        """Check if the language is RTL"""
        rtl_languages = {'ar', 'fa', 'he', 'ur', 'arc', 'az', 'dv', 'ku', 'nqo'}
        return lang_code in rtl_languages

    def _analyze_language_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze language-specific elements in the page"""
        # Validate input
        if not soup or not isinstance(soup, BeautifulSoup):
            return {
                'lang_attributes': [],
                'dir_attributes': [],
                'multilingual_meta': {},
                'translation_links': []
            }

        try:
            elements = {
                'lang_attributes': self._find_lang_attributes(soup),
                'dir_attributes': self._find_dir_attributes(soup),
                'multilingual_meta': self._find_multilingual_meta(soup),
                'translation_links': self._find_translation_links(soup)
            }
            return elements
        except Exception as e:
            logger.error(f"Error analyzing language elements: {str(e)}")
            return {
                'lang_attributes': [],
                'dir_attributes': [],
                'multilingual_meta': {},
                'translation_links': []
            }

    def _find_lang_attributes(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Find elements with lang attributes"""
        elements = []
        for element in soup.find_all(attrs={'lang': True}):
            elements.append({
                'tag': element.name,
                'lang': element['lang']
            })
        return elements

    def _find_dir_attributes(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Find elements with dir attributes"""
        elements = []
        for element in soup.find_all(attrs={'dir': True}):
            elements.append({
                'tag': element.name,
                'dir': element['dir']
            })
        return elements

    def _find_multilingual_meta(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Find multilingual meta tags"""
        return {
            'alternate_links': [
                {
                    'href': link['href'],
                    'hreflang': link['hreflang']
                }
                for link in soup.find_all('link', rel='alternate', hreflang=True)
            ],
            'content_language': soup.find('meta', {'http-equiv': 'content-language'})['content']
            if soup.find('meta', {'http-equiv': 'content-language'})
            else None
        }

    def _find_translation_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Find language switcher links"""
        translation_links = []
        
        # Common patterns for language switcher links
        patterns = [
            {'class_': re.compile(r'lang|language|translate', re.I)},
            {'id': re.compile(r'lang|language|translate', re.I)},
            {'href': re.compile(r'[?&]lang=|/[a-z]{2}(?:-[A-Z]{2})?/', re.I)}
        ]
        
        for pattern in patterns:
            links = soup.find_all('a', pattern)
            for link in links:
                translation_links.append({
                    'text': link.get_text(strip=True),
                    'href': link.get('href', ''),
                    'lang': link.get('hreflang', '')
                })
        
        return translation_links

    def _detect_charset(self, content: str) -> str:
        """Detect character encoding"""
        try:
            result = detect_charset(content.encode())
            return result['encoding']
        except Exception:
            return 'utf-8'  # Default to UTF-8 if detection fails

    def get_language_name(self, lang_code: str) -> Dict[str, str]:
        """Get language names for a given language code"""
        try:
            lang_info = LANGUAGE_NAMES.get(lang_code.split('-')[0], {
                'name': 'Unknown',
                'native': 'Unknown'
            })
            return {
                'name': lang_info['name'],
                'native': lang_info['native'],
                'code': lang_code
            }
        except Exception:
            return {
                'name': 'Unknown',
                'native': 'Unknown',
                'code': lang_code
            }