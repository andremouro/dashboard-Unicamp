# Generated by Django 4.2 on 2023-09-18 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_socio_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='socio',
            name='MUNICIPIO',
            field=models.CharField(default='NA', max_length=35),
        ),
    ]
