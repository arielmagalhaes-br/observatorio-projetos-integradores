from django.contrib import admin
from django.urls import path
from projetos.views import home, novo_projeto, meus_projetos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    # É OBRIGATÓRIO ter o name='novo_projeto' e name='meus_projetos' no final
    path('novo-projeto/', novo_projeto, name='novo_projeto'),
    path('meus-projetos/', meus_projetos, name='meus_projetos'),
]