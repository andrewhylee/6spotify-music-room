# Generated by Django 4.0 on 2022-01-03 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0002_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='current_song',
            field=models.CharField(max_length=50, null=True),
        ),
    ]