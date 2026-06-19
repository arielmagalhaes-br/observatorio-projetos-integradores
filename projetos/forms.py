from django import forms

from .models import Projeto


class ProjetoBaseForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = [
            'titulo',
            'semestre',
            'resumo',
            'inspiracao',
            'descricao',
            'proximos_passos',
            'Link_repositorio',
            'Link_prototipo',
            'link_demo',
            'link_video',
            'status',
        ]

    # Observação: este ModelForm é propositalmente “básico”.
    # Campos que não existem no Model (ex: proximos_passos) serão tratados
    # em refatorações futuras ou ajustados conforme o modelo real.

