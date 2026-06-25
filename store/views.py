from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit, Categorie, Panier, Commande, LigneCommande, Adresse, Paiement, Reclamation,SupportMessage,DemandeSAV, Commande

from .forms import ReclamationForm, SupportMessageForm, DemandeSAVForm

from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings


from django.core.paginator import Paginator
from django.utils import timezone





# ─── ACCUEIL ─────────────────────────────────────────────────
def accueil(request):
    produits_recents = Produit.objects.all().order_by('-date_ajout')[:8]
    categories = Categorie.objects.all()
    return render(request, 'store/accueil.html', {
        'produits_recents': produits_recents,
        'categories': categories,
    })


# ─── INSCRIPTION ─────────────────────────────────────────────
def inscription(request):
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not all([nom, prenom, email, password, password2]):
            messages.error(request, 'Tous les champs sont obligatoires.')
            return redirect('inscription')

        if password != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return redirect('inscription')

        if len(password) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
            return redirect('inscription')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
            return redirect('inscription')

        utilisateur = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=prenom, last_name=nom
        )
        login(request, utilisateur)
        messages.success(request, f'Bienvenue {prenom} ! Votre compte a été créé.')
        return redirect('accueil')

    return render(request, 'store/inscription.html')


# ─── CONNEXION ───────────────────────────────────────────────
def connexion(request):
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        utilisateur = authenticate(request, username=email, password=password)

        if utilisateur is not None:
            login(request, utilisateur)
            messages.success(request, f'Bon retour, {utilisateur.first_name} !')
            return redirect('accueil')
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
            return redirect('connexion')

    return render(request, 'store/connexion.html')


