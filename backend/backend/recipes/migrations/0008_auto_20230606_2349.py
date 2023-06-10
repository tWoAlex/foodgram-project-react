# Generated by Django 3.2 on 2023-06-06 18:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_rename_maesurement_unit_ingredient_measurement_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Длительность'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='text',
            field=models.TextField(default='', max_length=1024, verbose_name='Описание'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Название'),
        ),
    ]