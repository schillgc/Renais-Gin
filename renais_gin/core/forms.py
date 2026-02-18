"""
Forms for Renais Gin core application.
"""

from django import forms
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from .models import UserPDFDocument, KarmaPledge, CommunityCircle, UserProfile, Bottle


class PDFUploadForm(forms.ModelForm):
    """Form for uploading PDF documents"""

    class Meta:
        model = UserPDFDocument
        fields = ['title', 'description', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document Title',
                'maxlength': '255'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of this document',
                'maxlength': '500'
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': '.pdf'
            }),
        }
        labels = {
            'pdf_file': 'PDF File (max 10MB)'
        }

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            # Check file size (10MB limit)
            if pdf_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB.")

            # Check file extension
            if not pdf_file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")

            # Check content type
            if pdf_file.content_type != 'application/pdf':
                raise forms.ValidationError("Invalid file type. Please upload a PDF file.")

        return pdf_file


class PledgeForm(forms.ModelForm):
    """Form for submitting karma pledges"""

    class Meta:
        model = KarmaPledge
        fields = ['pledge_text', 'impact_plan', 'impact_type']
        widgets = {
            'pledge_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'I pledge to use this rebate to create positive impact by...',
                'data-max-length': '500'
            }),
            'impact_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "I'll accomplish this by taking these specific actions...",
                'data-max-length': '500'
            }),
            'impact_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'pledge_text': 'Your Pledge',
            'impact_plan': 'Implementation Plan',
            'impact_type': 'Impact Category'
        }

    def clean_pledge_text(self):
        text = self.cleaned_data.get('pledge_text', '').strip()
        if len(text) < 20:
            raise forms.ValidationError("Pledge must be at least 20 characters long.")
        if len(text) > 500:
            raise forms.ValidationError("Pledge must be less than 500 characters.")
        return text

    def clean_impact_plan(self):
        plan = self.cleaned_data.get('impact_plan', '').strip()
        if len(plan) < 20:
            raise forms.ValidationError("Impact plan must be at least 20 characters long.")
        if len(plan) > 500:
            raise forms.ValidationError("Impact plan must be less than 500 characters.")
        return plan


class CommunityCircleForm(forms.ModelForm):
    """Form for creating community circles"""

    focus_areas = forms.MultipleChoiceField(
        choices=[
            ('environmental', 'Environmental'),
            ('community', 'Community'),
            ('education', 'Education'),
            ('arts', 'Arts & Culture'),
            ('health', 'Health & Wellness'),
            ('other', 'Other'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        help_text="Select the focus areas for your community circle"
    )

    class Meta:
        model = CommunityCircle
        fields = ['name', 'location', 'description', 'focus_areas']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Circle Name (e.g., "Renais Gin London Circle")',
                'maxlength': '100'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country (e.g., "London, UK")',
                'maxlength': '100'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What is your circle about? What kind of impact do you want to create?',
                'maxlength': '1000'
            }),
        }
        labels = {
            'name': 'Circle Name',
            'location': 'Location',
            'description': 'Description',
            'focus_areas': 'Focus Areas'
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 3:
            raise forms.ValidationError("Circle name must be at least 3 characters long.")
        return name

    def clean_location(self):
        location = self.cleaned_data.get('location', '').strip()
        if len(location) < 3:
            raise forms.ValidationError("Please provide a valid location.")
        return location


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""

    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )
    country = forms.CharField(  # Add this field for the User model
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Country'
        }),
        label='Country'
    )

    class Meta:
        model = UserProfile
        fields = []  # Remove 'country' from here since it's on the User model, not UserProfile

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            self.fields['country'].initial = self.user.country

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(id=self.user.id).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            # Update user fields
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.country = self.cleaned_data['country']  # Update country on User model
            if commit:
                self.user.save()

        if commit:
            profile.save()
        return profile


class ValidationForm(forms.Form):
    """Form for validating community pledges"""

    approval = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'data-toggle': 'toggle',
            'data-on': 'Approve',
            'data-off': 'Reject',
            'data-onstyle': 'success',
            'data-offstyle': 'danger'
        }),
        label='Approve this pledge?'
    )
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional: Add your feedback, suggestions, or reasons for approval/rejection...',
            'maxlength': '500'
        }),
        label='Comments (Optional)'
    )

    def clean_comments(self):
        comments = self.cleaned_data.get('comments', '').strip()
        if len(comments) > 500:
            raise forms.ValidationError("Comments must be less than 500 characters.")
        return comments


