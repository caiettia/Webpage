from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_tag_project_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='demo_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
