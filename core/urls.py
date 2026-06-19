from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# 1. Certifique-se de que o 'sair' está sendo importado aqui:
from projetos.views import home, login_view, meus_projetos, novo_projeto, editar_projeto, perfil, vitrine, sair, editar_perfil, detalhe_projeto, gateway_view
from projetos.views import admin_dashboard, professor_dashboard, parceiro_dashboard, curadoria, analisar_projeto, parcerias, matchmaking_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', gateway_view, name='gateway'),
    path('home/', home, name='home'),
    path('login/', login_view, name='login'),
    # 2. Adicione esta linha exata para registrar o botão:
    path('sair/', sair, name='sair'), 
    
    path('meus-projetos/', meus_projetos, name='meus_projetos'),
    path('novo-projeto/', novo_projeto, name='novo_projeto'),
    path('perfil/', perfil, name='perfil'),
    path('vitrine/', vitrine, name='vitrine'),
    path('projeto/<int:id>/editar/', editar_projeto, name='editar_projeto'),
    path('projeto/<int:id>/', detalhe_projeto, name='detalhe_projeto'),
    path('curadoria/projeto/<int:id>/', analisar_projeto, name='analisar_projeto'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('professor-dashboard/', professor_dashboard, name='professor_dashboard'),
    path('curadoria/', curadoria, name='curadoria'),
    path('parcerias/', parcerias, name='parcerias'),
    path('parceiro-dashboard/', parceiro_dashboard, name='parceiro_dashboard'),
    path('matchmaking/', matchmaking_view, name='matchmaking'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
