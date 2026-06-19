from .auth_utils import get_user_perfil, get_user_role, is_admin_user, is_professor_user


def auth_context(request):
    user = getattr(request, 'user', None)
    role = get_user_role(user)

    return {
        'usuario_perfil': get_user_perfil(user),
        'usuario_tipo': role,
        'usuario_admin': is_admin_user(user),
        'usuario_professor': is_professor_user(user),
        'usuario_aluno': role == 'ALUNO',
        'usuario_parceiro': role == 'PARCEIRO',
    }
