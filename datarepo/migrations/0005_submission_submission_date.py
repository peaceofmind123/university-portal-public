# Generated by Django 2.0.1 on 2018-01-22 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datarepo', '0004_auto_20180122_0833'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='submission_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of Submission'),
        ),
    ]
