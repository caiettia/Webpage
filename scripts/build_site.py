"""Render pages and copy locally managed assets. Run CSS compilation afterward."""
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.portfolio_generator import REPO_ROOT, render_site


def main():
    output = REPO_ROOT / 'docs'
    pages = render_site()
    for name, content in pages.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8', newline='\n')
    # Remove case-study output for projects that are no longer featured.
    for old_page in (output / 'projects').glob('*/index.html'):
        if old_page.relative_to(output).as_posix() not in pages:
            old_page.unlink()
    shutil.copytree(REPO_ROOT / 'src/static', output / 'static/projects', dirs_exist_ok=True)
    (output / 'resume').mkdir(exist_ok=True)
    shutil.copyfile(REPO_ROOT / 'resumes/Resume_2026.pdf', output / 'resume/Andrew-Caietti-Resume.pdf')
    urls = ['https://acaietti.com/' + name.removesuffix('index.html') for name in pages]
    (output / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join('<url><loc>' + url + '</loc></url>' for url in urls) + '\n</urlset>\n', encoding='utf-8')
    (output / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://acaietti.com/sitemap.xml\n', encoding='utf-8')
    print(f'Built {len(pages)} pages, local assets, résumé, and sitemap.')


if __name__ == '__main__':
    main()
