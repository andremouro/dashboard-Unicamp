# Generated by Django 4.1.6 on 2023-02-07 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_alter_file_unidade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='nome_longo',
            field=models.CharField(max_length=100),
        ),
    ]
