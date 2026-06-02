from django.test import TestCase
from django.urls import reverse

from .models import Project


class PortfolioOrderingTests(TestCase):
    def test_portfolio_uses_requested_project_order(self):
        ordered_titles = [
            "Dude, Where's My Board?",
            'TideEye: Underwater Visibility',
            'My Personal Site',
            'WMATA DC Metro Analysis',
            'Hype Words: Social Media Mining and Classification',
            'Visualizing Bird Migrations',
            'NOAA: Waves and Buoys Scraping',
            'Regularization Techniques',
            'Comparing Regressors',
            'Music Frequency Analysis',
            'El Nino/La Nina Time Series Analysis',
        ]

        for title in reversed(ordered_titles):
            Project.objects.create(
                title=title,
                description='Test description',
                github_url=f'https://example.com/{title.replace(" ", "-")}',
            )

        response = self.client.get(reverse('portfolio'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [project.title for project in response.context['projects']],
            ordered_titles,
        )
