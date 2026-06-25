from django.contrib import admin
from django.utils.html import format_html, mark_safe
# from .models import Categorie, Produit, Panier, Commande, LigneCommande, Adresse, Paiement, Reclamation, SupportMessage

from django.utils import timezone


from .models import (
    Categorie, Produit, Panier, Commande, LigneCommande, 
    Adresse, Paiement, Reclamation, SupportMessage,
    DemandeSAV, DocumentSAV  # ← Ajoutez ces imports
)


admin.site.site_header = "🛒 ShopZone Administration"
admin.site.site_title = "ShopZone Admin"
admin.site.index_title = "Tableau de bord"


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom', 'description', 'nombre_produits']
    search_fields = ['nom']

    def nombre_produits(self, obj):
        count = Produit.objects.filter(categorie=obj).count()
        return format_html(
            '<span style="background:#e94560;color:white;padding:3px 12px;border-radius:12px;font-size:12px;font-weight:bold;">{} produits</span>',
            count
        )
    nombre_produits.short_description = "Produits"


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['apercu_image', 'nom', 'categorie', 'prix_affiche', 'stock_affiche', 'date_ajout']
    list_filter = ['categorie', 'date_ajout']
    search_fields = ['nom', 'description']
    ordering = ['-date_ajout']
    readonly_fields = ['date_ajout', 'apercu_image_detail']

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'categorie')
        }),
        ('Prix et stock', {
            'fields': ('prix', 'quantite_stock')
        }),
        ('Image', {
            'fields': ('image', 'apercu_image_detail')
        }),
        ('Date', {
            'fields': ('date_ajout',)
        }),
    )

    def apercu_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:55px;height:55px;object-fit:cover;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.15);"/>',
                obj.image.url
            )
        return mark_safe('<span style="font-size:24px;">📦</span>')
    apercu_image.short_description = ""

    def apercu_image_detail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:220px;height:220px;object-fit:cover;border-radius:14px;box-shadow:0 4px 15px rgba(0,0,0,0.2);"/>',
                obj.image.url
            )
        return "Aucune image"
    apercu_image_detail.short_description = "Aperçu"

    def prix_affiche(self, obj):
        return format_html(
            '<span style="background:#fff3f5;color:#e94560;padding:4px 12px;border-radius:20px;font-weight:bold;font-size:13px;">{} DH</span>',
            obj.prix
        )
    prix_affiche.short_description = "Prix"
    prix_affiche.admin_order_field = 'prix'

    def stock_affiche(self, obj):
        if obj.quantite_stock == 0:
            return mark_safe(
                '<span style="background:#fff0f0;color:#dc3545;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;">❌ Rupture</span>'
            )
        elif obj.quantite_stock < 5:
            return format_html(
                '<span style="background:#fffbe6;color:#e6a817;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;">⚠️ {} restants</span>',
                obj.quantite_stock
            )
        else:
            return format_html(
                '<span style="background:#f0fff4;color:#28a745;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;">✅ {} en stock</span>',
                obj.quantite_stock
            )
    stock_affiche.short_description = "Stock"
    stock_affiche.admin_order_field = 'quantite_stock'


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ['produit', 'quantite', 'prix_unitaire', 'total_ligne_affiche']
    fields = ['produit', 'quantite', 'prix_unitaire', 'total_ligne_affiche']

    def total_ligne_affiche(self, obj):
        return format_html(
            '<strong style="color:#e94560;">{} DH</strong>',
            obj.total_ligne()
        )
    total_ligne_affiche.short_description = "Sous-total"


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['numero', 'client_info', 'date_commande', 'statut_badge', 'montant_affiche', 'articles']
    list_filter = ['statut', 'date_commande']
    search_fields = ['utilisateur__first_name', 'utilisateur__last_name', 'utilisateur__email']
    ordering = ['-date_commande']
    readonly_fields = ['date_commande', 'montant_total', 'utilisateur']
    inlines = [LigneCommandeInline]

    fieldsets = (
        ('Client', {
            'fields': ('utilisateur',)
        }),
        ('Adresse de livraison', {
            'fields': ('adresse',)
        }),
        ('Commande', {
            'fields': ('date_commande', 'montant_total', 'statut')
        }),
    )

    def numero(self, obj):
        return format_html(
            '<span style="background:#1a1a2e;color:white;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:bold;">#{}</span>',
            obj.id
        )
    numero.short_description = "N°"

    def client_info(self, obj):
        return format_html(
            '<div><strong>{} {}</strong><br><small style="color:#888;">{}</small></div>',
            obj.utilisateur.first_name or '',
            obj.utilisateur.last_name or '',
            obj.utilisateur.email or ''
        )
    client_info.short_description = "Client"

    def statut_badge(self, obj):
        styles = {
            'en_attente':     ('⏳', '#fff8e1', '#f59e0b', 'En attente'),
            'confirmee':      ('✅', '#e8f5e9', '#28a745', 'Confirmée'),
            'en_preparation': ('🔧', '#e3f2fd', '#1976d2', 'En préparation'),
            'annulee':        ('❌', '#ffebee', '#dc3545', 'Annulée'),
        }
        icon, bg, color, label = styles.get(obj.statut, ('', '#eee', '#333', obj.statut))
        return format_html(
            '<span style="background:{};color:{};padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;">{} {}</span>',
            bg, color, icon, label
        )
    statut_badge.short_description = "Statut"

    def montant_affiche(self, obj):
        return format_html(
            '<span style="background:#fff3f5;color:#e94560;padding:4px 12px;border-radius:20px;font-weight:bold;">{} DH</span>',
            obj.montant_total
        )
    montant_affiche.short_description = "Total"

    def articles(self, obj):
        return format_html(
            '<span style="color:#666;">{} article(s)</span>',
            obj.lignes.count()
        )
    articles.short_description = "Articles"


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ['client_panier', 'produit_affiche', 'quantite', 'total_affiche']
    search_fields = ['utilisateur__first_name', 'utilisateur__email']

    def client_panier(self, obj):
        return format_html(
            '<strong>{} {}</strong>',
            obj.utilisateur.first_name,
            obj.utilisateur.last_name
        )
    client_panier.short_description = "Client"

    def produit_affiche(self, obj):
        return format_html(
            '<span style="color:#1a1a2e;font-weight:600;">{}</span>',
            obj.produit.nom
        )
    produit_affiche.short_description = "Produit"

    def total_affiche(self, obj):
        return format_html(
            '<span style="color:#e94560;font-weight:bold;">{} DH</span>',
            obj.total_item()
        )
    total_affiche.short_description = "Total"


