# Generated by Django 3.2 on 2023-06-11 08:26

from django.db import migrations, models
import pathlib


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to=pathlib.PureWindowsPath('D:/Мусорка/Практикум/foodgram-project-react/backend/backend/media'), verbose_name='Картинка'),
        ),
    ]
