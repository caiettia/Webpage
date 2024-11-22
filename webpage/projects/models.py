from django.db import models

# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    github_url = models.URLField()
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title