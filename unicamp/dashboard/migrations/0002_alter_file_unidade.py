# Generated by Django 4.1.6 on 2023-02-07 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='UNIDADE',
            field=models.CharField(max_length=100),
        ),
    ]
