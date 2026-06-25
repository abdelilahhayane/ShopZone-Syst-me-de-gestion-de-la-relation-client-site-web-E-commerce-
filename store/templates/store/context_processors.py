from .models import Panier

def panier_count(request):
    if request.user.is_authenticated:
        count = Panier.objects.filter(utilisateur=request.user).count()
    else:
        count = 0
    return {'panier_count': count}