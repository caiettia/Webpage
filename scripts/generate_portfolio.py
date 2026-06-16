from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DJANGO_APP_ROOT = REPO_ROOT / "webpage"

if str(DJANGO_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(DJANGO_APP_ROOT))

from projects.portfolio_generator import write_portfolio_page


def main() -> int:
    output_path = write_portfolio_page()
    print(f"Generated {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
