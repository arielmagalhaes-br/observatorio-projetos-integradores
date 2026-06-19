from django.contrib import admin
from .models import Perfil, Tecnologia, ODS, Projeto, ImagemProjeto, Demanda, Turma

# Register your models here.

admin.site.register(Perfil)
admin.site.register(Tecnologia)
admin.site.register(ODS)
admin.site.register(Projeto)
admin.site.register(ImagemProjeto)
admin.site.register(Demanda)
admin.site.register(Turma)