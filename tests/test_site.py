import copy
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit

from scripts.portfolio_generator import (
    REPO_ROOT, load_portfolio_data, render_projects, render_site, validate_data,
)


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.ids = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])


class ContentTests(unittest.TestCase):
    def test_valid_content(self):
        validate_data(load_portfolio_data())

    def test_invalid_content_fails_before_publish(self):
        changes = [
            lambda d: d['projects'][0].update(slug='../escape'),
            lambda d: d['projects'][1].update(slug=d['projects'][0]['slug']),
            lambda d: d['projects'][0].update(title=''),
            lambda d: d['projects'][0].update(tags=['unknown']),
            lambda d: d['projects'][0].update(github_url='javascript:alert(1)'),
            lambda d: d['projects'][0].update(image_url='https://example.com/image.webp'),
            lambda d: d['projects'][0].update(problem=None),
            lambda d: d['tag_order'].append(d['tag_order'][0]),
        ]
        for change in changes:
            data = copy.deepcopy(load_portfolio_data())
            change(data)
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_data(data)

    def test_text_is_escaped_in_text_and_attributes(self):
        project = copy.deepcopy(load_portfolio_data()['projects'][0])
        project['title'] = '\" onerror=\"alert(1) <script>bad</script>'
        project['description'] = '<script>bad</script>'
        html = render_projects([project])
        self.assertNotIn('<script>', html)
        for tag, attrs in Document(html).elements:
            self.assertNotIn('onerror', attrs)
            if tag == 'img':
                self.assertEqual(attrs['alt'], project['title'])


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = render_site()

    def test_generated_pages_match_sources(self):
        for name, expected in self.pages.items():
            with self.subTest(page=name):
                self.assertEqual((REPO_ROOT / 'docs' / name).read_text(encoding='utf-8'), expected)

    def test_local_links_assets_and_fragments_resolve(self):
        root = (REPO_ROOT / 'docs').resolve()
        for name, html in self.pages.items():
            document = Document(html)
            self.assertEqual(len(document.ids), len(set(document.ids)), name)
            for tag, attrs in document.elements:
                for attr in ('href', 'src'):
                    url = attrs.get(attr, '')
                    if not url or urlsplit(url).scheme or url.startswith('//'):
                        continue
                    parts = urlsplit(url)
                    target = root / (parts.path.lstrip('/') if parts.path.startswith('/') else str(Path(name).parent / parts.path))
                    if not parts.path:
                        target = root / name
                    if target.is_dir():
                        target /= 'index.html'
                    with self.subTest(page=name, url=url):
                        self.assertTrue(target.resolve().is_relative_to(root))
                        self.assertTrue(target.is_file(), f'Missing asset: {url}')
                        if parts.fragment and target.suffix == '.html':
                            ids = Document(target.read_text(encoding='utf-8')).ids
                            self.assertIn(unquote(parts.fragment), ids)
                if 'aria-controls' in attrs:
                    self.assertIn(attrs['aria-controls'], document.ids)

    def test_metadata_and_headings(self):
        descriptions = []
        for name, html in self.pages.items():
            elements = Document(html).elements
            self.assertEqual(sum(tag == 'h1' for tag, _ in elements), 1, name)
            self.assertEqual(sum(attrs.get('aria-current') == 'page' for _, attrs in elements), 1, name)
            self.assertNotIn('cdn.tailwindcss.com', html)
            self.assertNotIn('{{', html)
            descriptions += [attrs['content'] for _, attrs in elements if attrs.get('name') == 'description']
            self.assertTrue(any(attrs.get('property') == 'og:image' for _, attrs in elements))
            self.assertTrue(any(attrs.get('rel') == 'canonical' for _, attrs in elements))
        self.assertEqual(len(set(descriptions)), len(self.pages))

    def test_images_are_local_sized_and_lazy(self):
        for name, html in self.pages.items():
            for tag, attrs in Document(html).elements:
                if tag != 'img' or '/images/' not in attrs.get('src', ''):
                    continue
                self.assertTrue(attrs['src'].startswith('/static/'))
                if attrs['src'].endswith('.webp'):
                    self.assertIn('width', attrs)
                    self.assertIn('height', attrs)
                    self.assertLess((REPO_ROOT / 'docs' / attrs['src'].lstrip('/')).stat().st_size, 150_000)
                    if not name.startswith('projects/'):
                        self.assertEqual(attrs.get('loading'), 'lazy')


if __name__ == '__main__':
    unittest.main()