@admin.register(Adresse)
class AdresseAdmin(admin.ModelAdmin):
    list_display = ['utilisateur_info', 'nom_complet', 'ville', 'code_postal', 'pays', 'est_defaut_badge']
    list_filter = ['pays', 'est_defaut']
    search_fields = ['utilisateur__first_name', 'utilisateur__last_name', 'utilisateur__email', 'ville', 'code_postal']

    def utilisateur_info(self, obj):
        return format_html(
            '<div><strong>{} {}</strong><br><small style="color:#888;">{}</small></div>',
            obj.utilisateur.first_name or '',
            obj.utilisateur.last_name or '',
            obj.utilisateur.email or ''
        )
    utilisateur_info.short_description = "Utilisateur"

    def est_defaut_badge(self, obj):
        if obj.est_defaut:
            return mark_safe(
                '<span style="background:#e8f5e9;color:#28a745;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;">🏠 Défaut</span>'
            )
        return mark_safe(
            '<span style="background:#f8f9fa;color:#6c757d;padding:4px 12px;border-radius:20px;font-size:12px;">Adresse</span>'
        )
    est_defaut_badge.short_description = "Type"


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['reference', 'commande_info', 'mode_paiement', 'montant_affiche', 'statut_badge', 'date_paiement']
    list_filter = ['mode_paiement', 'statut', 'date_paiement']
    search_fields = ['reference', 'commande__utilisateur__first_name', 'commande__utilisateur__email']
    readonly_fields = ['reference', 'date_paiement']

    def commande_info(self, obj):
        return format_html(
            '<div><strong>Commande #{}</strong><br><small style="color:#888;">{} {}</small></div>',
            obj.commande.id,
            obj.commande.utilisateur.first_name or '',
            obj.commande.utilisateur.last_name or ''
        )
    commande_info.short_description = "Commande"

    def montant_affiche(self, obj):
        return format_html(
            '<span style="background:#fff3f5;color:#e94560;padding:4px 12px;border-radius:20px;font-weight:bold;">{} DH</span>',
            obj.montant
        )
    montant_affiche.short_description = "Montant"

    def statut_badge(self, obj):
        styles = {
            'en_attente': ('⏳', '#fff8e1', '#f59e0b'),
            'reussi':     ('✅', '#e8f5e9', '#28a745'),
            'echoue':     ('❌', '#ffebee', '#dc3545'),
            'rembourse':  ('↩️', '#e3f2fd', '#1976d2'),
        }
        icon, bg, color = styles.get(obj.statut, ('', '#eee', '#333'))
        return format_html(
            '<span style="background:{};color:{};padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;">{} {}</span>',
            bg, color, icon, obj.get_statut_display()
        )
    statut_badge.short_description = "Statut"






