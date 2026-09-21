# Historical Django application

This directory preserves the original Python/Django, AWS, and Docker learning
project. It is not the application served at acaietti.com. The current site is
built from `src/` and `content/` into `docs/` by the root build commands.

The old templates, models, migrations, Docker setup, and dependencies are kept
for reference. They are not maintained as a production deployment. Review the
dependencies and environment configuration before running this application.
Debug mode defaults to off and must be explicitly enabled for local work.

The portfolio renderer has moved to `scripts/portfolio_generator.py` at the
repository root. A compatibility import here preserves historical imports;
current site tests run without Django. Existing portfolio routes redirect to the
static site and its tag-filter URLs.

If the historical dependencies are installed, its remaining checks can be run
from this directory with `SECRET_KEY` and `ALLOWED_HOSTS` set in the environment:

```sh
python -B manage.py test projects
```

No database, AWS credentials, Django installation, or Docker runtime is needed
for the root static-site build.
