# Andrew Caietti's personal site

A static portfolio for applied AI, analytics, and engineering, published at
[acaietti.com](https://acaietti.com) through GitHub Pages. Python renders HTML from
shared templates and project data; Tailwind compiles a static stylesheet. There
is no application server or database in the production site.

## Get started

Requirements: Python 3.11+ and Node.js 22+. The normal build needs no Python packages.

```sh
npm ci
npm run build
npm run preview
```

Open http://127.0.0.1:8000. On Windows PowerShell, use `npm.cmd` / `npx.cmd` if
your execution policy blocks the npm PowerShell wrappers.

## Edit the site

| Location | Purpose |
| --- | --- |
| `content/portfolio/projects.json` | Project order, descriptions, tags, links, and featured case studies |
| `src/templates/` | Shared layout, header, footer, and page content |
| `src/styles.css` | Tailwind directives and custom styles |
| `tailwind.config.js` | Design tokens and utility-class source paths |
| `src/static/` | Maintained JavaScript, icons, and optimized images |
| `resumes/Resume_2026.pdf` | Source for the downloadable résumé |
| `scripts/` | Static renderer and optional image optimization |
| `docs/` | Generated publish output; rebuild instead of editing pages here |
| `webpage/` | Historical Django/Docker application; not deployed or needed to build |

After editing sources, run `npm run build` and commit the resulting `docs/`
changes alongside the sources. CI always rebuilds before publishing, so a
source-only change cannot silently leave the portfolio stale.

To add a project, provide a unique lowercase hyphenated `slug`, `title`,
`description`, local `image_url`, `tags`, and an HTTPS source or demo link.
Tags must appear in `tag_order`. Set `featured: true` and provide `summary`,
`problem`, `approach`, and `result` to include a homepage card and generate a
case-study page. Keep claims grounded in the actual project; don't add metrics
without evidence. All project and filter text is escaped during rendering.

The homepage, portfolio, and case studies share this data. Navigation, metadata,
theme behavior, and footer share one template or script. The contact form posts
to the existing Formspree endpoint; local tests do not send messages.

### Images

Project thumbnails are committed as 800 × 450 WebP files. All project images are
local, with lazy loading below the fold. The hero uses an optimized WebP and
social previews use a JPEG for compatibility. Normal builds never fetch images.

For an intentional refresh from each project's `image_source`:

```sh
python -m pip install -r scripts/requirements-images.txt
python scripts/optimize_images.py
npm run build
```

Remote sources are downloaded only by this optional refresh command. Local
originals currently live in `webpage/projects/static/projects/images/`.
Animated sources use a static preview frame. Review new thumbnails after refresh.

### Résumé and sharing metadata

Replace `resumes/Resume_2026.pdf` with the desired current résumé and rebuild;
the public link remains `/resume/Andrew-Caietti-Resume.pdf`. Page descriptions
live in the renderer; canonical and social tags live in the shared base template.
The build also generates `sitemap.xml` and `robots.txt`. `docs/CNAME` is retained.

## Verify changes

```sh
npm run build
npx playwright install chromium
npm test
```

The Python checks validate schema, safe text rendering, generated output, page
headings, metadata, local links, anchors, and image sizes. Browser checks cover
desktop and phone layouts, filters and deep links, keyboard navigation, hover/click and keyboard
description expansion, reduced motion, theme persistence, the résumé download,
and usable pages with JavaScript disabled. The contact check validates fields
without submitting the form.

To use an already installed Edge browser on Windows:

```powershell
$env:PLAYWRIGHT_CHANNEL = 'msedge'
npm.cmd test
```

## Deployment

Pull requests build and run the checks without publishing. Pushes to `main` and
manual workflow runs on `main` build, validate, and upload a Pages artifact; the
deploy job runs only after all checks pass. Browser traces are retained on
failure. Hosting remains GitHub Pages, with the existing custom domain/CDN setup.

The optional legacy Django checks are separate. See `webpage/README.md` before
running or modifying that historical application.
