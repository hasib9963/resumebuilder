from django import forms
from .models import Resume

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = [
            'title', 'full_name', 'email', 'phone', 'profile_image', 
            'summary', 'skills', 'expertise', 'languages', 'references',
            'experience', 'education', 'address', 'linkedin', 'portfolio'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'e.g., Senior Software Engineer'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': '+1 (555) 123-4567'
            }),
            'summary': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'Describe your professional background and career objectives...'
            }),
            'skills': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'Python, Django, JavaScript, Project Management, etc.'
            }),
            'expertise': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'Web Development, Database Design, Team Leadership, etc.'
            }),
            'languages': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'English | Fluent\nSpanish | Intermediate\nFrench | Basic'
            }),
            'references': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'John Smith | Senior Manager | +1 (555) 123-4567 | john.smith@company.com'
            }),
            'experience': forms.Textarea(attrs={
                'rows': 6,
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'Format each experience as:\nJob Title | Company | Date Range | Description\nSenior Developer | Tech Company | 2020-2023 | Developed web applications...'
            }),
            'education': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'Format each education as:\nDegree | Institution | Date Range | Details\nBSc Computer Science | University Name | 2018-2022 | GPA: 3.8/4.0'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'Your complete address'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'portfolio': forms.URLInput(attrs={
                'class': 'form-input w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500',
                'placeholder': 'https://yourportfolio.com'
            }),
        }
        help_texts = {
            'experience': 'Use the format: Job Title | Company | Dates | Description (one per line)',
            'education': 'Use the format: Degree | Institution | Dates | Details (one per line)',
            'languages': 'Use the format: Language | Proficiency Level (one per line)',
            'references': 'Use the format: Name | Profession | Phone | Email (one per line)',
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if len(phone) < 10:
                raise forms.ValidationError("Please enter a valid phone number.")
        return phone

    def clean_summary(self):
        summary = self.cleaned_data.get('summary')
        if summary and len(summary.split()) < 10:
            raise forms.ValidationError("Summary should be at least 10 words long.")
        return summary