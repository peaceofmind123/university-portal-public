# Generated by Django 2.0.1 on 2018-01-22 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datarepo', '0005_submission_submission_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentuser',
            name='courses',
        ),
    ]
