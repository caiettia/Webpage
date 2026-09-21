"""Compatibility imports for the historical Django application.

The maintained static renderer lives in scripts/portfolio_generator.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.portfolio_generator import (  # noqa: F401
    REPO_ROOT, PORTFOLIO_DATA_PATH, PORTFOLIO_TEMPLATE_PATH, PORTFOLIO_OUTPUT_PATH,
    FILTERS_MARKER, PROJECTS_MARKER, load_portfolio_data, load_projects,
    collect_tags, load_tag_order, render_filters, render_projects,
    render_portfolio_page, write_portfolio_page,
)
