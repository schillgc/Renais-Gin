from django import forms

from .models import Bottle, CommunityCircle, KarmaPledge, UserPDFDocument


class BottleRegistrationForm(forms.Form):
    bottle_id = forms.CharField(
        max_length=100,
        strip=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the unique bottle ID',
        }),
    )

    def clean_bottle_id(self):
        bottle_id = self.cleaned_data['bottle_id']
        if Bottle.objects.filter(bottle_id=bottle_id, registered=True).exists():
            raise forms.ValidationError('This bottle has already been registered.')
        return bottle_id


class PledgeSubmissionForm(forms.ModelForm):
    class Meta:
        model = KarmaPledge
        fields = ['pledge_text', 'impact_plan']
        widgets = {
            'pledge_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': 2000,
                'data-max-length': '2000',
            }),
            'impact_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': 4000,
            }),
        }

    def clean(self):
        cleaned = super().clean()
        pledge_text = (cleaned.get('pledge_text') or '').strip()
        impact_plan = (cleaned.get('impact_plan') or '').strip()
        if len(pledge_text) < 20:
            self.add_error('pledge_text', 'Describe your pledge in at least 20 characters.')
        if len(impact_plan) < 20:
            self.add_error('impact_plan', 'Describe your impact plan in at least 20 characters.')
        cleaned['pledge_text'] = pledge_text
        cleaned['impact_plan'] = impact_plan
        return cleaned


class CommunityCircleForm(forms.ModelForm):
    class Meta:
        model = CommunityCircle
        fields = ['name', 'location', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = UserPDFDocument
        fields = ['title', 'description', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            if pdf_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB.")

            if not pdf_file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")

            header = pdf_file.read(5)
            pdf_file.seek(0)
            if header != b'%PDF-':
                raise forms.ValidationError("The uploaded file is not a valid PDF.")

        return pdf_file
