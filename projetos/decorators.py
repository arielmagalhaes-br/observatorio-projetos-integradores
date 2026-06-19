from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

from .auth_utils import get_user_role


def role_required(*allowed_roles):
    """Decorator to require that the logged user has one of the allowed perfil.tipo_usuario values.

    Usage: @role_required('ADMIN') or @role_required('PROFESSOR', 'ADMIN')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            if user is None or not user.is_authenticated:
                messages.error(request, 'Acesso negado: autentique-se.')
                return redirect('login')

            tipo = get_user_role(user)
            if not tipo:
                messages.error(request, 'Acesso negado: perfil inexistente.')
                return redirect('home')

            if tipo not in allowed_roles:
                messages.error(request, 'Acesso negado: permissão insuficiente.')
                return redirect('home')

            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
