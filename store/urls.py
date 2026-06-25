from django.urls import path
from . import views

from .views import creer_reclamation

urlpatterns = [
    # Accueil
    path('', views.accueil, name='accueil'),

    # Authentification
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),

    # Profil
    path('profil/', views.profil, name='profil'),
    path('mot-de-passe-oublie/', views.CustomPasswordResetView.as_view(), name='mot_de_passe_oublie'),
    path('mot-de-passe-oublie-envoye/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reinitialiser-mot-de-passe/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('mot-de-passe-change/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Produits
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produits/<int:id>/', views.detail_produit, name='detail_produit'),

    # Panier
    path('panier/', views.panier, name='panier'),
    path('panier/ajouter/<int:produit_id>/', views.ajouter_panier, name='ajouter_panier'),
    path('panier/supprimer/<int:item_id>/', views.supprimer_panier, name='supprimer_panier'),
    path('panier/modifier/<int:item_id>/', views.modifier_quantite, name='modifier_quantite'),
    path('panier/vider/', views.vider_panier, name='vider_panier'),

    # Adresses
    path('mes-adresses/', views.mes_adresses, name='mes_adresses'),
    path('ajouter-adresse/', views.ajouter_adresse, name='ajouter_adresse'),
    path('modifier-adresse/<int:adresse_id>/', views.modifier_adresse, name='modifier_adresse'),
    path('supprimer-adresse/<int:adresse_id>/', views.supprimer_adresse, name='supprimer_adresse'),

    # Commandes
    path('checkout/', views.checkout, name='checkout'),
    path('commander/', views.passer_commande, name='passer_commande'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('commande/<int:commande_id>/', views.detail_commande, name='detail_commande'),
    path('commande/<int:commande_id>/annuler/', views.annuler_commande, name='annuler_commande'),


    # reclamation
    path('reclamation/', creer_reclamation, name='creer_reclamation'),
    path('mes-reclamations/', views.mes_reclamations, name='mes_reclamations'),



    path('support/', views.support_view, name='support'),
    # path('sav/', views.sav_view, name='sav'),
    # path('mes-demandes-sav/', views.mes_demandes_sav, name='mes_demandes_sav'),
    # path('demande-sav/<int:demande_id>/', views.detail_demande_sav, name='detail_demande_sav'),
    # path('demande-sav/<int:demande_id>/annuler/', views.annuler_demande_sav, name='annuler_demande_sav'),
    path('sav/', views.sav_view, name='sav'),
    path('mes-demandes-sav/', views.mes_demandes_sav, name='mes_demandes_sav'),  # ← Vérifiez cette ligne
    path('demande-sav/<int:demande_id>/', views.detail_demande_sav, name='detail_demande_sav'),
    path('demande-sav/<int:demande_id>/annuler/', views.annuler_demande_sav, name='annuler_demande_sav'),

]