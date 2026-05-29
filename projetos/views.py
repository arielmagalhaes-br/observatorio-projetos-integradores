from django.shortcuts import render

def home(request):
    return render(request, 'projetos/home.html')

def novo_projeto(request):
    return render(request, 'projetos/novo_projeto.html')

def meus_projetos(request):
    return render(request, 'projetos/meus_projetos.html')