

from django import forms
from .models import Reclamation, SupportMessage, DemandeSAV


class ReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        fields = ['sujet', 'description']
        widgets = {
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le sujet de votre réclamation',
                'style': 'font-size:14px;border-radius:4px;border:1px solid #ddd;padding:8px 12px;width:100%;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez votre problème en détails...',
                'style': 'font-size:14px;border-radius:4px;border:1px solid #ddd;padding:8px 12px;width:100%;'
            })
        }


        # SupportMessage


# class SupportMessageForm(forms.ModelForm):
#     class Meta:
#         model = SupportMessage
#         fields = ['nom_complet', 'email', 'telephone', 'sujet', 'message']
#         widgets = {
#             'nom_complet': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Votre nom complet',
#                 'style': 'font-size:14px;border-radius:8px;border:1px solid #ddd;padding:10px 15px;'
#             }),
#             'email': forms.EmailInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Votre adresse email',
#                 'style': 'font-size:14px;border-radius:8px;border:1px solid #ddd;padding:10px 15px;'
#             }),
#             'telephone': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Votre numéro de téléphone (optionnel)',
#                 'style': 'font-size:14px;border-radius:8px;border:1px solid #ddd;padding:10px 15px;'
#             }),
#             'sujet': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Sujet de votre message',
#                 'style': 'font-size:14px;border-radius:8px;border:1px solid #ddd;padding:10px 15px;'
#             }),
#             'message': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 5,
#                 'placeholder': 'Décrivez votre demande en détails...',
#                 'style': 'font-size:14px;border-radius:8px;border:1px solid #ddd;padding:10px 15px;resize:vertical;'
#             })
#         }
#         labels = {
#             'nom_complet': 'Nom complet',
#             'email': 'Email',
#             'telephone': 'Téléphone (optionnel)',
#             'sujet': 'Sujet',
#             'message': 'Message',
#         }

class SupportMessageForm(forms.ModelForm):
    class Meta:
        model = SupportMessage
        fields = ['nom_complet', 'email', 'telephone', 'sujet', 'message']
        widgets = {
            'nom_complet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre adresse email'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre numéro de téléphone (optionnel)'
            }),
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sujet de votre message'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Décrivez votre demande en détails...'
            })
        }







class DemandeSAVForm(forms.ModelForm):
    class Meta:
        model = DemandeSAV
        fields = [
            'type_demande', 'motif', 'numero_commande', 'description',
            'quantite', 'piece_jointe', 'piece_jointe_2'
        ]
        widgets = {
            'type_demande': forms.Select(attrs={
                'class': 'form-select',
                'style': 'border-radius:8px;padding:10px;border:1px solid #ddd;'
            }),
            'motif': forms.Select(attrs={
                'class': 'form-select',
                'style': 'border-radius:8px;padding:10px;border:1px solid #ddd;'
            }),
            'numero_commande': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: CMD-2024-00123',
                'style': 'border-radius:8px;padding:10px;border:1px solid #ddd;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez votre demande en détails...',
                'style': 'border-radius:8px;padding:10px;border:1px solid #ddd;resize:vertical;'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'style': 'border-radius:8px;padding:10px;border:1px solid #ddd;'
            }),
            'piece_jointe': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf,.doc,.docx',
                'style': 'border-radius:8px;padding:10px;border:1px solid #ddd;'
            }),
            'piece_jointe_2': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf,.doc,.docx',
                'style': 'border-radius:8px;padding:10px;border:1px solid #ddd;'
            }),
        }
        labels = {
            'type_demande': 'Type de demande *',
            'motif': 'Motif *',
            'numero_commande': 'Numéro de commande *',
            'description': 'Description *',
            'quantite': 'Quantité concernée *',
            'piece_jointe': 'Pièce jointe (facultatif)',
            'piece_jointe_2': 'Pièce jointe supplémentaire (facultatif)',
        }
        help_texts = {
            'piece_jointe': 'Formats acceptés : JPG, PNG, PDF, DOC',
            'numero_commande': 'Trouvez ce numéro dans votre email de confirmation',
        }