# Generated by Django 3.0.8 on 2020-08-23 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20200823_1015'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='watchlist',
        ),
        migrations.AddField(
            model_name='user',
            name='watchlist',
            field=models.CharField(default='', max_length=300),
        ),
    ]