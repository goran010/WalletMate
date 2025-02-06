from django.contrib.auth.models import Group

def is_admin_context(request):
    if request.user.is_authenticated:
        is_admin = (
            request.user.is_superuser or 
            request.user.groups.filter(name='administracija').exists()
        )
    else:
        is_admin = False

    return {'is_admin': is_admin}
