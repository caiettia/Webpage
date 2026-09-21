from django.test import SimpleTestCase
from django.urls import reverse

from .portfolio_generator import load_projects, load_tag_order, render_portfolio_page


class PortfolioGeneratorTests(SimpleTestCase):
    def test_project_data_and_tags_are_valid(self):
        projects = load_projects()
        self.assertTrue(projects)
        self.assertEqual(len(projects), len({project["slug"] for project in projects}))
        self.assertTrue(set(tag for project in projects for tag in project["tags"]).issubset(load_tag_order()))

    def test_rendered_html_contains_every_project(self):
        html = render_portfolio_page()
        self.assertNotIn("{{PORTFOLIO_", html)
        for project in load_projects():
            self.assertIn('id="description-' + project["slug"] + '"', html)


class PortfolioRedirectTests(SimpleTestCase):
    def test_portfolio_redirects_to_static_site(self):
        response = self.client.get(reverse("portfolio"))

        self.assertRedirects(
            response,
            "https://acaietti.com/portfolio/",
            fetch_redirect_response=False,
        )

    def test_projects_by_tag_redirects_to_static_site_filter(self):
        response = self.client.get(reverse("projects_by_tag", args=["Python"]))

        self.assertRedirects(
            response,
            "https://acaietti.com/portfolio/?tag=Python",
            fetch_redirect_response=False,
        )
