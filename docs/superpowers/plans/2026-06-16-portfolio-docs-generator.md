# Portfolio Docs Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move portfolio content into a single structured data file, generate the docs portfolio page from it, and retire Django as the runtime content source for portfolio.

**Architecture:** Keep the current static portfolio page shell as an HTML template and generate only the filter pills and project cards from structured JSON data. Django’s `/portfolio/` route becomes a redirect so the docs page is the single live source.

**Tech Stack:** Python, static HTML, Django test framework

---

### Task 1: Add Structured Portfolio Content

**Files:**
- Create: `E:/Website/content/portfolio/projects.json`

- [ ] **Step 1: Add the ordered project dataset**

Create a JSON array whose item order matches the current portfolio order and includes title, description, image URL, tag list, GitHub URL, and optional demo URL for every portfolio card.

### Task 2: Template The Static Portfolio Page

**Files:**
- Create: `E:/Website/docs/portfolio/index.template.html`
- Modify: `E:/Website/docs/portfolio/index.html`

- [ ] **Step 1: Copy the current docs portfolio page into a reusable template**

Preserve the existing page shell, styles, and scripts while replacing the hardcoded filter and project card markup with placeholder markers for generated HTML.

- [ ] **Step 2: Regenerate the static page from the template**

Ensure the final generated `docs/portfolio/index.html` matches the current design while sourcing its content from data.

### Task 3: Add The Generator

**Files:**
- Create: `E:/Website/scripts/generate_portfolio.py`

- [ ] **Step 1: Implement a deterministic generator**

Read the JSON data, derive unique tags in first-seen order, generate HTML snippets for the filters and cards, inject them into the template, and write the output file.

- [ ] **Step 2: Add a simple command-line entry point**

Support running the script directly with Python from the repo root.

### Task 4: Retire Django As Portfolio Runtime

**Files:**
- Modify: `E:/Website/webpage/projects/views.py`

- [ ] **Step 1: Replace the database-backed portfolio view**

Make the Django `/portfolio/` route redirect to the static `/portfolio/` page instead of querying `Project` and `Tag`.

### Task 5: Add Regression Tests

**Files:**
- Modify: `E:/Website/webpage/projects/tests.py`

- [ ] **Step 1: Replace the old ordering test**

Add tests that validate:
- the generator preserves project ordering from JSON
- the generator renders the expected tag pills
- the generated HTML contains the expected GitHub and demo links
- Django `/portfolio/` returns the expected redirect response

- [ ] **Step 2: Run focused verification**

Run the Django test module for `projects.tests` and run the generator script to confirm the checked-in docs output is up to date.
