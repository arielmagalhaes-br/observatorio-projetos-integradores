from django.shortcuts import render, redirect, get_object_or_404
# Importações de segurança e login do Django
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.utils import timezone


from .models import Projeto, Perfil, Tecnologia, ODS, ImagemProjeto, Demanda, Turma
from .decorators import role_required
from .auth_utils import is_admin_user, is_professor_or_admin, redirect_name_for_user


def _authenticate_by_username_or_email(request, identifier, password):
    identifier = (identifier or '').strip()
    user = authenticate(request, username=identifier, password=password)

    if user is None and identifier:
        matched_user = User.objects.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier)
        ).first()

        if matched_user:
            user = authenticate(request, username=matched_user.get_username(), password=password)

    return user

def login_view(request):
    if request.user.is_authenticated and request.method == 'GET':
        return redirect(redirect_name_for_user(request.user))

    if request.method == 'POST':
        usuario_digitado = request.POST.get('username')
        senha_digitada = request.POST.get('password')
        user = _authenticate_by_username_or_email(request, usuario_digitado, senha_digitada)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Bem-vindo de volta, {user.username}!')
            return redirect(redirect_name_for_user(user))
        else:
            messages.error(request, 'Usuário ou senha incorretos. Tente novamente.')
            return redirect('login')
    return render(request, 'projetos/login.html')


def gateway_view(request):
    if request.user.is_authenticated:
        return redirect(redirect_name_for_user(request.user))
    return render(request, 'projetos/gateway.html')


@login_required(login_url='/login/')
def home(request):
    contexto = {
        'total_projetos': 0,
        'projetos_aprovados': 0,
        'projetos_pendentes': 0,
        'projetos_recentes': [],
        'projeto_em_ajuste': None,
    }

    if hasattr(request.user, 'perfil'):
        meus_projetos = request.user.perfil.projetos.all().order_by('-data_atualizacao')

        contexto['total_projetos'] = meus_projetos.count()
        contexto['projetos_aprovados'] = meus_projetos.filter(status='APROVADO').count()
        contexto['projetos_pendentes'] = meus_projetos.filter(status__in=['AJUSTES', 'REVISAO']).count()
        
        q = request.GET.get('q')
        if q:
            meus_projetos = meus_projetos.filter(titulo__icontains=q)
            
        contexto['projetos_recentes'] = meus_projetos[:4]
        contexto['projetos'] = meus_projetos[:4]

        # Banner de UX: mostrar apenas se houver um projeto com status='AJUSTES'
        contexto['projeto_em_ajuste'] = meus_projetos.filter(status='AJUSTES').first()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'projetos/partials/lista_projetos_recentes.html', contexto)

    return render(request, 'projetos/home.html', contexto)



@login_required(login_url='/login/')
@role_required('ALUNO')
def meus_projetos(request):
    projetos = []
    total_projetos = 0
    total_aprovados = 0
    total_revisao = 0
    total_pendentes = 0
    
    if hasattr(request.user, 'perfil'):
        projetos = request.user.perfil.projetos.all().order_by('-data_criacao')
        total_projetos = projetos.count()
        total_aprovados = projetos.filter(status='APROVADO').count()
        total_revisao = projetos.filter(status='REVISAO').count()
        total_pendentes = projetos.filter(status__in=['RASCUNHO', 'AJUSTES']).count()

        q = request.GET.get('q')
        filtro_status = request.GET.get('status')
        ods = request.GET.get('ods')
        linguagem = request.GET.get('linguagem')
        banco = request.GET.get('banco')

        # filtro por título
        if q:
            projetos = projetos.filter(titulo__icontains=q)

        # filtro por status (rápido a partir dos cards)
        if filtro_status == 'PENDENTES':
            projetos = projetos.filter(status__in=['RASCUNHO', 'AJUSTES'])
        elif filtro_status:
            projetos = projetos.filter(status=filtro_status)

        # filtros ManyToMany por tecnologias/ODS
        if ods:
            projetos = projetos.filter(tecnologias__nome__iexact=ods)
        if linguagem:
            projetos = projetos.filter(tecnologias__nome__iexact=linguagem)
        if banco:
            projetos = projetos.filter(tecnologias__nome__iexact=banco)

        # evitar duplicados quando aplicar filtros M2M
        if ods or linguagem or banco:
            projetos = projetos.distinct()

        page_number = request.GET.get('page')
        paginator = Paginator(projetos, 5)
        projetos = paginator.get_page(page_number)
    
    contexto = {
        'projetos': projetos,
        'total_projetos': total_projetos,
        'total_aprovados': total_aprovados,
        'total_revisao': total_revisao,
        'total_pendentes': total_pendentes
    }
    return render(request, 'projetos/meus_projetos.html', contexto)


