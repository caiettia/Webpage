from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    github_url = models.URLField()
    image_url = models.URLField(blank=True, null=True)
    tags = models.ManyToManyField('Tag', related_name = 'projects', blank=True)

    def __str__(self):
        return self.title