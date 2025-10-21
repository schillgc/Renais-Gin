"""
Forms for Renais Gin core application.
"""

from django import forms
from django.core.validators import MinLengthValidator
from .models import Bottle, KarmaPledge, CommunityCircle


class BottleRegistrationForm(forms.Form):
    """Form for registering a new bottle."""

    bottle_id = forms.CharField(
        max_length=50,
        required=True,
        label="Bottle ID",
        help_text="Unique identifier found on your bottle",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., BOT_2023_001'
        })
    )

    batch_id = forms.CharField(
        max_length=100,
        required=True,
        label="Batch ID",
        help_text="Production batch identifier",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., BATCH_123'
        })
    )

    production_date = forms.DateField(
        required=True,
        label="Production Date",
        help_text="When the bottle was produced",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    terroir_region = forms.CharField(
        max_length=100,
        required=False,
        initial="Chablis",
        label="Terroir Region",
        help_text="Geographical origin of the grapes",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Chablis'
        })
    )

    terroir_vintage = forms.CharField(
        max_length=10,
        required=False,
        initial="2022",
        label="Vintage",
        help_text="Year of grape harvest",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2022'
        })
    )

    qr_code = forms.ImageField(
        required=False,
        label="QR Code Image",
        help_text="Optional: Upload a picture of the bottle's QR code",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    def clean_bottle_id(self):
        """Validate bottle ID uniqueness."""
        bottle_id = self.cleaned_data['bottle_id']
        if Bottle.objects.filter(bottle_id=bottle_id).exists():
            raise forms.ValidationError("This bottle ID is already registered.")
        return bottle_id

    def clean_production_date(self):
        """Validate production date is not in the future."""
        production_date = self.cleaned_data['production_date']
        from django.utils import timezone
        if production_date > timezone.now().date():
            raise forms.ValidationError("Production date cannot be in the future.")
        return production_date


class PledgeSubmissionForm(forms.Form):
    """Form for submitting a karma pledge."""

    bottle_id = forms.CharField(
        max_length=50,
        required=True,
        label="Select Bottle",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    pledge_text = forms.CharField(
        required=True,
        label="Your Pledge Statement",
        help_text="Be specific about how you'll use the $5 rebate for positive impact",
        validators=[MinLengthValidator(20)],
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'I pledge to use this $5 rebate to...'
        })
    )

    impact_plan = forms.CharField(
        required=True,
        label="Impact Plan",
        help_text="Describe your specific plan for implementing this pledge",
        validators=[MinLengthValidator(30)],
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Here is how I will make it happen...'
        })
    )

    def __init__(self, *args, **kwargs):
        """Initialize form with available bottles."""
        available_bottles = kwargs.pop('available_bottles', None)
        super().__init__(*args, **kwargs)

        if available_bottles:
            bottle_choices = [
                (bottle.bottle_id, f"{bottle.bottle_id} - {bottle.terroir_region} ({bottle.terroir_vintage})")
                for bottle in available_bottles
            ]
            self.fields['bottle_id'].widget.choices = bottle_choices
        else:
            self.fields['bottle_id'].widget.choices = [('', 'No bottles available')]

    def clean_pledge_text(self):
        """Validate pledge text quality."""
        pledge_text = self.cleaned_data['pledge_text']
        words = pledge_text.split()

        if len(words) < 10:
            raise forms.ValidationError("Pledge should be more detailed (minimum 10 words).")

        # Check for meaningful content
        meaningful_indicators = ['plant', 'help', 'support', 'create', 'improve', 'donate']
        if not any(indicator in pledge_text.lower() for indicator in meaningful_indicators):
            raise forms.ValidationError("Pledge should clearly state a positive action.")

        return pledge_text

    def clean_impact_plan(self):
        """Validate impact plan specificity."""
        impact_plan = self.cleaned_data['impact_plan']
        words = impact_plan.split()

        if len(words) < 15:
            raise forms.ValidationError("Impact plan should be more specific (minimum 15 words).")

        # Check for actionable content
        actionable_indicators = ['will', 'plan to', 'going to', 'organize', 'coordinate', 'partner with']
        if not any(indicator in impact_plan.lower() for indicator in actionable_indicators):
            raise forms.ValidationError("Impact plan should include specific actions and timeline.")

        return impact_plan


class CommunityCircleForm(forms.ModelForm):
    """Form for creating a community circle."""

    class Meta:
        model = CommunityCircle
        fields = ['name', 'location', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Pacific Northwest Greens'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Seattle, WA'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your community circle\'s mission and focus areas...'
            }),
        }

    focus_areas = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('environmental', 'Environmental Conservation'),
            ('community', 'Community Development'),
            ('education', 'Education & Awareness'),
            ('sustainable', 'Sustainable Living'),
            ('food', 'Food Security'),
            ('health', 'Community Health'),
            ('arts', 'Arts & Culture'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        help_text="Select the focus areas for your community circle"
    )

    def clean_name(self):
        """Validate circle name uniqueness."""
        name = self.cleaned_data['name']
        if CommunityCircle.objects.filter(name=name, is_active=True).exists():
            raise forms.ValidationError("A community circle with this name already exists.")
        return name


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        from .models import UserProfile
        model = UserProfile
        fields = ['country', 'city', 'bio', 'avatar', 'email_notifications']
        widgets = {
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself and your sustainability interests...'
            }),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        """Initialize form with user data."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        """Save profile and user data."""
        profile = super().save(commit=False)

        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()

        if commit:
            profile.save()

        return profile
