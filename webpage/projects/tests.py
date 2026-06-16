from django.test import SimpleTestCase
from django.urls import reverse

from .portfolio_generator import load_projects, load_tag_order, render_portfolio_page


class PortfolioGeneratorTests(SimpleTestCase):
    def test_project_data_preserves_current_order(self):
        self.assertEqual(
            [project["title"] for project in load_projects()],
            [
                "Dude, Where's My Board?",
                "TideEye: Underwater Visibility",
                "My Personal Site",
                "WMATA DC Metro Analysis",
                "Hype Words: Social Media Mining and Classification",
                "Visualizing Bird Migrations",
                "NOAA: Waves and Buoys Scraping",
                "Regularization Techniques",
                "Comparing Regressors",
                "Music Frequency Analysis",
                "El Nino/La Nina Time Series Analysis",
            ],
        )

    def test_tag_order_preserves_current_filter_order(self):
        self.assertEqual(
            load_tag_order(),
            [
                "Python",
                "Machine Learning",
                "Kepler.gl",
                "AWS",
                "Javascript",
                "Transformers",
                "SKLearn",
                "R",
                "node",
                "Docker",
                "Computer Vision",
                "Supabase",
            ],
        )

    def test_rendered_html_contains_expected_links_and_order(self):
        html = render_portfolio_page()

        self.assertNotIn("{{PORTFOLIO_FILTERS}}", html)
        self.assertNotIn("{{PORTFOLIO_PROJECTS}}", html)
        self.assertIn('href="https://github.com/caiettia/surfshop"', html)
        self.assertIn('href="https://www.dudewheresmyboard.com/"', html)
        self.assertIn('href="https://vis.acaietti.com"', html)

        first_project_index = html.index("Dude, Where's My Board?")
        second_project_index = html.index("TideEye: Underwater Visibility")
        last_project_index = html.index("El Nino/La Nina Time Series Analysis")

        self.assertLess(first_project_index, second_project_index)
        self.assertLess(second_project_index, last_project_index)


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
