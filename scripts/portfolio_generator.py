"""Dependency-free renderer for the static site; Django is not part of the build."""
from __future__ import annotations
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_DATA_PATH = REPO_ROOT / 'content/portfolio/projects.json'
TEMPLATES = REPO_ROOT / 'src/templates'
PORTFOLIO_TEMPLATE_PATH = TEMPLATES / 'portfolio.html'
PORTFOLIO_OUTPUT_PATH = REPO_ROOT / 'docs/portfolio/index.html'
FILTERS_MARKER = '{{PORTFOLIO_FILTERS}}'
PROJECTS_MARKER = '{{PORTFOLIO_PROJECTS}}'


def validate_data(data: object) -> dict:
    if not isinstance(data, dict) or not isinstance(data.get('projects'), list) or not data['projects']:
        raise ValueError('Portfolio data must include a nonempty projects list.')
    tags = data.get('tag_order')
    if not isinstance(tags, list) or not all(isinstance(tag, str) and tag.strip() for tag in tags):
        raise ValueError('tag_order must contain nonempty strings.')
    if len(set(tags)) != len(tags):
        raise ValueError('tag_order contains duplicates.')
    slugs = set()
    for project in data['projects']:
        if not isinstance(project, dict):
            raise ValueError('Each project must be an object.')
        for field in ('title', 'description', 'slug', 'image_url'):
            if not isinstance(project.get(field), str) or not project[field].strip():
                raise ValueError(f'Project requires a nonempty {field}.')
        slug = project['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs:
            raise ValueError(f'Invalid or duplicate project slug: {slug}')
        slugs.add(slug)
        project_tags = project.get('tags')
        if not isinstance(project_tags, list) or not all(isinstance(tag, str) and tag in tags for tag in project_tags):
            raise ValueError(f'{slug}: tags must appear in tag_order.')
        if len(set(project_tags)) != len(project_tags):
            raise ValueError(f'{slug}: duplicate tags.')
        if not re.fullmatch(r'/static/projects/images/[a-z0-9-]+\.webp', project['image_url']):
            raise ValueError(f'{slug}: use a local optimized WebP thumbnail.')
        for field in ('github_url', 'demo_url'):
            url = project.get(field)
            if url is not None and (not isinstance(url, str) or urlsplit(url).scheme != 'https' or not urlsplit(url).netloc):
                raise ValueError(f'{slug}: {field} must be an HTTPS URL or null.')
        if not (project.get('github_url') or project.get('demo_url')):
            raise ValueError(f'{slug}: provide a source or demo link.')
        if 'featured' in project and not isinstance(project['featured'], bool):
            raise ValueError(f'{slug}: featured must be a boolean.')
        if project.get('featured'):
            for field in ('summary', 'problem', 'approach', 'result'):
                if not isinstance(project.get(field), str) or not project[field].strip():
                    raise ValueError(f'{slug}: featured projects require {field}.')
    return data


def load_portfolio_data() -> dict:
    return validate_data(json.loads(PORTFOLIO_DATA_PATH.read_text(encoding='utf-8')))


def load_projects() -> list[dict]:
    return load_portfolio_data()['projects']


def collect_tags(projects: list[dict]) -> list[str]:
    return list(dict.fromkeys(tag for project in projects for tag in project['tags']))


def load_tag_order(projects: list[dict] | None = None) -> list[str]:
    return load_portfolio_data()['tag_order']


def template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding='utf-8')


def fill(source: str, values: dict[str, str]) -> str:
    def replace(match):
        key = match.group(1)
        if key not in values:
            raise ValueError(f'Unresolved template marker: {key}')
        return values[key]
    return re.sub(r'\{\{([A-Z_]+)\}\}', replace, source)


def render_page(content: str, title: str, description: str, path: str, scripts: str = '') -> str:
    header = template('header.html')
    active_path = '/portfolio/' if path.startswith('/projects/') else path
    header = header.replace(f'href="{active_path}" class="nav-link"', f'href="{active_path}" class="nav-link nav-link--active" aria-current="page"')
    html = fill(template('base.html'), {
        'TITLE': escape(title), 'DESCRIPTION': escape(description),
        'CANONICAL': escape('https://acaietti.com' + path),
        'HEADER': header, 'CONTENT': content, 'FOOTER': template('footer.html'), 'SCRIPTS': scripts,
    })
    return '\n'.join(line.rstrip() for line in html.splitlines()) + '\n'


