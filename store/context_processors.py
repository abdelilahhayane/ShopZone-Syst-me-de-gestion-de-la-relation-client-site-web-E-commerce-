from .models import Panier


def panier_count(request):
    """Ajoute le nombre d'articles du panier au contexte global"""
    count = 0
    if request.user.is_authenticated:
        try:
            count = Panier.objects.filter(utilisateur=request.user).count()
        except Exception:
            count = 0
    return {'panier_count': count}
