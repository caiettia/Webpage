from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO_DATA_PATH = REPO_ROOT / "content" / "portfolio" / "projects.json"
PORTFOLIO_TEMPLATE_PATH = REPO_ROOT / "docs" / "portfolio" / "index.template.html"
PORTFOLIO_OUTPUT_PATH = REPO_ROOT / "docs" / "portfolio" / "index.html"
FILTERS_MARKER = "{{PORTFOLIO_FILTERS}}"
PROJECTS_MARKER = "{{PORTFOLIO_PROJECTS}}"


def load_portfolio_data() -> dict[str, Any]:
    data = json.loads(PORTFOLIO_DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Portfolio data must be an object.")
    if "projects" not in data or not isinstance(data["projects"], list):
        raise ValueError("Portfolio data must include a projects list.")
    if "tag_order" in data and not isinstance(data["tag_order"], list):
        raise ValueError("Portfolio tag_order must be a list when provided.")
    return data


def load_projects() -> list[dict[str, Any]]:
    return load_portfolio_data()["projects"]


def collect_tags(projects: list[dict[str, Any]]) -> list[str]:
    tags: list[str] = []
    seen: set[str] = set()
    for project in projects:
        for tag in project.get("tags", []):
            if tag not in seen:
                seen.add(tag)
                tags.append(tag)
    return tags


def load_tag_order(projects: list[dict[str, Any]] | None = None) -> list[str]:
    data = load_portfolio_data()
    if data.get("tag_order"):
        return data["tag_order"]
    if projects is None:
        projects = data["projects"]
    return collect_tags(projects)


def render_filters(tags: list[str]) -> str:
    lines = [
        '                <div class="portfolio-filters flex flex-wrap gap-2 sm:gap-3 mb-6 sm:mb-8" role="group" aria-label="Filter projects by tag">',
        '                    <button type="button" class="portfolio-pill portfolio-pill--active" data-filter="" aria-pressed="true">',
        "                        All",
        "                    </button>",
    ]
    for tag in tags:
        safe_tag = escape(tag)
        lines.extend(
            [
                f'                    <button type="button" class="portfolio-pill" data-filter="{safe_tag}" aria-pressed="false">',
                f"                        {safe_tag}",
                "                    </button>",
            ]
        )
    lines.append("                </div>")
    return "\n".join(lines)


def _escape_text(value: str) -> str:
    return escape(value, quote=False)


def _render_project_tags(tags: list[str]) -> str:
    lines = ['                                    <div class="flex flex-wrap gap-1.5">']
    for tag in tags:
        safe_tag = escape(tag)
        lines.append(
            f'                                        <button type="button" class="portfolio-card-tag" data-filter="{safe_tag}" aria-label="Filter by {safe_tag}">{safe_tag}</button>'
        )
    lines.append("                                    </div>")
    return "\n".join(lines)


def _render_project_links(project: dict[str, Any]) -> str:
    title = _escape_text(project["title"])
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


def render_projects(projects: list[dict[str, Any]]) -> str:
    lines = ['                <ul id="portfolio-grid" class="portfolio-grid list-none p-0 m-0" role="list">']
    for index, project in enumerate(projects, start=1):
        title = _escape_text(project["title"])
        description = _escape_text(project["description"])
        image_url = escape(project["image_url"])
        tags = project.get("tags", [])
        data_tags = escape(",".join(tags))
        lines.extend(
            [
                f"                    <!-- Project {index}: {title} -->",
                f'                    <li class="portfolio-card" data-tags="{data_tags}">',
                '                        <article class="group flex flex-col rounded-xl sm:rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 overflow-hidden shadow-sm hover:shadow-lg hover:border-slate-300 dark:hover:border-slate-500 transition-all duration-300">',
                '                            <div class="aspect-video w-full overflow-hidden bg-slate-100 dark:bg-slate-800 flex-shrink-0">',
                f'                                <img src="{image_url}" alt="{title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">',
                "                            </div>",
                '                            <div class="flex flex-col flex-1 min-h-0 p-4 sm:p-5">',
                f'                                <h2 class="text-lg sm:text-xl font-semibold text-surface-900 dark:text-slate-100 mb-1.5 sm:mb-2">{title}</h2>',
                f'                                <p class="portfolio-card-description text-slate-600 dark:text-slate-300 text-sm sm:text-base">{description}</p>',
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
    projects = load_projects()
    filters_html = render_filters(load_tag_order(projects))
    projects_html = render_projects(projects)
    template = (
        PORTFOLIO_TEMPLATE_PATH.read_text(encoding="utf-8")
        if template_text is None
        else template_text
    )
    if FILTERS_MARKER not in template or PROJECTS_MARKER not in template:
        raise ValueError("Portfolio template is missing required markers.")
    return (
        template.replace(FILTERS_MARKER, filters_html)
        .replace(PROJECTS_MARKER, projects_html)
    )


def write_portfolio_page() -> Path:
    output = render_portfolio_page()
    PORTFOLIO_OUTPUT_PATH.write_text(output, encoding="utf-8")
    return PORTFOLIO_OUTPUT_PATH
