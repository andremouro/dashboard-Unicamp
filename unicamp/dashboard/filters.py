import django_filters
from .models import DACMOOD, HOST, SOCIO

class DACMOODFilter(django_filters.FilterSet):
    unidade = django_filters.ChoiceFilter(choices = [])
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unidade'].extra['choices'] = [
            (ip, ip)
            for ip in DACMOOD.objects.values_list('unidade', flat=True).distinct()
        ]    
    class Meta:
        model = DACMOOD
        fields = ['unidade']
        

class HOSTFilter(django_filters.FilterSet):
    nivel = django_filters.ChoiceFilter(choices = [])
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['nivel'].extra['choices'] = [
            (ip, ip)
            for ip in HOST.objects.values_list('nivel', flat=True).distinct()
        ]    
    class Meta:
        model = HOST
        fields = ['nivel']    

class SOCIOFilter(django_filters.FilterSet):
    nivel = django_filters.ChoiceFilter(choices = [])
    papel = django_filters.ChoiceFilter(choices = [])
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['nivel'].extra['choices'] = [
            ['ENSINO MÉDIO','ENSINO MÉDIO'],['GRADUAÇÃO','GRADUAÇÃO'],['PÓS GRADUAÇÃO','PÓS GRADUAÇÃO']
        ]    
        self.filters['papel'].extra['choices'] = [
            ['Discente','Discente'],['Docente','Docente'],['Formador','Formador'] 
        ]
    class Meta:
        model = SOCIO
        fields = ['nivel', 'papel']      