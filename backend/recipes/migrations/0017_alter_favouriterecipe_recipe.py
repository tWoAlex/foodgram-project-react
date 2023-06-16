# Generated by Django 3.2 on 2023-06-11 11:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_auto_20230611_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favouriterecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourited_by', to='recipes.recipe', verbose_name='Рецепт'),
        ),
    ]