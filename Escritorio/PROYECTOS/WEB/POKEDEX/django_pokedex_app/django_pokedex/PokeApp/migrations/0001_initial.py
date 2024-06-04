# Generated by Django 5.0.5 on 2024-06-04 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pokemon_main',
            fields=[
                ('name', models.CharField(max_length=100)),
                ('unique_id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('possible_values', models.CharField(max_length=255)),
                ('image', models.URLField(blank=True)),
                ('best_stat', models.CharField(max_length=100)),
                ('best_stat_value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Pokemon_main_especies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('species', models.CharField(max_length=255)),
            ],
        ),
    ]
