from allauth.account.forms import SignupForm
from django import forms

from administration.models import Temoignage
from public.models import User, Meeting, Comment


class CustomSignupForm(SignupForm):
    nom = forms.CharField(
        max_length=50, required=True, label="Nom",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre nom"})
    )
    prenom = forms.CharField(
        max_length=100, required=True, label="Prénom",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre prénom"})
    )
    contact = forms.CharField(
        max_length=100, required=True, label="Contact",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre contact"})
    )
    role = forms.ChoiceField(
        choices=User.ROLES, required=True, label="Rôle",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    company = forms.CharField(
        max_length=255, required=False, label="Entreprise",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre entreprise"})
    )
    sector = forms.CharField(
        max_length=255, required=False, label="Secteur d'activité",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre secteur"})
    )
    description = forms.CharField(
        required=False, label="Description",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Décrivez-vous"})
    )

    def save(self, request):
        user = super().save(request)
        user.nom = self.cleaned_data["nom"]
        user.prenom = self.cleaned_data["prenom"]
        user.contact = self.cleaned_data["contact"]
        user.role = self.cleaned_data["role"]
        user.company = self.cleaned_data["company"]
        user.sector = self.cleaned_data["sector"]
        user.description = self.cleaned_data["description"]
        user.save()
        return user


class MeetingForm(forms.ModelForm):
    sponsor = forms.ModelChoiceField(
        queryset=User.objects.filter(role="sponsor"),
        label="Choisissez un sponsor",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        label="Date et heure de début"
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        label="Date et heure de fin"
    )

    class Meta:
        model = Meeting
        fields = ["sponsor", "start_time", "end_time"]

    def clean(self):
        cleaned_data = super().clean()
        participant = self.instance.participant if self.instance.pk else self.initial.get('participant')

        # Vérifier que le participant ne dépasse pas 5 sponsors
        if Meeting.objects.filter(participant=participant).count() >= 5:
            raise forms.ValidationError("Vous avez atteint la limite de 5 sponsors.")

        return cleaned_data


class TemoignageForm(forms.ModelForm):
    class Meta:
        model = Temoignage
        fields = ['nom', 'email', 'telephone', 'temoignage', 'note']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre téléphone'}),
            'temoignage': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre témoignage'}),
            'note': forms.Select(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'email', 'content']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre Nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre Email'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre Commentaire', 'rows': 4}),
        }