@login_required(login_url='/login/')
@role_required('ALUNO')
def novo_projeto(request):
    contexto = {
        'form_data': {},
        'form_lists': {},
    }

    if request.method == 'POST':
        from django.db import transaction

        # =============================
        # Validação de uploads (antes do atomic)
        # =============================
        logo_max_bytes = 2 * 1024 * 1024      # 2MB
        prints_max_bytes = 5 * 1024 * 1024    # 5MB
        allowed_mime_prefix = ("image/png", "image/jpeg", "image/webp")

        arquivos_logo = request.FILES.getlist('logo') if 'logo' in request.FILES else []
        arquivos_prints = request.FILES.getlist('prints') if 'prints' in request.FILES else []
        acao = request.POST.get('acao')
        status_final = 'RASCUNHO' if acao == 'rascunho' else 'REVISAO'

        titulo = request.POST.get('titulo', '').strip()
        semestre = request.POST.get('semestre', '').strip()
        resumo = request.POST.get('resumo', '').strip()
        inspiracao = request.POST.get('inspiracao', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        proximos_passos = request.POST.get('proximos_passos', '').strip()
        link_repositorio = request.POST.get('link_repositorio', '').strip()
        link_prototipo = request.POST.get('link_prototipo', '').strip()
        link_demo = request.POST.get('link_demo', '').strip()
        link_video = request.POST.get('link_video', '').strip()
        linguagens = request.POST.getlist('linguagens')
        bancos = request.POST.getlist('banco_dados')
        ods_list = request.POST.getlist('ods')

        contexto = {
            'form_data': request.POST,
            'form_lists': {
                'linguagens': linguagens,
                'banco_dados': bancos,
                'ods': ods_list,
            },
        }

        # Valida logo (se enviado)
        for f in arquivos_logo:
            if f.size > logo_max_bytes:
                messages.error(request, 'A logo excede o tamanho máximo (2MB).')
                return render(request, 'projetos/novo_projeto.html', contexto)
            if getattr(f, 'content_type', '') not in allowed_mime_prefix:
                messages.error(request, 'Formato de logo inválido. Envie apenas PNG, JPG ou WEBP.')
                return render(request, 'projetos/novo_projeto.html', contexto)

        # Valida prints (se enviados)
        for f in arquivos_prints:
            if f.size > prints_max_bytes:
                messages.error(request, 'Um dos prints excede o tamanho máximo (5MB).')
                return render(request, 'projetos/novo_projeto.html', contexto)
            if getattr(f, 'content_type', '') not in allowed_mime_prefix:
                messages.error(request, 'Formato de print inválido. Envie apenas PNG, JPG ou WEBP.')
                return render(request, 'projetos/novo_projeto.html', contexto)

        if status_final == 'REVISAO':
            campos_obrigatorios = [
                (titulo, 'Título do projeto'),
                (semestre, 'Semestre'),
                (resumo, 'Resumo'),
                (inspiracao, 'Inspiração'),
                (descricao, 'O que ele faz'),
            ]
            pendencias = [label for value, label in campos_obrigatorios if not value]

            if not linguagens and not bancos:
                pendencias.append('Tecnologias usadas')

            ods_validos = []
            for ods in ods_list:
                if str(ods).isdigit() and ODS.objects.filter(numero=int(ods)).exists():
                    ods_validos.append(ods)
            if not ods_validos:
                pendencias.append('ODS')

            if not any([link_repositorio, link_prototipo, link_demo]):
                pendencias.append('Pelo menos um link útil')

            if not arquivos_logo and not arquivos_prints:
                pendencias.append('Pelo menos uma logo ou print da tela')

            if pendencias:
                messages.error(
                    request,
                    'Para enviar para curadoria, preencha: ' + ', '.join(pendencias) + '.'
                )
                return render(request, 'projetos/novo_projeto.html', contexto)

        with transaction.atomic():
            turma_aluno = request.user.perfil.turma if hasattr(request.user, 'perfil') else None

            novo_proj = Projeto.objects.create(
                titulo=titulo,
                semestre=semestre,
                resumo=resumo,
                inspiracao=inspiracao,
                descricao=descricao,
                Link_repositorio=link_repositorio,
                Link_prototipo=link_prototipo,
                link_demo=link_demo,
                status=status_final,
                turma=turma_aluno
            )

            if hasattr(request.user, 'perfil'):
                novo_proj.autores.add(request.user.perfil)
            else:
                perfil = Perfil.objects.create(usuario=request.user)
                novo_proj.autores.add(perfil)

            autores_txt = request.POST.get('autores', '')
            if autores_txt:
                emails = [e.strip() for e in autores_txt.split(',') if e.strip()]
                for em in emails:
                    u = User.objects.filter(email__iexact=em).first() or User.objects.filter(username__iexact=em).first()
                    if u and hasattr(u, 'perfil'):
                        novo_proj.autores.add(u.perfil)

            tecnologias_ids = linguagens + bancos
            tecnologias_selecionadas = []
            linguagens_selecionadas = set(linguagens)
            banco_selecionados = set(bancos)

            for nome in tecnologias_ids:
                if not nome:
                    continue

                if nome in linguagens_selecionadas:
                    categoria = 'LING'
                elif nome in banco_selecionados:
                    categoria = 'BD'
                else:
                    categoria = 'LING'

                tech_obj, _ = Tecnologia.objects.get_or_create(nome=nome, defaults={'categoria': categoria})
                # Se a tecnologia já existe, mas categoria estiver vazia (ou divergente), não tentamos sobrescrever.
                tecnologias_selecionadas.append(tech_obj)

            if tecnologias_selecionadas:
                novo_proj.tecnologias.add(*tecnologias_selecionadas)

            for o in ods_list:
                if str(o).isdigit():
                    try:
                        ods_obj = ODS.objects.filter(numero=int(o)).first()
                    except (TypeError, ValueError):
                        ods_obj = None
                else:
                    ods_obj = ODS.objects.filter(nome__iexact=o).first()

                # Se não existir no banco, apenas ignora (sem quebrar o atomic)
                if ods_obj:
                    novo_proj.ods.add(ods_obj)


            # Salva apenas imagens válidas das chaves esperadas no formulário
            for key in ['logo', 'prints']:
                if key in request.FILES:
                    files = request.FILES.getlist(key)
                    for f in files:
                        if getattr(f, 'content_type', '').startswith('image/'):
                            ImagemProjeto.objects.create(projeto=novo_proj, imagem=f)

            if status_final == 'RASCUNHO':
                messages.info(request, 'Seu projeto foi salvo como rascunho.')
            else:
                messages.success(request, 'Projeto enviado para curadoria com sucesso!')
            return redirect('meus_projetos')
    return render(request, 'projetos/novo_projeto.html', contexto)


def _contexto_edicao_projeto(projeto):
    bancos = {'mysql', 'mongodb', 'firebase', 'sqlite', 'postgresql'}
    linguagens = []
    banco_dados = []

    for tecnologia in projeto.tecnologias.all():
        nome = tecnologia.nome
        if tecnologia.categoria == 'BD' or nome.lower() in bancos:
            banco_dados.append(nome)
        else:
            linguagens.append(nome)

    return {
        'projeto_editando': projeto,
        'form_data': {
            'titulo': projeto.titulo,
            'semestre': projeto.semestre,
            'resumo': projeto.resumo,
            'inspiracao': projeto.inspiracao,
            'descricao': projeto.descricao,
            'link_repositorio': projeto.Link_repositorio,
            'link_prototipo': projeto.Link_prototipo,
            'link_demo': projeto.link_demo,
        },
        'form_lists': {
            'linguagens': linguagens,
            'banco_dados': banco_dados,
            'ods': [str(ods.numero) for ods in projeto.ods.all()],
        },
    }


@login_required(login_url='/login/')
@role_required('ALUNO')
def editar_projeto(request, id):
    projeto = get_object_or_404(
        Projeto.objects.prefetch_related('autores', 'tecnologias', 'ods', 'imagens'),
        id=id,
    )

    perfil = getattr(request.user, 'perfil', None)
    if perfil is None or not projeto.autores.filter(pk=perfil.pk).exists():
        messages.error(request, 'Você não tem permissão para editar este projeto.')
        return redirect('meus_projetos')

    if projeto.status not in ['RASCUNHO', 'AJUSTES']:
        messages.error(request, 'Somente projetos em rascunho ou ajustes podem ser editados.')
        return redirect('detalhe_projeto', id=projeto.id)

    contexto = _contexto_edicao_projeto(projeto)

    if request.method == 'POST':
        from django.db import transaction

        logo_max_bytes = 2 * 1024 * 1024
        prints_max_bytes = 5 * 1024 * 1024
        allowed_mime_prefix = ("image/png", "image/jpeg", "image/webp")

        arquivos_logo = request.FILES.getlist('logo') if 'logo' in request.FILES else []
        arquivos_prints = request.FILES.getlist('prints') if 'prints' in request.FILES else []
        acao = request.POST.get('acao')
        status_final = 'RASCUNHO' if acao == 'rascunho' else 'REVISAO'

        titulo = request.POST.get('titulo', '').strip()
        semestre = request.POST.get('semestre', '').strip()
        resumo = request.POST.get('resumo', '').strip()
        inspiracao = request.POST.get('inspiracao', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        link_repositorio = request.POST.get('link_repositorio', '').strip()
        link_prototipo = request.POST.get('link_prototipo', '').strip()
        link_demo = request.POST.get('link_demo', '').strip()
        linguagens = request.POST.getlist('linguagens')
        bancos = request.POST.getlist('banco_dados')
        ods_list = request.POST.getlist('ods')

        contexto = {
            'projeto_editando': projeto,
            'form_data': request.POST,
            'form_lists': {
                'linguagens': linguagens,
                'banco_dados': bancos,
                'ods': ods_list,
            },
        }

        for f in arquivos_logo:
            if f.size > logo_max_bytes:
                messages.error(request, 'A logo excede o tamanho máximo (2MB).')
                return render(request, 'projetos/novo_projeto.html', contexto)
            if getattr(f, 'content_type', '') not in allowed_mime_prefix:
                messages.error(request, 'Formato de logo inválido. Envie apenas PNG, JPG ou WEBP.')
                return render(request, 'projetos/novo_projeto.html', contexto)

        for f in arquivos_prints:
            if f.size > prints_max_bytes:
                messages.error(request, 'Um dos prints excede o tamanho máximo (5MB).')
                return render(request, 'projetos/novo_projeto.html', contexto)
            if getattr(f, 'content_type', '') not in allowed_mime_prefix:
                messages.error(request, 'Formato de print inválido. Envie apenas PNG, JPG ou WEBP.')
                return render(request, 'projetos/novo_projeto.html', contexto)

        if status_final == 'REVISAO':
            pendencias = [
                label for value, label in [
                    (titulo, 'Título do projeto'),
                    (semestre, 'Semestre'),
                    (resumo, 'Resumo'),
                    (inspiracao, 'Inspiração'),
                    (descricao, 'O que ele faz'),
                ] if not value
            ]

            if not linguagens and not bancos:
                pendencias.append('Tecnologias usadas')

            ods_validos = [
                ods for ods in ods_list
                if str(ods).isdigit() and ODS.objects.filter(numero=int(ods)).exists()
            ]
            if not ods_validos:
                pendencias.append('ODS')

            if not any([link_repositorio, link_prototipo, link_demo]):
                pendencias.append('Pelo menos um link útil')

            if not arquivos_logo and not arquivos_prints and not projeto.imagens.exists():
                pendencias.append('Pelo menos uma logo ou print da tela')

            if pendencias:
                messages.error(
                    request,
                    'Para enviar para curadoria, preencha: ' + ', '.join(pendencias) + '.'
                )
                return render(request, 'projetos/novo_projeto.html', contexto)

        with transaction.atomic():
            projeto.titulo = titulo
            projeto.semestre = semestre
            projeto.resumo = resumo
            projeto.inspiracao = inspiracao
            projeto.descricao = descricao
            projeto.Link_repositorio = link_repositorio
            projeto.Link_prototipo = link_prototipo
            projeto.link_demo = link_demo
            projeto.status = status_final
            projeto.feedback_professor = '' if status_final == 'REVISAO' else projeto.feedback_professor
            projeto.save()

            projeto.tecnologias.clear()
            tecnologias_ids = linguagens + bancos
            linguagens_selecionadas = set(linguagens)
            banco_selecionados = set(bancos)
            tecnologias_selecionadas = []

            for nome in tecnologias_ids:
                if not nome:
                    continue

                categoria = 'BD' if nome in banco_selecionados else 'LING'
                if nome in linguagens_selecionadas:
                    categoria = 'LING'

                tech_obj, _ = Tecnologia.objects.get_or_create(nome=nome, defaults={'categoria': categoria})
                tecnologias_selecionadas.append(tech_obj)

            if tecnologias_selecionadas:
                projeto.tecnologias.add(*tecnologias_selecionadas)

            projeto.ods.clear()
            for o in ods_list:
                if str(o).isdigit():
                    ods_obj = ODS.objects.filter(numero=int(o)).first()
                else:
                    ods_obj = ODS.objects.filter(nome__iexact=o).first()

                if ods_obj:
                    projeto.ods.add(ods_obj)

            for key in ['logo', 'prints']:
                if key in request.FILES:
                    for f in request.FILES.getlist(key):
                        if getattr(f, 'content_type', '').startswith('image/'):
                            ImagemProjeto.objects.create(projeto=projeto, imagem=f)

            if status_final == 'RASCUNHO':
                messages.info(request, 'Rascunho atualizado com sucesso.')
            else:
                messages.success(request, 'Projeto reenviado para curadoria com sucesso!')

            return redirect('meus_projetos')

    return render(request, 'projetos/novo_projeto.html', contexto)



@login_required(login_url='/login/')
def perfil(request):
    contexto = {'total_projetos': 0, 'projetos_aprovados': 0, 'projetos_pendentes': 0, 'projetos_em_revisao': 0}
    if hasattr(request.user, 'perfil'):
        meus_projetos = request.user.perfil.projetos.all()
        contexto['total_projetos'] = meus_projetos.count()
        contexto['projetos_aprovados'] = meus_projetos.filter(status='APROVADO').count()
        contexto['projetos_pendentes'] = meus_projetos.filter(status='AJUSTES').count()
        contexto['projetos_em_revisao'] = meus_projetos.filter(status='REVISAO').count()
    return render(request, 'projetos/perfil.html', contexto)


def vitrine(request):
    projetos = Projeto.objects.filter(status='APROVADO').order_by('-data_criacao')

    termo_pesquisa = request.GET.get('q')
    tech = request.GET.get('tech')  # tecnologia (nome curto)
    linguagem = request.GET.get('linguagem')
    banco = request.GET.get('banco')
    filtro_ods = request.GET.get('ods')  # ODS (numero)

    if termo_pesquisa:
        projetos = projetos.filter(
            Q(titulo__icontains=termo_pesquisa) |
            Q(resumo__icontains=termo_pesquisa) |
            Q(descricao__icontains=termo_pesquisa)
        )

    if tech:
        projetos = projetos.filter(tecnologias__nome__iexact=tech)

    if linguagem:
        projetos = projetos.filter(tecnologias__nome__iexact=linguagem)

    if banco:
        projetos = projetos.filter(tecnologias__nome__iexact=banco)

    if filtro_ods:
        try:
            if str(filtro_ods).isdigit():
                projetos = projetos.filter(ods__numero=int(filtro_ods))
            else:
                projetos = projetos.filter(ods__nome__icontains=filtro_ods)
        except Exception:
            pass

    if tech or linguagem or banco or filtro_ods:
        projetos = projetos.distinct()

    contexto = {
        'projetos': projetos,
        'termo_pesquisa': termo_pesquisa,
        'tech': tech,
        'linguagem': linguagem,
        'banco': banco,
        'filtro_ods': filtro_ods,
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'projetos/partials/grid_projetos.html', contexto)
        
    return render(request, 'projetos/vitrine.html', contexto)



def sair(request):
    logout(request)
    messages.info(request, 'Você saiu do sistema com segurança.')
    return redirect('gateway')


def detalhe_projeto(request, id):
    projeto = get_object_or_404(Projeto, id=id)
    projeto.data_atualizacao = timezone.now()
    projeto.save(update_fields=['data_atualizacao'])

    pode_editar = False
    if request.user.is_authenticated and hasattr(request.user, 'perfil'):
        perfil = request.user.perfil
        if projeto.status in ['RASCUNHO', 'AJUSTES'] and projeto.autores.filter(pk=perfil.pk).exists():
            pode_editar = True
    contexto = {
        'projeto': projeto,
        'imagens': projeto.imagens.all(),
        'pode_editar': pode_editar
    }
    return render(request, 'projetos/detalhe_projeto.html', contexto)


@login_required(login_url='/login/')
def editar_perfil(request):
    perfil = getattr(request.user, 'perfil', None)
    if perfil is None:
        perfil = Perfil.objects.create(usuario=request.user)
    if request.method == 'POST':
        perfil.biografia = request.POST.get('biografia')
        perfil.LinkedIn = request.POST.get('LinkedIn')
        perfil.github = request.POST.get('github')
        if request.FILES.get('foto'):
            perfil.foto = request.FILES.get('foto')
        perfil.save()
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('perfil')
    return render(request, 'projetos/editar_perfil.html')


def _dashboard_metricas_context(request):
    turmas = Turma.objects.all().order_by('-semestre', 'nome')
    turma_id = request.GET.get('turma')
    turma_selecionada = None

    projetos_filtrados = Projeto.objects.all()
    if turma_id and turma_id.isdigit():
        turma_selecionada = Turma.objects.filter(id=int(turma_id)).first()
        if turma_selecionada:
            projetos_filtrados = projetos_filtrados.filter(turma=turma_selecionada)

    ano = timezone.now().year
    semestre_letivo = f"{ano}.1" if timezone.now().month <= 6 else f"{ano}.2"

    demandas_abertas = Demanda.objects.filter(status='NOVA').count()
    demandas_semestre = Demanda.objects.filter(status='NOVA', data_criacao__year=ano).count()
    projetos_publicados = projetos_filtrados.filter(status='APROVADO').count()
    projetos_publicados_semestre = projetos_filtrados.filter(status='APROVADO', semestre=semestre_letivo).count()
    projetos_pendentes = projetos_filtrados.filter(status='AJUSTES').count()
    projetos_em_analise = projetos_filtrados.filter(status='REVISAO').count()

    ods_ranking = ODS.objects.filter(projeto__in=projetos_filtrados).annotate(
        total_projects=Count('projeto')
    ).order_by('-total_projects')[:5]

    ods_chart_items = []
    if ods_ranking.exists():
        for ods in ods_ranking:
            valor = ods.total_projects
            ods_chart_items.append({
                'label': f"ODS {ods.numero} - {ods.nome}",
                'value': valor,
                'percent': min(int((valor / 6) * 100), 100),
                'highlight': ods.numero == 4,
            })
    elif not turma_selecionada:
        ods_chart_items = [
            {'label': 'ODS 16 - Paz, Justiça e Instituições Eficazes', 'value': 3, 'percent': 50, 'highlight': False},
            {'label': "ODS 14 - Vida Debaixo D'Água", 'value': 1, 'percent': 17, 'highlight': False},
            {'label': 'ODS 4 - Educação de Qualidade', 'value': 4, 'percent': 67, 'highlight': True},
            {'label': 'ODS 8 - Emprego Digno e Cresc. Econ.', 'value': 3, 'percent': 50, 'highlight': False},
            {'label': 'ODS 9 - Indústria, Inov. e Infraestrutura', 'value': 3, 'percent': 50, 'highlight': False},
        ]

    return {
        'demandas_abertas': demandas_abertas,
        'demandas_semestre': demandas_semestre,
        'projetos_publicados': projetos_publicados,
        'projetos_publicados_semestre': projetos_publicados_semestre,
        'projetos_pendentes': projetos_pendentes,
        'projetos_em_analise': projetos_em_analise,
        'ods_chart_items': ods_chart_items,
        'turmas': turmas,
        'turma_selecionada': turma_selecionada,
    }


@login_required(login_url='/login/')
def admin_dashboard(request):
    if not is_admin_user(request.user):
        messages.error(request, 'Acesso não autorizado')
        return redirect('home')

    return render(request, 'projetos/admin_dashboard.html', _dashboard_metricas_context(request))


@login_required(login_url='/login/')
def professor_dashboard(request):
    if not is_professor_or_admin(request.user):
        messages.error(request, 'Acesso não autorizado')
        return redirect('home')

    return render(request, 'projetos/professor_dashboard.html', _dashboard_metricas_context(request))




@login_required(login_url='/login/')
@role_required('PARCEIRO')
def parceiro_dashboard(request):
    contexto = {'minhas_demandas': request.user.perfil.demanda_set.all() if hasattr(request.user, 'perfil') else []}
    return render(request, 'projetos/parceiro_dashboard.html', contexto)

@login_required(login_url='/login/')
def curadoria(request):
    if not is_professor_or_admin(request.user):
        messages.error(request, 'Acesso não autorizado')
        return redirect('home')

    projetos = Projeto.objects.prefetch_related('tecnologias', 'ods', 'autores__usuario').filter(status='REVISAO')
    termo_pesquisa = request.GET.get('q', '').strip()
    filtro_curso = request.GET.get('curso', '').strip()
    filtro_semestre = request.GET.get('semestre', '').strip()

    if termo_pesquisa:
        projetos = projetos.filter(
            Q(titulo__icontains=termo_pesquisa) |
            Q(resumo__icontains=termo_pesquisa) |
            Q(descricao__icontains=termo_pesquisa) |
            Q(autores__usuario__first_name__icontains=termo_pesquisa) |
            Q(autores__usuario__last_name__icontains=termo_pesquisa) |
            Q(autores__usuario__username__icontains=termo_pesquisa) |
            Q(autores__curso__icontains=termo_pesquisa)
        ).distinct()

    if filtro_curso:
        projetos = projetos.filter(autores__curso__icontains=filtro_curso).distinct()

    if filtro_semestre:
        projetos = projetos.filter(semestre=filtro_semestre).distinct()

    contexto = {
        'projetos': projetos,
        'termo_pesquisa': termo_pesquisa,
        'filtro_curso': filtro_curso,
        'filtro_semestre': filtro_semestre,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'projetos/partials/curadoria_tabela.html', contexto)

    return render(request, 'projetos/curadoria.html', contexto)


@login_required(login_url='/login/')
def analisar_projeto(request, id):
    if not is_professor_or_admin(request.user):
        messages.error(request, 'Acesso não autorizado')
        return redirect('home')

    projeto = get_object_or_404(Projeto, id=id)

    if request.method == 'POST':
        acao = request.POST.get('acao')
        feedback = request.POST.get('feedback_professor', '').strip()

        if acao == 'ajustes' and not feedback:
            messages.error(request, 'Escreva um feedback antes de devolver o projeto para ajustes.')
        elif acao == 'aprovar':
            projeto.status = 'APROVADO'
            projeto.feedback_professor = feedback
            projeto.save()
            messages.success(request, 'Projeto aprovado com sucesso.')
            return redirect('curadoria')
        elif acao == 'ajustes':
            projeto.status = 'AJUSTES'
            projeto.feedback_professor = feedback
            projeto.save()
            messages.success(request, 'Projeto devolvido para ajustes.')
            return redirect('curadoria')

    contexto = {
        'projeto': projeto,
        'imagens': projeto.imagens.all(),
    }
    return render(request, 'projetos/analisar_projeto.html', contexto)


@login_required(login_url='/login/')
def parcerias(request):
    if not is_professor_or_admin(request.user):
        messages.error(request, 'Acesso não autorizado')
        return redirect('home')

    termo_pesquisa = request.GET.get('q', '').strip()
    filtro_ods = request.GET.get('ods', '').strip()
    filtro_setor = request.GET.get('setor', '').strip()
    filtro_semestre = request.GET.get('semestre', '').strip()

    demandas = Demanda.objects.select_related('organizacao', 'ods_relacionado').order_by('-data_criacao')

    if termo_pesquisa:
        demandas = demandas.filter(
            Q(titulo__icontains=termo_pesquisa) |
            Q(descricao__icontains=termo_pesquisa) |
            Q(setores_relacionados__icontains=termo_pesquisa) |
            Q(organizacao__nome_organizacao__icontains=termo_pesquisa)
        )

    if filtro_ods:
        demandas = demandas.filter(ods_relacionado__numero=filtro_ods)

    if filtro_setor:
        demandas = demandas.filter(setores_relacionados__icontains=filtro_setor)

    if filtro_semestre and '.' in filtro_semestre:
        ano, semestre = filtro_semestre.split('.', 1)
        if ano.isdigit():
            demandas = demandas.filter(data_criacao__year=int(ano))
            if semestre == '1':
                demandas = demandas.filter(data_criacao__month__lte=6)
            elif semestre == '2':
                demandas = demandas.filter(data_criacao__month__gte=7)

    filtros_ativos = any([termo_pesquisa, filtro_ods, filtro_setor, filtro_semestre])
    total_demandas = demandas.count()

    demandas_cards = []
    if total_demandas:
        paginator = Paginator(demandas, 4)
        page_obj = paginator.get_page(request.GET.get('page'))

        for demanda in page_obj.object_list:
            semestre_demanda = demanda.semestre or (f"{demanda.data_criacao.year}.1" if demanda.data_criacao.month <= 6 else f"{demanda.data_criacao.year}.2")
            ods_numero = demanda.ods_relacionado.numero if demanda.ods_relacionado else None
            if ods_numero is None:
                primeiro_ods = demanda.ods.first()
                ods_numero = primeiro_ods.numero if primeiro_ods else None

            demandas_cards.append({
                'organizacao': demanda.parceiro_display,
                'setor': demanda.setores_relacionados,
                'titulo': demanda.titulo,
                'descricao': demanda.descricao,
                'semestre': semestre_demanda,
                'ods': ods_numero,
                'id': demanda.id,
            })
    else:
        paginator = None
        page_obj = None

    if not total_demandas and not filtros_ativos:
        demandas_cards = [
            {
                'organizacao': 'Praia Limpa',
                'setor': 'Reciclagem',
                'titulo': 'App Praia Limpa',
                'descricao': 'A ONG Praia Limpa está lançando uma iniciativa com o SENAC de desenvolvimento de um aplicativo para as suas atividades.',
                'semestre': '2026.1',
                'ods': 14,
                'id': None,
            },
            {
                'organizacao': 'Casa da Cultura',
                'setor': 'Eventos',
                'titulo': 'App Encontro Cultural',
                'descricao': 'A Casa da Cultura de Recife está lançando uma iniciativa com o SENAC de desenvolvimento de um aplicativo para a democratização do acesso a eventos culturais na cidade do Recife.',
                'semestre': '2026.1',
                'ods': 11,
                'id': None,
            },
        ]
        total_demandas = 4

    cards_visiveis = len(demandas_cards)
    contexto = {
        'demandas_cards': demandas_cards,
        'empty_slots': range(max(0, 4 - cards_visiveis)),
        'total_demandas': total_demandas,
        'exibindo_inicio': 1 if total_demandas else 0,
        'exibindo_fim': min(4, total_demandas),
        'page_obj': page_obj,
        'termo_pesquisa': termo_pesquisa,
        'filtro_ods': filtro_ods,
        'filtro_setor': filtro_setor,
        'filtro_semestre': filtro_semestre,
    }

    return render(request, 'projetos/parcerias.html', contexto)


@login_required(login_url='/login/')
def matchmaking_view(request):
    if not is_professor_or_admin(request.user):
        messages.error(request, 'Acesso não autorizado')
        return redirect('home')

    filtro_curso = request.GET.get('curso', '').strip()
    filtro_semestre = request.GET.get('semestre', '').strip()

    demandas = Demanda.objects.select_related('organizacao', 'ods_relacionado').order_by('-data_criacao')

    if filtro_curso:
        demandas = demandas.filter(organizacao__curso__icontains=filtro_curso)

    if filtro_semestre and '.' in filtro_semestre:
        ano, semestre = filtro_semestre.split('.', 1)
        if ano.isdigit():
            demandas = demandas.filter(data_criacao__year=int(ano))
            if semestre == '1':
                demandas = demandas.filter(data_criacao__month__lte=6)
            elif semestre == '2':
                demandas = demandas.filter(data_criacao__month__gte=7)

    novas_demandas = demandas.filter(status='NOVA')
    temas_validados = demandas.filter(status='VALIDADA')
    em_desenvolvimento = demandas.filter(status='DESENVOLVIMENTO')
    solucoes_entregues = demandas.filter(status='ENTREGUE')

    contexto = {
        'novas_demandas': novas_demandas,
        'temas_validados': temas_validados,
        'em_desenvolvimento': em_desenvolvimento,
        'solucoes_entregues': solucoes_entregues,
        'filtro_curso': filtro_curso,
        'filtro_semestre': filtro_semestre,
    }
    return render(request, 'projetos/matchmaking.html', contexto)
