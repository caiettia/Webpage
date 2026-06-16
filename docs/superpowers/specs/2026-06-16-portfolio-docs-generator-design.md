# Portfolio Docs Generator Design

**Goal**

Refactor the portfolio so project content lives in one structured data file, the `/docs` portfolio page is generated from that data without changing its current visual design, and the Django portfolio route stops acting as the authoritative runtime source.

**Scope**

- Move hardcoded portfolio project metadata out of [docs/portfolio/index.html](/E:/Website/docs/portfolio/index.html).
- Preserve the current card layout, tags, ordering, GitHub links, and demo links in the generated docs output.
- Add a small generator that renders the final static portfolio page from a template plus structured data.
- Retire Django as the live portfolio renderer by redirecting its `/portfolio/` route to the static site path instead of reading from the database.

**Non-Goals**

- Reworking the visual design of the portfolio cards or page chrome.
- Deleting the existing Django models or admin setup.
- Converting the other docs pages (`/`, `/experience/`, `/contact/`) to generated pages in this change.

**Approved Approach**

1. Store portfolio project metadata in a single JSON file under repo content.
2. Preserve the existing static page shell as a template file with placeholder markers for:
   - generated filter pills
   - generated project card markup
3. Add a Python generator script that:
   - reads the JSON data
   - derives the unique tag filter order from project tag appearance order
   - renders filter and project markup
   - injects the generated HTML into the template
   - writes the final `docs/portfolio/index.html`
4. Update Django’s portfolio route so it redirects to the static `/portfolio/` page, making Django clearly non-authoritative for this content.
5. Replace the old Django ordering test with generator-focused tests that validate:
   - project ordering
   - filter/tag rendering
   - GitHub link rendering
   - demo link rendering

**Data Shape**

Each project record should include:

- `title`
- `description`
- `image_url`
- `tags`
- `github_url`
- `demo_url` (optional)

Ordering will be represented by array order in the JSON file so the data file itself is the source of truth.

**Why This Design**

- Keeps the deployed docs page static and fast.
- Makes project content editable in one place.
- Minimizes risk by preserving the existing markup/CSS/JS contract.
- Avoids client-side rendering complexity for a page that already works well as static HTML.
- Leaves a clean future path if Django ever needs to consume the same JSON later.

**Files Expected To Change**

- Add a shared portfolio data file.
- Add a docs portfolio HTML template.
- Add a generator script and tests.
- Regenerate [docs/portfolio/index.html](/E:/Website/docs/portfolio/index.html).
- Update [webpage/projects/views.py](/E:/Website/webpage/projects/views.py) to redirect instead of querying models.
- Update [webpage/projects/tests.py](/E:/Website/webpage/projects/tests.py) to validate the new generator/redirect behavior.

**Risks And Mitigations**

- Risk: generated markup drifts from the current CSS/JS expectations.
  Mitigation: keep the existing HTML structure and classes intact, changing only the source of project/filter content.

- Risk: tag pill order changes unexpectedly.
  Mitigation: derive tag order from first appearance in the project list, matching the content source deterministically.

- Risk: Django links break for local use.
  Mitigation: keep the route alive with a redirect rather than removing it.