def render_filters(tags: list[str]) -> str:
    buttons = ['<button type="button" class="portfolio-pill portfolio-pill--active" data-filter="" aria-pressed="true">All</button>']
    buttons += [f'<button type="button" class="portfolio-pill" data-filter="{escape(tag)}" aria-pressed="false">{escape(tag)}</button>' for tag in tags]
    return '<div class="portfolio-filters flex flex-wrap gap-2 sm:gap-3 mb-6 sm:mb-8" role="group" aria-label="Filter projects by tag" hidden>' + '\n'.join(buttons) + '</div>\n<p id="portfolio-status" class="sr-only" role="status" aria-live="polite" aria-atomic="true"></p>'


def project_links(project: dict) -> str:
    links = []
    for field, label in [('demo_url', 'Live site'), ('github_url', 'Source code')]:
        if project.get(field):
            links.append(f'<a href="{escape(project[field])}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center min-h-11 text-sm font-semibold text-brand-700 dark:text-brand-300 underline underline-offset-4" aria-label="{label}: {escape(project["title"])} (opens in new tab)">{label}<span class="sr-only"> (opens in new tab)</span></a>')
    return '<div class="flex flex-wrap gap-x-4 gap-y-1">' + '\n'.join(links) + '</div>'


def _render_project_tags(tags: list[str]) -> str:
    lines = ['                                    <div class="flex flex-wrap gap-1.5">']
    for tag in tags:
        safe_tag = escape(tag)
        lines.append(
            f'                                        <button type="button" class="portfolio-card-tag" data-filter="{safe_tag}" aria-label="Filter by {safe_tag}" disabled>{safe_tag}</button>'
        )
    lines.append("                                    </div>")
    return "\n".join(lines)

def _render_project_links(project: dict) -> str:
    title = escape(project["title"])
    github_url = project.get("github_url")
    demo_url = project.get("demo_url")
    lines = ['                                    <div class="flex items-center gap-1.5">']
    if github_url:
        lines.extend(
            [
                f'                                        <a href="{escape(github_url)}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-lg text-slate-500 dark:text-slate-300 hover:text-surface-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors flex-shrink-0" aria-label="View {title} on GitHub">',
                '                                            <i class="fab fa-github text-base sm:text-lg"></i>',
                "                                        </a>",
            ]
        )
    if demo_url:
        lines.extend(
            [
                f'                                        <a href="{escape(demo_url)}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-lg text-slate-500 dark:text-slate-300 hover:text-surface-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors flex-shrink-0" aria-label="Visit {title} live site">',
                '                                            <i class="fas fa-external-link-alt text-base sm:text-lg"></i>',
                "                                        </a>",
            ]
        )
    lines.append("                                    </div>")
    return "\n".join(lines)

def render_projects(projects: list[dict]) -> str:
    lines = ['                <ul id="portfolio-grid" class="portfolio-grid list-none p-0 m-0" role="list">']
    for index, project in enumerate(projects, start=1):
        title = escape(project["title"])
        description = escape(project["description"])
        image_url = escape(project["image_url"])
        tags = project.get("tags", [])
        data_tags = escape(json.dumps(tags))
        lines.extend(
            [

                f'                    <li class="portfolio-card" data-tags="{data_tags}">',
                '                        <article class="group flex flex-col rounded-xl sm:rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 overflow-hidden shadow-sm hover:shadow-lg hover:border-slate-300 dark:hover:border-slate-500 transition-all duration-300">',
                '                            <div class="aspect-video w-full overflow-hidden bg-slate-100 dark:bg-slate-800 flex-shrink-0">',
                f'                                <img src="{image_url}" alt="{title}" width="800" height="450" loading="lazy" decoding="async" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">',
                "                            </div>",
                '                            <div class="flex flex-col flex-1 min-h-0 p-4 sm:p-5">',
                f'                                <h2 class="text-lg sm:text-xl font-semibold text-surface-900 dark:text-slate-100 mb-1.5 sm:mb-2">{title}</h2>',
                f'                                <p id="description-{project["slug"]}" class="portfolio-card-description text-slate-600 dark:text-slate-300 text-sm sm:text-base">{description}</p>',
                '                                <div class="mt-auto pt-3 sm:pt-4 border-t border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between gap-2">',
                _render_project_tags(tags),
                _render_project_links(project),
                "                                </div>",
                "                            </div>",
                "                        </article>",
                "                    </li>",
                "",
            ]
        )
    lines.append("                </ul>")
    return "\n".join(lines)


