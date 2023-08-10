
from django.db import models

class File(models.Model):
    id = models.AutoField(primary_key=True)
    INSTITUICAO = models.CharField(max_length=15)
    nome_longo = models.CharField(max_length=100)
    sigla = models.CharField(max_length=15)
    ano = models.CharField(max_length=15)
    UNIDADE = models.CharField(max_length=100)
    NIVEL = models.CharField(max_length=15)
    PAPEL = models.CharField(max_length=15)
    USUARIO_ID = models.CharField(max_length=15)
    def __str__(self):	##Esta linha fará com que as entradas de dados no nosso banco de dados sejam apresentadas pelo 'id'
        return self.id

class DACMOOD(models.Model):
    id = models.IntegerField(primary_key=True)
    ra = models.CharField(max_length=100)
    nome_curto = models.CharField(max_length=35)
    papel = models.CharField(max_length=35)
    instituicao = models.CharField(max_length=35)
    nivel = models.CharField(max_length=35)
    unidade = models.CharField(max_length=35)
    sigla_uni = models.CharField(max_length=35)
    def __str__(self):	##Esta linha fará com que as entradas de dados no nosso banco de dados sejam apresentadas pelo 'id'
        return self.id
        

class HOST(models.Model):
    nome_curto = models.CharField(max_length=35)
    instituicao = models.CharField(max_length=35)
    nivel = models.CharField(max_length=35)
    unidade = models.CharField(max_length=35)
    sigla_uni = models.CharField(max_length=35)
    hosp = models.CharField(max_length=35)
    
class SOCIO(models.Model):
    MATRICULA_RA = models.CharField(max_length=100)
    SEXO = models.CharField(max_length = 10)
    COR_RACA = models.CharField(max_length = 100)
    ESC_FUNDAMENTAL1 = models.CharField(max_length = 100)
    ESC_FUNDAMENTAL2 = models.CharField(max_length = 100)
    ESC_MEDIO = models.CharField(max_length = 100)
    EST_CIVIL = models.CharField(max_length = 100)
    DATA_NASCIMENTO = models.CharField(max_length = 100)
    FILHOS = models.IntegerField()
    RENDA_MES_FAMILIA = models.IntegerField()
    CP = models.IntegerField()
    CPE = models.IntegerField()
    CR = models.IntegerField()
    CRP = models.IntegerField()