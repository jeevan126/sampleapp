# Generated by Django 4.2 on 2023-04-05 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("student", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="file_content",
            field=models.FileField(null=True, upload_to=""),
        ),
    ]