def render_portfolio_page(template_text: str | None = None) -> str:
    data = load_portfolio_data()
    source = template('portfolio.html') if template_text is None else template_text
    if FILTERS_MARKER not in source or PROJECTS_MARKER not in source:
        raise ValueError('Portfolio template is missing required markers.')
    content = fill(source, {'PORTFOLIO_FILTERS': render_filters(data['tag_order']), 'PORTFOLIO_PROJECTS': render_projects(data['projects'])})
    return render_page(content, 'Portfolio — Andrew Caietti', 'Explore Andrew Caietti’s projects in applied AI, computer vision, analytics, and full-stack engineering.', '/portfolio/', '<script src="/static/projects/js/portfolio.js" defer></script>')


def write_portfolio_page() -> Path:
    PORTFOLIO_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PORTFOLIO_OUTPUT_PATH.write_text(render_portfolio_page(), encoding='utf-8', newline='\n')
    return PORTFOLIO_OUTPUT_PATH


def render_featured(projects: list[dict]) -> str:
    cards = []
    for project in projects:
        cards.append(f'''<article class="flex flex-col rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 overflow-hidden shadow-sm">
    <img src="{escape(project['image_url'])}" alt="{escape(project['title'])}" width="800" height="450" loading="lazy" decoding="async" class="aspect-video w-full object-cover">
    <div class="flex flex-col flex-1 p-5">
        <h3 class="text-lg font-semibold mb-2"><a href="/projects/{project['slug']}/" class="hover:text-brand-700 dark:hover:text-brand-300">{escape(project['title'])}</a></h3>
        <p class="text-slate-600 dark:text-slate-300 mb-4">{escape(project['summary'])}</p>
        <div class="mt-auto">{_render_project_links(project)}</div>
    </div>
</article>''')
    return '''<section id="featured-projects" class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
    <div class="flex items-center justify-between flex-wrap gap-4 mb-8">
        <h2 class="text-2xl font-bold tracking-tight">Featured Projects</h2>
        <a href="/portfolio/" class="font-semibold text-brand-700 dark:text-brand-300 underline underline-offset-4">View all projects</a>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">''' + '\n'.join(cards) + '</div>\n</section>'


def render_case_study(project: dict) -> str:
    sections = ''.join(f'<section class="mt-8"><h2 class="text-xl font-semibold mb-3">{label}</h2><p class="text-slate-600 dark:text-slate-300 leading-relaxed">{escape(project[field])}</p></section>' for field, label in [('problem', 'The problem'), ('approach', 'What I built'), ('result', 'The result')])
    content = f'''<main id="main-content" tabindex="-1" class="main-safe flex-1 w-full">
    <article class="mx-auto max-w-3xl px-4 sm:px-6 py-10 sm:py-14">
        <a href="/portfolio/" class="text-brand-700 dark:text-brand-300 underline underline-offset-4">Back to portfolio</a>
        <h1 class="text-3xl sm:text-4xl font-bold mt-6 mb-4">{escape(project['title'])}</h1>
        <p class="text-lg text-slate-600 dark:text-slate-300 mb-6">{escape(project['summary'])}</p>
        <img src="{escape(project['image_url'])}" alt="{escape(project['title'])}" width="800" height="450" class="w-full aspect-video object-cover rounded-2xl" fetchpriority="high">
        {sections}
        <div class="mt-8 pt-4 border-t border-slate-200 dark:border-slate-700">{project_links(project)}</div>
    </article>
</main>'''
    return render_page(content, project['title'] + ' — Andrew Caietti', project['summary'], '/projects/' + project['slug'] + '/')


def render_site() -> dict[str, str]:
    data = load_portfolio_data()
    featured = [project for project in data['projects'] if project.get('featured')]
    pages = {
        'index.html': render_page(fill(template('home.html'), {'FEATURED_PROJECTS': render_featured(featured)}), 'Andrew Caietti — Applied AI & Analytics', 'Andrew Caietti is an applied AI and analytics solutions engineer. Explore his projects, experience, and work turning complex problems into practical products.', '/'),
        'portfolio/index.html': render_portfolio_page(),
        'experience/index.html': render_page(template('experience.html'), 'Experience — Andrew Caietti', 'Andrew Caietti’s experience in solutions engineering, applied AI, analytics, research, and technical leadership. Download his résumé.', '/experience/'),
        'contact/index.html': render_page(template('contact.html'), 'Contact — Andrew Caietti', 'Get in touch with Andrew Caietti about applied AI, analytics, engineering, and collaboration.', '/contact/'),
    }
    for project in featured:
        pages['projects/' + project['slug'] + '/index.html'] = render_case_study(project)
    return pages
