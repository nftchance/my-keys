# Generated by Django 4.1 on 2022-09-05 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="RepoKey",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="RepoFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("commit", models.TextField()),
                ("file_name", models.TextField()),
                ("contents_hash", models.TextField()),
                ("keys", models.ManyToManyField(to="repos.repokey")),
            ],
        ),
        migrations.CreateModel(
            name="Repo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("full_name", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("files", models.ManyToManyField(to="repos.repofile")),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
    ]