@admin.register(Reclamation)
class ReclamationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'client',
        'sujet',
        'statut',
        'date_creation'
    )

    list_filter = (
        'statut',
        'date_creation'
    )

    search_fields = (
        'client__username',
        'sujet'
    )




@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ['sujet', 'nom_complet', 'email', 'statut_colored', 'priorite_colored', 'date_creation']
    list_filter = ['statut', 'priorite', 'date_creation']
    search_fields = ['sujet', 'message', 'nom_complet', 'email', 'telephone']
    readonly_fields = ['date_creation', 'date_reponse']
    fieldsets = (
        ('Informations Client', {
            'fields': ('nom_complet', 'email', 'telephone', 'client')
        }),
        ('Message', {
            'fields': ('sujet', 'message')
        }),
        ('Gestion', {
            'fields': ('statut', 'priorite', 'reponse', 'reponse_par', 'date_reponse')
        }),
        ('Informations', {
            'fields': ('date_creation',),
            'classes': ('collapse',)
        }),
    )
    
    def statut_colored(self, obj):
        colors = {
            'non_lu': '#dc3545',
            'en_cours': '#ffc107',
            'traite': '#28a745',
            'ferme': '#6c757d',
        }
        return format_html(
            '<span style="background-color:{};color:white;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.statut, '#6c757d'),
            obj.get_statut_display()
        )
    statut_colored.short_description = 'Statut'
    
    def priorite_colored(self, obj):
        colors = {
            'faible': '#6c757d',
            'moyenne': '#17a2b8',
            'elevee': '#ffc107',
            'urgent': '#dc3545',
        }
        return format_html(
            '<span style="background-color:{};color:white;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.priorite, '#6c757d'),
            obj.get_priorite_display()
        )
    priorite_colored.short_description = 'Priorité'
    
    def save_model(self, request, obj, form, change):
        if obj.reponse and not obj.date_reponse:
            obj.reponse_par = request.user
            obj.date_reponse = timezone.now()
        super().save_model(request, obj, form, change)
    
    actions = ['marquer_en_cours', 'marquer_traite', 'marquer_ferme']
    
    def marquer_en_cours(self, request, queryset):
        queryset.update(statut='en_cours')
    marquer_en_cours.short_description = "Marquer comme 'En cours'"
    
    def marquer_traite(self, request, queryset):
        queryset.update(statut='traite')
    marquer_traite.short_description = "Marquer comme 'Traité'"
    
    def marquer_ferme(self, request, queryset):
        queryset.update(statut='ferme')
    marquer_ferme.short_description = "Marquer comme 'Fermé'"



# store/admin.py


# ... vos configurations admin existantes ...

