# Generated by Django 3.2 on 2023-06-06 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_rename_ingredientrecipe_component'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='component',
            options={'verbose_name': 'Компонент', 'verbose_name_plural': 'Компоненты'},
        ),
    ]