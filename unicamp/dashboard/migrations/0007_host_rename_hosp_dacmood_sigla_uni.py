# Generated by Django 4.2 on 2023-06-22 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_dacmood'),
    ]

    operations = [
        migrations.CreateModel(
            name='HOST',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_curto', models.CharField(max_length=35)),
                ('instituicao', models.CharField(max_length=35)),
                ('nivel', models.CharField(max_length=35)),
                ('unidade', models.CharField(max_length=35)),
                ('sigla_uni', models.CharField(max_length=35)),
                ('hosp', models.CharField(max_length=35)),
            ],
        ),
        migrations.RenameField(
            model_name='dacmood',
            old_name='hosp',
            new_name='sigla_uni',
        ),
    ]
