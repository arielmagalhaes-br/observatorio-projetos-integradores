from django.db import models  
from django.contrib.auth.models import User  

# Create your models here.

class Turma(models.Model):
    nome = models.CharField(max_length=100)
    semestre = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.nome} ({self.semestre})"

class Perfil(models.Model):
    TIPOS_USUARIO = (
        ('ALUNO', 'Aluno/Egresso'),
        ('PROFESSOR', 'Professor Orientador'),
        ('ADMIN', 'Administrador'),
        ('PARCEIRO', 'Organização Parceira'),
    )

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=20, choices=TIPOS_USUARIO, default='ALUNO')
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, blank=True, related_name='perfis')

    # Campos Alunos/Professores
    curso = models.CharField(max_length=100, blank=True, null=True)
    biografia = models.TextField(blank=True, null=True)

    # Campos Parceiros
    nome_organizacao = models.CharField(max_length=150, blank=True, null=True)
    setor_atuacao = models.CharField(max_length=100, blank=True, null=True)

    # Redes Sociais e Foto
    LinkedIn = models.URLField(blank=True, null=True)
    github = models.URLField(max_length=100, blank=True, null=True)
    instagram = models.URLField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='perfil_fotos/', blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.get_tipo_usuario_display()})"
    
class Tecnologia(models.Model):
    CATEGORIA_CHOICES = (
        ('LING', 'Linguagem'),
        ('BD', 'Banco de Dados'),
        ('DESIGN', 'Design/Ferramenta'),
    )
    nome = models.CharField(max_length=50)
    categoria = models.CharField(max_length=10, choices=CATEGORIA_CHOICES)

    def __str__(self):
        return self.nome
    
class ODS(models.Model):
    numero = models.IntegerField(unique=True)
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f"ODS {self.numero}: {self.nome}"
    
class Projeto(models.Model):
    STATUS_CHOICES = (
        ('RASCUNHO', 'Rascunho'),
        ('REVISAO', 'Em revisão'),
        ('AJUSTES', 'Pendente de Ajustes'),
        ('APROVADO', 'Aprovado'),
    )

    titulo = models.CharField(max_length=200)
    semestre = models.CharField(max_length=10)
    resumo = models.TextField()
    inspiracao = models.TextField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    # Aquivo de Documentação
    documentacao_pdf = models.FileField(upload_to='documentos_projetos/', blank=True, null=True)

    # Relacionamentos
    autores = models.ManyToManyField(Perfil, related_name='projetos')
    tecnologias = models.ManyToManyField(Tecnologia, blank=True)
    ods = models.ManyToManyField(ODS, blank=True)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, blank=True, related_name='projetos')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RASCUNHO')

    # Avaliação do Professor
    nota_conceito = models.CharField(max_length=10, blank=True, null=True)
    feedback_professor = models.TextField(blank=True, null=True)

    # Links Externos
    Link_repositorio = models.URLField(blank=True, null=True)
    Link_prototipo = models.URLField(blank=True, null=True)
    link_demo = models.URLField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.titulo

    @property
    def capa_url(self):
        primeira_imagem = self.imagens.first()
        if primeira_imagem and primeira_imagem.imagem:
            return primeira_imagem.imagem.url
        return None
    
class ImagemProjeto(models.Model):
    projeto = models.ForeignKey(Projeto, related_name='imagens', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='projetos_galeria/')

class Demanda(models.Model):
    STATUS_DEMANDA = (
        ('NOVA', 'Nova Demanda'),
        ('VALIDADA', 'Tema Validado'),
        ('DESENVOLVIMENTO', 'Em Desenvolvimento'),
        ('ENTREGUE', 'Soluções Entregues'),
    )
    organizacao = models.ForeignKey(Perfil, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'PARCEIRO'}, null=True, blank=True)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    setores_relacionados = models.CharField(max_length=200, blank=True, null=True)
    ods_relacionado = models.ForeignKey(ODS, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_DEMANDA, default='NOVA')
    
    # Novos campos solicitados
    parceiro = models.CharField(max_length=150, blank=True, null=True)
    semestre = models.CharField(max_length=10, blank=True, null=True)
    ods = models.ManyToManyField(ODS, blank=True, related_name='demandas_ods')
    
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        nome_parceiro = self.parceiro or (self.organizacao.nome_organizacao if self.organizacao else 'Nenhum')
        return f"{self.titulo} - {nome_parceiro}"

    @property
    def parceiro_display(self):
        if self.parceiro:
            return self.parceiro
        if self.organizacao and self.organizacao.nome_organizacao:
            return self.organizacao.nome_organizacao
        return 'Nenhum'