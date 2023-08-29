# Generated by Django 4.2 on 2023-08-10 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_host_rename_hosp_dacmood_sigla_uni'),
    ]

    operations = [
        migrations.CreateModel(
            name='SOCIO',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('MATRICULA_RA', models.CharField(max_length=100)),
                ('SEXO', models.CharField(max_length=10)),
                ('COR_RACA', models.CharField(max_length=100)),
                ('ESC_FUNDAMENTAL1', models.CharField(max_length=100)),
                ('ESC_FUNDAMENTAL2', models.CharField(max_length=100)),
                ('ESC_MEDIO', models.CharField(max_length=100)),
                ('EST_CIVIL', models.CharField(max_length=100)),
                ('DATA_NASCIMENTO', models.CharField(max_length=100)),
                ('FILHOS', models.IntegerField()),
                ('RENDA_MES_FAMILIA', models.IntegerField()),
                ('CP', models.IntegerField()),
                ('CPE', models.IntegerField()),
                ('CR', models.IntegerField()),
                ('CRP', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='dacmood',
            name='ra',
            field=models.CharField(max_length=100),
        ),
    ]