class BottleRegistrationForm(forms.Form):
    """Form for registering bottles"""

    bottle_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter bottle ID (e.g., RG2023ABC123)',
            'autocomplete': 'off',
            'spellcheck': 'false'
        }),
        label='Bottle ID',
        help_text='Enter the unique ID found on your Renais Gin bottle or QR code'
    )

    def clean_bottle_id(self):
        bottle_id = self.cleaned_data.get('bottle_id', '').strip().upper()

        if not bottle_id:
            raise forms.ValidationError("Please enter a bottle ID.")

        # Basic format validation (adjust based on your bottle ID format)
        if len(bottle_id) < 5:
            raise forms.ValidationError("Bottle ID appears to be too short.")

        # Check if bottle exists in system
        from .models import Bottle
        try:
            bottle = Bottle.objects.get(bottle_id=bottle_id)
        except Bottle.DoesNotExist:
            raise forms.ValidationError("This bottle ID does not exist in our system.")

        # Check if already registered
        if bottle.registered:
            raise forms.ValidationError("This bottle has already been registered.")

        return bottle_id


class BottleSearchForm(forms.Form):
    """Form for searching bottles"""

    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by bottle ID or batch ID...',
            'autocomplete': 'off'
        }),
        label='Search Bottles'
    )

    status_filter = forms.ChoiceField(
        choices=[
            ('', 'All Statuses'),
            ('unregistered', 'Unregistered'),
            ('registered', 'Registered'),
            ('pledged', 'Pledged'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Filter by Status'
    )


class PledgeSearchForm(forms.Form):
    """Form for searching pledges"""

    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by pledge text or impact plan...',
            'autocomplete': 'off'
        }),
        label='Search Pledges'
    )

    status_filter = forms.ChoiceField(
        choices=[
            ('', 'All Statuses'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('needs_review', 'Needs Review'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Filter by Status'
    )

    impact_type_filter = forms.ChoiceField(
        choices=[
            ('', 'All Impact Types'),
            ('environmental', 'Environmental'),
            ('community', 'Community'),
            ('education', 'Education'),
            ('other', 'Other'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Filter by Impact Type'
    )


class CommunityCircleSearchForm(forms.Form):
    """Form for searching community circles"""

    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by circle name or location...',
            'autocomplete': 'off'
        }),
        label='Search Circles'
    )

    location_filter = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by location...',
            'autocomplete': 'off'
        }),
        label='Filter by Location'
    )


class ContactForm(forms.Form):
    """Form for contacting support"""

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name'
        }),
        label='Your Name'
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        label='Email Address'
    )

    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject of your message'
        }),
        label='Subject'
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Please describe your issue or question in detail...',
            'maxlength': '1000'
        }),
        label='Message'
    )

    urgency = forms.ChoiceField(
        choices=[
            ('low', 'Low - General question'),
            ('medium', 'Medium - Need help with something'),
            ('high', 'High - Urgent issue affecting my account'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Urgency Level',
        initial='medium'
    )

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 10:
            raise forms.ValidationError("Please provide a more detailed message.")
        if len(message) > 1000:
            raise forms.ValidationError("Message must be less than 1000 characters.")
        return message


class ImpactReportForm(forms.Form):
    """Form for generating impact reports"""

    report_type = forms.ChoiceField(
        choices=[
            ('user', 'Personal Impact Report'),
            ('circle', 'Community Circle Report'),
            ('movement', 'Global Movement Report'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Report Type'
    )

    time_period = forms.ChoiceField(
        choices=[
            ('7days', 'Last 7 Days'),
            ('30days', 'Last 30 Days'),
            ('90days', 'Last 90 Days'),
            ('1year', 'Last Year'),
            ('all', 'All Time'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Time Period',
        initial='30days'
    )

    include_details = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Include detailed breakdown'
    )

    include_charts = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Include charts and graphs'
    )


class PasswordChangeForm(forms.Form):
    """Form for changing password"""

    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your current password'
        }),
        label='Current Password'
    )

    new_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password (min 8 characters)'
        }),
        label='New Password',
        help_text='Password must be at least 8 characters long.'
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        label='Confirm New Password'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Your current password is incorrect.")
        return current_password

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("The new passwords do not match.")
        return confirm_password

    def save(self):
        new_password = self.cleaned_data.get('new_password')
        self.user.set_password(new_password)
        self.user.save()
