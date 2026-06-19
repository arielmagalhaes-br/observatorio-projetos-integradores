from django.core.exceptions import ObjectDoesNotExist


def get_user_perfil(user):
    if not user or not user.is_authenticated:
        return None

    try:
        return user.perfil
    except (AttributeError, ObjectDoesNotExist):
        return None


def get_user_role(user):
    if not user or not user.is_authenticated:
        return ''

    perfil = get_user_perfil(user)
    if perfil and perfil.tipo_usuario:
        return perfil.tipo_usuario

    if user.is_superuser or user.is_staff:
        return 'ADMIN'

    return ''


def is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_superuser or get_user_role(user) == 'ADMIN'))


def is_professor_user(user):
    return get_user_role(user) == 'PROFESSOR'


def is_professor_or_admin(user):
    return is_admin_user(user) or is_professor_user(user)


def redirect_name_for_user(user):
    role = get_user_role(user)

    if is_admin_user(user):
        return 'admin_dashboard'
    if role == 'PROFESSOR':
        return 'professor_dashboard'
    if role == 'PARCEIRO':
        return 'parceiro_dashboard'
    if role == 'ALUNO':
        return 'home'

    return 'editar_perfil'
