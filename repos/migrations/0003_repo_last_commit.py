# Generated by Django 4.1 on 2022-09-05 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("repos", "0002_remove_repofile_contents_hash_repo_default_branch"),
    ]

    operations = [
        migrations.AddField(
            model_name="repo",
            name="last_commit",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
    ]