@admin.register(DemandeSAV)
class DemandeSAVAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'client_info', 'type_demande_badge', 'motif_badge', 
        'statut_colored', 'numero_commande', 'date_creation'
    ]
    list_filter = ['type_demande', 'statut', 'motif', 'date_creation']
    search_fields = [
        'client__username', 'client__email', 'client__first_name', 
        'client__last_name', 'numero_commande', 'description'
    ]
    readonly_fields = ['date_creation', 'date_modification', 'date_traitement', 'date_validation']
    
    fieldsets = (
        ('Client', {
            'fields': ('client',)
        }),
        ('Commande', {
            'fields': ('commande', 'numero_commande')
        }),
        ('Détails de la demande', {
            'fields': ('type_demande', 'motif', 'description', 'quantite')
        }),
        ('Produits concernés', {
            'fields': ('produits',)
        }),
        ('Pièces jointes', {
            'fields': ('piece_jointe', 'piece_jointe_2')
        }),
        ('Suivi', {
            'fields': ('statut', 'commentaire', 'date_creation', 'date_modification', 'date_traitement', 'date_validation')
        }),
        ('Informations de retour', {
            'fields': ('adresse_retour', 'numero_suivi', 'transporteur'),
            'classes': ('collapse',)
        }),
        ('Remboursement', {
            'fields': ('montant_remboursement', 'remboursement_effectue', 'date_remboursement'),
            'classes': ('collapse',)
        }),
    )

    def client_info(self, obj):
        return format_html(
            '<div><strong>{} {}</strong><br><small style="color:#666;">{}</small></div>',
            obj.client.first_name or '',
            obj.client.last_name or '',
            obj.client.email or ''
        )
    client_info.short_description = 'Client'

    def type_demande_badge(self, obj):
        icons = {
            'retour': '📦',
            'echange': '🔄',
            'garantie': '🛡️',
            'remboursement': '💰',
            'reparation': '🔧',
        }
        colors = {
            'retour': '#ffc107',
            'echange': '#17a2b8',
            'garantie': '#28a745',
            'remboursement': '#6f42c1',
            'reparation': '#fd7e14',
        }
        return format_html(
            '<span style="background:{};color:white;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600;">{} {}</span>',
            colors.get(obj.type_demande, '#6c757d'),
            icons.get(obj.type_demande, '📌'),
            obj.get_type_demande_display()
        )
    type_demande_badge.short_description = 'Type'

    def motif_badge(self, obj):
        colors = {
            'defectueux': '#dc3545',
            'ne_correspond_pas': '#ffc107',
            'mauvais_taille': '#fd7e14',
            'livraison_tardive': '#17a2b8',
            'produit_abime': '#dc3545',
            'autre': '#6c757d',
        }
        return format_html(
            '<span style="background:{};color:white;padding:2px 10px;border-radius:12px;font-size:10px;">{}</span>',
            colors.get(obj.motif, '#6c757d'),
            obj.get_motif_display()
        )
    motif_badge.short_description = 'Motif'

    def statut_colored(self, obj):
        colors = {
            'en_attente': ('#ffc107', '⏳'),
            'validee': ('#17a2b8', '✅'),
            'en_cours': ('#667eea', '🔧'),
            'expediee': ('#28a745', '📦'),
            'terminee': ('#28a745', '🎯'),
            'rejetee': ('#dc3545', '❌'),
        }
        bg, icon = colors.get(obj.statut, ('#6c757d', '📌'))
        return format_html(
            '<span style="background:{};color:white;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600;">{} {}</span>',
            bg, icon, obj.get_statut_display()
        )
    statut_colored.short_description = 'Statut'

    def save_model(self, request, obj, form, change):
        # Si le statut change, enregistrer les dates
        if 'statut' in form.changed_data:
            if obj.statut == 'validee' and not obj.date_validation:
                obj.date_validation = timezone.now()
            elif obj.statut == 'en_cours' and not obj.date_traitement:
                obj.date_traitement = timezone.now()
        super().save_model(request, obj, form, change)

    # Actions en masse
    actions = ['valider_demandes', 'mettre_en_cours', 'terminer_demandes', 'rejeter_demandes']

    def valider_demandes(self, request, queryset):
        for demande in queryset:
            if demande.statut == 'en_attente':
                demande.marquer_validee()
        self.message_user(request, f"{queryset.count()} demande(s) validée(s).")
    valider_demandes.short_description = "Valider les demandes sélectionnées"

    def mettre_en_cours(self, request, queryset):
        for demande in queryset:
            if demande.statut in ['validee', 'en_attente']:
                demande.marquer_en_cours()
        self.message_user(request, f"{queryset.count()} demande(s) mise(s) en cours.")
    mettre_en_cours.short_description = "Mettre en cours"

    def terminer_demandes(self, request, queryset):
        for demande in queryset:
            if demande.statut != 'rejetee':
                demande.marquer_terminee()
        self.message_user(request, f"{queryset.count()} demande(s) terminée(s).")
    terminer_demandes.short_description = "Terminer les demandes"

    def rejeter_demandes(self, request, queryset):
        for demande in queryset:
            if demande.statut == 'en_attente':
                demande.marquer_rejetee()
        self.message_user(request, f"{queryset.count()} demande(s) rejetée(s).")
    rejeter_demandes.short_description = "Rejeter les demandes"

@admin.register(DocumentSAV)
class DocumentSAVAdmin(admin.ModelAdmin):
    list_display = ['id', 'demande_link', 'type_document_badge', 'date_creation', 'est_envoye_badge']
    list_filter = ['type_document', 'est_envoye', 'date_creation']
    search_fields = ['demande__client__username', 'demande__numero_commande']

    def demande_link(self, obj):
        return format_html(
            '<a href="/admin/store/demandesav/{}/change/" style="color:#007185;">Demande #{} - {}</a>',
            obj.demande.id,
            obj.demande.id,
            obj.demande.client.username
        )
    demande_link.short_description = 'Demande'

    def type_document_badge(self, obj):
        colors = {
            'retour': '#ffc107',
            'echange': '#17a2b8',
            'reparation': '#fd7e14',
            'remboursement': '#28a745',
        }
        return format_html(
            '<span style="background:{};color:white;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.type_document, '#6c757d'),
            obj.get_type_document_display()
        )
    type_document_badge.short_description = 'Type'

    def est_envoye_badge(self, obj):
        if obj.est_envoye:
            return mark_safe('<span style="color:#28a745;">✅ Envoyé</span>')
        return mark_safe('<span style="color:#ffc107;">⏳ Non envoyé</span>')
    est_envoye_badge.short_description = 'Statut'