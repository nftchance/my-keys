# Generated by Django 4.1 on 2022-09-05 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("repos", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="repofile",
            name="contents_hash",
        ),
        migrations.AddField(
            model_name="repo",
            name="default_branch",
            field=models.CharField(default="master", max_length=255),
            preserve_default=False,
        ),
    ]
