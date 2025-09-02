from django import forms
from .models import UserPDFDocument


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
            # Check file size (max 10MB)
            if pdf_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB.")

            # Check file extension
            if not pdf_file.name.endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")

        return pdf_file