# ─── DÉCONNEXION ─────────────────────────────────────────────
def deconnexion(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('connexion')


# ─── PROFIL ──────────────────────────────────────────────────
@login_required(login_url='connexion')
def profil(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'modifier_infos':
            prenom = request.POST.get('prenom', '').strip()
            nom = request.POST.get('nom', '').strip()
            email = request.POST.get('email', '').strip()

            if not all([prenom, nom, email]):
                messages.error(request, 'Tous les champs sont obligatoires.')
                return redirect('profil')

            if User.objects.filter(username=email).exclude(id=request.user.id).exists():
                messages.error(request, 'Cet email est déjà utilisé.')
                return redirect('profil')

            request.user.first_name = prenom
            request.user.last_name = nom
            request.user.email = email
            request.user.username = email
            request.user.save()
            messages.success(request, 'Profil mis à jour avec succès !')

        elif action == 'changer_mdp':
            ancien = request.POST.get('ancien_mdp', '')
            nouveau = request.POST.get('nouveau_mdp', '')
            confirmation = request.POST.get('confirmation_mdp', '')

            if not request.user.check_password(ancien):
                messages.error(request, 'Ancien mot de passe incorrect.')
                return redirect('profil')

            if nouveau != confirmation:
                messages.error(request, 'Les mots de passe ne correspondent pas.')
                return redirect('profil')

            if len(nouveau) < 6:
                messages.error(request, 'Minimum 6 caractères.')
                return redirect('profil')

            request.user.set_password(nouveau)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Mot de passe changé !')

        return redirect('profil')

    try:
        commandes_count = Commande.objects.filter(utilisateur=request.user).count()
    except Exception:
        commandes_count = 0

    return render(request, 'store/profile.html', {
        'commandes_count': commandes_count,
    })

# ─── MOT DE PASSE OUBLIÉ ─────────────────────────────────────
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

class CustomPasswordResetView(PasswordResetView):
    template_name = 'store/mot_de_passe_oublie.html'
    email_template_name = 'store/password_reset_email.html'
    success_url = '/mot-de-passe-oublie-envoye/'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'store/mot_de_passe_oublie_envoye.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'store/reinitialiser_mot_de_passe.html'
    success_url = '/mot-de-passe-change/'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'store/mot_de_passe_change.html'


# ─── LISTE PRODUITS ──────────────────────────────────────────
def liste_produits(request):
    produits = Produit.objects.all()
    categories = Categorie.objects.all()
    categorie_id = request.GET.get('categorie')
    recherche = request.GET.get('q', '').strip()

    if categorie_id:
        produits = produits.filter(categorie__id=categorie_id)
    if recherche:
        produits = produits.filter(nom__icontains=recherche)

    return render(request, 'store/liste_produits.html', {
        'produits': produits,
        'categories': categories,
        'categorie_id': int(categorie_id) if categorie_id else None,
        'recherche': recherche,
        'total_produits': produits.count(),
    })


# ─── DÉTAIL PRODUIT ──────────────────────────────────────────
def detail_produit(request, id):
    produit = get_object_or_404(Produit, id=id)
    produits_similaires = Produit.objects.filter(
        categorie=produit.categorie
    ).exclude(id=id)[:4]
    return render(request, 'store/detail_produit.html', {
        'produit': produit,
        'produits_similaires': produits_similaires,
    })


# ─── PANIER ──────────────────────────────────────────────────
@login_required(login_url='connexion')
def panier(request):
    items = Panier.objects.filter(utilisateur=request.user)
    total = sum(item.total_item() for item in items)
    return render(request, 'store/panier.html', {
        'items': items,
        'total': total,
    })


@login_required(login_url='connexion')
def ajouter_panier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    item, created = Panier.objects.get_or_create(
        utilisateur=request.user, produit=produit
    )
    if not created:
        item.quantite += 1
        item.save()
        messages.success(request, f'Quantité mise à jour pour "{produit.nom}".')
    else:
        messages.success(request, f'"{produit.nom}" ajouté au panier !')
    
    # If ?checkout=true, go to cart; otherwise return to previous page
    if request.GET.get('checkout') == 'true':
        return redirect('panier')
    return redirect(request.META.get('HTTP_REFERER', 'panier'))


@login_required(login_url='connexion')
def supprimer_panier(request, item_id):
    item = get_object_or_404(Panier, id=item_id, utilisateur=request.user)
    nom = item.produit.nom
    item.delete()
    messages.warning(request, f'"{nom}" retiré du panier.')
    return redirect('panier')


@login_required(login_url='connexion')
def modifier_quantite(request, item_id):
    item = get_object_or_404(Panier, id=item_id, utilisateur=request.user)
    action = request.POST.get('action')
    if action == 'augmenter':
        item.quantite += 1
        item.save()
    elif action == 'diminuer':
        if item.quantite > 1:
            item.quantite -= 1
            item.save()
        else:
            item.delete()
            messages.warning(request, 'Produit retiré du panier.')
    return redirect('panier')


@login_required(login_url='connexion')
def vider_panier(request):
    Panier.objects.filter(utilisateur=request.user).delete()
    messages.warning(request, 'Votre panier a été vidé.')
    return redirect('panier')


# ─── ADRESSES ────────────────────────────────────────────────
@login_required(login_url='connexion')
def mes_adresses(request):
    adresses = Adresse.objects.filter(utilisateur=request.user)
    return render(request, 'store/mes_adresses.html', {
        'adresses': adresses,
    })


@login_required(login_url='connexion')
def ajouter_adresse(request):
    if request.method == 'POST':
        nom_complet = request.POST.get('nom_complet', '').strip()
        rue = request.POST.get('rue', '').strip()
        ville = request.POST.get('ville', '').strip()
        code_postal = request.POST.get('code_postal', '').strip()
        pays = request.POST.get('pays', 'France').strip()
        telephone = request.POST.get('telephone', '').strip()
        est_defaut = request.POST.get('est_defaut') == 'on'

        if not all([nom_complet, rue, ville, code_postal, telephone]):
            messages.error(request, 'Tous les champs sont obligatoires.')
            return redirect('ajouter_adresse')

        if est_defaut:
            Adresse.objects.filter(utilisateur=request.user).update(est_defaut=False)

        Adresse.objects.create(
            utilisateur=request.user,
            nom_complet=nom_complet,
            rue=rue,
            ville=ville,
            code_postal=code_postal,
            pays=pays,
            telephone=telephone,
            est_defaut=est_defaut
        )
        messages.success(request, 'Adresse ajoutée avec succès !')
        return redirect('mes_adresses')

    return render(request, 'store/ajouter_adresse.html')


@login_required(login_url='connexion')
def modifier_adresse(request, adresse_id):
    adresse = get_object_or_404(Adresse, id=adresse_id, utilisateur=request.user)

    if request.method == 'POST':
        adresse.nom_complet = request.POST.get('nom_complet', '').strip()
        adresse.rue = request.POST.get('rue', '').strip()
        adresse.ville = request.POST.get('ville', '').strip()
        adresse.code_postal = request.POST.get('code_postal', '').strip()
        adresse.pays = request.POST.get('pays', 'France').strip()
        adresse.telephone = request.POST.get('telephone', '').strip()
        est_defaut = request.POST.get('est_defaut') == 'on'

        if not all([adresse.nom_complet, adresse.rue, adresse.ville, adresse.code_postal, adresse.telephone]):
            messages.error(request, 'Tous les champs sont obligatoires.')
            return redirect('modifier_adresse', adresse_id=adresse.id)

        if est_defaut:
            Adresse.objects.filter(utilisateur=request.user).update(est_defaut=False)

        adresse.est_defaut = est_defaut
        adresse.save()
        messages.success(request, 'Adresse modifiée avec succès !')
        return redirect('mes_adresses')

    return render(request, 'store/modifier_adresse.html', {
        'adresse': adresse,
    })


@login_required(login_url='connexion')
def supprimer_adresse(request, adresse_id):
    adresse = get_object_or_404(Adresse, id=adresse_id, utilisateur=request.user)
    adresse.delete()
    messages.warning(request, 'Adresse supprimée.')
    return redirect('mes_adresses')


# ─── CHECKOUT ──────────────────────────────────────────────
@login_required(login_url='connexion')
def checkout(request):
    items = Panier.objects.filter(utilisateur=request.user)
    if not items.exists():
        messages.error(request, 'Votre panier est vide.')
        return redirect('panier')

    adresses = Adresse.objects.filter(utilisateur=request.user)
    total = sum(item.total_item() for item in items)

    if request.method == 'POST':
        adresse_id = request.POST.get('adresse_id')
        if not adresse_id:
            messages.error(request, 'Veuillez sélectionner une adresse de livraison.')
            return redirect('checkout')

        adresse = get_object_or_404(Adresse, id=adresse_id, utilisateur=request.user)

        # Check stock
        for item in items:
            if item.produit.quantite_stock < item.quantite:
                messages.error(request, f'Stock insuffisant pour "{item.produit.nom}". Disponible: {item.produit.quantite_stock}')
                return redirect('panier')

        # Create order
        commande = Commande.objects.create(
            utilisateur=request.user,
            adresse=adresse,
            montant_total=total
        )

        # Create order lines and decrement stock
        for item in items:
            LigneCommande.objects.create(
                commande=commande,
                produit=item.produit,
                quantite=item.quantite,
                prix_unitaire=item.produit.prix
            )
            item.produit.quantite_stock -= item.quantite
            item.produit.save()

        # Create payment (simulated as successful)
        import uuid
        paiement = Paiement.objects.create(
            commande=commande,
            mode_paiement='carte',  # Could be from form
            montant=total,
            statut='reussi',
            reference=f"PAY-{uuid.uuid4().hex[:8].upper()}"
        )

        items.delete()
        messages.success(request, f'Commande #{commande.id} passée avec succès ! Paiement confirmé.')
        return redirect('detail_commande', commande_id=commande.id)

    return render(request, 'store/checkout.html', {
        'items': items,
        'adresses': adresses,
        'total': total,
    })


# ─── PASSER COMMANDE ─────────────────────────────────────────
@login_required(login_url='connexion')
def passer_commande(request):
    # Redirect to checkout
    return redirect('checkout')


# ─── MES COMMANDES ───────────────────────────────────────────
@login_required(login_url='connexion')
def mes_commandes(request):
    commandes = Commande.objects.filter(
        utilisateur=request.user
    ).order_by('-date_commande')
    return render(request, 'store/mes_commandes.html', {
        'commandes': commandes,
    })


# ─── DÉTAIL COMMANDE ─────────────────────────────────────────
@login_required(login_url='connexion')
def detail_commande(request, commande_id):
    commande = get_object_or_404(
        Commande, id=commande_id, utilisateur=request.user
    )
    statuts_etapes = [
        ('en_attente',     'En attente',     'fa-clock'),
        ('confirmee',      'Confirmée',      'fa-check'),
        ('en_preparation', 'En préparation', 'fa-cog'),
    ]
    return render(request, 'store/datail_commande.html', {
        'commande': commande,
        'statuts_etapes': statuts_etapes,
    })


@login_required(login_url='connexion')
def annuler_commande(request, commande_id):
    commande = get_object_or_404(
        Commande, id=commande_id, utilisateur=request.user
    )

    if commande.statut != 'en_attente':
        messages.error(request, 'Cette commande ne peut plus être annulée.')
        return redirect('detail_commande', commande_id=commande.id)

    # Restore stock
    for ligne in commande.lignes.all():
        ligne.produit.quantite_stock += ligne.quantite
        ligne.produit.save()

    # Update payment if exists
    try:
        paiement = Paiement.objects.get(commande=commande)
        paiement.statut = 'rembourse'
        paiement.save()
    except Paiement.DoesNotExist:
        pass

    commande.statut = 'annulee'
    commande.save()

    messages.success(request, f'Commande #{commande.id} annulée avec succès.')
    return redirect('mes_commandes')




# ─── DÉTAIL Reclamation ─────────────────────────────────────────

# @login_required
# def creer_reclamation(request):

#     if request.method == 'POST':
#         form = ReclamationForm(request.POST)

#         if form.is_valid():
#             reclamation = form.save(commit=False)
#             reclamation.client = request.user
#             reclamation.save()

#             return redirect('mes_reclamations')

#     else:
#         form = ReclamationForm()

#     return render(
#         request,
#         'store/creer_reclamation.html',
#         {'form': form}
#     )

# @login_required
# def creer_reclamation(request):
#     if request.method == 'POST':
#         form = ReclamationForm(request.POST)
#         if form.is_valid():
#             reclamation = form.save(commit=False)
#             reclamation.client = request.user
#             reclamation.save()
#             return redirect('mes_reclamations')
#     else:
#         form = ReclamationForm()
    
#     return render(request, 'store/creer_reclamation.html', {'form': form})
# 3.


@login_required
def creer_reclamation(request):
    if request.method == 'POST':
        form = ReclamationForm(request.POST)
        if form.is_valid():
            reclamation = form.save(commit=False)
            reclamation.client = request.user
            reclamation.save()
            messages.success(request, 'Votre réclamation a été envoyée avec succès !')
            return redirect('mes_reclamations')
    else:
        form = ReclamationForm()
    
    return render(request, 'store/creer_reclamation.html', {'form': form})

@login_required
def mes_reclamations(request):
    reclamations = Reclamation.objects.filter(client=request.user).order_by('-date_creation')
    return render(request, 'store/mes_reclamations.html', {'reclamations': reclamations})



def support(request):
    """Page de support client (accessible sans authentification)"""
    return render(request, 'store/support.html')

@login_required
def sav(request):
    """Page Service Après-Vente (nécessite authentification)"""
    return render(request, 'store/sav.html')





# ─── Support Message ─────────────────────────────────────────



def support_view(request):
    """
    Page de support client (accessible sans authentification)
    """
    if request.method == 'POST':
        form = SupportMessageForm(request.POST)
        if form.is_valid():
            # Sauvegarder le message
            support_message = form.save(commit=False)
            
            # Si l'utilisateur est connecté, l'associer au message
            if request.user.is_authenticated:
                support_message.client = request.user
                support_message.nom_complet = request.user.get_full_name() or request.user.username
                support_message.email = request.user.email
            
            support_message.save()
            
            # Envoyer un email de confirmation au client
            try:
                send_mail(
                    subject=f"Confirmation de votre message support - {support_message.sujet}",
                    message=f"""
Bonjour {support_message.nom_complet},

Nous avons bien reçu votre message concernant : {support_message.sujet}

Notre équipe support va traiter votre demande dans les plus brefs délais.

Résumé de votre message :
{support_message.message}

Nous vous répondrons à l'adresse : {support_message.email}

Cordialement,
L'équipe Support
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[support_message.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Erreur d'envoi d'email: {e}")
            
            # Envoyer une notification à l'admin (email)
            try:
                send_mail(
                    subject=f"Nouveau message support - {support_message.sujet}",
                    message=f"""
Nouveau message de support reçu !

Client : {support_message.nom_complet}
Email : {support_message.email}
Téléphone : {support_message.telephone or 'Non renseigné'}
Sujet : {support_message.sujet}

Message :
{support_message.message}

Connectez-vous à l'admin pour répondre :
{settings.SITE_URL}/admin/store/supportmessage/{support_message.id}/change/
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Erreur d'envoi d'email admin: {e}")
            
            messages.success(request, 'Votre message a été envoyé avec succès ! Notre équipe vous répondra dans les plus brefs délais.')
            return redirect('support')
    else:
        form = SupportMessageForm()
        
        # Pré-remplir les champs si l'utilisateur est connecté
        if request.user.is_authenticated:
            initial_data = {
                'nom_complet': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
            form = SupportMessageForm(initial=initial_data)
    
    return render(request, 'store/support.html', {'form': form})

@staff_member_required
def admin_support_messages(request):
    """
    Vue admin pour voir tous les messages support (accessible uniquement aux staff)
    """
    messages_list = SupportMessage.objects.all().order_by('-date_creation')
    
    # Statistiques
    stats = {
        'total': messages_list.count(),
        'non_lu': messages_list.filter(statut='non_lu').count(),
        'en_cours': messages_list.filter(statut='en_cours').count(),
        'traite': messages_list.filter(statut='traite').count(),
        'ferme': messages_list.filter(statut='ferme').count(),
    }
    
    return render(request, 'admin/support_messages.html', {
        'messages_list': messages_list,
        'stats': stats,
    })






# store/views.py
@login_required
def sav_view(request):
    """
    Page principale SAV - Création d'une demande
    """
    if request.method == 'POST':
        form = DemandeSAVForm(request.POST, request.FILES)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.client = request.user
            
            # Associer à une commande existante si trouvée
            numero_commande = form.cleaned_data.get('numero_commande')
            if numero_commande:
                try:
                    # Chercher par ID (car le modèle Commande n'a pas de champ numero_commande)
                    commande = Commande.objects.get(
                        id=numero_commande,
                        utilisateur=request.user
                    )
                    demande.commande = commande
                    demande.numero_commande = f"CMD-{commande.id}"  # Stocker le numéro formaté
                except (Commande.DoesNotExist, ValueError):
                    # Si ce n'est pas un ID valide, garder le numéro saisi
                    demande.numero_commande = numero_commande
            
            demande.save()
            
            messages.success(
                request,
                '✅ Votre demande SAV a été envoyée avec succès ! '
                'Nous la traiterons dans les plus brefs délais.'
            )
            return redirect('mes_demandes_sav')
    else:
        form = DemandeSAVForm()
    
    return render(request, 'store/sav.html', {'form': form})

# @login_required
# def sav_view(request):
#     """
#     Page principale SAV - Création d'une demande
#     """
#     if request.method == 'POST':
#         form = DemandeSAVForm(request.POST, request.FILES)
#         if form.is_valid():
#             demande = form.save(commit=False)
#             demande.client = request.user
            
#             # Associer à une commande existante si trouvée
#             if demande.numero_commande:
#                 try:
#                     commande = Commande.objects.get(
#                         numero_commande=demande.numero_commande,
#                         utilisateur=request.user
#                     )



#                     demande.commande = commande
#                 except Commande.DoesNotExist:
#                     pass
            
#             demande.save()
            
#             messages.success(
#                 request,
#                 '✅ Votre demande SAV a été envoyée avec succès ! '
#                 'Nous la traiterons dans les plus brefs délais.'
#             )
#             return redirect('mes_demandes_sav')
#     else:
#         form = DemandeSAVForm()
    
#     return render(request, 'store/sav.html', {'form': form})


@login_required
def mes_demandes_sav(request):
    """
    Liste des demandes SAV du client
    """
    demandes = DemandeSAV.objects.filter(client=request.user).order_by('-date_creation')
    
    # Statistiques
    stats = {
        'total': demandes.count(),
        'en_attente': demandes.filter(statut='en_attente').count(),
        'en_cours': demandes.filter(statut__in=['validee', 'en_cours', 'expediee']).count(),
        'terminees': demandes.filter(statut='terminee').count(),
        'rejetees': demandes.filter(statut='rejetee').count(),
    }
    
    paginator = Paginator(demandes, 10)
    page_number = request.GET.get('page')
    demandes_page = paginator.get_page(page_number)
    
    return render(request, 'store/mes_demandes_sav.html', {
        'demandes': demandes_page,
        'stats': stats,
    })

@login_required
def detail_demande_sav(request, demande_id):
    """
    Détail d'une demande SAV
    """
    demande = get_object_or_404(DemandeSAV, id=demande_id, client=request.user)
    return render(request, 'store/detail_demande_sav.html', {'demande': demande})

@login_required
def annuler_demande_sav(request, demande_id):
    """
    Annuler une demande SAV (seulement si en attente)
    """
    demande = get_object_or_404(DemandeSAV, id=demande_id, client=request.user)
    
    if demande.statut == 'en_attente':
        demande.delete()
        messages.success(request, '✅ La demande SAV a été annulée.')
    else:
        messages.error(request, '❌ Cette demande ne peut pas être annulée.')
    
    return redirect('mes_demandes_sav')