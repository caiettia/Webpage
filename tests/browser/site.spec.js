const { test, expect } = require('@playwright/test');

const pages = ['/', '/portfolio/', '/experience/', '/contact/', '/projects/dude-wheres-my-board/', '/projects/tideeye/', '/projects/world-cup-tracker/'];

for (const width of [390, 1440]) {
  test(`pages render without overflow or errors at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    for (const path of pages) {
      const response = await page.goto(path);
      expect(response.status()).toBe(200);
      await expect(page.locator('h1')).toHaveCount(1);
      await expect(page.locator('[aria-current="page"]')).toHaveCount(1);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      for (const image of await page.locator('img').all()) {
        await image.scrollIntoViewIfNeeded();
        await expect.poll(() => image.evaluate(element => element.complete && element.naturalWidth > 0)).toBe(true);
      }
    }
    expect(errors).toEqual([]);
  });
}

test('closed mobile menu is skipped; open menu manages focus and Escape', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto('/');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  await page.keyboard.press('Tab'); // Brand
  await page.keyboard.press('Tab');
  await expect(page.locator('#theme-toggle')).toBeFocused();
  const toggle = page.locator('#nav-toggle');
  await toggle.focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('#nav-menu a').first()).toBeFocused();
  await expect(toggle).toHaveAttribute('aria-expanded', 'true');
  await page.keyboard.press('Shift+Tab');
  await expect(toggle).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.locator('#nav-menu a').first()).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(toggle).toBeFocused();
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await toggle.click();
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'true');
  await expect(page.locator('html')).toHaveCSS('overflow', 'hidden');
  await page.setViewportSize({ width: 1440, height: 900 });
  // Resizing completes before the media-query change event necessarily runs.
  // An open mobile menu is already non-inert, so that alone cannot signal completion.
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(page.locator('#nav-menu')).not.toHaveAttribute('inert');
  await expect.poll(() => page.evaluate(() => document.documentElement.style.overflow)).toBe('');
  await page.setViewportSize({ width: 390, height: 900 });
  await expect(page.locator('#nav-menu')).toHaveAttribute('inert');
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
});

test('portfolio filters, deep links, empty state, and keyboard expansion', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto('/portfolio/?tag=Computer%20Vision');
  await expect(page.locator('.portfolio-card:visible')).toHaveCount(1);
  const card = page.locator('.portfolio-card:visible');
  await expect(card.locator('h2')).toHaveText('TideEye: Underwater Visibility');
  await expect(page.getByText('Read more', { exact: true })).toHaveCount(0);
  await expect(page.getByText('Read case study', { exact: true })).toHaveCount(0);
  const description = card.locator('.portfolio-card-description');
  await description.focus();
  await page.keyboard.press('Enter');
  await expect(description).toHaveAttribute('aria-expanded', 'true');
  await expect(card).toHaveClass(/portfolio-card--expanded/);
  await page.keyboard.press('Space');
  await expect(description).toHaveAttribute('aria-expanded', 'false');
  await card.locator('h2').click();
  await expect(card).toHaveClass(/portfolio-card--pinned/);
  await card.locator('h2').click();
  await expect(card).not.toHaveClass(/portfolio-card--expanded/);
  await page.locator('h1').hover();
  await card.locator('h2').hover();
  await expect(card).toHaveClass(/portfolio-card--expanded/, { timeout: 4500 });
  await page.locator('h1').hover();
  await expect(card).not.toHaveClass(/portfolio-card--expanded/);
  await expect(card.locator('a .fa-github')).toHaveCount(1);
  await expect(card.locator('a .fa-external-link-alt')).toHaveCount(1);
  await page.getByRole('button', { name: 'All', exact: true }).click();
  expect(await page.locator('.portfolio-card:visible').count()).toBeGreaterThan(1);
  await page.getByRole('button', { name: 'Filter by Supabase', exact: true }).click();
  await expect(page).toHaveURL(/tag=Supabase/);
  await expect(page.locator('.portfolio-card:visible')).toHaveCount(1);
  await expect(page.locator('.portfolio-pill[data-filter="Supabase"]')).toBeFocused();
  await page.reload();
  await expect(page.locator('.portfolio-card:visible')).toHaveCount(1);
  await page.goto('/portfolio/?tag=does-not-exist');
  await expect(page.locator('#portfolio-empty')).toBeVisible();
  await page.getByRole('button', { name: 'All', exact: true }).click();
  await expect(page.locator('#portfolio-empty')).toBeHidden();
});

test('theme persists across pages', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto('/');
  await page.getByRole('button', { name: 'Switch to dark mode' }).click();
  await page.goto('/experience/');
  await expect(page.locator('html')).toHaveClass(/dark/);
  await page.getByRole('button', { name: 'Switch to light mode' }).click();
  await page.reload();
  await expect(page.locator('html')).not.toHaveClass(/dark/);
});

test('featured cards stay reachable with reduced motion', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  const cards = page.locator('#featured-projects article');
  await expect(cards).toHaveCount(3);
  for (const card of await cards.all()) {
    await card.scrollIntoViewIfNeeded();
    await expect(card).toBeInViewport();
    expect(await card.evaluate(element => { const rect = element.getBoundingClientRect(); return rect.left >= 0 && rect.right <= innerWidth; })).toBe(true);
  }
});

test('pages and navigation work without JavaScript', async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 900 } });
  const page = await context.newPage();
  await page.goto('http://127.0.0.1:8000/portfolio/');
  await expect(page.locator('#nav-menu')).toBeVisible();
  const cards = page.locator('.portfolio-card');
  const rects = await cards.evaluateAll(elements => elements.map(element => element.getBoundingClientRect().toJSON()));
  for (let i = 1; i < rects.length; i++) expect(rects[i].top).toBeGreaterThanOrEqual(rects[i - 1].bottom);
  await expect(page.locator('.portfolio-filters')).toBeHidden();
  expect(await page.locator('.portfolio-card-description').first().evaluate(element => getComputedStyle(element).webkitLineClamp)).toBe('none');
  await page.locator('#nav-menu').getByRole('link', { name: 'Contact', exact: true }).click();
  await expect(page.locator('form')).toHaveAttribute('action', 'https://formspree.io/f/mleajrzq');
  await context.close();
});

test('resume is downloadable and contact validation prevents an empty submission', async ({ page, request }) => {
  await page.goto('/experience/');
  const resume = page.getByRole('link', { name: 'Download résumé (PDF)' });
  const response = await request.get(await resume.getAttribute('href'));
  expect(response.ok()).toBe(true);
  expect((await response.body()).subarray(0, 5).toString()).toBe('%PDF-');
  await page.goto('/contact/');
  expect(await page.locator('form').evaluate(form => form.checkValidity())).toBe(false);
  await expect(page.getByLabel('Your email')).toHaveAttribute('autocomplete', 'email');
});
