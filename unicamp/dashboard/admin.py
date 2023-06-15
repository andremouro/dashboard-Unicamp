from django.contrib import admin

# Register your models here.

from .models import File
from .models import DACMOOD

admin.site.register(File)
admin.site.register(DACMOOD)
