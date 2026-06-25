from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Catégorie
class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name_plural = "Catégories"


# Adresse
class Adresse(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    nom_complet = models.CharField(max_length=200)
    rue = models.CharField(max_length=200)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=20)
    pays = models.CharField(max_length=100, default='France')
    telephone = models.CharField(max_length=20)
    est_defaut = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nom_complet} - {self.rue}, {self.ville}"

    class Meta:
        verbose_name_plural = "Adresses"


# Produit
class Produit(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    quantite_stock = models.IntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


# Panier
class Panier(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)

    def total_item(self):
        return self.produit.prix * self.quantite

    def __str__(self):
        return f"{self.utilisateur.username} - {self.produit.nom}"


# Commande
class Commande(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('en_preparation', 'En préparation'),
        ('annulee', 'Annulée'),
    ]

    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    adresse = models.ForeignKey(Adresse, on_delete=models.SET_NULL, null=True, blank=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Commande #{self.id} - {self.utilisateur.username}"


# Détail de commande
class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def total_ligne(self):
        return (self.quantite or 0) * (self.prix_unitaire or 0)

    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"


# Paiement
class Paiement(models.Model):
    MODES = [
        ('carte', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('virement', 'Virement bancaire'),
    ]

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
    mode_paiement = models.CharField(max_length=20, choices=MODES, default='carte')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('reussi', 'Réussi'),
        ('echoue', 'Échoué'),
        ('rembourse', 'Remboursé'),
    ], default='en_attente')
    reference = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Paiement #{self.reference} - {self.commande}"
    





# Reclamation

# class Reclamation(models.Model):

#     STATUT_CHOICES = [
#         ('en_cours', 'En cours'),
#         ('resolue', 'Résolue'),
#         ('rejetee', 'Rejetée'),
#     ]

#     client = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE
#     )

#     sujet = models.CharField(max_length=200)

#     description = models.TextField()

#     statut = models.CharField(
#         max_length=20,
#         choices=STATUT_CHOICES,
#         default='En cours'
#     )

#     date_creation = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.sujet


class Reclamation(models.Model):
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),      # (valeur stockée, valeur affichée)
        ('resolue', 'Résolue'),
        ('rejetee', 'Rejetée'),
    ]

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reclamations'
    )

    sujet = models.CharField(max_length=200)
    description = models.TextField()

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_cours'
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sujet
    

# SupportMessage
class SupportMessage(models.Model):
    STATUS_CHOICES = [
        ('non_lu', 'Non lu'),
        ('en_cours', 'En cours'),
        ('traite', 'Traité'),
        ('ferme', 'Fermé'),
    ]

    PRIORITY_CHOICES = [
        ('faible', 'Faible'),
        ('moyenne', 'Moyenne'),
        ('elevee', 'Élevée'),
        ('urgent', 'Urgent'),
    ]

    # Informations du client
    nom_complet = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True, null=True)
    
    # Message
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='non_lu')
    priorite = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='moyenne')
    
    # Réponse du support
    reponse = models.TextField(blank=True, null=True)
    reponse_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reponses_support')
    date_reponse = models.DateTimeField(null=True, blank=True)
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Client connecté ou non
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages_support')
    
    def __str__(self):
        return f"{self.sujet} - {self.nom_complet}"
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Message Support"
        verbose_name_plural = "Messages Support"





##SAV



# ... vos modèles existants ...

class DemandeSAV(models.Model):
    TYPE_CHOICES = [
        ('retour', 'Retour produit'),
        ('echange', 'Échange produit'),
        ('garantie', 'Garantie'),
        ('remboursement', 'Remboursement'),
        ('reparation', 'Réparation'),
    ]

    STATUT_CHOICES = [
        ('en_attente', 'En attente de validation'),
        ('validee', 'Validée'),
        ('en_cours', 'En cours de traitement'),
        ('expediee', 'Expédiée'),
        ('terminee', 'Terminée'),
        ('rejetee', 'Rejetée'),
    ]

    MOTIF_CHOICES = [
        ('defectueux', 'Produit defectueux'),
        ('ne_correspond_pas', 'Ne correspond pas à la description'),
        ('mauvais_taille', 'Mauvaise taille / couleur'),
        ('livraison_tardive', 'Livraison tardive'),
        ('produit_abime', 'Produit abîmé / endommagé'),
        ('autre', 'Autre motif'),
    ]

    # Informations client
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demandes_sav')
    
    # Commande concernée
    commande = models.ForeignKey('Commande', on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes_sav')
    numero_commande = models.CharField(max_length=50, blank=True, null=True)
    
    # Détails de la demande
    type_demande = models.CharField(max_length=20, choices=TYPE_CHOICES)
    motif = models.CharField(max_length=30, choices=MOTIF_CHOICES, default='autre')
    description = models.TextField(help_text="Décrivez votre demande en détails")
    
    # Produits concernés
    produits = models.ManyToManyField('Produit', blank=True, related_name='demandes_sav')
    quantite = models.IntegerField(default=1)
    
    # Pièces jointes
    piece_jointe = models.FileField(upload_to='sav/', blank=True, null=True)
    piece_jointe_2 = models.FileField(upload_to='sav/', blank=True, null=True)
    
    # Statut et suivi
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    commentaire = models.TextField(blank=True, null=True, help_text="Commentaire du support")
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_traitement = models.DateTimeField(blank=True, null=True)
    date_validation = models.DateTimeField(blank=True, null=True)
    
    # Informations de retour
    adresse_retour = models.TextField(blank=True, null=True)
    numero_suivi = models.CharField(max_length=100, blank=True, null=True)
    transporteur = models.CharField(max_length=50, blank=True, null=True)
    
    # Remboursement
    montant_remboursement = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remboursement_effectue = models.BooleanField(default=False)
    date_remboursement = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_type_demande_display()} - {self.client.username} - {self.date_creation.strftime('%d/%m/%Y')}"

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Demande SAV"
        verbose_name_plural = "Demandes SAV"

    def marquer_validee(self):
        self.statut = 'validee'
        self.date_validation = timezone.now()
        self.save()

    def marquer_en_cours(self):
        self.statut = 'en_cours'
        self.date_traitement = timezone.now()
        self.save()

    def marquer_terminee(self):
        self.statut = 'terminee'
        self.save()

    def marquer_rejetee(self):
        self.statut = 'rejetee'
        self.save()

    def est_traitable(self):
        return self.statut in ['en_attente', 'validee']

class DocumentSAV(models.Model):
    DEMANDE_CHOICES = [
        ('retour', 'Bon de retour'),
        ('echange', 'Bon d\'échange'),
        ('reparation', 'Bon de réparation'),
        ('remboursement', 'Avis de remboursement'),
    ]

    demande = models.ForeignKey(DemandeSAV, on_delete=models.CASCADE, related_name='documents')
    type_document = models.CharField(max_length=20, choices=DEMANDE_CHOICES)
    fichier = models.FileField(upload_to='documents_sav/')
    date_creation = models.DateTimeField(auto_now_add=True)
    est_envoye = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_type_document_display()} - {self.demande.id}"

    class Meta:
        ordering = ['-date_creation']